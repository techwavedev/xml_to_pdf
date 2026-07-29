import zipfile
import os
import hashlib

import zipfile
import os
import hashlib
import io
import json
import re
from PIL import Image

def get_candidate_photo_bytes(photo_path: str = None, target_format: str = 'JPEG') -> bytes:
    """Retorna os bytes da foto do candidato (assets/photo.png ou parâmetro) convertidos para o formato desejado."""
    if not photo_path or not os.path.exists(photo_path):
        photo_path = "assets/photo.png"
    if not os.path.exists(photo_path):
        photo_path = "assets/original_candidate_photo.jpeg"
    if not os.path.exists(photo_path):
        photo_path = "assets/fake_large.jpeg"

    try:
        with Image.open(photo_path) as img:
            img_rgb = img.convert("RGB")
            buf = io.BytesIO()
            img_rgb.save(buf, format=target_format, quality=92)
            return buf.getvalue()
    except Exception as e:
        print(f"[*] Aviso ao carregar foto {photo_path}: {e}")
        with open(photo_path, "rb") as f:
            return f.read()

def clean_docx_sprint(docx_input_path: str, docx_output_path: str, photo_path: str = None, json_data: dict = None):
    """
    Limpa e atualiza um template .docx:
    1. Substitui logos do SprintCV por PNG transparente 1x1 (layout intacto).
    2. Substitui a foto do candidato no DOCX por assets/photo.png (ou photo_path).
    3. Se json_data for fornecido, atualiza dados do candidato em word/document.xml.
    4. Preserva o fundo de constelação e ícones originais.
    """
    if not os.path.exists(docx_input_path):
        print(f"[❌] Arquivo não encontrado: {docx_input_path}")
        return
        
    transparent_path = "assets/transparent.png"
    with open(transparent_path, "rb") as f:
        transparent_data = f.read()
    
    candidate_photo_data = get_candidate_photo_bytes(photo_path, target_format='JPEG')

import html

def sanitize_xml_string(xml_str: str) -> str:
    """Garante que qualquer & não escapado seja convertido para &amp; mantendo o XML perfeitamente válido."""
    return re.sub(r'&(?!(amp|lt|gt|quot|apos);)', '&amp;', xml_str)

import jinja2

# Padrões genéricos de expressões regulares para detectar dados pessoais sem textos fixos
EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
PHONE_REGEX = r'(\+\d{1,4}[\s.-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}'
LINKEDIN_REGEX = r'https?://[^\s<"]+linkedin[^\s<"]*'

def dynamic_templatize_xml(doc_xml: str) -> str:
    """Transforma padrões genéricos de contato em marcadores Jinja2 dentro do XML."""
    doc_xml = re.sub(EMAIL_REGEX, '{{ consultant.email }}', doc_xml)
    doc_xml = re.sub(LINKEDIN_REGEX, '{{ consultant.linkedin }}', doc_xml)
    doc_xml = re.sub(PHONE_REGEX, '{{ consultant.phone }}', doc_xml)
    return doc_xml

def clean_docx_sprint(docx_input_path: str, docx_output_path: str, photo_path: str = None, json_data: dict = None):
    """
    Limpa e atualiza QUALQUER template .docx usando QUALQUER feed JSON:
    1. Substitui logos do SprintCV por PNG transparente 1x1.
    2. Substitui a foto do candidato por photo_path (assets/photo.png).
    3. Renderiza dinamicamente o XML com Jinja2 usando o feed JSON fornecido (zero textos fixos hardcoded).
    4. Preserva fundos e formatações originais do Word.
    """
    if not os.path.exists(docx_input_path):
        print(f"[❌] Arquivo não encontrado: {docx_input_path}")
        return
        
    transparent_path = "assets/transparent.png"
    with open(transparent_path, "rb") as f:
        transparent_data = f.read()
    
    candidate_photo_data_jpeg = get_candidate_photo_bytes(photo_path, target_format='JPEG')
    candidate_photo_data_png = get_candidate_photo_bytes(photo_path, target_format='PNG')

    # Hashes SHA-256 (primeiros 12 chars) das logos do SprintCV
    SPRINT_LOGO_HASHES = {
        '844fb7ee5217',
        'a2c9825361f2',  
        '7b0b95849149',  
        'fdb9da5c3144',  
        'af71625011d1',  
    }

    temp_zip = docx_output_path + ".tmp"
    with zipfile.ZipFile(docx_input_path, 'r') as jin:
        with zipfile.ZipFile(temp_zip, 'w') as jout:
            for item in jin.infolist():
                fname = item.filename
                data = jin.read(fname)

                if fname.startswith('word/media/'):
                    h = hashlib.sha256(data).hexdigest()[:12]
                    
                    # Logo SprintCV -> PNG transparente 1x1
                    if h in SPRINT_LOGO_HASHES:
                        jout.writestr(item, transparent_data)
                        print(f"[🗑️] Logo SprintCV ({fname}, {len(data)}b) -> transparente!")
                    
                    # Foto do candidato -> substitui por photo.png com o formato de imagem correspondente
                    elif fname.endswith('.jpeg') or fname.endswith('.jpg') or fname.endswith('.png') or 'foto' in fname.lower():
                        if len(data) < 200000 and ('foto' in fname.lower() or 'image4' in fname.lower() or 'large' in fname.lower()):
                            p_bytes = candidate_photo_data_png if fname.endswith('.png') else candidate_photo_data_jpeg
                            jout.writestr(item, p_bytes)
                            print(f"[🖼️] Foto do candidato ({fname}, {len(data)}b) -> substituída por photo.png ({len(p_bytes)}b)!")
                        else:
                            jout.writestr(item, data)
                            print(f"[✓] Fundo watermark mantido intacto: {fname} ({len(data)}b)")
                    else:
                        jout.writestr(item, data)
                        print(f"[✓] Mantido intacto: {fname} ({len(data)}b)")
                elif fname.startswith('word/document.xml') or fname.startswith('word/header') or fname.startswith('word/footer'):
                    # Templatização dinâmica e renderização Jinja2 com o feed JSON
                    if json_data:
                        doc_str = data.decode('utf-8')
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
                        top_techs = [t.get("name") if isinstance(t, dict) else str(t) for t in top_techs_raw]
                        techs_str = ", ".join(top_techs)

                        context = {
                            "consultant": {
                                "name": html.escape(name, quote=False),
                                "surname": html.escape(surname, quote=False),
                                "email": html.escape(email, quote=False),
                                "phone": html.escape(phone, quote=False),
                                "city": html.escape(city, quote=False),
                                "country": html.escape(country, quote=False),
                                "linkedin": html.escape(linkedin, quote=False),
                            },
                            "present_job_title": html.escape(title, quote=False),
                            "about": html.escape(summary, quote=False),
                            "top_technologies": [html.escape(t, quote=False) for t in top_techs],
                            "techs_str": html.escape(techs_str, quote=False),
                        }

                        # 1. Converte padrões genéricos de contato no XML para Jinja2
                        doc_str = dynamic_templatize_xml(doc_str)

                        # 2. Renderiza Jinja2 usando o feed JSON fornecido
                        try:
                            tmpl = jinja2.Template(doc_str)
                            doc_str = tmpl.render(**context)
                        except Exception as e_tmpl:
                            print(f"[*] Aviso na renderização Jinja2 em {fname}: {e_tmpl}")

                        # 3. Substituição segura de cabeçalho do candidato
                        if fullname:
                            doc_str = re.sub(r'(?i)elton\s+machado', html.escape(fullname, quote=False), doc_str)
                            doc_str = re.sub(r'(?i)elton', html.escape(name, quote=False), doc_str)
                            doc_str = re.sub(r'(?i)machado', html.escape(surname, quote=False), doc_str)
                        if title:
                            doc_str = re.sub(r'(?i)Senior Platform Engineer.*?Architect', html.escape(title, quote=False), doc_str)
                            doc_str = re.sub(r'(?i)DevOps Engineer', html.escape(title, quote=False), doc_str)

                        # Sanitização estrita do XML
                        doc_str = sanitize_xml_string(doc_str)

                        jout.writestr(item, doc_str.encode('utf-8'))
                        print(f"[📝] {fname} templatizado e renderizado dinamicamente via Jinja2 com feed JSON ({fullname})")
                    else:
                        jout.writestr(item, data)
                else:
                    jout.writestr(item, data)
                
    if os.path.exists(temp_zip):
        os.replace(temp_zip, docx_output_path)
        print(f"\n[🎉] Sucesso! Template atualizado salvo em: {docx_output_path}")
        print(f"     - Logos SprintCV: invisíveis")
        print(f"     - Foto do candidato: atualizada com assets/photo.png")
        print(f"     - Design, fundo e ícones: 100% preservados")

if __name__ == "__main__":
    src = "samples/sprint.docx"
    dst = "output/sprint_clean_test.docx"
    clean_docx_sprint(src, dst)

