#!/usr/bin/env python3
"""
cv_builder.py
-------------------------------------------------------------------------
Gerador de Currículos PDF a partir de JSON com Suporte a Múltiplos Templates Gráficos 
e Incorporação Automática de Metadados ATS XML.

Fluxo:
 1. Carrega os dados do CV em formato JSON (base única de dados).
 2. Converte automaticamente o JSON para HR-XML (padrão internacional ATS).
 3. Renderiza o CV no template gráfico escolhido (modern, classic, tech_dark, etc.).
 4. Converte o HTML em PDF com renderização gráfica profissional.
 5. Injeta o XML gerado no PDF (anexo, metadados XMP e dicionário /Info).
 6. Salva o PDF otimizado para ATS na pasta output/.

Uso:
  python3 cv_builder.py --json sample_cv.json --template modern
  python3 cv_builder.py --json sample_cv.json --template classic
  python3 cv_builder.py --json sample_cv.json --template tech_dark --out output/meu_cv_tech.pdf
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

def render_html_template(json_data: dict, template_name: str) -> str:
    """Renderiza os dados JSON em um arquivo HTML usando Jinja2."""
    template_file = TEMPLATES_DIR / f"{template_name}.html"
    if not template_file.exists():
        # Se for um caminho direto para um arquivo html customizado
        template_file = Path(template_name)
        if not template_file.exists():
            print(f"[❌] Template '{template_name}' não encontrado na pasta templates/ ou no caminho especificado.")
            sys.exit(1)

    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()

    jinja_template = Template(template_content)
    rendered_html = jinja_template.render(**json_data)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    temp_html_path = OUTPUT_DIR / f"temp_{template_name}.html"
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(rendered_html)

    print(f"[✓] Template HTML '{template_name}' renderizado com sucesso: {temp_html_path}")
    return str(temp_html_path)

def html_to_pdf(html_path: str, temp_pdf_path: str) -> str:
    """Converte arquivo HTML para PDF via Google Chrome Headless ou fallback."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if os.path.exists(CHROME_PATH):
        cmd = [
            CHROME_PATH,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={temp_pdf_path}",
            html_path
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"[✓] PDF gráfico renderizado via Google Chrome Headless: {temp_pdf_path}")
            return temp_pdf_path
        except Exception as e:
            print(f"[*] Aviso ao executar Chrome Headless: {e}")
            
    # Fallback caso o Chrome não consiga imprimir: utiliza script nativo generate_sample_pdf
    print("[*] Utilizando gerador PDF de fallback...")
    import generate_sample_pdf
    generate_sample_pdf.create_simple_pdf(temp_pdf_path)
    return temp_pdf_path

def build_cv_from_json(json_path: str, template_name: str = "modern", output_pdf: str = None):
    """Executa o fluxo completo: JSON -> HR-XML + HTML PDF -> PDF Otimizado com XML ATS."""
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

    # 2. Renderizar HTML a partir do Template escolhido
    rendered_html = render_html_template(json_data, template_name)

    # 3. Converter HTML em PDF
    temp_pdf = str(OUTPUT_DIR / "temp_rendered.pdf")
    html_to_pdf(rendered_html, temp_pdf)

    # 4. Injetar XML e Metadados ATS no PDF
    embed_xml_cv.embed_xml_into_pdf(temp_pdf, xml_output_path, output_pdf, attachment_name="resume.xml")

    # Limpeza de arquivos temporários
    if os.path.exists(temp_pdf):
        os.remove(temp_pdf)
    if os.path.exists(rendered_html):
        os.remove(rendered_html)

    print(f"\n=======================================================")
    print(f" 🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
    print(f" PDF Final Otimizado para ATS: {output_pdf}")
    print(f" Base de dados JSON: {json_path}")
    print(f" Template utilizado: {template_name}")
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
    parser.add_argument("--template", default="modern", help="Nome do template gráfico (modern, classic, tech_dark) ou caminho do arquivo HTML (padrão: modern)")
    parser.add_argument("--out", default=None, help="Caminho do PDF de saída (padrão: output/<nome>_<template>_ats.pdf)")
    parser.add_argument("--list-templates", action="store_true", help="Lista os templates gráficos disponíveis.")

    args = parser.parse_args()

    if args.list_templates:
        list_templates()
        return

    build_cv_from_json(args.json, args.template, args.out)

if __name__ == "__main__":
    main()
