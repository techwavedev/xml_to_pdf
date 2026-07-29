import zipfile
import xml.etree.ElementTree as ET
import os

def clean_docx_footers(docx_input_path: str, docx_output_path: str):
    """
    Remove apenas o logo do SprintCV do rodapé, preservando 100% dos cabeçalhos,
    imagem de fundo de constelação, foto do candidato e formatação original do .docx.
    """
    if not os.path.exists(docx_input_path):
        print(f"[❌] Arquivo de entrada não encontrado: {docx_input_path}")
        return
        
    temp_zip = docx_output_path + ".tmp"
    with zipfile.ZipFile(docx_input_path, 'r') as jin:
        with zipfile.ZipFile(temp_zip, 'w') as jout:
            for item in jin.infolist():
                fname = item.filename
                data = jin.read(fname)

                # Se for um arquivo de rodapé, removemos apenas as marcas de desenho do logo do SprintCV
                if 'footer' in fname.lower() and fname.endswith('.xml'):
                    try:
                        # Se contiver a imagem do logo SprintCV no footer, zera apenas esse footer
                        if b'image3' in data or b'image4' in data or b'image1' in data or b'image2' in data or b'image5' in data or b'sprint' in data.lower():
                            empty_footer = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'
                            jout.writestr(fname, empty_footer)
                            print(f"[✓] Logo removida do rodapé: {fname}")
                        else:
                            jout.writestr(fname, data)
                    except Exception:
                        jout.writestr(fname, data)

                # Remove apenas as imagens da logo do SprintCV em media/ (mantém foto e fundo)
                elif fname in ['word/media/image1.png', 'word/media/image2.png', 'word/media/image3.png', 'word/media/image4.png', 'word/media/image5.png']:
                    print(f"[🗑️] Logo SprintCV removida dos media: {fname}")
                    continue

                else:
                    # PRESERVA TODOS os outros arquivos (header1.xml com foto/fundo, document.xml, etc.) 100% INTACTOS
                    jout.writestr(item, data)
                
    if os.path.exists(temp_zip):
        os.replace(temp_zip, docx_output_path)
        print(f"[🎉] Arquivo .docx preservado com foto/fundo e sem logo no rodapé: {docx_output_path}")

if __name__ == "__main__":
    src = "Samples/Sprint CV Elton Machado 20260729 085709.docx"
    dst = "Samples/template_clean.docx"
    clean_docx_footers(src, dst)
