import zipfile
import os

EMPTY_FOOTER_XML = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'
EMPTY_HEADER_XML = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'

# Apenas a foto do candidato (image7/large_foto) e o fundo de constelação (image6) são mantidos
ALLOWED_MEDIA = ['word/media/image6.png', 'word/media/image7.jpeg', 'word/media/large_foto.jpeg']

def clean_docx_footers(docx_input_path: str, docx_output_path: str):
    """Remove 100% de todas as marcas d'água e logos (escuras, claras e d'água) do SprintCV no arquivo .docx."""
    if not os.path.exists(docx_input_path):
        print(f"[❌] Arquivo de entrada não encontrado: {docx_input_path}")
        return
        
    temp_zip = docx_output_path + ".tmp"
    with zipfile.ZipFile(docx_input_path, 'r') as jin:
        with zipfile.ZipFile(temp_zip, 'w') as jout:
            for item in jin.infolist():
                fname = item.filename
                
                # Zera todos os arquivos de rodapé
                if 'footer' in fname.lower() and fname.endswith('.xml'):
                    jout.writestr(fname, EMPTY_FOOTER_XML)
                    print(f"[✓] Rodapé limpo: {fname}")
                    
                # Zera os arquivos de cabeçalho que contêm a marca d'água do SprintCV
                elif 'header' in fname.lower() and fname.endswith('.xml'):
                    # Zera o cabeçalho para apagar a marca d'água
                    jout.writestr(fname, EMPTY_HEADER_XML)
                    print(f"[✓] Cabeçalho/Marca d'água SprintCV limpo: {fname}")
                
                # Se for um arquivo na pasta media/ que NÃO seja a foto ou o fundo de constelação, apaga
                elif fname.startswith('word/media/'):
                    if fname in ALLOWED_MEDIA:
                        jout.writestr(item, jin.read(fname))
                    else:
                        print(f"[🗑️] Logo/Marca d'água excluída do arquivo .docx: {fname}")
                        continue
                else:
                    jout.writestr(item, jin.read(fname))
                
    if os.path.exists(temp_zip):
        os.replace(temp_zip, docx_output_path)
        print(f"[🎉] Arquivo .docx 100% purificado sem NENHUMA marca d'água ou logo do SprintCV: {docx_output_path}")

if __name__ == "__main__":
    src = "Samples/Sprint CV Elton Machado 20260729 085709.docx"
    dst = "Samples/template_clean.docx"
    clean_docx_footers(src, dst)
