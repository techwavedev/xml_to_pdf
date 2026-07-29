import os
import zipfile
import re
import json
import xml.etree.ElementTree as ET

def test():
    with open("sample_cv.json") as f:
        data = json.load(f)

    consultant = data.get("consultant", {})
    name = consultant.get("name", "John")
    surname = consultant.get("surname", "Doe")
    fullname = f"{name} {surname}".strip()
    title = data.get("present_job_title", "Senior DevOps Specialist")
    email = consultant.get("email", "")
    phone = consultant.get("phone", "")
    city = consultant.get("city", "")
    country = consultant.get("country", "")
    location = f"{city}, {country}".strip(", ")
    linkedin = consultant.get("linkedin", "")

    substitutions = [
        (r"(?i)elton\s+machado", fullname),
        (r"(?i)elton\.machado@gmail\.com", email),
        (r"\(\+351\)\s*308803508", phone),
        (r"\+55\s*47\s*99\s*162\s*2489", phone),
        (r"Aveiro\s*,\s*Portugal", location),
        (r"Itapema,\s*SC", location),
        (r"http://pt\.linkedin\.com/in/eltonmachado", linkedin),
        (r"linkedin\.com/in/eltonmachado", linkedin),
        (r"(?i)Senior Platform Engineer & AI/Cloud Architect \| Site Reliability Engineer", title),
        (r"(?i)DevOps Engineer", title),
    ]

    for sample in ["ITExpert.docx", "ITResume.docx", "MLOps.docx", "sprint.docx"]:
        path = f"samples/{sample}"
        if os.path.exists(path):
            with zipfile.ZipFile(path, "r") as z:
                doc_xml = z.read("word/document.xml").decode("utf-8")
                for pat, repl in substitutions:
                    doc_xml = re.sub(pat, repl, doc_xml)
                root = ET.fromstring(doc_xml.encode("utf-8"))
                texts = [node.text for node in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t") if node.text]
                print(f"=== Replaced {sample} ===")
                print("Header preview:", " ".join(texts[:25]))
                print()

if __name__ == "__main__":
    test()
