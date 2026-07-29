import os
import subprocess
import json
import cv_builder
import zipfile
import xml.etree.ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Carrega dados do JSON
with open('sample_cv.json', 'r') as f:
    cv_data = json.load(f)

consultant = cv_data.get('consultant', {})
candidate_name = f"{consultant.get('name')} {consultant.get('surname')}".strip()

templates = ['expert', 'itresume', 'mlops', 'sprint']

print("=" * 80)
print(" 🚀 AUTONOMOUS AGENT TEST LOOP & FULL VERIFICATION")
print("=" * 80)

loop_passed = True

for t in templates:
    t_path = f"samples/{t}.docx"
    print(f"\n[*] Generating PDF for template: {t_path}")
    pdf_out = cv_builder.build_cv_from_json("sample_cv.json", docx_template=t_path, out_docx=False)
    
    if pdf_out and os.path.exists(pdf_out):
        print(f"  ✓ PDF File Successfully Generated: {pdf_out}")
        
        # Inspeciona texto extraído do PDF
        cmd_txt = ["/opt/homebrew/bin/pdftotext", pdf_out, "-"]
        res_txt = subprocess.run(cmd_txt, capture_output=True, text=True)
        pdf_text = res_txt.stdout.strip()
        
        # Verifica se nome do candidato está presente
        if candidate_name.lower() in pdf_text.lower():
            print(f"  ✓ Candidate Name ('{candidate_name}') verified in PDF text")
        else:
            print(f"  ❌ FAILED: Candidate Name ('{candidate_name}') missing from PDF text")
            loop_passed = False
            
        # Verifica se strings antigas foram expurgadas do PDF
        forbidden = ['European Commission', 'BNP Paribas', 'Helimax', 'NSX', 'Aveiro', 'Elton Machado', 'Portuguese', 'Dutch']
        found_old = [f for f in forbidden if f.lower() in pdf_text.lower()]
        if not found_old:
            print("  ✓ ZERO old sample strings found in PDF text")
        else:
            print(f"  ❌ FAILED: Old strings found in PDF text: {found_old}")
            loop_passed = False
    else:
        print(f"  ❌ FAILED to generate PDF for {t}")
        loop_passed = False

print("\n" + "=" * 80)
if loop_passed:
    print(" 🎉 AUTONOMOUS TEST LOOP PASSED WITH 100% SUCCESS ACROSS ALL TEMPLATES!")
else:
    print(" ⚠️ TEST LOOP APONTOU INCONSISTÊNCIAS.")
print("=" * 80)
