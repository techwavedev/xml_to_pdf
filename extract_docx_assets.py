import zipfile
import os

docx_path = 'Samples/Sprint CV Elton Machado 20260729 085709.docx'
assets_dir = 'assets'
os.makedirs(assets_dir, exist_ok=True)

with zipfile.ZipFile(docx_path) as z:
    for f in z.namelist():
        if 'media/' in f and not f.endswith('/'):
            filename = os.path.basename(f)
            data = z.read(f)
            dest_path = os.path.join(assets_dir, filename)
            with open(dest_path, 'wb') as out_f:
                out_f.write(data)
            print(f"[✓] Extracted asset: {filename} ({len(data)} bytes) -> {dest_path}")
