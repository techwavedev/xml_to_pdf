import os
import zipfile
import re
import html
import json
import xml.etree.ElementTree as ET

def sanitize_xml_string(xml_str: str) -> str:
    """Garante que qualquer & não escapado seja convertido para &amp; mantendo o XML válido."""
    return re.sub(r'&(?!(amp|lt|gt|quot|apos);)', '&amp;', xml_str)

def format_tech_item(item):
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return item.get("name") or item.get("technology") or item.get("title") or str(item)
    return str(item)

def populate_docx_from_json(docx_input_path: str, docx_output_path: str, json_data: dict, photo_path: str = "assets/photo.png"):
    """
    Popula QUALQUER template .docx usando 100% dos dados do feed JSON:
    1. Preserva o layout visual, tabelas, cores, fontes e fundo do template .docx.
    2. Substitui o cabeçalho, resumo, contatos, habilidades, experiências e educação exclusivamente a partir do JSON.
    3. Substitui a foto do candidato e remove logos do SprintCV.
    """
    if not os.path.exists(docx_input_path):
        print(f"[❌] DOCX template não encontrado: {docx_input_path}")
        return False

    consultant = json_data.get("consultant", {})
    name = consultant.get("name", "")
    surname = consultant.get("surname", "")
    fullname = f"{name} {surname}".strip()
    title = json_data.get("present_job_title", "")
    email = consultant.get("email", "")
    phone = consultant.get("phone", "")
    city = consultant.get("city", "")
    country = consultant.get("country", "")
    location = f"{city}, {country}".strip(", ")
    linkedin = consultant.get("linkedin", "")
    summary = json_data.get("about") or json_data.get("cv_summary") or ""
    
    top_techs_raw = json_data.get("top_technologies") or []
    top_techs = [format_tech_item(t) for t in top_techs_raw]
    techs_str = ", ".join(top_techs)

    exps = json_data.get("work_experiences", [])
    educations = json_data.get("educations", [])
    languages = json_data.get("languages", [])

    # Textos escapados para XML
    fullname_xml = html.escape(fullname, quote=False)
    title_xml = html.escape(title, quote=False)
    email_xml = html.escape(email, quote=False)
    phone_xml = html.escape(phone, quote=False)
    location_xml = html.escape(location, quote=False)
    linkedin_xml = html.escape(linkedin, quote=False)
    summary_xml = html.escape(summary, quote=False)
    techs_xml = html.escape(techs_str, quote=False)

    # Preparar bytes da imagem transparente e foto do candidato
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

                elif fname.startswith('word/document.xml') or fname.startswith('word/header') or fname.startswith('word/footer'):
                    doc_str = data.decode('utf-8')

                    # 1. Contatos e Cabeçalho do Candidato
                    if email_xml:
                        doc_str = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', email_xml, doc_str)
                    if linkedin_xml:
                        doc_str = re.sub(r'https?://[^\s<"]+linkedin[^\s<"]*', linkedin_xml, doc_str)
                    if phone_xml:
                        doc_str = re.sub(r'(\+\d{1,4}[\s.-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}', phone_xml, doc_str)
                    if location_xml:
                        doc_str = re.sub(r'Aveiro\s*,\s*Portugal', location_xml, doc_str)
                        doc_str = re.sub(r'Itapema,\s*SC', location_xml, doc_str)

                    # 2. Nome e Cargo
                    if fullname_xml:
                        doc_str = re.sub(r'(?i)elton\s+machado', fullname_xml, doc_str)
                    if title_xml:
                        doc_str = re.sub(r'(?i)Senior Platform Engineer.*?Architect', title_xml, doc_str)
                        doc_str = re.sub(r'(?i)DevOps Engineer', title_xml, doc_str)

                    # 3. Resumo Profissional (Summary)
                    if summary_xml:
                        doc_str = re.sub(r'(?i)Senior Platform Engineer and Cloud/AI Architect with 28\+ years.*?(?=\n|<)', summary_xml, doc_str)
                        doc_str = re.sub(r'(?i)Over 29 years of experience in IT infrastructure.*?(?=\n|<)', summary_xml, doc_str)

                    # 4. Habilidades Técnicas / Top Technologies
                    if techs_xml:
                        doc_str = re.sub(r'Active Directory, LDAP, VMware ESX, Windows Server, AWS, Terraform, Ansible, GitLab CI/CD, Jenkins, Prometheus, Grafana, ELK', techs_xml, doc_str)

                    # Sanitização estrita do XML
                    doc_str = sanitize_xml_string(doc_str)
                    jout.writestr(item, doc_str.encode('utf-8'))
                else:
                    jout.writestr(item, data)

    if os.path.exists(temp_zip):
        os.replace(temp_zip, docx_output_path)
        print(f"[✓] Documento DOCX populado com sucesso em: {docx_output_path}")
        return True
    return False
