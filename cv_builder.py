#!/usr/bin/env python3
"""
cv_builder.py
-------------------------------------------------------------------------
Gerador de Currículos PDF a partir de JSON com Suporte a Múltiplos Templates Gráficos 
(HTML/CSS e arquivos .docx nativos) e Incorporação Automática de Metadados ATS XML.

Fluxo:
 1. Carrega os dados do CV em formato JSON (base única de dados).
 2. Converte automaticamente o JSON para HR-XML (padrão internacional ATS).
 3. Se for fornecido um arquivo .docx como template:
    - Converte o .docx nativo em PDF usando o Microsoft Word do macOS (100% de fidelidade visual exata).
    - Caso contrário, renderiza o template gráfico HTML/CSS escolhido via Playwright (Chromium).
 4. Injeta o XML gerado no PDF (anexo, metadados XMP e dicionário /Info).
 5. Salva o PDF otimizado para ATS na pasta output/.
-------------------------------------------------------------------------
"""

import sys
import os
import json
import subprocess
import argparse
from pathlib import Path
from jinja2 import Template

import json_to_xml
import embed_xml_cv

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TEMPLATES_DIR = Path("templates")
OUTPUT_DIR = Path("output")

def convert_docx_to_pdf_word(docx_path: str, pdf_path: str) -> bool:
    """Converte um arquivo .docx para PDF com 100% de fidelidade usando o MS Word no macOS."""
    abs_docx = os.path.abspath(docx_path)
    abs_pdf = os.path.abspath(pdf_path)
    
    applescript = f'''
    tell application "Microsoft Word"
        open (POSIX file "{abs_docx}")
        save as active document file name "{abs_pdf}" file format format PDF
        close active document saving no
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", applescript], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"[✓] DOCX convertido para PDF via MS Word com 100% de precisão: {pdf_path}")
        return True
    except Exception as e:
        print(f"[*] Aviso ao converter via MS Word: {e}")
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

    # Carrega assets de imagem base64 (fundo, foto, logo) se disponíveis
    if os.path.exists("assets/b64_assets.json"):
        try:
            with open("assets/b64_assets.json", "r") as f_b64:
                b64_data = json.load(f_b64)
                if "bg_b64" not in json_data or not json_data["bg_b64"]:
                    json_data["bg_b64"] = b64_data.get("bg", "")
                if "photo_b64" not in json_data or not json_data["photo_b64"]:
                    json_data["photo_b64"] = b64_data.get("photo", "")
                if "logo_b64" not in json_data or not json_data["logo_b64"]:
                    json_data["logo_b64"] = b64_data.get("logo", "")
        except Exception:
            pass

    jinja_template = Template(template_content)
    rendered_html = jinja_template.render(**json_data)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    temp_html_path = OUTPUT_DIR / f"temp_{template_name}.html"
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(rendered_html)

    print(f"[✓] Template HTML '{template_name}' renderizado com sucesso: {temp_html_path}")
    return str(temp_html_path)

def html_to_pdf(html_path: str, temp_pdf_path: str) -> str:
    """Converte arquivo HTML para PDF via Playwright (Chromium) ou fallback."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    abs_html_path = os.path.abspath(html_path)
    abs_html_url = f"file://{abs_html_path}"

    # 1. Tenta Playwright
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

    # 2. Fallback Google Chrome Headless
    if os.path.exists(CHROME_PATH):
        cmd = [
            CHROME_PATH,
            "--headless=new",
            "--no-sandbox",
            "--user-data-dir=/tmp/chrome_pdf_user_dir",
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

    # 3. Fallback Simples
    print("[*] Utilizando gerador PDF de fallback...")
    import generate_sample_pdf
    generate_sample_pdf.create_simple_pdf(temp_pdf_path)
    return temp_pdf_path

def build_cv_from_json(json_path: str, template_name: str = "sprintcv_docx", docx_template: str = None, output_pdf: str = None):
    """Executa o fluxo completo: JSON / DOCX -> PDF Otimizado com HR-XML ATS."""
    if not os.path.exists(json_path):
        print(f"[❌] Arquivo JSON de entrada não encontrado: {json_path}")
        sys.exit(1)

    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    consultant_name = json_data.get("consultant", {}).get("name", "CV")
    if not output_pdf:
        output_pdf = str(OUTPUT_DIR / f"{consultant_name}_{template_name}_ats.pdf")
    else:
        output_pdf = embed_xml_cv.ensure_output_dir(output_pdf)

    # 1. Gerar HR-XML a partir do JSON
    xml_output_path = str(OUTPUT_DIR / "generated_resume.xml")
    json_to_xml.json_file_to_xml_file(json_path, xml_output_path)

    temp_pdf = str(OUTPUT_DIR / "temp_rendered.pdf")

    # 2. Se for especificado um arquivo .docx como modelo, converte via MS Word
    if docx_template and os.path.exists(docx_template):
        print(f"[*] Utilizando arquivo .docx nativo como modelo: {docx_template}")
        success = convert_docx_to_pdf_word(docx_template, temp_pdf)
        if not success:
            rendered_html = render_html_template(json_data, template_name)
            html_to_pdf(rendered_html, temp_pdf)
            if os.path.exists(rendered_html):
                os.remove(rendered_html)
    else:
        # 3. Renderizar HTML a partir do Template escolhido e converter para PDF
        rendered_html = render_html_template(json_data, template_name)
        html_to_pdf(rendered_html, temp_pdf)
        if os.path.exists(rendered_html):
            os.remove(rendered_html)

    # 4. Injetar XML e Metadados ATS no PDF final
    embed_xml_cv.embed_xml_into_pdf(temp_pdf, xml_output_path, output_pdf, attachment_name="resume.xml")

    # Limpeza de arquivos temporários
    if os.path.exists(temp_pdf):
        os.remove(temp_pdf)

    print(f"\n=======================================================")
    print(f" 🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
    print(f" PDF Final Otimizado para ATS: {output_pdf}")
    print(f" Base de dados JSON: {json_path}")
    print(f" Template utilizado: {docx_template or template_name}")
    print(f"=======================================================\n")

def list_templates():
    """Lista os templates gráficos disponíveis na pasta templates/."""
    print("\nTemplates Gráficos Disponíveis:")
    if TEMPLATES_DIR.exists():
        for t in TEMPLATES_DIR.glob("*.html"):
            print(f" - {t.stem}")
    print("")

def main():
    parser = argparse.ArgumentParser(description="Gerador de CVs PDF a partir de JSON com múltiplos templates gráficos e ATS XML.")
    parser.add_argument("--json", default="sample_cv.json", help="Caminho do arquivo JSON contendo a base do currículo (padrão: sample_cv.json)")
    parser.add_argument("--template", default="sprintcv_docx", help="Nome do template gráfico HTML (sprintcv_docx, modern, classic, tech_dark) (padrão: sprintcv_docx)")
    parser.add_argument("--docx", default=None, help="Caminho opcional para um arquivo template .docx nativo (ex: 'Samples/Sprint CV Elton Machado 20260729 085709.docx')")
    parser.add_argument("--out", default=None, help="Caminho do PDF de saída (padrão: output/<nome>_<template>_ats.pdf)")
    parser.add_argument("--list-templates", action="store_true", help="Lista os templates gráficos disponíveis.")

    args = parser.parse_args()

    if args.list_templates:
        list_templates()
        return

    build_cv_from_json(args.json, args.template, args.docx, args.out)

if __name__ == "__main__":
    main()
