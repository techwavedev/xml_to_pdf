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

def get_run_font_size(r: ET.Element) -> float:
    rPr = r.find(f"{{{W_NS}}}rPr")
    if rPr is not None:
        sz = rPr.find(f"{{{W_NS}}}sz")
        if sz is not None and f"{{{W_NS}}}val" in sz.attrib:
            try:
                return float(sz.attrib[f"{{{W_NS}}}val"]) / 2.0
            except ValueError:
                pass
    return 10.0

def sanitize_paragraph_style(p: ET.Element):
    pPr = p.find(f"{{{W_NS}}}pPr")
    if pPr is not None:
        pStyle = pPr.find(f"{{{W_NS}}}pStyle")
        if pStyle is not None:
            pPr.remove(pStyle)
        
        rPr = pPr.find(f"{{{W_NS}}}rPr")
        if rPr is not None:
            for tag in ["sz", "szCs"]:
                elem = rPr.find(f"{{{W_NS}}}{tag}")
                if elem is not None:
                    rPr.remove(elem)

def set_run_font_size(r: ET.Element, pt_size: float):
    rPr = r.find(f"{{{W_NS}}}rPr")
    if rPr is None:
        rPr = ET.SubElement(r, f"{{{W_NS}}}rPr")
    
    val_str = str(int(pt_size * 2))
    
    sz = rPr.find(f"{{{W_NS}}}sz")
    if sz is None:
        sz = ET.SubElement(rPr, f"{{{W_NS}}}sz")
    sz.attrib[f"{{{W_NS}}}val"] = val_str

    szCs = rPr.find(f"{{{W_NS}}}szCs")
    if szCs is None:
        szCs = ET.SubElement(rPr, f"{{{W_NS}}}szCs")
    szCs.attrib[f"{{{W_NS}}}val"] = val_str

def create_run_with_exact_proto(text: str, proto_r: ET.Element = None, target_pt: float = None) -> ET.Element:
    if proto_r is not None:
        new_r = copy.deepcopy(proto_r)
    else:
        new_r = ET.Element(f"{{{W_NS}}}r")

    t_elem = new_r.find(f"{{{W_NS}}}t")
    if t_elem is None:
        t_elem = ET.SubElement(new_r, f"{{{W_NS}}}t")
    t_elem.text = text

    if target_pt is not None:
        set_run_font_size(new_r, target_pt)
    else:
        current_sz = get_run_font_size(new_r)
        if current_sz > 14.0:
            set_run_font_size(new_r, 10.0)

    return new_r

def set_p_text_with_proto_r(p: ET.Element, text: str, proto_r: ET.Element = None, target_pt: float = None):
    sanitize_paragraph_style(p)
    runs = list(p.findall(f"{{{W_NS}}}r"))
    
    if proto_r is None and runs:
        for r in runs:
            if get_run_font_size(r) <= 14.0:
                proto_r = r
                break
        if proto_r is None:
            proto_r = runs[0]

    for r in runs:
        p.remove(r)

    p.append(create_run_with_exact_proto(text, proto_r, target_pt))

def replace_dynamic_text_in_tree(root: ET.Element, json_data: dict):
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

    for p in root.iter(f"{{{W_NS}}}p"):
        p_txt = ''.join([t.text for t in p.iter(f"{{{W_NS}}}t") if t.text])
        if not p_txt.strip():
            continue

        if "elton" in p_txt.lower() or "machado" in p_txt.lower():
            if "@" in p_txt and email:
                set_p_text_with_proto_r(p, f"Email: {email}")
            elif "linkedin" in p_txt.lower() and linkedin:
                set_p_text_with_proto_r(p, f"LinkedIn: {linkedin}")
            elif len(p_txt) < 40 and fullname:
                set_p_text_with_proto_r(p, fullname)

        if any(loc in p_txt for loc in ["Aveiro", "Portugal", "Itapema", "SC"]) and location:
            if not any(k in p_txt.lower() for k in ["experience", "summary", "education"]):
                set_p_text_with_proto_r(p, f"Location: {location}")

def populate_docx_from_json(docx_input_path: str, docx_output_path: str, json_data: dict, photo_path: str = "assets/photo.png"):
    if not os.path.exists(docx_input_path):
        print(f"[❌] Modelo .docx não encontrado: {docx_input_path}")
        return False

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
                    root = ET.fromstring(doc_str)

                    # 1. Substituição Dinâmica de Contatos e Nome no XML Tree
                    replace_dynamic_text_in_tree(root, json_data)

                    # 2. Purga de Skill Ratings Legados (APENAS PARÁGRAFOS <w:p>, NUNCA TABELAS PRINCIPAIS)
                    for parent in list(root.iter()):
                        if parent.tag in [f"{{{W_NS}}}body", f"{{{W_NS}}}tc"]:
                            for child in list(parent):
                                if child.tag == f"{{{W_NS}}}p":
                                    c_txt = ''.join([t.text for t in child.iter(f"{{{W_NS}}}t") if t.text]).strip()
                                    if re.search(r'\(\d+(\.\d+)?\s*years?\)', c_txt, re.IGNORECASE) or any(kw in c_txt.lower() for kw in [
                                        "competence rating", "self-assessment", "industry experience",
                                        "european institutions", "trainings", "hashicorp", "hackerrank",
                                        "technology experience*"
                                    ]):
                                        parent.remove(child)

                    # 3. EXTRAÇÃO DE PROTÓTIPOS DE RUN COM TAMANHO DE FONTE RIGOROSO
                    all_p = list(root.iter(f"{{{W_NS}}}p"))

                    subheading_proto_r = None
                    body_proto_r = None
                    bullet_proto_r = None

                    subheading_p_proto = None
                    body_p_proto = None
                    bullet_p_proto = None

                    for p in all_p:
                        p_txt = ''.join([t.text for t in p.iter(f"{{{W_NS}}}t") if t.text]).strip()
                        if not p_txt:
                            continue

                        runs = p.findall(f"{{{W_NS}}}r")
                        for r in runs:
                            # CRITICAL FIX: NEVER use a run as a prototype if it contains a drawing or image!
                            if r.find(f".//{{{W_NS}}}drawing") is not None or r.find(f".//{{{W_NS}}}pict") is not None:
                                continue
                                
                            t_elem = r.find(f"{{{W_NS}}}t")
                            if t_elem is None or not t_elem.text or not t_elem.text.strip():
                                continue

                            sz = get_run_font_size(r)
                            if sz <= 10.0:
                                if body_proto_r is None:
                                    body_proto_r = copy.deepcopy(r)
                                    body_p_proto = copy.deepcopy(p)
                                if p_txt.startswith("-") or p_txt.startswith("•"):
                                    if bullet_proto_r is None:
                                        bullet_proto_r = copy.deepcopy(r)
                                        bullet_p_proto = copy.deepcopy(p)
                            elif 10.5 <= sz <= 14.0:
                                if subheading_proto_r is None:
                                    subheading_proto_r = copy.deepcopy(r)
                                    subheading_p_proto = copy.deepcopy(p)

                    if body_proto_r is None and all_p:
                        for p in reversed(all_p):
                            runs = p.findall(f"{{{W_NS}}}r")
                            if runs and get_run_font_size(runs[0]) <= 14.0:
                                body_proto_r = copy.deepcopy(runs[0])
                                body_p_proto = copy.deepcopy(p)
                                break
                    if subheading_proto_r is None:
                        subheading_proto_r = copy.deepcopy(body_proto_r)
                        subheading_p_proto = copy.deepcopy(body_p_proto)
                    if bullet_proto_r is None:
                        bullet_proto_r = copy.deepcopy(body_proto_r)
                        bullet_p_proto = copy.deepcopy(body_p_proto)

                    # 4. BUSCA ANCORA E CONTAINER PAI DIRETO (tc ou body)
                    exp_start_p = None
                    exp_target_container = None

                    sample_company_keywords = [
                        "work experience", "professional experience", "employment history",
                        "experience", "tenforce", "biglevel", "whooo", "helimax", "cloud architect",
                        "senior platform engineer", "european commission"
                    ]

                    for parent in root.iter():
                        if parent.tag in [f"{{{W_NS}}}body", f"{{{W_NS}}}tc"]:
                            for child in list(parent):
                                if child.tag == f"{{{W_NS}}}p":
                                    txt = ''.join([t.text for t in child.iter(f"{{{W_NS}}}t") if t.text]).lower()
                                    if any(k in txt for k in ["work experience", "professional experience", "employment history"]) or txt == "experience":
                                        exp_start_p = child
                                        exp_target_container = parent
                                        break
                            if exp_start_p is not None:
                                break

                    if exp_start_p is None:
                        tables = list(root.iter(f"{{{W_NS}}}tbl"))
                        body = root.find(f"{{{W_NS}}}body")
                        target_c = body
                        if len(tables) > 0:
                            cells = list(tables[0].iter(f"{{{W_NS}}}tc"))
                            if len(cells) >= 2:
                                target_c = cells[-1]

                        for child in list(target_c):
                            if child.tag == f"{{{W_NS}}}p":
                                txt = ''.join([t.text for t in child.iter(f"{{{W_NS}}}t") if t.text]).lower()
                                if any(k in txt for k in sample_company_keywords) or re.search(r'\d{2}-\d{4}\s*-\s*\d{2}-\d{4}', txt):
                                    exp_start_p = child
                                    exp_target_container = target_c
                                    break

                    if exp_start_p is not None and exp_target_container is not None and exps:
                        curr_children = list(exp_target_container)
                        s_idx = curr_children.index(exp_start_p)
                        txt_start = ''.join([t.text for t in exp_start_p.iter(f"{{{W_NS}}}t") if t.text]).lower()
                        is_header = any(k in txt_start for k in ["work experience", "professional experience", "employment history"]) or txt_start == "experience"
                        
                        start_insert_idx = s_idx + (1 if is_header else 0)

                        nodes_to_remove = []
                        for child in curr_children[start_insert_idx:]:
                            if child.tag in [f"{{{W_NS}}}p", f"{{{W_NS}}}tbl"]:
                                c_txt = ''.join([t.text for t in child.iter(f"{{{W_NS}}}t") if t.text]).lower().strip()
                                
                                # CRITICAL FIX: Only break if it's ACTUALLY a heading (short text exact match).
                                # DO NOT break just because a job description says "teaching skills".
                                if c_txt in ["education", "certifications", "languages", "technical skills", "skills", "training"]:
                                    break
                                
                                # Add the old node to be deleted.
                                nodes_to_remove.append(child)

                        # Se a própria âncora inicial não for um header genérico, remova ela também
                        if not is_header and exp_start_p in list(exp_target_container):
                            nodes_to_remove.append(exp_start_p)

                        for node in set(nodes_to_remove):
                            if node in list(exp_target_container):
                                exp_target_container.remove(node)

                        insert_pos = s_idx if not is_header else s_idx + 1
                        for exp in exps:
                            exp_title = f"{exp.get('title', '')} — {exp.get('company', '')} ({exp.get('period', '')})"
                            p_title = copy.deepcopy(subheading_p_proto) if subheading_p_proto is not None else ET.Element(f"{{{W_NS}}}p")
                            set_p_text_with_proto_r(p_title, exp_title, subheading_proto_r, target_pt=11.0)
                            exp_target_container.insert(insert_pos, p_title)
                            insert_pos += 1

                            if exp.get("description"):
                                p_desc = copy.deepcopy(body_p_proto) if body_p_proto is not None else ET.Element(f"{{{W_NS}}}p")
                                set_p_text_with_proto_r(p_desc, exp["description"], body_proto_r, target_pt=9.5)
                                exp_target_container.insert(insert_pos, p_desc)
                                insert_pos += 1

                            for task in exp.get("responsibilities", []):
                                p_task = copy.deepcopy(bullet_p_proto) if bullet_p_proto is not None else ET.Element(f"{{{W_NS}}}p")
                                task_str = task if task.startswith("•") or task.startswith("-") else f"• {task}"
                                set_p_text_with_proto_r(p_task, task_str, bullet_proto_r, target_pt=9.5)
                                exp_target_container.insert(insert_pos, p_task)
                                insert_pos += 1

                            if exp.get("technologies"):
                                p_tech = copy.deepcopy(body_p_proto) if body_p_proto is not None else ET.Element(f"{{{W_NS}}}p")
                                set_p_text_with_proto_r(p_tech, f"Technologies: {', '.join(exp['technologies'])}", body_proto_r, target_pt=9.0)
                                exp_target_container.insert(insert_pos, p_tech)
                                insert_pos += 1

                    # 5. SUBSTITUIÇÃO DO RESUMO PROFISSIONAL
                    summary_h_p = None
                    summary_container = None
                    for container in root.iter():
                        if container.tag in [f"{{{W_NS}}}body", f"{{{W_NS}}}tc"]:
                            for child in list(container):
                                if child.tag == f"{{{W_NS}}}p":
                                    txt = ''.join([t.text for t in child.iter(f"{{{W_NS}}}t") if t.text]).lower()
                                    if any(k in txt for k in ["professional summary", "summary", "about me", "my mission"]):
                                        summary_h_p = child
                                        summary_container = container
                                        break
                            if summary_h_p is not None:
                                break

                    if summary_h_p is not None and summary_container is not None and summary:
                        s_idx = list(summary_container).index(summary_h_p) + 1
                        if s_idx < len(summary_container) and summary_container[s_idx].tag == f"{{{W_NS}}}p":
                            set_p_text_with_proto_r(summary_container[s_idx], summary, body_proto_r, target_pt=9.5)

                    doc_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
                    doc_str = sanitize_xml_string(doc_str)
                    jout.writestr(item, doc_str.encode('utf-8'))

                elif fname.startswith('word/header') or fname.startswith('word/footer'):
                    doc_str = data.decode('utf-8')
                    root = ET.fromstring(doc_str)
                    replace_dynamic_text_in_tree(root, json_data)
                    doc_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
                    doc_str = sanitize_xml_string(doc_str)
                    jout.writestr(item, doc_str.encode('utf-8'))
                else:
                    jout.writestr(item, data)

    if os.path.exists(temp_zip):
        os.replace(temp_zip, docx_output_path)
        print(f"[✓] Documento DOCX populado com SUPORTE COMPLETO A EXPERT.DOCX em: {docx_output_path}")
        return True
    return False
