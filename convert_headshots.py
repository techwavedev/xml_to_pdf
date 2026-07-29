#!/usr/bin/env python3
"""Convert generated headshot PNGs to JPEGs in assets folder."""
from PIL import Image
import os, shutil

brain = '/Users/elton/.gemini/antigravity-ide/brain/674b985c-481d-4066-ab01-0980c02156df'
assets = os.path.join(os.path.dirname(__file__), 'assets')

files = {
    'male': 'headshot_male_1785319301286.png',
    'female': 'headshot_female_1785319311607.png',
}

for name, src_file in files.items():
    src = os.path.join(brain, src_file)
    if not os.path.exists(src):
        print(f"[SKIP] {src} not found")
        continue
    img = Image.open(src).convert('RGB')
    
    # Large version
    large_path = os.path.join(assets, f'fake_{name}_large.jpeg')
    img.save(large_path, 'JPEG', quality=90)
    print(f'[OK] {name} large: {os.path.getsize(large_path)} bytes -> {large_path}')
    
    # Small thumbnail version
    small = img.resize((150, 150), Image.LANCZOS)
    small_path = os.path.join(assets, f'fake_{name}_small.jpeg')
    small.save(small_path, 'JPEG', quality=85)
    print(f'[OK] {name} small: {os.path.getsize(small_path)} bytes -> {small_path}')

# Update defaults (backward compat with existing script)
shutil.copy2(os.path.join(assets, 'fake_male_large.jpeg'), os.path.join(assets, 'fake_large.jpeg'))
shutil.copy2(os.path.join(assets, 'fake_male_small.jpeg'), os.path.join(assets, 'fake_small.jpeg'))
print('\n[OK] Defaults (fake_large/fake_small) updated to male version.')
print('Done!')
