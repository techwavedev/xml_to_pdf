#!/usr/bin/env python3
"""
cv_builder.py
-------------------------------------------------------------------------
Gerador de Currículos PDF a partir de JSON com Suporte Multiplataforma 
(macOS, Windows, Linux) a Templates DOCX e HTML/CSS, com Incorporação ATS HR-XML.

Fluxo:
 1. Carrega os dados do CV em formato JSON (base única de dados).
 2. Converte automaticamente o JSON para HR-XML (padrão internacional ATS).
 3. Se for fornecido um arquivo .docx de entrada (--docx):
    - Limpa automaticamente as logos/imagens do rodapé (ex: logo SprintCV).
    - Converte o .docx nativo em PDF com 100% de fidelidade (MS Word no Windows/macOS, LibreOffice no Linux/Windows/Mac).
    - Caso contrário, renderiza o template gráfico HTML/CSS escolhido via Playwright (Chromium).
 4. O resultado final gerado é SEMPRE um arquivo PDF (.pdf) salvo em output/.
 5. Injeta o XML gerado no PDF (anexo, metadados XMP e dicionário /Info).
 6. (Opcional) Gera um arquivo .docx de saída somente se o usuário solicitar via --out-docx.
-------------------------------------------------------------------------
"""

import sys
import os
import json
import shutil
import platform
import subprocess
import argparse
from pathlib import Path
from jinja2 import Template

import json_to_xml
import embed_xml_cv
import clean_docx_completely

CHROME_PATH_MAC = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TEMPLATES_DIR = Path("templates")
OUTPUT_DIR = Path("output")

def convert_docx_to_pdf_cross_platform(docx_path: str, pdf_path: str) -> bool:
    """Converte um arquivo .docx para PDF de forma multiplataforma (macOS, Windows, Linux)."""
    abs_docx = os.path.abspath(docx_path)
    abs_pdf = os.path.abspath(pdf_path)
    system = platform.system()

    # 1. No Windows (se MS Word estiver instalado)
    if system == "Windows":
        try:
            import win32com.client
            word = win32com.client.Dispatch("Word.Application")
            doc = word.Documents.Open(abs_docx)
            doc.SaveAs(abs_pdf, FileFormat=17) # 17 = wdFormatPDF
            doc.Close()
            word.Quit()
            print(f"[✓] DOCX convertido para PDF via MS Word (Windows): {pdf_path}")
            return True
        except Exception as e_win:
            print(f"[*] Tentativa de conversão via MS Word no Windows falhou: {e_win}")

    # 2. No macOS (via AppleScript MS Word)
    if system == "Darwin":
        applescript = f'''
        tell application "Microsoft Word"
            open (POSIX file "{abs_docx}")
            save as active document file name "{abs_pdf}" file format format PDF
            close active document saving no
        end tell
        '''
        try:
            subprocess.run(["osascript", "-e", applescript], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"[✓] DOCX convertido para PDF via MS Word (macOS): {pdf_path}")
            return True
        except Exception:
            pass

    # 3. No Linux, Windows ou macOS (via LibreOffice / soffice se instalado)
    soffice_bin = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice_bin:
        try:
            out_dir = os.path.dirname(abs_pdf)
            cmd = [soffice_bin, "--headless", "--convert-to", "pdf", abs_docx, "--outdir", out_dir]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            converted_default = os.path.join(out_dir, Path(abs_docx).stem + ".pdf")
            if os.path.exists(converted_default) and converted_default != abs_pdf:
                os.replace(converted_default, abs_pdf)
            print(f"[✓] DOCX convertido para PDF via LibreOffice ({system}): {pdf_path}")
            return True
        except Exception as e_lo:
            print(f"[*] Conversão via LibreOffice falhou: {e_lo}")

    return False

def render_html_template(json_data: dict, template_name: str) -> str:
    """Renderiza os dados JSON em um arquivo HTML usando Jinja2."""
    template_file = TEMPLATES_DIR / f"{template_name}.html"
    if not template_file.exists():
        template_file = Path(template_name)
        if not template_file.exists():
            print(f"[❌] Template '{template_name}' não encontrado na pasta templates/ ou no caminho especificado.")
            sys.exit(1)

    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()

import base64

def ensure_b64_assets(json_data: dict) -> dict:
    """Carrega e converte assets de imagem (foto.png e fundo) para base64 se não fornecidos."""
    assets_dir = Path("assets")
    
    # 1. Carregar photo.png como photo_b64
    if "photo_b64" not in json_data or not json_data["photo_b64"]:
        photo_path = assets_dir / "photo.png"
        if not photo_path.exists():
            photo_path = assets_dir / "original_candidate_photo.jpeg"
        if not photo_path.exists():
            photo_path = assets_dir / "fake_large.jpeg"
            
        if photo_path.exists():
            with open(photo_path, "rb") as f:
                json_data["photo_b64"] = base64.b64encode(f.read()).decode('utf-8')
                print(f"[✓] Foto do candidato embutida ({photo_path.name}) -> photo_b64")

    # 2. Carregar imagem de fundo (constelação) como bg_b64
    if "bg_b64" not in json_data or not json_data["bg_b64"]:
        bg_path = assets_dir / "image7.jpeg"
        if not bg_path.exists():
            bg_path = assets_dir / "image6.png"
        if not bg_path.exists():
            bg_path = assets_dir / "image4.png"
            
        if bg_path.exists():
            with open(bg_path, "rb") as f:
                json_data["bg_b64"] = base64.b64encode(f.read()).decode('utf-8')
                print(f"[✓] Fundo watermark embutido ({bg_path.name}) -> bg_b64")

    # 3. Atualizar/Salvar assets/b64_assets.json
    try:
        b64_payload = {
            "photo": json_data.get("photo_b64", ""),
            "bg": json_data.get("bg_b64", "")
        }
        with open(assets_dir / "b64_assets.json", "w", encoding="utf-8") as f:
            json.dump(b64_payload, f)
    except Exception:
        pass

    return json_data

def render_html_template(json_data: dict, template_name: str) -> str:
    """Renderiza os dados JSON em um arquivo HTML usando Jinja2."""
    template_file = TEMPLATES_DIR / f"{template_name}.html"
    if not template_file.exists():
        template_file = Path(template_name)
        if not template_file.exists():
            print(f"[❌] Template '{template_name}' não encontrado na pasta templates/ ou no caminho especificado.")
            sys.exit(1)

    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()

    # Garante a codificação base64 de assets de imagem (foto e fundo)
    json_data = ensure_b64_assets(json_data)

    jinja_template = Template(template_content)
    rendered_html = jinja_template.render(**json_data)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    temp_html_path = OUTPUT_DIR / f"temp_{template_name}.html"
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(rendered_html)

    print(f"[✓] Template HTML '{template_name}' renderizado com sucesso: {temp_html_path}")
    return str(temp_html_path)

def html_to_pdf(html_path: str, temp_pdf_path: str) -> str:
    """Converte arquivo HTML para PDF de forma multiplataforma via Playwright (Chromium) ou Chrome."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    abs_html_path = os.path.abspath(html_path)
    abs_html_url = f"file://{abs_html_path}"

    # 1. Tenta Playwright (Multiplataforma: Windows, Linux, Mac)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(abs_html_url, wait_until="networkidle")
            page.pdf(
                path=temp_pdf_path,
                format="A4",
                print_background=True,
                margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
            )
            browser.close()
        print(f"[✓] PDF gráfico renderizado via Playwright (Chromium): {temp_pdf_path}")
        return temp_pdf_path
    except Exception as e_pw:
        print(f"[*] Playwright não disponível/falhou: {e_pw}. Tentando Google Chrome...")

    # 2. Fallback Google Chrome Headless (Multiplataforma)
    chrome_bin = shutil.which("google-chrome") or shutil.which("chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if not chrome_bin and os.path.exists(CHROME_PATH_MAC):
        chrome_bin = CHROME_PATH_MAC

    if chrome_bin:
        cmd = [
            chrome_bin,
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={temp_pdf_path}",
            abs_html_url
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"[✓] PDF gráfico renderizado via Google Chrome Headless: {temp_pdf_path}")
            return temp_pdf_path
        except Exception as e_chrome:
            print(f"[*] Aviso ao executar Chrome Headless: {e_chrome}")

    # 3. Fallback: Se nem Playwright nem Chrome estiverem disponíveis
    print("[❌] Erro: Playwright ou Chrome Headless são necessários para renderizar o PDF gráfico.")
    return temp_pdf_path

DOCX_TO_TEMPLATE_MAP = {
    "expert": "modern",
    "itexpert": "modern",
    "modern": "modern",
    "resume": "classic",
    "itresume": "classic",
    "classic": "classic",
    "mlops": "tech_dark",
    "dark": "tech_dark",
    "tech_dark": "tech_dark",
    "sprint": "sprintcv_docx",
    "sprint_clean": "sprintcv_docx",
    "sprintcv": "sprintcv_docx",
}

def find_docx_file(docx_arg: str) -> str:
    """Encontra o arquivo .docx aceitando variação de maiúsculas/minúsculas ou nome parcial em samples/."""
    if not docx_arg:
        return None
    if os.path.exists(docx_arg):
        return docx_arg

    p = Path(docx_arg)
    search_dirs = [p.parent, Path("samples"), Path(".")]
    target_stem = p.stem.lower()

    for sdir in search_dirs:
        if sdir.exists():
            for candidate in sdir.glob("*.docx"):
                c_stem = candidate.stem.lower()
                if target_stem in c_stem or c_stem in target_stem:
                    print(f"[🔍] Arquivo DOCX localizado: '{candidate}' (para '{docx_arg}')")
                    return str(candidate)

    return docx_arg

def resolve_template_name(template_name: str, docx_template: str = None) -> str:
    """Mapeia o arquivo .docx de entrada ou nome do template para o modelo HTML/CSS gráfico correspondente."""
    if docx_template:
        stem = Path(docx_template).stem.lower()
        for key, target_tmpl in DOCX_TO_TEMPLATE_MAP.items():
            if key in stem or stem in key:
                return target_tmpl
    return template_name or "sprintcv_docx"

def build_cv_from_json(json_path: str, template_name: str = "sprintcv_docx", docx_template: str = None, output_pdf: str = None, out_docx: str = None):
    """Executa o fluxo completo de forma multiplataforma: JSON / DOCX -> PDF Otimizado com HR-XML ATS."""
    if not os.path.exists(json_path):
        print(f"[❌] Arquivo JSON de entrada não encontrado: {json_path}")
        sys.exit(1)

    # Localiza o arquivo .docx aceitando nomes parciais/minúsculas (ex: 'samples/expert.docx' -> 'samples/ITExpert.docx')
    if docx_template:
        resolved_docx = find_docx_file(docx_template)
        if resolved_docx and os.path.exists(resolved_docx):
            docx_template = resolved_docx

    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    # Resolve o template gráfico com base no modelo DOCX ou parâmetro fornecido
    effective_template = resolve_template_name(template_name, docx_template)

    # Garante o carregamento de photo_b64 e bg_b64
    json_data = ensure_b64_assets(json_data)

    consultant = json_data.get("consultant", {})
    c_name = f"{consultant.get('name', '')}_{consultant.get('surname', '')}".strip("_") or "CV"

    # Nomeia o PDF final baseado no sample/template utilizado se output_pdf não for explicitado
    if not output_pdf:
        if docx_template:
            sample_stem = Path(docx_template).stem
            output_pdf = str(OUTPUT_DIR / f"{sample_stem}_{c_name}_ats.pdf")
        else:
            json_stem = Path(json_path).stem
            output_pdf = str(OUTPUT_DIR / f"{json_stem}_{effective_template}_{c_name}_ats.pdf")
    else:
        output_pdf = embed_xml_cv.ensure_output_dir(output_pdf)

    # 1. Gerar HR-XML a partir do JSON
    xml_output_path = str(OUTPUT_DIR / "generated_resume.xml")
    json_to_xml.json_file_to_xml_file(json_path, xml_output_path)

    temp_pdf = str(OUTPUT_DIR / "temp_rendered.pdf")

    # 2. Se for especificado um arquivo .docx de entrada, limpa os rodapés, atualiza foto/dados e converte nativamente para PDF
    if docx_template and os.path.exists(docx_template):
        sample_stem = Path(docx_template).stem
        print(f"\n[*] Utilizando modelo .docx de entrada como DESIGN BASE: {docx_template}")
        
        # Gera o DOCX populado com o layout e formatação originais do modelo
        populated_docx = str(OUTPUT_DIR / f"{sample_stem}_{c_name}.docx")
        clean_docx_completely.clean_docx_sprint(docx_template, populated_docx, photo_path="assets/photo.png", json_data=json_data)
        print(f"[✓] Arquivo DOCX populado com a formatação original salvo em: {populated_docx}")
        
        # Converte o .docx populado para PDF com 100% de fidelidade ao layout do Word
        success = convert_docx_to_pdf_cross_platform(populated_docx, temp_pdf)
        
        if success:
            embed_xml_cv.embed_xml_into_pdf(temp_pdf, xml_output_path, output_pdf, attachment_name="resume.xml")
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)
            if not out_docx and os.path.exists(populated_docx):
                os.remove(populated_docx)
            print(f"\n=======================================================")
            print(f" 🎉 PROCESSO CONCLUÍDO COM SUCESSO! ({platform.system()})")
            print(f" 📄 PDF de Saída (Fidelidade Word 100%): {output_pdf}")
            print(f" 📊 Base de dados JSON: {json_path}")
            print(f" 🎨 Modelo .docx utilizado: {docx_template}")
            print(f"=======================================================\n")
            return
        else:
            print(f"\n[⚠️] O MS Word não está em execução ou o LibreOffice não foi encontrado no seu sistema.")
            print(f"     📄 O arquivo .docx populado mantendo 100% da formatação e design original foi salvo em:")
            print(f"        -> {populated_docx}")
            print(f"     💡 Para converter seu modelo .docx diretamente para PDF no Mac:")
            print(f"        1. Certifique-se de que o Microsoft Word está aberto, ou")
            print(f"        2. Instale o LibreOffice via Terminal: brew install --cask libreoffice")
            print(f"     [*] Renderizando versão visual alternativa via HTML/CSS...")
            
            rendered_html = render_html_template(json_data, effective_template)
            html_to_pdf(rendered_html, temp_pdf)
            if os.path.exists(rendered_html):
                os.remove(rendered_html)
    else:
        # 3. Renderizar HTML a partir do Template escolhido se não for fornecido arquivo .docx
        rendered_html = render_html_template(json_data, effective_template)
        html_to_pdf(rendered_html, temp_pdf)
        if os.path.exists(rendered_html):
            os.remove(rendered_html)

    # 4. Injetar XML e Metadados ATS no PDF final de saída
    embed_xml_cv.embed_xml_into_pdf(temp_pdf, xml_output_path, output_pdf, attachment_name="resume.xml")

    # Limpeza de arquivos temporários
    if os.path.exists(temp_pdf):
        os.remove(temp_pdf)

    print(f"\n=======================================================")
    print(f" 🎉 PROCESSO CONCLUÍDO COM SUCESSO! ({platform.system()})")
    print(f" 📄 PDF de Saída (Final): {output_pdf}")
    print(f" 📊 Base de dados JSON: {json_path}")
    print(f" 🎨 Modelo utilizado: {docx_template or template_name}")
    if out_docx:
        print(f" 📝 DOCX de Saída Adicional: {out_docx}")
    print(f"=======================================================\n")

def list_templates():
    """Lista os templates gráficos disponíveis na pasta templates/."""
    print("\nTemplates Gráficos Disponíveis:")
    if TEMPLATES_DIR.exists():
        for t in TEMPLATES_DIR.glob("*.html"):
            print(f" - {t.stem}")
    print("")

def main():
    parser = argparse.ArgumentParser(description="Gerador de CVs PDF a partir de JSON Multiplataforma (Windows, Linux, Mac) com ATS XML.")
    parser.add_argument("--json", default="sample_cv.json", help="Caminho do arquivo JSON contendo a base do currículo (padrão: sample_cv.json)")
    parser.add_argument("--template", default="sprintcv_docx", help="Nome do template gráfico HTML (sprintcv_docx, modern, classic, tech_dark) (padrão: sprintcv_docx)")
    parser.add_argument("--docx", default=None, help="Caminho opcional para um arquivo modelo .docx de ENTRADA (ex: 'Samples/Sprint CV Elton Machado 20260729 085709.docx')")
    parser.add_argument("--out", default=None, help="Caminho do PDF de SAÍDA (padrão: output/<nome>_<template>_ats.pdf)")
    parser.add_argument("--out-docx", action="store_true", help="Gera também um arquivo .docx de saída sem logos de rodapé além do PDF de saída.")
    parser.add_argument("--list-templates", action="store_true", help="Lista os templates gráficos disponíveis.")

    args = parser.parse_args()

    if args.list_templates:
        list_templates()
        return

    build_cv_from_json(args.json, args.template, args.docx, args.out, args.out_docx)

if __name__ == "__main__":
    main()
