import zipfile
import xml.etree.ElementTree as ET
import os

docx_path = 'Samples/Sprint CV Elton Machado 20260729 085709.docx'

with zipfile.ZipFile(docx_path) as z:
    for f in z.namelist():
        if f.startswith('word/media/'):
            print(f"Media file: {f} ({len(z.read(f))} bytes)")
        elif 'footer' in f or 'header' in f:
            print(f"Footer/Header file: {f}")
            xml_data = z.read(f)
            root = ET.fromstring(xml_data)
            drawings = root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing')
            shapes = root.findall('.//{urn:schemas-microsoft-com:vml}shape')
            pics = root.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/picture}pic')
            print(f"   -> Drawings count: {len(drawings)}, Shapes count: {len(shapes)}, Pics count: {len(pics)}")
