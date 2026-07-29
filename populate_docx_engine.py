import os
import zipfile
import re
import html
import json
import copy
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

def set_p_runs_text(p: ET.Element, text: str):
    """Substitui o texto preservando a estrutura de runs originais."""
    runs = list(p.findall(f"{{{W_NS}}}r"))
    if not runs:
        r = ET.SubElement(p, f"{{{W_NS}}}r")
        t = ET.SubElement(r, f"{{{W_NS}}}t")
        t.text = text
        return

    first_r = runs[0]
    for r in runs[1:]:
        p.remove(r)

    t_elem = first_r.find(f"{{{W_NS}}}t")
    if t_elem is None:
        t_elem = ET.SubElement(first_r, f"{{{W_NS}}}t")
    t_elem.text = text

def populate_docx_from_json(docx_input_path: str, docx_output_path: str, json_data: dict, photo_path: str = "assets/photo.png"):
    """
    Motor Genérico de Povoamento com PURGA TOTAL DE 200+ PARÁGRAFOS E TABELAS SOBRESSALENTES:
    - Remove 100% de classificações de auto-avaliação, tabelas de anos de experiência e treinamentos antigos.
    - Povoa todas as 5 experiências profissionais e seções exclusivamente do JSON.
    - Preserva o layout e formatação do modelo OpenXML original.
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

                    body = root.find(f"{{{W_NS}}}body")

                    # PURGA AGRESSIVA DE 200+ PARÁGRAFOS/TABELAS DE AMOSTRAS SOBRESSALENTES
                    forbidden_sample_keywords = [
                        "competence rating", "self-assessment", "industry experience",
                        "european institutions", "trainings", "hashicorp", "hackerrank",
                        "years)", "scale from 1 to 5", "banking", "education management"
                    ]

                    for p_elem in list(root.iter()):
                        for child in list(p_elem):
                            c_txt = ''.join([t.text for t in child.iter(f"{{{W_NS}}}t") if t.text]).lower()
                            if any(kw in c_txt for kw in forbidden_sample_keywords):
                                if child.tag in [f"{{{W_NS}}}p", f"{{{W_NS}}}tbl"]:
                                    p_elem.remove(child)

                    # Localiza a tabela principal do cabeçalho / grid
                    tables = list(root.iter(f"{{{W_NS}}}tbl"))
                    all_p = list(root.iter(f"{{{W_NS}}}p"))

                    heading_proto = None
                    subheading_proto = None
                    body_proto = None
                    bullet_proto = None

                    for p in all_p:
                        p_txt = ''.join([t.text for t in p.iter(f"{{{W_NS}}}t") if t.text]).strip()
                        if any(k in p_txt.lower() for k in ["work experience", "professional experience", "education", "skills", "languages", "summary"]):
                            if heading_proto is None:
                                heading_proto = copy.deepcopy(p)
                        elif p_txt.startswith("-") or p_txt.startswith("•"):
                            if bullet_proto is None:
                                bullet_proto = copy.deepcopy(p)
                        elif len(p_txt) > 40:
                            if body_proto is None:
                                body_proto = copy.deepcopy(p)
                        elif len(p_txt) > 0 and subheading_proto is None:
                            subheading_proto = copy.deepcopy(p)

                    if heading_proto is None and all_p:
                        heading_proto = copy.deepcopy(all_p[0])
                    if body_proto is None and all_p:
                        body_proto = copy.deepcopy(all_p[-1])
                    if subheading_proto is None:
                        subheading_proto = copy.deepcopy(heading_proto)
                    if bullet_proto is None:
                        bullet_proto = copy.deepcopy(body_proto)

                    primary_table = tables[0] if len(tables) > 0 else None
                    is_full_sidebar_layout = False
                    sidebar_tc = None
                    main_tc = None

                    if primary_table is not None:
                        tbl_text = ''.join([t.text for t in primary_table.iter(f"{{{W_NS}}}t") if t.text]).lower()
                        if any(k in tbl_text for k in ["work experience", "professional experience", "professional summary", "elton"]):
                            cells = list(primary_table.iter(f"{{{W_NS}}}tc"))
                            if len(cells) >= 2:
                                is_full_sidebar_layout = True
                                sidebar_tc = cells[0]
                                main_tc = cells[-1]

                    target_main_container = main_tc if is_full_sidebar_layout and main_tc is not None else body
                    target_sidebar_container = sidebar_tc if is_full_sidebar_layout and sidebar_tc is not None else body

                    # 1. Resumo Profissional
                    if summary:
                        summary_ps = [p for p in target_main_container.findall(f"{{{W_NS}}}p") if "summary" in ''.join([t.text for t in p.iter(f"{{{W_NS}}}t") if t.text]).lower()]
                        if summary_ps:
                            p_idx = list(target_main_container).index(summary_ps[0])
                            if p_idx + 1 < len(target_main_container) and target_main_container[p_idx + 1].tag == f"{{{W_NS}}}p":
                                set_p_runs_text(target_main_container[p_idx + 1], summary)

                    # 2. Experiências Profissionais
                    exp_headings = [p for p in target_main_container.findall(f"{{{W_NS}}}p") if any(k in ''.join([t.text for t in p.iter(f"{{{W_NS}}}t") if t.text]).lower() for k in ["work experience", "professional experience"])]
                    if exp_headings and exps:
                        exp_h = exp_headings[0]
                        start_idx = list(target_main_container).index(exp_h) + 1

                        for child in list(target_main_container)[start_idx:]:
                            child_txt = ''.join([t.text for t in child.iter(f"{{{W_NS}}}t") if t.text]).lower()
                            if any(k in child_txt for k in ["education", "certifications", "languages", "technical skills"]):
                                break
                            if child.tag == f"{{{W_NS}}}p":
                                target_main_container.remove(child)

                        curr_idx = start_idx
                        for exp in exps:
                            exp_title = f"{exp.get('title', '')} — {exp.get('company', '')} ({exp.get('period', '')})"
                            p_title = copy.deepcopy(subheading_proto)
                            set_p_runs_text(p_title, exp_title)
                            target_main_container.insert(curr_idx, p_title)
                            curr_idx += 1

                            if exp.get("description"):
                                p_desc = copy.deepcopy(body_proto)
                                set_p_runs_text(p_desc, exp["description"])
                                target_main_container.insert(curr_idx, p_desc)
                                curr_idx += 1

                            for task in exp.get("responsibilities", []):
                                p_task = copy.deepcopy(bullet_proto)
                                task_str = task if task.startswith("•") or task.startswith("-") else f"• {task}"
                                set_p_runs_text(p_task, task_str)
                                target_main_container.insert(curr_idx, p_task)
                                curr_idx += 1

                            if exp.get("technologies"):
                                p_tech = copy.deepcopy(body_proto)
                                set_p_runs_text(p_tech, f"Technologies: {', '.join(exp['technologies'])}")
                                target_main_container.insert(curr_idx, p_tech)
                                curr_idx += 1

                    # 3. Educação
                    edu_headings = [p for p in target_main_container.findall(f"{{{W_NS}}}p") if "education" in ''.join([t.text for t in p.iter(f"{{{W_NS}}}t") if t.text]).lower()]
                    if not edu_headings and target_sidebar_container != target_main_container:
                        edu_headings = [p for p in target_sidebar_container.findall(f"{{{W_NS}}}p") if "education" in ''.join([t.text for t in p.iter(f"{{{W_NS}}}t") if t.text]).lower()]

                    if edu_headings and educations:
                        edu_h = edu_headings[0]
                        parent_c = target_sidebar_container if edu_h in list(target_sidebar_container) else target_main_container
                        e_idx = list(parent_c).index(edu_h) + 1

                        for child in list(parent_c)[e_idx:]:
                            c_txt = ''.join([t.text for t in child.iter(f"{{{W_NS}}}t") if t.text]).lower()
                            if any(k in c_txt for k in ["certifications", "languages", "trainings", "contacts", "work experience"]):
                                break
                            if child.tag == f"{{{W_NS}}}p":
                                parent_c.remove(child)

                        for edu in educations:
                            degree = edu.get("degree") or edu.get("course_name") or edu.get("course") or ""
                            school = edu.get("institution") or edu.get("course_institution") or edu.get("school") or ""
                            year = edu.get("year") or edu.get("course_end_date_year") or edu.get("period") or ""
                            p_edu = copy.deepcopy(subheading_proto)
                            set_p_runs_text(p_edu, f"{degree} — {school} ({year})")
                            parent_c.insert(e_idx, p_edu)
                            e_idx += 1

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
        print(f"[✓] Documento DOCX populado com PURGA AGRESSIVA em: {docx_output_path}")
        return True
    return False
