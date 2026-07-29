import zipfile
import os

def remove_logo_from_docx(docx_input_path: str, docx_output_path: str):
    """Remove a imagem/logo do rodapé do arquivo .docx nativo."""
    if not os.path.exists(docx_input_path):
        return
        
    temp_zip = docx_output_path + ".tmp"
    with zipfile.ZipFile(docx_input_path, 'r') as jin:
        with zipfile.ZipFile(temp_zip, 'w') as jout:
            for item in jin.infolist():
                # Ignora as imagens do logo do SprintCV no footer (image3.png, image4.png)
                if item.filename in ['word/media/image3.png', 'word/media/image4.png']:
                    continue
                jout.writestr(item, jin.read(item.filename))
                
    if os.path.exists(temp_zip):
        os.replace(temp_zip, docx_output_path)
        print(f"[✓] Imagem do rodapé SprintCV removida do arquivo .docx: {docx_output_path}")

if __name__ == "__main__":
    src = "Samples/Sprint CV Elton Machado 20260729 085709.docx"
    dst = "Samples/template_clean.docx"
    remove_logo_from_docx(src, dst)
