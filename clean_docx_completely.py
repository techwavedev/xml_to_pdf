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
                    
                    # Foto JPEG do candidato -> substitui por photo.png
                    elif fname.endswith('.jpeg') or fname.endswith('.jpg') or 'foto' in fname.lower():
                        # Não substitui a watermark de fundo (image7.jpeg ~228KB)
                        if len(data) < 200000:
                            jout.writestr(item, candidate_photo_data)
                            print(f"[🖼️] Foto do candidato ({fname}, {len(data)}b) -> substituída por photo.png ({len(candidate_photo_data)}b)!")
                        else:
                            # Imagem de fundo watermark preservada
                            jout.writestr(item, data)
                            print(f"[✓] Fundo watermark mantido intacto: {fname} ({len(data)}b)")
                    else:
                        # Manter SVGs, fundos de constelação e outros PNGs intactos
                        jout.writestr(item, data)
                        print(f"[✓] Mantido intacto: {fname} ({len(data)}b)")
                elif fname == 'word/document.xml' and json_data:
                    # Substituir dados do candidato se houver json_data
                    doc_str = data.decode('utf-8')
                    consultant = json_data.get("consultant", {})
                    name = consultant.get("name", "")
                    surname = consultant.get("surname", "")
                    fullname = f"{name} {surname}".strip()
                    title = json_data.get("present_job_title", "")
                    email = consultant.get("email", "")
                    phone = consultant.get("phone", "")

                    if fullname:
                        doc_str = re.sub(r'Elton Machado', fullname, doc_str)
                    if title:
                        doc_str = re.sub(r'DevOps Engineer', title, doc_str)
                    
                    jout.writestr(item, doc_str.encode('utf-8'))
                    print(f"[📝] document.xml atualizado com dados de {fullname} ({title})")
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

