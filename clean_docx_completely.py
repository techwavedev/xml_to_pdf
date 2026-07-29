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
    
    candidate_photo_data_jpeg = get_candidate_photo_bytes(photo_path, target_format='JPEG')
    candidate_photo_data_png = get_candidate_photo_bytes(photo_path, target_format='PNG')

    # Hashes SHA-256 (primeiros 12 chars) das logos do SprintCV
    SPRINT_LOGO_HASHES = {
        '844fb7ee5217',  # 1592 bytes (Logo principal, azul escuro)
        'a2c9825361f2',  # 238 bytes  
        '7b0b95849149',  # 286 bytes
        'fdb9da5c3144',  # 437 bytes
        'af71625011d1',  # 9240 bytes (Logo grande no rodapé - image6 no sprint.docx)
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
                        # Não substitui a watermark de fundo (image7.jpeg ~228KB)
                        if len(data) < 200000 and ('foto' in fname.lower() or 'image4' in fname.lower() or 'large' in fname.lower()):
                            p_bytes = candidate_photo_data_png if fname.endswith('.png') else candidate_photo_data_jpeg
                            jout.writestr(item, p_bytes)
                            print(f"[🖼️] Foto do candidato ({fname}, {len(data)}b) -> substituída por photo.png ({len(p_bytes)}b)!")
                        else:
                            # Imagem de fundo watermark preservada
                            jout.writestr(item, data)
                            print(f"[✓] Fundo watermark mantido intacto: {fname} ({len(data)}b)")
                    else:
                        # Manter SVGs, fundos de constelação e outros PNGs intactos
                        jout.writestr(item, data)
                        print(f"[✓] Mantido intacto: {fname} ({len(data)}b)")
                elif fname.startswith('word/document.xml') or fname.startswith('word/header') or fname.startswith('word/footer'):
                    # Substituição abrangente de textos do candidato no XML do Word com sanitização XML
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

                        # Escapa caracteres especiais de XML (& -> &amp;) para os valores inseridos
                        fullname_xml = html.escape(fullname, quote=False)
                        title_xml = html.escape(title, quote=False)
                        email_xml = html.escape(email, quote=False)
                        phone_xml = html.escape(phone, quote=False)
                        location_xml = html.escape(location, quote=False)
                        linkedin_xml = html.escape(linkedin, quote=False)

                        # Regex de substituição para cabeçalho e contatos do candidato
                        if fullname:
                            doc_str = re.sub(r'(?i)elton\s+machado', fullname_xml, doc_str)
                        if title:
                            doc_str = re.sub(r'(?i)Senior Platform Engineer (&amp;|&) AI/Cloud Architect \| Site Reliability Engineer', title_xml, doc_str)
                            doc_str = re.sub(r'(?i)DevOps Engineer', title_xml, doc_str)
                            doc_str = re.sub(r'(?i)Senior Platform Engineer', title_xml, doc_str)
                        if email:
                            doc_str = re.sub(r'(?i)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email_xml, doc_str)
                        if phone:
                            doc_str = re.sub(r'\(\+351\)\s*308803508', phone_xml, doc_str)
                            doc_str = re.sub(r'\+55\s*47\s*99\s*162\s*2489', phone_xml, doc_str)
                        if location:
                            doc_str = re.sub(r'Aveiro\s*,\s*Portugal', location_xml, doc_str)
                            doc_str = re.sub(r'Itapema,\s*SC', location_xml, doc_str)
                        if linkedin:
                            doc_str = re.sub(r'https?://[a-zA-Z0-9./_-]*linkedin[a-zA-Z0-9./_-]*', linkedin_xml, doc_str)

                        # Sanitização estrita do XML para garantir que não existam & soltos sem &amp;
                        doc_str = sanitize_xml_string(doc_str)

                        jout.writestr(item, doc_str.encode('utf-8'))
                        print(f"[📝] {fname} atualizado e sanitizado com dados de {fullname} ({title})")
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

