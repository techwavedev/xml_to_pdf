import zipfile
import os

docx_path = 'Samples/Sprint Curriculum Elton Machado 20260729 085733.docx'
out_dir = 'scratch/media_preview'

os.makedirs(out_dir, exist_ok=True)

with zipfile.ZipFile(docx_path, 'r') as z:
    for name in z.namelist():
        if name.startswith('word/media/'):
            data = z.read(name)
            filename = os.path.basename(name)
            with open(os.path.join(out_dir, filename), 'wb') as f:
                f.write(data)
            print(f"Extracted {filename} ({len(data)} bytes)")
