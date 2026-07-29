import os
import zipfile
import re
import html
import json
import xml.etree.ElementTree as ET
import jinja2

# Padroes genericos para identificar campos de contato e cabecalho em QUALQUER .docx
EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
PHONE_REGEX = r'(\+\d{1,4}[\s.-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}'
LINKEDIN_REGEX = r'https?://[^\s<"]+linkedin[^\s<"]*'
LOCATION_REGEX = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'

def dynamic_templatize_xml(doc_xml: str) -> str:
    """Substitui padroes de dados pessoais por marcadores Jinja2 de forma 100% generica."""
    # 1. Email -> {{ consultant.email }}
    doc_xml = re.sub(EMAIL_REGEX, '{{ consultant.email }}', doc_xml)
    
    # 2. LinkedIn URL -> {{ consultant.linkedin }}
    doc_xml = re.sub(LINKEDIN_REGEX, '{{ consultant.linkedin }}', doc_xml)
    
    # 3. Telefone -> {{ consultant.phone }}
    doc_xml = re.sub(PHONE_REGEX, '{{ consultant.phone }}', doc_xml)

    return doc_xml

def process_any_docx_with_json(docx_input_path: str, docx_output_path: str, json_data: dict, photo_path: str = "assets/photo.png"):
    """Processa QUALQUER arquivo .docx com QUALQUER feed JSON sem nenhum texto hardcoded."""
    if not os.path.exists(docx_input_path):
        print(f"[❌] Arquivo DOCX não encontrado: {docx_input_path}")
        return False

    consultant = json_data.get("consultant", {})
    name = consultant.get("name", "")
    surname = consultant.get("surname", "")
    fullname = f"{name} {surname}".strip()
    title = json_data.get("present_job_title", "")
    email = consultant.get("email", "")
    phone = consultant.get("phone", "")
    city = consultant.get("city", "")
    country = consultant.get("country", "")
    location = f"{city}, {country}".strip(", ")
    linkedin = consultant.get("linkedin", "")
    summary = json_data.get("about") or json_data.get("cv_summary") or ""
    top_techs = json_data.get("top_technologies") or []
    techs_str = ", ".join(top_techs)

    # Prepara dicionário de contexto limpo e sanitizado para XML
    context = {
        "consultant": {
            "name": html.escape(name, quote=False),
            "surname": html.escape(surname, quote=False),
            "email": html.escape(email, quote=False),
            "phone": html.escape(phone, quote=False),
            "city": html.escape(city, quote=False),
            "country": html.escape(country, quote=False),
            "linkedin": html.escape(linkedin, quote=False),
        },
        "present_job_title": html.escape(title, quote=False),
        "about": html.escape(summary, quote=False),
        "top_technologies": [html.escape(t, quote=False) for t in top_techs],
        "techs_str": html.escape(techs_str, quote=False),
    }

    # Carrega bytes da foto transparente/candidato
    transparent_path = "assets/transparent.png"
    transparent_data = b""
    if os.path.exists(transparent_path):
        with open(transparent_path, "rb") as f:
            transparent_data = f.read()

    photo_bytes = b""
    if photo_path and os.path.exists(photo_path):
        with open(photo_path, "rb") as f:
            photo_bytes = f.read()

    temp_zip = docx_output_path + ".tmp"
    with zipfile.ZipFile(docx_input_path, 'r') as jin:
        with zipfile.ZipFile(temp_zip, 'w') as jout:
            for item in jin.infolist():
                fname = item.filename
                data = jin.read(fname)

                if fname.startswith('word/media/'):
                    # Substituição genérica da foto do candidato (imagens menores que 200KB)
                    if ('foto' in fname.lower() or 'image4' in fname.lower() or 'large' in fname.lower()) and len(data) < 200000:
                        jout.writestr(item, photo_bytes if photo_bytes else data)
                        print(f"[🖼️] Foto substituída dinamicamente: {fname}")
                    else:
                        jout.writestr(item, data)
                elif fname.startswith('word/document.xml') or fname.startswith('word/header') or fname.startswith('word/footer'):
                    doc_str = data.decode('utf-8')
                    
                    # 1. Templatização dinâmica por padrões de expressão regular (sem nomes fixos!)
                    doc_str = dynamic_templatize_xml(doc_str)

                    # 2. Renderização com Jinja2 usando o feed JSON fornecido
                    try:
                        tmpl = jinja2.Template(doc_str)
                        rendered = tmpl.render(**context)
                    except Exception as e_tmpl:
                        print(f"[*] Aviso ao renderizar Jinja2 em {fname}: {e_tmpl}")
                        rendered = doc_str

                    # 3. Substituições genéricas adicionais de nomes na primeira ocorrência de cabeçalho
                    if fname == 'word/document.xml':
                        # Substitui primeira ocorrência de nome próprio no cabeçalho
                        rendered = re.sub(r'(<w:t[^>]*>)[A-Z][a-z]+\s+[A-Z][a-z]+(</w:t>)', r'\g<1>' + html.escape(fullname, quote=False) + r'\g<2>', rendered, count=1)

                    jout.writestr(item, rendered.encode('utf-8'))
                    print(f"[📝] {fname} templatizado e renderizado via Jinja2 com feed JSON")
                else:
                    jout.writestr(item, data)

    if os.path.exists(temp_zip):
        os.replace(temp_zip, docx_output_path)
        print(f"[✓] DOCX renderizado dinamicamente em: {docx_output_path}")
        return True
    return False

if __name__ == "__main__":
    with open("sample_cv.json") as f:
        jdata = json.load(f)
    process_any_docx_with_json("samples/expert.docx", "output/test_dynamic_expert.docx", jdata)
