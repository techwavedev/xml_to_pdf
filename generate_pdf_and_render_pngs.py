import os
import subprocess
import json
import zipfile
import cv_builder

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

templates = [
    ("expert", "samples/expert.docx"),
    ("itresume", "samples/itresume.docx"),
    ("mlops", "samples/mlops.docx"),
    ("sprint", "samples/sprint.docx")
]

print("=" * 75)
print("  🚀 FULL PIPELINE: POPULATE DOCX -> CONVERT PDF -> RENDER PNG IMAGES")
print("=" * 75)

for name, t_path in templates:
    print(f"\n[*] Generating PDF for template: {t_path}")
    pdf_out = cv_builder.build_cv_from_json("sample_cv.json", docx_template=t_path, out_docx=False)
    
    if pdf_out and os.path.exists(pdf_out):
        print(f"✓ PDF Output Created: {pdf_out}")
        
        # Render PDF pages to PNG using pdftoppm
        png_prefix = os.path.join(OUTPUT_DIR, f"{name}_page")
        cmd_render = ["/opt/homebrew/bin/pdftoppm", "-png", "-r", "150", pdf_out, png_prefix]
        res = subprocess.run(cmd_render, capture_output=True, text=True)
        
        # Extract text using pdftotext
        cmd_txt = ["/opt/homebrew/bin/pdftotext", pdf_out, "-"]
        res_txt = subprocess.run(cmd_txt, capture_output=True, text=True)
        extracted_txt = res_txt.stdout.strip()
        
        print(f"   • Extracted PDF Text Length: {len(extracted_txt)} chars")
        print(f"   • Text Preview: {extracted_txt[:200]}...")
    else:
        print(f"❌ Failed to generate PDF for {name}")

print("\n" + "=" * 75)
print("  📸 GENERATED PNG IMAGES FOR VISUAL VERIFICATION:")
print("=" * 75)
for f in sorted(os.listdir(OUTPUT_DIR)):
    if f.endswith(".png"):
        f_path = os.path.abspath(os.path.join(OUTPUT_DIR, f))
        print(f"  • {f}: file://{f_path}")
