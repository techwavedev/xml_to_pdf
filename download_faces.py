#!/usr/bin/env python3
"""Download realistic AI-generated faces from thispersondoesnotexist.com
and save as properly cropped/sized JPEG files for the CV template."""
import urllib.request
import time
import os
from PIL import Image
import io

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

def download_face(output_name: str):
    """Download a face from thispersondoesnotexist.com and save as JPEG."""
    url = "https://thispersondoesnotexist.com"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req) as response:
        data = response.read()
    
    img = Image.open(io.BytesIO(data)).convert('RGB')
    w, h = img.size
    
    # Make it square if not already
    if w != h:
        size = min(w, h)
        left = (w - size) // 2
        top = (h - size) // 2
        img = img.crop((left, top, left + size, top + size))
    
    # Save large version (original size)
    large_path = os.path.join(ASSETS, f'fake_{output_name}_large.jpeg')
    img.save(large_path, 'JPEG', quality=90)
    print(f'[OK] {output_name} large: {img.size} -> {os.path.getsize(large_path)} bytes')
    
    # Save small thumbnail (150x150 to match the sprint.docx photo slot)
    small = img.resize((150, 150), Image.LANCZOS)
    small_path = os.path.join(ASSETS, f'fake_{output_name}_small.jpeg')
    small.save(small_path, 'JPEG', quality=85)
    print(f'[OK] {output_name} small: {small.size} -> {os.path.getsize(small_path)} bytes')
    
    return img

if __name__ == '__main__':
    print("Downloading male face...")
    male = download_face('male')
    
    # Wait to get a different face
    time.sleep(2)
    
    print("\nDownloading female face...")
    female = download_face('female')
    
    # Set male as the default
    import shutil
    shutil.copy2(os.path.join(ASSETS, 'fake_male_large.jpeg'), os.path.join(ASSETS, 'fake_large.jpeg'))
    shutil.copy2(os.path.join(ASSETS, 'fake_male_small.jpeg'), os.path.join(ASSETS, 'fake_small.jpeg'))
    print("\n[OK] Defaults set to male version.")
    print("\nDone! Files saved in assets/:")
    print("  - fake_male_large.jpeg / fake_male_small.jpeg")
    print("  - fake_female_large.jpeg / fake_female_small.jpeg")
    print("  - fake_large.jpeg / fake_small.jpeg (defaults = male)")
    print("\nNote: thispersondoesnotexist.com gives random faces each time.")
    print("Re-run this script if you don't like the faces you got.")
