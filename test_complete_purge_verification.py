import cv_builder
import zipfile
import xml.etree.ElementTree as ET

for sample in ['samples/expert.docx', 'samples/itresume.docx', 'samples/mlops.docx', 'samples/sprint.docx']:
    cv_builder.build_cv_from_json('sample_cv.json', docx_template=sample, out_docx=True)

print("\n=======================================================")
print("  ABSOLUTE VERIFICATION OF TOTAL OLD PARAGRAPH PURGE")
print("=======================================================")

OLD_KEYWORDS = [
    'European Commission', 'ING', 'BNP Paribas', 'Tenforce', 'BigLevel',
    'Whooo Management', 'Helimax', 'Iconic Mind', 'Netspace', 'CERT IPN',
    'ENA', 'Econoteca', 'Cafidata', 'Intranet', 'Elton', 'Machado',
    'Aveiro', 'Portugal', 'Lusófona', 'Universidade Aberta', 'HashiCorp',
    'Udemy', 'HackerRank', 'NSX', 'vSphere', 'Courier-IMAP', 'Active Directory'
]

for docx in ['output/expert_Doe_Hummus.docx', 'output/itresume_Doe_Hummus.docx', 'output/mlops_Doe_Hummus.docx', 'output/sprint_Doe_Hummus.docx']:
    with zipfile.ZipFile(docx, 'r') as z:
        data = z.read('word/document.xml').decode('utf-8', errors='ignore')
        root = ET.fromstring(data)
        texts = [t.text.strip() for t in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text and t.text.strip()]
        
        found_old = [t for t in texts if any(k.lower() in t.lower() for k in OLD_KEYWORDS)]
        print(f"\n📄 File: {docx}")
        print(f"   Total Text Elements: {len(texts)}")
        print(f"   Old Personal Remnants Remaining: {len(found_old)}")
        if found_old:
            print(f"   ⚠️ Remnants Found: {found_old[:5]}")
        else:
            print("   ✓ ZERO OLD PERSONAL EXPERIENCES REMAIN!")
