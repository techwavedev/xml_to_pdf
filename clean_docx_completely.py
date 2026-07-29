import zipfile
import os

EMPTY_FOOTER_XML = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'

def clean_docx_footers(docx_input_path: str, docx_output_path: str):
    """Substitui todos os arquivos de rodapé (footer*.xml) por rodapés vazios no .docx."""
    if not os.path.exists(docx_input_path):
        print(f"[❌] Arquivo de entrada não encontrado: {docx_input_path}")
        return
        
    temp_zip = docx_output_path + ".tmp"
    with zipfile.ZipFile(docx_input_path, 'r') as jin:
        with zipfile.ZipFile(temp_zip, 'w') as jout:
            for item in jin.infolist():
                # Se for um arquivo de rodapé, substitui por XML completamente vazio
                if 'footer' in item.filename.lower() and item.filename.endswith('.xml'):
                    jout.writestr(item.filename, EMPTY_FOOTER_XML)
                    print(f"[✓] Rodapé limpo: {item.filename}")
                # Remove também as imagens do logo do SprintCV
                elif item.filename in ['word/media/image3.png', 'word/media/image4.png', 'word/media/image1.png', 'word/media/image2.png', 'word/media/image5.png']:
                    continue
                else:
                    jout.writestr(item, jin.read(item.filename))
                
    if os.path.exists(temp_zip):
        os.replace(temp_zip, docx_output_path)
        print(f"[🎉] Arquivo .docx 100% limpo sem NENHUM logo no rodapé: {docx_output_path}")

if __name__ == "__main__":
    src = "Samples/Sprint CV Elton Machado 20260729 085709.docx"
    dst = "Samples/template_clean.docx"
    clean_docx_footers(src, dst)
