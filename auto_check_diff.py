import json
import zipfile
import xml.etree.ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# 1. Carrega dados do JSON
with open('sample_cv.json', 'r') as f:
    json_data = json.load(f)

# Extrai todas as strings do JSON
json_strings = set()
def extract_json_strings(obj):
    if isinstance(obj, str):
        if len(obj.strip()) > 1:
            json_strings.add(obj.strip())
    elif isinstance(obj, dict):
        for v in obj.values():
            extract_json_strings(v)
    elif isinstance(obj, list):
        for item in obj:
            extract_json_strings(item)

extract_json_strings(json_data)

# 2. Inspeciona cada arquivo DOCX na pasta output
samples = ['expert', 'itresume', 'mlops', 'sprint']

for s in samples:
    docx_file = f"output/{s}_Doe_Hummus.docx"
    print(f"\n=======================================================")
    print(f"🔍 AUTO CHECK AUDIT FOR: {docx_file}")
    print(f"=======================================================")
    
    try:
        with zipfile.ZipFile(docx_file, 'r') as z:
            doc_xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
            root = ET.fromstring(doc_xml)
            
            # Pega todos os textos do XML
            texts = [t.text.strip() for t in root.iter(f'{{{W_NS}}}t') if t.text and t.text.strip()]
            
            print(f"• Total Text Runs: {len(texts)}")
            
            # Palavras chaves de amostragem antigas que JAMAIS devem existir
            old_forbidden = [
                'European Commission', 'DIGIT A4', 'BNP Paribas', 'ING06', 'Tenforce', 
                'BigLevel', 'Whooo', 'Helimax', 'Iconic Mind', 'Netspace', 'CERT IPN', 
                'ENA - Escola', 'Econoteca', 'Cafidata', 'Intranet', 'Elton', 'Machado', 
                'Aveiro', 'Portugal', 'Lusófona', 'Universidade Aberta', 'HashiCorp', 
                'Udemy', 'HackerRank', 'NSX', 'vSphere', 'Courier-IMAP', 'Active Directory',
                'Belgian', 'Portuguese', 'Brazilian'
            ]
            
            found_forbidden = []
            for t in texts:
                for kw in old_forbidden:
                    if kw.lower() in t.lower():
                        found_forbidden.append(f"'{kw}' found in text run: '{t}'")
            
            if found_forbidden:
                print(f"❌ AUDIT FAILED! {len(found_forbidden)} forbidden old sample strings detected:")
                for item in found_forbidden[:10]:
                    print(f"   - {item}")
            else:
                print("✓ PASS: ZERO forbidden old sample strings detected!")
                
            print("\n• Sample Output Text Preview:")
            for idx, text in enumerate(texts[:15]):
                print(f"   [{idx+1}] {text}")
                
    except Exception as e:
        print(f"❌ Could not open {docx_file}: {e}")
