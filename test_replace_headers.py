import zipfile
import re
import html
import json

with open("sample_cv.json") as f:
    cv_data = json.load(f)

c = cv_data.get("consultant", {})
fname = c.get("name", "")
lname = c.get("surname", "")
fullname = f"{fname} {lname}"
linkedin = c.get("linkedin", "")

for s in ["samples/expert.docx", "samples/itresume.docx", "samples/mlops.docx", "samples/sprint.docx"]:
    with zipfile.ZipFile(s, "r") as z:
        doc_xml = z.read("word/document.xml").decode("utf-8")

    doc_xml = re.sub(r"(?i)\belton\b", html.escape(fname, quote=False), doc_xml)
    doc_xml = re.sub(r"(?i)\bmachado\b", html.escape(lname, quote=False), doc_xml)
    doc_xml = re.sub(r"(?i)(?:https?://)?(?:[a-z0-9-]+\.)*linkedin\.com/[^\s<\"']+", html.escape(linkedin, quote=False), doc_xml)

    has_elton = bool(re.search(r"elton|machado", doc_xml, re.I))
    print(f"{s} -> Name & LinkedIn replaced. Remaining personal text: {has_elton}")
