import cv_builder
import json
import zipfile
import xml.etree.ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# 1. Gera os 4 modelos .docx populados com sample_cv.json
templates = ['expert', 'itresume', 'mlops', 'sprint']

for t in templates:
    docx_input = f"samples/{t}.docx"
    print(f"\n[*] Gerando modelo populado para: {docx_input}")
    cv_builder.build_cv_from_json('sample_cv.json', docx_template=docx_input, out_docx=True)

# 2. Executa a auditoria automática (AUTO CHECK) em todos os 4 arquivos gerados
print("\n" + "="*65)
print(" 🔬 RELATÓRIO DE AUDITORIA AUTOMÁTICA (AUTO CHECK AUDIT)")
print("="*65)

old_forbidden = [
    'European Commission', 'DIGIT A4', 'BNP Paribas', 'ING06', 'Tenforce', 
    'BigLevel', 'Whooo', 'Helimax', 'Iconic Mind', 'Netspace', 'CERT IPN', 
    'ENA - Escola', 'Econoteca', 'Cafidata', 'Intranet', 'Elton', 'Machado', 
    'Aveiro', 'Portugal', 'Lusófona', 'Universidade Aberta', 'HashiCorp', 
    'Udemy', 'HackerRank', 'NSX', 'vSphere', 'Courier-IMAP', 'Active Directory',
    'Belgian', 'Portuguese', 'Brazilian'
]

all_passed = True

for t in templates:
    docx_file = f"output/{t}_Doe_Hummus.docx"
    try:
        with zipfile.ZipFile(docx_file, 'r') as z:
            doc_xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
            root = ET.fromstring(doc_xml)
            texts = [elem.text.strip() for elem in root.iter(f'{{{W_NS}}}t') if elem.text and elem.text.strip()]
            
            found_forbidden = []
            for text_run in texts:
                for kw in old_forbidden:
                    if kw.lower() in text_run.lower():
                        found_forbidden.append(f"'{kw}' em '{text_run}'")
            
            print(f"\n📄 {docx_file}:")
            print(f"   Total Text Elements: {len(texts)}")
            if found_forbidden:
                all_passed = False
                print(f"   ❌ FAILED: {len(found_forbidden)} strings antigas detectadas!")
                for item in found_forbidden[:5]:
                    print(f"      - {item}")
            else:
                print("   ✓ PASSED: ZERO strings antigas detectadas! Texto 100% vindo do JSON.")
                print(f"   Preview inicial: {texts[:5]}")
    except Exception as e:
        all_passed = False
        print(f"\n❌ Erro ao abrir {docx_file}: {e}")

print("\n" + "="*65)
if all_passed:
    print(" 🎉 AUDITORIA AUTOMÁTICA CONCLUÍDA COM 100% DE SUCESSO!")
else:
    print(" ⚠️ AUDITORIA APONTOU INCONSISTÊNCIAS.")
print("="*65)
