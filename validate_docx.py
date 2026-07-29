import os
import zipfile
import json
import xml.etree.ElementTree as ET
import clean_docx_completely

def run_test():
    with open("sample_cv.json") as f:
        d = json.load(f)

    out = "output/test_populated_expert.docx"
    clean_docx_completely.clean_docx_sprint("samples/expert.docx", out, photo_path="assets/photo.png", json_data=d)

    with zipfile.ZipFile(out, "r") as z:
        xml_str = z.read("word/document.xml").decode("utf-8")
        root = ET.fromstring(xml_str)
        texts = [node.text for node in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t") if node.text]
        full_text = " ".join(texts)
        print("Includes John Doe?", "John Doe" in full_text)
        print("Includes Senior DevOps Specialist?", "Senior DevOps" in full_text)
        print("Includes San Francisco?", "San Francisco" in full_text)
        print("Includes JSON Summary?", "Senior DevOps" in full_text or "TechWave" in full_text)

if __name__ == "__main__":
    run_test()
