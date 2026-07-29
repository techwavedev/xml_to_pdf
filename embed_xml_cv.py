#!/usr/bin/env python3
"""
embed_xml_cv.py
-------------------------------------------------------------------------
Ferramenta automatizada para incorporar e injetar metadados XML estruturados
em CVs/Currículos em PDF para compatibilidade com sistemas ATS (Applicant Tracking Systems).

Esta ferramenta resolve falhas comuns de leitura/parsing nos sistemas ATS
incorporando XML estruturado (padrão HR-XML) diretamente no PDF de 3 formas complementares:

1. Anexo de Arquivo PDF (/EmbeddedFiles): Anexa o arquivo 'resume.xml' diretamente
   dentro do contêiner PDF. Leitores de PDF/A-3 e sistemas ATS modernos leem anexos XML.
2. Fluxo de Metadados XMP (/Metadata): Injeta um pacote XMP RDF padrão com namespaces
   XML personalizados e Dublin Core na raiz do catálogo do PDF.
3. Informações do Documento PDF (/Info): Atualiza os campos /Keywords, /Author, /Title
   e /Subject para extratores e sistemas ATS legados.

Uso:
  # 1. Incorporar XML em um Currículo PDF (vai por padrão para a pasta output/):
  python3 embed_xml_cv.py embed --pdf meu_curriculo.pdf --xml sample_cv.xml

  # 2. Verificar metadados XML incorporados em um PDF existente:
  python3 embed_xml_cv.py verify --pdf output/meu_curriculo_ats.pdf

  # 3. Extrair XML anexo de um Currículo PDF:
  python3 embed_xml_cv.py extract --pdf output/meu_curriculo_ats.pdf

Mecanismo:
  Suporta a biblioteca 'pypdf' (se instalada) ou fallback nativo da biblioteca padrão do Python.
-------------------------------------------------------------------------
"""

import sys
import os
import re
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

DEFAULT_OUTPUT_DIR = "output"

def ensure_output_dir(path_str: str) -> str:
    """Garante que o caminho de saída esteja dentro da pasta output/ e que o diretório exista."""
    path = Path(path_str)
    # Se o caminho for apenas um nome de arquivo ou não estiver explicitamente em output/, direciona para output/
    if not path.is_absolute() and len(path.parts) == 1:
        path = Path(DEFAULT_OUTPUT_DIR) / path
    
    # Cria o diretório pai caso não exista
    if path.parent:
        os.makedirs(path.parent, exist_ok=True)
        
    return str(path)

def validate_xml(xml_path: str) -> str:
    """Valida a sintaxe do arquivo XML e retorna seu conteúdo como texto."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        print(f"[✓] Sintaxe XML verificada e válida. Elemento raiz: <{root.tag}>")
        with open(xml_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"[❌] Erro de Validação XML em '{xml_path}': {e}")
        sys.exit(1)

def extract_summary_fields(xml_content: str) -> dict:
    """Extrai campos de resumo do XML para preencher os metadados /Info do PDF."""
    meta = {}
    try:
        root = ET.fromstring(xml_content)
        
        def find_first(tags):
            for tag in tags:
                elem = root.find(f".//{tag}")
                if elem is not None and elem.text and elem.text.strip():
                    return elem.text.strip()
            return None

        name = find_first(["GivenName", "FamilyName", "PersonName", "CandidateName", "Fullname", "Name"])
        if not name:
            given = find_first(["GivenName", "FirstName"])
            family = find_first(["FamilyName", "LastName"])
            if given and family:
                name = f"{given} {family}"
            elif given:
                name = given

        title = find_first(["Title", "JobTitle", "Headline", "Position"])
        summary = find_first(["ExecutiveSummary", "Summary", "Profile", "Objective"])
        
        skills = []
        for elem in root.findall(".//Skill"):
            if elem.text and elem.text.strip():
                skills.append(elem.text.strip())
                
        keywords = ", ".join(skills[:25]) if skills else "Curriculum Vitae, Currículo, XML Estruturado, ATS"

        if name:
            meta["Author"] = name
        if title:
            meta["Title"] = f"{name} - {title}" if name else title
        else:
            meta["Title"] = f"{name} - Currículo" if name else "Curriculum Vitae"
            
        if summary:
            meta["Subject"] = summary[:300].replace('\n', ' ')
        meta["Keywords"] = keywords

    except Exception as e:
        print(f"[*] Nota: Não foi possível extrair tags específicas ({e}), usando metadados padrão.")
        meta["Keywords"] = "Currículo, Resume, XML Estruturado, Automação ATS"
        
    return meta

def embed_xml_pypdf(pdf_path: str, xml_path: str, output_path: str, attachment_name: str = "resume.xml"):
    """Incorpora o XML no PDF utilizando a biblioteca pypdf."""
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import DecodedStreamObject, NameObject

    xml_content = validate_xml(xml_path)
    xml_bytes = xml_content.encode('utf-8')
    summary_meta = extract_summary_fields(xml_content)

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # 1. Anexo de arquivo (/EmbeddedFiles)
    writer.add_attachment(attachment_name, xml_bytes)
    print(f"[✓] Anexado '{attachment_name}' ({len(xml_bytes)} bytes) nos Anexos do PDF (/EmbeddedFiles).")

    # 2. Informações do Documento (/Info)
    doc_info = {
        "/Producer": "Conversor ATS XML CV (pypdf)",
        "/Keywords": summary_meta.get("Keywords", ""),
    }
    if "Author" in summary_meta:
        doc_info["/Author"] = summary_meta["Author"]
    if "Title" in summary_meta:
        doc_info["/Title"] = summary_meta["Title"]
    if "Subject" in summary_meta:
        doc_info["/Subject"] = summary_meta["Subject"]

    writer.add_metadata(doc_info)
    print(f"[✓] Atualizados os metadados do documento (/Keywords, /Author, /Title).")

    # 3. Fluxo de Metadados XMP (/Metadata)
    clean_summary = summary_meta.get('Subject', '').replace('<', '&lt;').replace('>', '&gt;')
    clean_title = summary_meta.get('Title', 'CV').replace('<', '&lt;').replace('>', '&gt;')

    xmp_packet = f"""<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/">
      <dc:format>application/pdf</dc:format>
      <dc:title><rdf:Alt><rdf:li xml:lang="x-default">{clean_title}</rdf:li></rdf:Alt></dc:title>
      <dc:description><rdf:Alt><rdf:li xml:lang="x-default">{clean_summary}</rdf:li></rdf:Alt></dc:description>
    </rdf:Description>
    <rdf:Description rdf:about="" xmlns:ats="http://ns.hr-xml.org/2007-04-15">
      <ats:StructuredResumeData><![CDATA[{xml_content}]]></ats:StructuredResumeData>
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>""".encode('utf-8')

    xmp_stream = DecodedStreamObject()
    xmp_stream._data = xmp_packet
    xmp_stream.update({
        NameObject("/Type"): NameObject("/Metadata"),
        NameObject("/Subtype"): NameObject("/XML"),
    })
    xmp_ref = writer._add_object(xmp_stream)
    writer._root_object.update({
        NameObject("/Metadata"): xmp_ref
    })
    print(f"[✓] Injetado fluxo de metadados XMP RDF no Catálogo do PDF.")

    output_path = ensure_output_dir(output_path)
    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"\n[🎉] PDF otimizado para ATS gerado com sucesso: {output_path}")

def embed_xml_native(pdf_path: str, xml_path: str, output_path: str, attachment_name: str = "resume.xml"):
    """Mecanismo de fallback nativo do Python (sem dependências externas)."""
    xml_content = validate_xml(xml_path)
    xml_bytes = xml_content.encode('utf-8')
    summary_meta = extract_summary_fields(xml_content)

    with open(pdf_path, 'rb') as f:
        orig_data = f.read()

    obj_pattern = re.compile(rb'(\d+)\s+(\d+)\s+obj')
    matches = obj_pattern.findall(orig_data)
    max_obj_id = max([int(m[0]) for m in matches]) if matches else 10

    ef_stream_id = max_obj_id + 1
    filespec_id = max_obj_id + 2
    embedded_files_id = max_obj_id + 3
    xmp_metadata_id = max_obj_id + 4
    info_dict_id = max_obj_id + 5
    catalog_id = max_obj_id + 6

    ef_stream_obj = (
        f"{ef_stream_id} 0 obj\n"
        f"<< /Type /EmbeddedFile /Subtype /text#2Fxml /Length {len(xml_bytes)} >>\n"
        f"stream\n"
    ).encode('ascii') + xml_bytes + b"\nendstream\nendobj\n\n"

    filespec_obj = (
        f"{filespec_id} 0 obj\n"
        f"<< /Type /Filespec /F ({attachment_name}) /UF ({attachment_name}) /EF << /F {ef_stream_id} 0 R >> >>\n"
        f"endobj\n\n"
    ).encode('ascii')

    embedded_files_obj = (
        f"{embedded_files_id} 0 obj\n"
        f"<< /Names [ ({attachment_name}) {filespec_id} 0 R ] >>\n"
        f"endobj\n\n"
    ).encode('ascii')

    clean_summary = summary_meta.get('Subject', '').replace('<', '&lt;').replace('>', '&gt;')
    clean_title = summary_meta.get('Title', 'CV').replace('<', '&lt;').replace('>', '&gt;')
    xmp_packet = f"""<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/">
      <dc:format>application/pdf</dc:format>
      <dc:title><rdf:Alt><rdf:li xml:lang="x-default">{clean_title}</rdf:li></rdf:Alt></dc:title>
      <dc:description><rdf:Alt><rdf:li xml:lang="x-default">{clean_summary}</rdf:li></rdf:Alt></dc:description>
    </rdf:Description>
    <rdf:Description rdf:about="" xmlns:ats="http://ns.hr-xml.org/2007-04-15">
      <ats:StructuredResumeData><![CDATA[{xml_content}]]></ats:StructuredResumeData>
    </rdf:Description>
  </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>""".encode('utf-8')

    xmp_obj = (
        f"{xmp_metadata_id} 0 obj\n"
        f"<< /Type /Metadata /Subtype /XML /Length {len(xmp_packet)} >>\n"
        f"stream\n"
    ).encode('ascii') + xmp_packet + b"\nendstream\nendobj\n\n"

    author = summary_meta.get("Author", "Candidato").replace("(", "\\(").replace(")", "\\)")
    title = summary_meta.get("Title", "CV").replace("(", "\\(").replace(")", "\\)")
    keywords = summary_meta.get("Keywords", "").replace("(", "\\(").replace(")", "\\)")
    subject = summary_meta.get("Subject", "").replace("(", "\\(").replace(")", "\\)")

    info_obj = (
        f"{info_dict_id} 0 obj\n"
        f"<< /Title ({title}) /Author ({author}) /Subject ({subject}) /Keywords ({keywords}) /Producer (ATS XML CV Converter) >>\n"
        f"endobj\n\n"
    ).encode('ascii')

    root_match = re.search(rb'/Root\s+(\d+)\s+(\d+)\s+R', orig_data)
    orig_root_id = int(root_match.group(1)) if root_match else 1

    catalog_obj = (
        f"{catalog_id} 0 obj\n"
        f"<< /Type /Catalog /Pages 2 0 R /Metadata {xmp_metadata_id} 0 R /Names << /EmbeddedFiles {embedded_files_id} 0 R >> >>\n"
        f"endobj\n\n"
    ).encode('ascii')

    new_objects = [ef_stream_obj, filespec_obj, embedded_files_obj, xmp_obj, info_obj, catalog_obj]
    
    start_offset = len(orig_data)
    out = bytearray(orig_data)
    if not orig_data.endswith(b'\n'):
        out.extend(b'\n')
    
    offsets = {}
    for obj_id, obj_bytes in zip(
        [ef_stream_id, filespec_id, embedded_files_id, xmp_metadata_id, info_dict_id, catalog_id],
        new_objects
    ):
        offsets[obj_id] = len(out)
        out.extend(obj_bytes)

    xref_start = len(out)
    xref_entries = [f"{offsets[i]:010d} 00000 n \n" for i in sorted(offsets.keys())]
    
    min_id = min(offsets.keys())
    count = len(offsets)
    
    xref_table = (
        f"xref\n"
        f"{min_id} {count}\n"
        + "".join(xref_entries) +
        f"trailer\n"
        f"<< /Size {max(offsets.keys()) + 1} /Root {catalog_id} 0 R /Info {info_dict_id} 0 R >>\n"
        f"startxref\n"
        f"{xref_start}\n"
        f"%%EOF\n"
    ).encode('ascii')

    out.extend(xref_table)

    output_path = ensure_output_dir(output_path)
    with open(output_path, "wb") as f:
        f.write(out)

    print(f"[✓] Mecanismo nativo do Python anexou o arquivo '{attachment_name}' e os metadados XMP.")
    print(f"\n[🎉] PDF otimizado para ATS gerado com sucesso: {output_path}")

def embed_xml_into_pdf(pdf_path: str, xml_path: str, output_path: str, attachment_name: str = "resume.xml"):
    """Escolhe o melhor mecanismo disponível (pypdf ou fallback nativo)."""
    if not os.path.exists(pdf_path):
        print(f"[❌] Arquivo PDF de entrada não encontrado: {pdf_path}")
        sys.exit(1)

    if not os.path.exists(xml_path):
        print(f"[❌] Arquivo XML de entrada não encontrado: {xml_path}")
        sys.exit(1)

    try:
        import pypdf
        print("[*] Utilizando a biblioteca 'pypdf' para manipulação do PDF...")
        embed_xml_pypdf(pdf_path, xml_path, output_path, attachment_name)
    except ImportError:
        print("[*] Biblioteca 'pypdf' não encontrada. Utilizando o mecanismo nativo do Python...")
        embed_xml_native(pdf_path, xml_path, output_path, attachment_name)

def verify_pdf(pdf_path: str):
    """Verifica se há anexos XML e metadados incorporados dentro de um arquivo PDF."""
    # Se a verificação for chamada com um caminho sem diretório, tenta em output/ primeiro se não achar no dir local
    if not os.path.exists(pdf_path):
        output_candidate = Path(DEFAULT_OUTPUT_DIR) / pdf_path
        if output_candidate.exists():
            pdf_path = str(output_candidate)
        else:
            print(f"[❌] Arquivo não encontrado: {pdf_path}")
            sys.exit(1)

    print(f"\n=======================================================")
    print(f" Verificando Anexos e Metadados do PDF: {pdf_path}")
    print(f"=======================================================")

    with open(pdf_path, 'rb') as f:
        data = f.read()

    has_xml_attachment = b'resume.xml' in data or b'EmbeddedFile' in data
    has_xmp = b'x:xmpmeta' in data or b'StructuredResumeData' in data or b'/Metadata' in data
    has_info = b'/Keywords' in data or b'/Author' in data or b'/Title' in data

    print(f"[1] Arquivos Anexados ao PDF (/EmbeddedFiles):")
    if has_xml_attachment:
        print(f"   [✓] Fluxo de anexo XML incorporado detectado.")
    else:
        print(f"   [!] Nenhum anexo XML incorporado foi detectado.")

    print(f"\n[2] Fluxo de Metadados XMP (/Metadata):")
    if has_xmp:
        print(f"   [✓] Fluxo de metadados XMP RDF detectado no Catálogo do PDF.")
    else:
        print(f"   [!] Nenhum fluxo de metadados XMP detectado.")

    print(f"\n[3] Metadados de Informação do Documento (/Info):")
    if has_info:
        print(f"   [✓] Dicionário de informações (/Keywords, /Author, etc.) detectado.")
    else:
        print(f"   [!] Nenhuma informação do documento detectada.")

    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        print("\n[+] Diagnóstico pypdf:")
        if reader.attachments:
            print(f"   Anexos ({len(reader.attachments)}): {list(reader.attachments.keys())}")
        if reader.metadata:
            print(f"   Palavras-chave (Keywords): {reader.metadata.get('/Keywords', '')}")
            print(f"   Autor: {reader.metadata.get('/Author', '')}")
            print(f"   Título: {reader.metadata.get('/Title', '')}")
    except ImportError:
        pass

    print("=======================================================\n")

def extract_xml_from_pdf(pdf_path: str, output_xml: str):
    """Extrai o anexo XML incorporado ou os metadados XMP do PDF para um arquivo .xml."""
    if not os.path.exists(pdf_path):
        output_candidate = Path(DEFAULT_OUTPUT_DIR) / pdf_path
        if output_candidate.exists():
            pdf_path = str(output_candidate)
        else:
            print(f"[❌] Arquivo não encontrado: {pdf_path}")
            sys.exit(1)

    output_xml = ensure_output_dir(output_xml)

    with open(pdf_path, 'rb') as f:
        data = f.read()

    xml_content = None

    if b'StructuredResumeData' in data:
        m = re.search(rb'<!\[CDATA\[(.*?)\]\]>', data, re.DOTALL)
        if m:
            xml_content = m.group(1)

    if not xml_content and b'<?xml' in data:
        start = data.find(b'<?xml')
        end = data.find(b'</Resume>')
        if start != -1 and end != -1:
            xml_content = data[start:end + len(b'</Resume>')]

    if xml_content:
        with open(output_xml, 'wb') as f:
            f.write(xml_content)
        print(f"[✓] XML incorporado extraído com sucesso ({len(xml_content)} bytes) para '{output_xml}'")
    else:
        print(f"[❌] Não foi possível localizar o fluxo de XML incorporado em '{pdf_path}'")

def main():
    parser = argparse.ArgumentParser(description="Incorporar ou Extrair descrição XML em PDF de Currículo para automação ATS.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Comando embed (incorporar)
    embed_parser = subparsers.add_parser("embed", help="Incorpora arquivo XML em um Currículo PDF.")
    embed_parser.add_argument("--pdf", required=True, help="Caminho do arquivo PDF de entrada.")
    embed_parser.add_argument("--xml", required=True, help="Caminho do arquivo XML de entrada.")
    embed_parser.add_argument("--out", default=None, help="Caminho do arquivo PDF de saída (padrão: output/<nome_do_pdf>_ats.pdf)")
    embed_parser.add_argument("--name", default="resume.xml", help="Nome do arquivo anexo dentro do PDF (padrão: resume.xml)")

    # Comando verify (verificar)
    verify_parser = subparsers.add_parser("verify", help="Verifica se há XML e metadados incorporados em um Currículo PDF.")
    verify_parser.add_argument("--pdf", required=True, help="Caminho do arquivo PDF para verificação.")

    # Comando extract (extrair)
    extract_parser = subparsers.add_parser("extract", help="Extrai o XML incorporado de um Currículo PDF.")
    extract_parser.add_argument("--pdf", required=True, help="Caminho do arquivo PDF de entrada.")
    extract_parser.add_argument("--out", default="resume_extraido.xml", help="Caminho do arquivo XML de saída (padrão: output/resume_extraido.xml)")

    args = parser.parse_args()

    if args.command == "embed":
        if args.out is None:
            pdf_stem = Path(args.pdf).stem
            args.out = f"{pdf_stem}_ats.pdf"
        embed_xml_into_pdf(args.pdf, args.xml, args.out, attachment_name=args.name)
    elif args.command == "verify":
        verify_pdf(args.pdf)
    elif args.command == "extract":
        extract_xml_from_pdf(args.pdf, args.out)

if __name__ == "__main__":
    main()
