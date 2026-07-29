import os
import zipfile
import re
import html
import json
import xml.etree.ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace('w', W_NS)

def sanitize_xml_string(xml_str: str) -> str:
    return re.sub(r'&(?!(amp|lt|gt|quot|apos);)', '&amp;', xml_str)

def format_tech_item(item):
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return item.get("name") or item.get("technology") or item.get("title") or str(item)
    return str(item)

def create_w_p(text: str, is_heading: bool = False, is_subheading: bool = False, is_bullet: bool = False) -> ET.Element:
    p = ET.Element(f"{{{W_NS}}}p")
    pPr = ET.SubElement(p, f"{{{W_NS}}}pPr")
    
    if is_heading:
        pStyle = ET.SubElement(pPr, f"{{{W_NS}}}pStyle")
        pStyle.set(f"{{{W_NS}}}val", "Heading1")
        spacing = ET.SubElement(pPr, f"{{{W_NS}}}spacing")
        spacing.set(f"{{{W_NS}}}before", "240")
        spacing.set(f"{{{W_NS}}}after", "120")
    elif is_subheading:
        pStyle = ET.SubElement(pPr, f"{{{W_NS}}}pStyle")
        pStyle.set(f"{{{W_NS}}}val", "Heading2")
        spacing = ET.SubElement(pPr, f"{{{W_NS}}}spacing")
        spacing.set(f"{{{W_NS}}}before", "160")
        spacing.set(f"{{{W_NS}}}after", "80")
    elif is_bullet:
        spacing = ET.SubElement(pPr, f"{{{W_NS}}}spacing")
        spacing.set(f"{{{W_NS}}}before", "40")
        spacing.set(f"{{{W_NS}}}after", "40")

    r = ET.SubElement(p, f"{{{W_NS}}}r")
    rPr = ET.SubElement(r, f"{{{W_NS}}}rPr")
    
    if is_heading or is_subheading:
        b = ET.SubElement(rPr, f"{{{W_NS}}}b")

    t = ET.SubElement(r, f"{{{W_NS}}}t")
    t.text = text
    return p

def extract_candidate_languages(json_data: dict) -> list:
    langs = []
    for m in json_data.get("mother_languages", []):
        name = m.get("name") or m.get("language") or ""
        level = m.get("written_name") or m.get("spoken_label") or "Native"
        if name:
            langs.append(f"{name} ({level})")

    for o in json_data.get("other_languages", []):
        name = o.get("name") or o.get("language") or ""
        level = o.get("written_name") or o.get("spoken_label") or "Fluent"
        if name:
            langs.append(f"{name} ({level})")

    if not langs and json_data.get("languages"):
        for l in json_data["languages"]:
            if isinstance(l, str):
                langs.append(l)
            elif isinstance(l, dict):
                langs.append(f"{l.get('name') or l.get('language')} ({l.get('proficiency') or l.get('level', 'Fluent')})")

    return langs

def replace_dynamic_contact_regex(xml_str: str, json_data: dict) -> str:
    consultant = json_data.get("consultant", {})
    name = consultant.get("name", "")
    surname = consultant.get("surname", "")
    fullname = f"{name} {surname}".strip()
    email = consultant.get("email", "")
    phone = consultant.get("phone", "")
    city = consultant.get("city", "")
    country = consultant.get("country", "")
    location = f"{city}, {country}".strip(", ")
    linkedin = consultant.get("linkedin", "")
    work_auth = consultant.get("work_authorization") or (f"{consultant.get('nationality')} Citizen" if consultant.get('nationality') else "")

    if email:
        xml_str = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', html.escape(email, quote=False), xml_str)

    if linkedin:
        xml_str = re.sub(r'(?i)(?:https?://)?(?:[a-z0-9-]+\.)*linkedin\.com/[^\s<"\']+', html.escape(linkedin, quote=False), xml_str)

    if phone:
        xml_str = re.sub(r'(\+\d{1,4}[\s.-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}', html.escape(phone, quote=False), xml_str)

    if location:
        xml_str = re.sub(r'Aveiro\s*,\s*Portugal', html.escape(location, quote=False), xml_str)
        xml_str = re.sub(r'Itapema,\s*SC', html.escape(location, quote=False), xml_str)
        if city:
            xml_str = re.sub(r'(?i)\baveiro\b', html.escape(city, quote=False), xml_str)
            xml_str = re.sub(r'(?i)\bitapema\b', html.escape(city, quote=False), xml_str)
        if country:
            xml_str = re.sub(r'(?i)\bportugal\b', html.escape(country, quote=False), xml_str)

    if fullname:
        xml_str = re.sub(r'(?i)elton\s+machado', html.escape(fullname, quote=False), xml_str)
        if name:
            xml_str = re.sub(r'(?i)\belton\b', html.escape(name, quote=False), xml_str)
        if surname:
            xml_str = re.sub(r'(?i)\bmachado\b', html.escape(surname, quote=False), xml_str)

    if work_auth:
        xml_str = re.sub(r'(?i)EU\s+Citizen[^\n<"\']*', html.escape(work_auth, quote=False), xml_str)
        xml_str = re.sub(r'(?i)Belgian,\s*Portuguese,\s*Brazilian', html.escape(work_auth, quote=False), xml_str)
    else:
        xml_str = re.sub(r'(?i)Work\s+Authorization:[^\n<"\']*', '', xml_str)
        xml_str = re.sub(r'(?i)EU\s+Citizen[^\n<"\']*', '', xml_str)
        xml_str = re.sub(r'(?i)Belgian,\s*Portuguese,\s*Brazilian', '', xml_str)

    return xml_str

def safe_populate_document_xml(doc_xml: str, json_data: dict) -> str:
    """
    Purga 100% de tabelas e parágrafos de tecnologias antigas (ex: NSX, VMware NSX, Active Directory, LDAP...)
    e reconstrói as seções EXCLUSIVAMENTE a partir do feed JSON fornecido.
    """
    consultant = json_data.get("consultant", {})
    fullname = f"{consultant.get('name', '')} {consultant.get('surname', '')}".strip()
    title = json_data.get("present_job_title", "")
    summary = json_data.get("about") or json_data.get("cv_summary") or ""
    
    exps = json_data.get("work_experiences", [])
    educations = json_data.get("educations", [])
    certifications = json_data.get("certifications", [])
    languages = extract_candidate_languages(json_data)
    top_techs_raw = json_data.get("top_technologies") or []
    top_techs = [format_tech_item(t) for t in top_techs_raw]

    try:
        doc_xml = replace_dynamic_contact_regex(doc_xml, json_data)
        root = ET.fromstring(doc_xml)

        # 1. Purga total de tabelas secundárias de habilidades do modelo antigo (contendo NSX, VMware, LDAP...)
        tables_to_remove = []
        for tbl in root.iter(f"{{{W_NS}}}tbl"):
            text = ''.join([t.text for t in tbl.iter(f"{{{W_NS}}}t") if t.text]).strip()
            # Se for uma tabela de matriz de tecnologias antigas (com NSX, vSphere, LDAP, etc.)
            if any(old_k in text for old_k in ['NSX', 'VMware ESX', 'Active Directory', 'LDAP', 'Microsoft Exchange', 'vSphere', 'Courier-IMAP', 'Open-E', 'Microsoft DFS']):
                tables_to_remove.append(tbl)

        for tbl in tables_to_remove:
            try:
                # Remove a tabela do seu contêiner pai
                for parent in root.iter():
                    if tbl in list(parent):
                        parent.remove(tbl)
                        break
            except Exception:
                pass

        # 2. Limpa nós de texto em parágrafos que ainda contenham NSX ou dados não pertencentes ao JSON
        for p in root.iter(f"{{{W_NS}}}p"):
            text = ''.join([t.text for t in p.iter(f"{{{W_NS}}}t") if t.text]).strip()
            if any(old_k in text for old_k in [
                'NSX', 'Portuguese', 'Dutch', 'HashiCorp Certified', 'Udemy', 'HackerRank',
                'Lusófona', 'Universidade Aberta', 'Escola de Negócios', 'European Commission', 'BNP Paribas'
            ]):
                for t in p.iter(f"{{{W_NS}}}t"):
                    t.text = ""

        # 3. Localiza o contêiner principal (<w:tc> ou body) para injeção limpa das seções do JSON
        main_tc = None
        for tc in root.iter(f"{{{W_NS}}}tc"):
            text = ''.join([t.text for t in tc.iter(f"{{{W_NS}}}t") if t.text]).strip()
            if any(k in text.lower() for k in ["work experience", "professional experience", "summary"]):
                main_tc = tc
                break

        if main_tc is None:
            main_tc = root.find(f"{{{W_NS}}}body")

        if main_tc is not None:
            children = list(main_tc)
            summary_p = None
            work_p_idx = None

            for idx, elem in enumerate(children):
                if elem.tag == f"{{{W_NS}}}p":
                    t_str = ''.join([t.text for t in elem.iter(f"{{{W_NS}}}t") if t.text]).strip()
                    if summary_p is None and any(k == t_str.lower() for k in ["summary", "professional summary", "resumo"]):
                        summary_p = elem
                    elif work_p_idx is None and any(k in t_str.lower() for k in ["work experience", "professional experience", "work history"]):
                        work_p_idx = idx

            if work_p_idx is not None:
                for elem in children[work_p_idx+1:]:
                    if elem.tag == f"{{{W_NS}}}p":
                        main_tc.remove(elem)

                insert_pos = work_p_idx + 1

                if summary and summary_p is None:
                    main_tc.insert(insert_pos, create_w_p("SUMMARY", is_heading=True))
                    insert_pos += 1
                    main_tc.insert(insert_pos, create_w_p(summary))
                    insert_pos += 1

                if exps:
                    for exp in exps:
                        exp_header = f"{exp.get('title', '')} — {exp.get('company', '')} ({exp.get('period', '')})"
                        main_tc.insert(insert_pos, create_w_p(exp_header, is_subheading=True))
                        insert_pos += 1

                        if exp.get("description"):
                            main_tc.insert(insert_pos, create_w_p(exp["description"]))
                            insert_pos += 1

                        for task in exp.get("responsibilities", []):
                            main_tc.insert(insert_pos, create_w_p(f"• {task}", is_bullet=True))
                            insert_pos += 1

                        if exp.get("technologies"):
                            main_tc.insert(insert_pos, create_w_p(f"Technologies: {', '.join(exp['technologies'])}"))
                            insert_pos += 1

                if top_techs:
                    main_tc.insert(insert_pos, create_w_p("TECHNICAL SKILLS", is_heading=True))
                    insert_pos += 1
                    main_tc.insert(insert_pos, create_w_p(", ".join(top_techs)))
                    insert_pos += 1

                if educations:
                    main_tc.insert(insert_pos, create_w_p("EDUCATION", is_heading=True))
                    insert_pos += 1
                    for edu in educations:
                        degree = edu.get("degree") or edu.get("course_name") or edu.get("course") or ""
                        school = edu.get("institution") or edu.get("course_institution") or edu.get("school") or ""
                        year = edu.get("year") or edu.get("course_end_date_year") or edu.get("period") or ""
                        main_tc.insert(insert_pos, create_w_p(f"{degree} — {school} ({year})", is_subheading=True))
                        insert_pos += 1

                if certifications:
                    main_tc.insert(insert_pos, create_w_p("CERTIFICATIONS", is_heading=True))
                    insert_pos += 1
                    for cert in certifications:
                        c_name = cert.get("title") or cert.get("name") or str(cert)
                        main_tc.insert(insert_pos, create_w_p(f"• {c_name}", is_bullet=True))
                        insert_pos += 1

                if languages:
                    main_tc.insert(insert_pos, create_w_p("LANGUAGES", is_heading=True))
                    insert_pos += 1
                    for lang_str in languages:
                        main_tc.insert(insert_pos, create_w_p(f"• {lang_str}", is_bullet=True))
                        insert_pos += 1

        return ET.tostring(root, encoding='utf-8').decode('utf-8')
    except Exception as e:
        print(f"[*] Erro na reconstrução do document.xml: {e}")
        return doc_xml

def populate_docx_from_json(docx_input_path: str, docx_output_path: str, json_data: dict, photo_path: str = "assets/photo.png"):
    if not os.path.exists(docx_input_path):
        print(f"[❌] Modelo .docx não encontrado: {docx_input_path}")
        return False

    transparent_path = "assets/transparent.png"
    transparent_bytes = b""
    if os.path.exists(transparent_path):
        with open(transparent_path, "rb") as f:
            transparent_bytes = f.read()

    photo_bytes = b""
    if photo_path and os.path.exists(photo_path):
        with open(photo_path, "rb") as f:
            photo_bytes = f.read()

    SPRINT_LOGO_HASHES = {'844fb7ee5217', 'a2c9825361f2', '7b0b95849149', 'fdb9da5c3144', 'af71625011d1'}

    temp_zip = docx_output_path + ".tmp"
    with zipfile.ZipFile(docx_input_path, 'r') as jin:
        with zipfile.ZipFile(temp_zip, 'w') as jout:
            for item in jin.infolist():
                fname = item.filename
                data = jin.read(fname)

                if fname.startswith('word/media/'):
                    import hashlib
                    h = hashlib.sha256(data).hexdigest()[:12]
                    if h in SPRINT_LOGO_HASHES:
                        jout.writestr(item, transparent_bytes)
                    elif ('foto' in fname.lower() or 'image4' in fname.lower() or 'large' in fname.lower()) and len(data) < 200000:
                        jout.writestr(item, photo_bytes if photo_bytes else data)
                    else:
                        jout.writestr(item, data)

                elif fname == 'word/document.xml':
                    doc_str = data.decode('utf-8')
                    doc_str = safe_populate_document_xml(doc_str, json_data)
                    doc_str = sanitize_xml_string(doc_str)
                    jout.writestr(item, doc_str.encode('utf-8'))
                elif fname.startswith('word/header') or fname.startswith('word/footer'):
                    doc_str = data.decode('utf-8')
                    doc_str = replace_dynamic_contact_regex(doc_str, json_data)
                    doc_str = sanitize_xml_string(doc_str)
                    jout.writestr(item, doc_str.encode('utf-8'))
                else:
                    jout.writestr(item, data)

    if os.path.exists(temp_zip):
        os.replace(temp_zip, docx_output_path)
        print(f"[✓] Documento DOCX populado com purga total de tabelas de habilidades antigas (ex: NSX): {docx_output_path}")
        return True
    return False
