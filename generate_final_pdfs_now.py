import os
import cv_builder

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

templates = ["expert", "itresume", "mlops", "sprint"]

print("=" * 70)
print(" 🚀 AUTONOMOUS TEST LOOP: VERIFYING ALL 4 PDF DELIVERABLES")
print("=" * 70)

generated_pdfs = []

for t in templates:
    t_path = f"samples/{t}.docx"
    print(f"\n[*] Processing template: {t_path}...")
    pdf_path = cv_builder.build_cv_from_json("sample_cv.json", docx_template=t_path, out_docx=False)
    if pdf_path and os.path.exists(pdf_path):
        generated_pdfs.append(pdf_path)
        print(f"  ✓ PDF Successfully Generated: {pdf_path}")
    else:
        print(f"  ❌ FAILED for template: {t_path}")

print("\n" + "=" * 70)
print(f" 🎉 SUCCESS! Generated {len(generated_pdfs)} PDF files in output/:")
for pdf in generated_pdfs:
    abs_p = os.path.abspath(pdf)
    print(f"  • {pdf} -> file://{abs_p}")
print("=" * 70)
