import zipfile
import re
import html
import json

with open("sample_cv.json") as f:
    cv_data = json.load(f)

c = cv_data.get("consultant", {})
city = c.get("city", "New York")
country = c.get("country", "US")

for s in ["samples/expert.docx", "samples/itresume.docx", "samples/mlops.docx", "samples/sprint.docx"]:
    with zipfile.ZipFile(s, "r") as z:
        doc_xml = z.read("word/document.xml").decode("utf-8")

    doc_xml = re.sub(r"(?i)\baveiro\b", html.escape(city, quote=False), doc_xml)
    doc_xml = re.sub(r"(?i)\bportugal\b", html.escape(country, quote=False), doc_xml)
    doc_xml = re.sub(r"(?i)\bitapema\b", html.escape(city, quote=False), doc_xml)

    has_location = bool(re.search(r"aveiro|portugal|itapema", doc_xml, re.I))
    print(f"{s} -> City & Country replaced. Remaining location text: {has_location}")
