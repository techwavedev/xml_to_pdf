import zipfile
import re
import html
import json

with open("sample_cv.json") as f:
    cv_data = json.load(f)

c = cv_data.get("consultant", {})
work_auth = c.get("work_authorization") or f"{c.get('nationality', 'US')} Citizen"

for s in ["samples/expert.docx", "samples/itresume.docx", "samples/mlops.docx", "samples/sprint.docx"]:
    with zipfile.ZipFile(s, "r") as z:
        doc_xml = z.read("word/document.xml").decode("utf-8")

    doc_xml = re.sub(r"(?i)EU\s+Citizen[^\n<\"']*", html.escape(work_auth, quote=False), doc_xml)
    doc_xml = re.sub(r"(?i)Belgian,\s*Portuguese,\s*Brazilian", html.escape(work_auth, quote=False), doc_xml)

    has_work_auth = bool(re.search(r"EU Citizen|Belgian|Portuguese|Brazilian", doc_xml, re.I))
    print(f"{s} -> Work Auth replaced. Remaining old auth text: {has_work_auth}")
