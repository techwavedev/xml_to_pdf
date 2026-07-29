import zipfile
import os
import hashlib

def clean_docx_sprint(docx_input_path: str, docx_output_path: str):
    """
    Limpa um template .docx do SprintCV:
    1. Substitui logos do SprintCV por PNG transparente 1x1 (layout intacto!)
    2. Substitui foto(s) do candidato por fotos fake de pessoa genérica
    Não altera NENHUM XML, mantendo 100% do design, fundo e ícones.
    """
    if not os.path.exists(docx_input_path):
        print(f"[❌] Arquivo não encontrado: {docx_input_path}")
        return
        
    transparent_path = "assets/transparent.png"
    fake_large_path = "assets/fake_large.jpeg"
    fake_small_path = "assets/fake_small.jpeg"
    
    with open(transparent_path, "rb") as f:
        transparent_data = f.read()
    with open(fake_large_path, "rb") as f:
        fake_large_data = f.read()
    with open(fake_small_path, "rb") as f:
        fake_small_data = f.read()

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
                    
                    # Foto JPEG do candidato -> foto fake de pessoa
                    elif fname.endswith('.jpeg') or fname.endswith('.jpg'):
                        # Decide qual tamanho usar com base no tamanho original
                        if len(data) > 50000:
                            jout.writestr(item, fake_large_data)
                            print(f"[🛡️] Foto grande ({fname}, {len(data)}b) -> fake person large!")
                        else:
                            jout.writestr(item, fake_small_data)
                            print(f"[🛡️] Foto pequena ({fname}, {len(data)}b) -> fake person small!")
                    else:
                        # Manter SVGs, fundos de constelação e outros PNGs intactos
                        jout.writestr(item, data)
                        print(f"[✓] Mantido intacto: {fname} ({len(data)}b)")
                else:
                    jout.writestr(item, data)
                
    if os.path.exists(temp_zip):
        os.replace(temp_zip, docx_output_path)
        print(f"\n[🎉] Sucesso! Template limpo salvo em: {docx_output_path}")
        print(f"     - Logos SprintCV: invisíveis")
        print(f"     - Foto do candidato: substituída por pessoa genérica")
        print(f"     - Design, fundo e ícones: 100% preservados")

if __name__ == "__main__":
    src = "Samples/sprint.docx"
    dst = "Samples/sprint_clean.docx"
    clean_docx_sprint(src, dst)
