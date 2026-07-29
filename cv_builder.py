#!/usr/bin/env python3
"""
cv_builder.py
-------------------------------------------------------------------------
Gerador de Currículos PDF a partir de JSON usando EXCLUSIVAMENTE os 
Modelos DOCX da pasta samples/ com Incorporação ATS HR-XML.

Fluxo:
 1. Carrega os dados do CV em formato JSON (base única de dados).
 2. Converte automaticamente o JSON para HR-XML (padrão internacional ATS).
 3. Seleciona o modelo .docx da pasta samples/ (ex: samples/expert.docx).
 4. Popula o modelo .docx com os dados do JSON mantendo o layout e formatação originais.
 5. Converte o .docx populado diretamente para PDF via LibreOffice Headless (soffice).
 6. Injeta o XML gerado no PDF final (anexo, metadados XMP e dicionário /Info).
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

import json_to_xml
import embed_xml_cv
import populate_docx_engine

OUTPUT_DIR = Path("output")
SAMPLES_DIR = Path("samples")

def find_docx_file(docx_arg: str) -> str:
    """Encontra o arquivo .docx aceitando variação de nome parcial em samples/."""
    if not docx_arg:
        docx_arg = "samples/expert.docx"
        
    if os.path.exists(docx_arg):
        return docx_arg

    p = Path(docx_arg)
    search_dirs = [p.parent, SAMPLES_DIR, Path(".")]
    target_stem = p.stem.lower()

    for sdir in search_dirs:
        if sdir.exists():
            for candidate in sdir.glob("*.docx"):
                c_stem = candidate.stem.lower()
                if target_stem in c_stem or c_stem in target_stem:
                    print(f"[🔍] Modelo DOCX localizado: '{candidate}' (para '{docx_arg}')")
                    return str(candidate)

    return docx_arg

def build_cv_from_json(json_path: str, docx_template: str = "samples/expert.docx", output_pdf: str = None, out_docx: str = None):
    """Executa o fluxo completo: JSON + DOCX Template -> PDF Otimizado com HR-XML ATS."""
    if not os.path.exists(json_path):
        print(f"[❌] Arquivo JSON de entrada não encontrado: {json_path}")
        sys.exit(1)

    # Resolve o caminho do modelo .docx (padrão: samples/expert.docx)
    docx_template = find_docx_file(docx_template or "samples/expert.docx")
    if not os.path.exists(docx_template):
        print(f"[❌] Modelo .docx não encontrado: {docx_template}")
        sys.exit(1)

    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    consultant = json_data.get("consultant", {})
    c_name = f"{consultant.get('name', '')}_{consultant.get('surname', '')}".strip("_") or "CV"
    sample_stem = Path(docx_template).stem

    if not output_pdf:
        output_pdf = str(OUTPUT_DIR / f"{sample_stem}_{c_name}_ats.pdf")
    else:
        output_pdf = embed_xml_cv.ensure_output_dir(output_pdf)

    # 1. Gerar HR-XML a partir do JSON
    xml_output_path = str(OUTPUT_DIR / "generated_resume.xml")
    json_to_xml.json_file_to_xml_file(json_path, xml_output_path)

    temp_pdf = str(OUTPUT_DIR / "temp_rendered.pdf")

    # 2. Popula o modelo .docx de entrada exclusivamente com os dados do JSON
    print(f"\n[*] Utilizando modelo .docx como DESIGN EXCLUSIVO: {docx_template}")
    populated_docx = str(OUTPUT_DIR / f"{sample_stem}_{c_name}.docx")
    populate_docx_engine.populate_docx_from_json(docx_template, populated_docx, json_data, photo_path="assets/photo.png")

    # 3. Converte o .docx populado diretamente para PDF via LibreOffice Headless (soffice)
    soffice_bin = shutil.which("soffice") or shutil.which("libreoffice") or "/opt/homebrew/bin/soffice"
    if soffice_bin and os.path.exists(soffice_bin if os.path.isabs(soffice_bin) else shutil.which(soffice_bin) or ""):
        abs_docx = os.path.abspath(populated_docx)
        out_dir = os.path.abspath(OUTPUT_DIR)
        cmd = [soffice_bin, "--headless", "--convert-to", "pdf", abs_docx, "--outdir", out_dir]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        default_pdf = str(OUTPUT_DIR / f"{sample_stem}_{c_name}.pdf")
        if os.path.exists(default_pdf):
            os.replace(default_pdf, temp_pdf)
        print(f"[✓] PDF gerado 100% diretamente do modelo .docx via LibreOffice Headless!")
    else:
        print("[❌] Erro: LibreOffice (soffice) é necessário para conversão headless de DOCX para PDF.")
        sys.exit(1)

    # Remove o arquivo .docx temporário caso o usuário NÃO tenha pedido --out-docx
    if not out_docx and os.path.exists(populated_docx):
        os.remove(populated_docx)
    elif out_docx and os.path.exists(populated_docx):
        print(f"[✓] Arquivo DOCX populado mantido em: {populated_docx}")

    # 4. Injetar XML e Metadados ATS no PDF final de saída
    embed_xml_cv.embed_xml_into_pdf(temp_pdf, xml_output_path, output_pdf, attachment_name="resume.xml")

    # Limpeza de PDF temporário
    if os.path.exists(temp_pdf):
        os.remove(temp_pdf)

    print(f"\n=======================================================")
    print(f" 🎉 PDF OTIMIZADO PARA ATS GERADO COM SUCESSO! ({platform.system()})")
    print(f" 📄 Arquivo PDF de Saída (Modelo DOCX): {output_pdf}")
    print(f" 📊 Base de dados JSON: {json_path}")
    print(f" 🎨 Modelo .docx utilizado: {docx_template}")
    print(f"=======================================================\n")
    return output_pdf

def list_samples():
    """Lista os modelos .docx disponíveis na pasta samples/."""
    print("\nModelos DOCX Disponíveis em samples/:")
    if SAMPLES_DIR.exists():
        for t in SAMPLES_DIR.glob("*.docx"):
            print(f" - {t.name}")
    print("")

def main():
    parser = argparse.ArgumentParser(description="Gerador de CVs PDF a partir de JSON usando EXCLUSIVAMENTE os modelos .docx de samples/.")
    parser.add_argument("--json", default="sample_cv.json", help="Caminho do arquivo JSON contendo a base do currículo (padrão: sample_cv.json)")
    parser.add_argument("--docx", default="samples/expert.docx", help="Caminho ou nome do modelo .docx em samples/ (ex: expert, itresume, mlops, sprint)")
    parser.add_argument("--out", default=None, help="Caminho do PDF de SAÍDA (padrão: output/<modelo>_<candidato>_ats.pdf)")
    parser.add_argument("--out-docx", action="store_true", help="Mantém também o arquivo .docx populado de saída além do PDF.")
    parser.add_argument("--list-samples", action="store_true", help="Lista os modelos .docx disponíveis na pasta samples/.")

    args = parser.parse_args()

    if args.list_samples:
        list_samples()
        return

    build_cv_from_json(args.json, docx_template=args.docx, output_pdf=args.out, out_docx=args.out_docx)

if __name__ == "__main__":
    main()
