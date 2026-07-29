#!/usr/bin/env python3
"""
json_to_xml.py
-------------------------------------------------------------------------
Converte dados de Currículo em formato JSON (base do CV) para o padrão HR-XML.
Permite extrair todas as informações do candidato a partir de um único JSON
para incorporar metadados ATS nos PDFs gerados.
-------------------------------------------------------------------------
"""

import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path

def convert_json_to_xml(json_data: dict) -> str:
    """Converte o dicionário JSON em uma string HR-XML formatada."""
    consultant = json_data.get("consultant", {})
    labels = json_data.get("cv_labels", {})
    
    root = ET.Element("Resume", {
        "xmlns": "http://ns.hr-xml.org/2007-04-15",
        "version": "3.0"
    })
    
    struct_resume = ET.SubElement(root, "StructuredXMLResume")
    
    # 1. Informações de Contato
    contact_info = ET.SubElement(struct_resume, "ContactInfo")
    person_name = ET.SubElement(contact_info, "PersonName")
    
    given_name = ET.SubElement(person_name, "GivenName")
    given_name.text = consultant.get("name", "")
    
    family_name = ET.SubElement(person_name, "FamilyName")
    family_name.text = consultant.get("surname", "")
    
    contact_method = ET.SubElement(contact_info, "ContactMethod")
    if consultant.get("email"):
        email = ET.SubElement(contact_method, "InternetEmailAddress")
        email.text = consultant.get("email")
    if consultant.get("phone"):
        phone = ET.SubElement(contact_method, "Telephone")
        phone.text = consultant.get("phone")
    if consultant.get("address"):
        loc = ET.SubElement(contact_method, "Location")
        loc.text = consultant.get("address")
    if consultant.get("linkedin"):
        web = ET.SubElement(contact_method, "InternetWebAddress")
        web.text = consultant.get("linkedin")

    # 2. Resumo Executivo / Perfil
    summary_text = json_data.get("about") or json_data.get("cv_summary", "")
    if summary_text:
        exec_summary = ET.SubElement(struct_resume, "ExecutiveSummary")
        exec_summary.text = summary_text.strip()

    # 3. Principais Competências & Habilidades (Core Competencies)
    tech_skills_raw = json_data.get("technical_skills", "")
    if tech_skills_raw:
        core_competencies = ET.SubElement(struct_resume, "CoreCompetencies")
        skills_list = [s.strip() for s in tech_skills_raw.replace(';', ',').split(',') if s.strip()]
        for skill_item in skills_list[:50]:
            skill_elem = ET.SubElement(core_competencies, "Skill")
            skill_elem.text = skill_item

    # 4. Realizações Relevantes
    accomplishments = json_data.get("relevant_accomplishments", "")
    if accomplishments:
        acc_elem = ET.SubElement(struct_resume, "KeyAchievements")
        acc_elem.text = accomplishments.strip()

    # 5. Experiência Profissional (EmploymentHistory)
    work_experiences = json_data.get("work_experiences", [])
    if work_experiences:
        emp_history = ET.SubElement(struct_resume, "EmploymentHistory")
        for exp in work_experiences:
            emp_org = ET.SubElement(emp_history, "EmployerOrg")
            if exp.get("company"):
                emp_name = ET.SubElement(emp_org, "EmployerOrgName")
                emp_name.text = exp.get("company")
            pos_hist = ET.SubElement(emp_org, "PositionHistory")
            if exp.get("title"):
                title_elem = ET.SubElement(pos_hist, "Title")
                title_elem.text = exp.get("title")
            if exp.get("period"):
                period_elem = ET.SubElement(pos_hist, "Period")
                period_elem.text = exp.get("period")
            if exp.get("description"):
                desc_elem = ET.SubElement(pos_hist, "Description")
                desc_elem.text = exp.get("description")

    # 6. Formação Acadêmica
    educations = json_data.get("educations", [])
    if educations:
        edu_history = ET.SubElement(struct_resume, "EducationHistory")
        for edu in educations:
            edu_org = ET.SubElement(edu_history, "EducationOrganization")
            if edu.get("course_institution"):
                school = ET.SubElement(edu_org, "SchoolName")
                school.text = edu.get("course_institution")
            if edu.get("course_name") or edu.get("degree"):
                deg = ET.SubElement(edu_org, "Degree")
                deg.text = f"{edu.get('degree', '')} - {edu.get('course_name', '')}".strip(" -")
            if edu.get("course_end_date_year"):
                comp = ET.SubElement(edu_org, "CompletionDate")
                comp.text = str(edu.get("course_end_date_year"))

    # 7. Idiomas
    mother_langs = json_data.get("mother_languages", [])
    other_langs = json_data.get("other_languages", [])
    all_langs = mother_langs + other_langs
    if all_langs:
        langs_elem = ET.SubElement(struct_resume, "Languages")
        for lang in all_langs:
            lang_node = ET.SubElement(langs_elem, "Language")
            name_node = ET.SubElement(lang_node, "LanguageName")
            name_node.text = lang.get("name", "")
            if lang.get("written_label"):
                prof_node = ET.SubElement(lang_node, "Proficiency")
                prof_node.text = f"Written: {lang.get('written_label')}, Spoken: {lang.get('spoken_label', '')}"

    # 8. Treinamentos e Certificações
    trainings = json_data.get("trainings", [])
    if trainings:
        cert_elem = ET.SubElement(struct_resume, "Certifications")
        for tr in trainings:
            cert_node = ET.SubElement(cert_elem, "Certification")
            cert_node.text = f"{tr.get('name', '')} ({tr.get('company', '')} - {tr.get('year', '')})".strip(" ()-")

    raw_str = ET.tostring(root, encoding="utf-8")
    parsed = minidom.parseString(raw_str)
    return parsed.toprettyxml(indent="  ")

def json_file_to_xml_file(json_path: str, output_xml_path: str) -> str:
    """Lê um arquivo JSON e salva o XML gerado."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    xml_str = convert_json_to_xml(data)
    
    out_dir = Path(output_xml_path).parent
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        
    with open(output_xml_path, 'w', encoding='utf-8') as f:
        f.write(xml_str)
        
    print(f"[✓] XML gerado a partir do JSON em: {output_xml_path}")
    return output_xml_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        j_path = sys.argv[1]
        x_path = sys.argv[2] if len(sys.argv) > 2 else "output/generated_cv.xml"
        json_file_to_xml_file(j_path, x_path)
    else:
        json_file_to_xml_file("sample_cv.json", "output/generated_cv.xml")
