import base64
import json
import os

with open('assets/image6.png', 'rb') as f:
    bg_b64 = base64.b64encode(f.read()).decode('utf-8')

photo_path = 'assets/sample_photo.png'
if not os.path.exists(photo_path):
    photo_path = 'assets/image7.jpeg'

with open(photo_path, 'rb') as f:
    photo_b64 = base64.b64encode(f.read()).decode('utf-8')

with open('assets/b64_assets.json', 'w') as f:
    json.dump({'bg': bg_b64, 'photo': photo_b64}, f)
print('b64_assets.json updated with real constellation background!')
