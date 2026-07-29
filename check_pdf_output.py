import cv_builder
import subprocess
import os
import zipfile
import xml.etree.ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

for sample in ['samples/expert.docx', 'samples/itresume.docx', 'samples/mlops.docx', 'samples/sprint.docx']:
    cv_builder.build_cv_from_json('sample_cv.json', docx_template=sample, out_docx=True)
    
    docx_stem = os.path.basename(sample).replace('.docx', '')
    out_docx = f"output/{docx_stem}_Doe_Hummus.docx"
    
    if os.path.exists(out_docx):
        with zipfile.ZipFile(out_docx, 'r') as z:
            doc_xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
            root = ET.fromstring(doc_xml)
            texts = [t.text.strip() for t in root.iter(f'{{{W_NS}}}t') if t.text and t.text.strip()]
            print(f"\n=======================================================")
            print(f"📄 Generated File: {out_docx}")
            print(f"   Total Text Elements: {len(texts)}")
            print(f"   First 8 runs: {texts[:8]}")
            print(f"   Last 8 runs: {texts[-8:]}")
            
            # Check for any old sample names or companies
            old_remnants = [t for t in texts if any(k in t for k in [
                'Elton', 'Machado', 'Aveiro', 'Portugal', 'European Commission', 'BNP Paribas',
                'Helimax', 'DIGIT A4', 'Lusófona', 'Universidade', 'HashiCorp', 'Udemy', 'HackerRank',
                '12-1999', '04-2004', '12-1997', 'Tomar', 'Portuguese', 'Dutch', 'NSX'
            ])]
            print(f"   Old Remnants Remaining: {len(old_remnants)}")
