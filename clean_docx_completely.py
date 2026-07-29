import zipfile
import os
import hashlib

def clean_docx_footers(docx_input_path: str, docx_output_path: str):
    """
    Substitui logos do SprintCV por uma imagem transparente (1x1) e 
    substitui a foto do candidato por um Avatar Genérico.
    Não altera NENHUM arquivo XML, garantindo 100% de preservação do layout!
    """
    if not os.path.exists(docx_input_path):
        print(f"[❌] Arquivo de entrada não encontrado: {docx_input_path}")
        return
        
    generic_avatar_path = "assets/fake_photo.jpeg"
    if not os.path.exists(generic_avatar_path):
        generic_avatar_path = "assets/sample_photo.jpeg"
        
    transparent_path = "assets/transparent.png"
    with open(transparent_path, "rb") as f:
        transparent_data = f.read()

    with open(generic_avatar_path, "rb") as f:
        generic_avatar_data = f.read()
        
    # Hashes SHA-256 conhecidos das logos do SprintCV inseridas nos templates
    SPRINT_LOGO_HASHES = {
        '844fb7ee5217', # 1592 bytes (Logo principal)
        'a2c9825361f2', # 238 bytes (Variante watermark)
        '7b0b95849149', # 286 bytes (Variante pequena)
        'fdb9da5c3144'  # 437 bytes (Variante)
    }

    temp_zip = docx_output_path + ".tmp"
    with zipfile.ZipFile(docx_input_path, 'r') as jin:
        with zipfile.ZipFile(temp_zip, 'w') as jout:
            for item in jin.infolist():
                fname = item.filename
                data = jin.read(fname)

                if fname.startswith('word/media/'):
                    h = hashlib.sha256(data).hexdigest()[:12]
                    
                    # Se for uma logo identificada do SprintCV, substitui por PNG Transparente 1x1
                    if h in SPRINT_LOGO_HASHES:
                        jout.writestr(item, transparent_data)
                        print(f"[🗑️] Logo SprintCV ({fname}) tornada invisível!")
                    
                    # Se for a foto JPEG do candidato, substitui pelo Avatar Falso
                    elif fname.endswith('.jpeg') or fname.endswith('.jpg'):
                        jout.writestr(item, generic_avatar_data)
                        print(f"[🛡️] Foto pessoal ({fname}) substituída pelo Avatar Genérico de Exemplo!")
                        
                    else:
                        jout.writestr(item, data) # Mantém fundos e outros ícones intactos
                else:
                    # Todos os XMLs (rodapés, cabeçalhos, design) são mantidos 100% INTACTOS
                    jout.writestr(item, data)
                
    if os.path.exists(temp_zip):
        os.replace(temp_zip, docx_output_path)
        print(f"[🎉] Arquivo .docx blindado com sucesso: Layout 100% original, mas sem logos e sem foto pessoal!")

if __name__ == "__main__":
    src = "Samples/modern.docx"
    dst = "Samples/template_clean.docx"
    clean_docx_footers(src, dst)
