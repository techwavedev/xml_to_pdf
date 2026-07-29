import subprocess
import os
import sys

def convert_docx_to_pdf_ms_word(docx_path: str, pdf_path: str) -> bool:
    """Converte um arquivo .docx para PDF de forma 100% exata usando o Microsoft Word no macOS."""
    abs_docx = os.path.abspath(docx_path)
    abs_pdf = os.path.abspath(pdf_path)
    
    applescript = f'''
    tell application "Microsoft Word"
        set docPath to POSIX file "{abs_docx}"
        set pdfPath to POSIX file "{abs_pdf}"
        set originalSetting to screen updating of application "Microsoft Word"
        set screen updating of application "Microsoft Word" to false
        open docPath
        save as active document file name pdfPath file format format PDF
        close active document saving no
        set screen updating of application "Microsoft Word" to originalSetting
    end tell
    '''
    try:
        res = subprocess.run(["osascript", "-e", applescript], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"[✓] DOCX convertido para PDF com 100% de precisão via Microsoft Word: {pdf_path}")
        return True
    except Exception as e:
        print(f"[❌] Falha ao converter via MS Word: {e}")
        return False

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "Samples/Sprint CV Elton Machado 20260729 085709.docx"
    dst = sys.argv[2] if len(sys.argv) > 2 else "output/exact_word_doc.pdf"
    convert_docx_to_pdf_ms_word(src, dst)
