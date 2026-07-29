import os
import zipfile
import json
import xml.etree.ElementTree as ET
import clean_docx_completely

def run_validation():
    with open("sample_cv.json") as f:
        d = json.load(f)

    for sample in ["ITExpert.docx", "ITResume.docx", "MLOps.docx", "sprint.docx"]:
        out = f"output/{sample[:-5]}_clean_validated.docx"
        clean_docx_completely.clean_docx_sprint(f"samples/{sample}", out, photo_path="assets/photo.png", json_data=d)
        
        errors = 0
        with zipfile.ZipFile(out, "r") as z:
            for xfile in z.namelist():
                if xfile.endswith(".xml"):
                    doc_bytes = z.read(xfile)
                    try:
                        ET.fromstring(doc_bytes)
                    except Exception as e:
                        print(f"❌ XML Error in {out} [{xfile}]: {e}")
                        errors += 1
        if errors == 0:
            print(f"✓ All XML files in {out} are 100% VALID and WELL-FORMED!\n")

if __name__ == "__main__":
    run_validation()
