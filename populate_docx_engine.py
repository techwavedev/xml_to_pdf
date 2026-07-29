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

def populate_docx_from_json(docx_input_path: str, docx_output_path: str, json_data: dict, photo_path: str = "assets/photo.png"):
    """
    Motor 100% Conforme com ECMA-376 OpenXML:
    - Garantia de que <w:sectPr> permaneça no final absoluto da tag <body> (eliminando o aviso de erro do MS Word).
    - Preservação da tabela de foto de cabeçalho e grid de colunas.
    """
    if not os.path.exists(docx_input_path):
        print(f"[❌] Modelo .docx não encontrado: {docx_input_path}")
        return False

    consultant = json_data.get("consultant", {})
    fullname = f"{consultant.get('name', '')} {consultant.get('surname', '')}".strip()
    title = json_data.get("present_job_title", "")
    email = consultant.get("email", "")
    phone = consultant.get("phone", "")
    location = f"{consultant.get('city', '')}, {consultant.get('country', '')}".strip(", ")
    linkedin = consultant.get("linkedin", "")
    summary = json_data.get("about") or json_data.get("cv_summary") or ""
    
    exps = json_data.get("work_experiences", [])
    educations = json_data.get("educations", [])
    certifications = json_data.get("certifications", [])
    languages = extract_candidate_languages(json_data)
    top_techs_raw = json_data.get("top_technologies") or []
    top_techs = [format_tech_item(t) for t in top_techs_raw]

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
                    doc_str = replace_dynamic_contact_regex(doc_str, json_data)
                    root = ET.fromstring(doc_str)

                    tables = list(root.iter(f"{{{W_NS}}}tbl"))
                    body = root.find(f"{{{W_NS}}}body")

                    is_full_sidebar_layout = False
                    sidebar_tc = None
                    main_tc = None

                    if len(tables) > 0:
                        tbl_text = ''.join([t.text for t in tables[0].iter(f"{{{W_NS}}}t") if t.text]).lower()
                        if any(k in tbl_text for k in ["work experience", "professional experience", "professional summary"]):
                            cells = list(tables[0].iter(f"{{{W_NS}}}tc"))
                            if len(cells) >= 2:
                                is_full_sidebar_layout = True
                                sidebar_tc = cells[0]
                                main_tc = cells[-1]

                    if is_full_sidebar_layout and sidebar_tc is not None and main_tc is not None:
                        # Layout de 2 Colunas (itresume.docx / sprint.docx)
                        for child in list(sidebar_tc):
                            if child.tag != f"{{{W_NS}}}tcPr":
                                sidebar_tc.remove(child)

                        sidebar_tc.append(create_w_p(fullname, is_heading=True))
                        if title:
                            sidebar_tc.append(create_w_p(title, is_subheading=True))
                        sidebar_tc.append(create_w_p("CONTACTS", is_heading=True))
                        if email:
                            sidebar_tc.append(create_w_p(f"Email: {email}"))
                        if phone:
                            sidebar_tc.append(create_w_p(f"Phone: {phone}"))
                        if location:
                            sidebar_tc.append(create_w_p(f"Location: {location}"))
                        if linkedin:
                            sidebar_tc.append(create_w_p(f"LinkedIn: {linkedin}"))

                        if top_techs:
                            sidebar_tc.append(create_w_p("TECHNICAL SKILLS", is_heading=True))
                            for tech in top_techs:
                                sidebar_tc.append(create_w_p(f"• {tech}", is_bullet=True))

                        if languages:
                            sidebar_tc.append(create_w_p("LANGUAGES", is_heading=True))
                            for lang_str in languages:
                                sidebar_tc.append(create_w_p(f"• {lang_str}", is_bullet=True))

                        for child in list(main_tc):
                            if child.tag != f"{{{W_NS}}}tcPr":
                                main_tc.remove(child)

                        main_tc.append(create_w_p(fullname, is_heading=True))
                        if title:
                            main_tc.append(create_w_p(title, is_subheading=True))

                        if summary:
                            main_tc.append(create_w_p("PROFESSIONAL SUMMARY", is_heading=True))
                            main_tc.append(create_w_p(summary))

                        if exps:
                            main_tc.append(create_w_p("WORK EXPERIENCE", is_heading=True))
                            for exp in exps:
                                exp_header = f"{exp.get('title', '')} — {exp.get('company', '')} ({exp.get('period', '')})"
                                main_tc.append(create_w_p(exp_header, is_subheading=True))

                                if exp.get("description"):
                                    main_tc.append(create_w_p(exp["description"]))

                                for task in exp.get("responsibilities", []):
                                    main_tc.append(create_w_p(f"• {task}", is_bullet=True))

                                if exp.get("technologies"):
                                    main_tc.append(create_w_p(f"Technologies: {', '.join(exp['technologies'])}"))

                        if educations:
                            main_tc.append(create_w_p("EDUCATION", is_heading=True))
                            for edu in educations:
                                degree = edu.get("degree") or edu.get("course_name") or edu.get("course") or ""
                                school = edu.get("institution") or edu.get("course_institution") or edu.get("school") or ""
                                year = edu.get("year") or edu.get("course_end_date_year") or edu.get("period") or ""
                                main_tc.append(create_w_p(f"{degree} — {school} ({year})", is_subheading=True))

                        if certifications:
                            main_tc.append(create_w_p("CERTIFICATIONS", is_heading=True))
                            for cert in certifications:
                                c_name = cert.get("title") or cert.get("name") or str(cert)
                                main_tc.append(create_w_p(f"• {c_name}", is_bullet=True))

                    else:
                        # Layout Single-Column (expert.docx / mlops.docx)
                        sect_pr = body.find(f"{{{W_NS}}}sectPr")
                        
                        # Remove apenas os parágrafos <w:p> antigos do corpo
                        for child in list(body):
                            if child.tag == f"{{{W_NS}}}p":
                                body.remove(child)

                        # Helper para inserir elementos SEMPRE ANTES do <w:sectPr> final
                        def append_to_body(elem):
                            if sect_pr is not None and sect_pr in list(body):
                                idx = list(body).index(sect_pr)
                                body.insert(idx, elem)
                            else:
                                body.append(elem)

                        if summary:
                            append_to_body(create_w_p("PROFESSIONAL SUMMARY", is_heading=True))
                            append_to_body(create_w_p(summary))

                        if exps:
                            append_to_body(create_w_p("WORK EXPERIENCE", is_heading=True))
                            for exp in exps:
                                exp_header = f"{exp.get('title', '')} — {exp.get('company', '')} ({exp.get('period', '')})"
                                append_to_body(create_w_p(exp_header, is_subheading=True))

                                if exp.get("description"):
                                    append_to_body(create_w_p(exp["description"]))

                                for task in exp.get("responsibilities", []):
                                    append_to_body(create_w_p(f"• {task}", is_bullet=True))

                                if exp.get("technologies"):
                                    append_to_body(create_w_p(f"Technologies: {', '.join(exp['technologies'])}"))

                        if top_techs:
                            append_to_body(create_w_p("TECHNICAL SKILLS", is_heading=True))
                            append_to_body(create_w_p(", ".join(top_techs)))

                        if educations:
                            append_to_body(create_w_p("EDUCATION", is_heading=True))
                            for edu in educations:
                                degree = edu.get("degree") or edu.get("course_name") or edu.get("course") or ""
                                school = edu.get("institution") or edu.get("course_institution") or edu.get("school") or ""
                                year = edu.get("year") or edu.get("course_end_date_year") or edu.get("period") or ""
                                append_to_body(create_w_p(f"{degree} — {school} ({year})", is_subheading=True))

                        if certifications:
                            append_to_body(create_w_p("CERTIFICATIONS", is_heading=True))
                            for cert in certifications:
                                c_name = cert.get("title") or cert.get("name") or str(cert)
                                append_to_body(create_w_p(f"• {c_name}", is_bullet=True))

                        if languages:
                            append_to_body(create_w_p("LANGUAGES", is_heading=True))
                            for lang_str in languages:
                                append_to_body(create_w_p(f"• {lang_str}", is_bullet=True))

                    doc_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
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
        print(f"[✓] Documento DOCX populado com estrita conformidade <w:sectPr> em: {docx_output_path}")
        return True
    return False
