import base64
import os
import json

def get_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

bg_b64 = get_base64("assets/image6.png")
photo_b64 = get_base64("assets/image7.jpeg")
logo_b64 = get_base64("assets/image3.png")

print(f"Background b64 len: {len(bg_b64)}")
print(f"Photo b64 len: {len(photo_b64)}")
print(f"Logo b64 len: {len(logo_b64)}")

with open("assets/b64_assets.json", "w") as f:
    json.dump({
        "bg": bg_b64,
        "photo": photo_b64,
        "logo": logo_b64
    }, f)
