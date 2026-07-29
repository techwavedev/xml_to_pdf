from PIL import Image
import os

src = "/Users/elton/.gemini/antigravity-ide/brain/988d0139-c487-40b8-8be7-4e8002ec3a97/fake_profile_photo_1785318873036.png"

img = Image.open(src).convert("RGB")

# Versão grande (1820x2557) - mesma da image7.jpeg original no sprint.docx
large = img.resize((1820, 2557), Image.LANCZOS)
large.save("assets/fake_large.jpeg", "JPEG", quality=92)
print(f"fake_large.jpeg: {large.size}, {os.path.getsize('assets/fake_large.jpeg')} bytes")

# Versão pequena (150x150) - mesma da large_foto.jpeg original no sprint.docx
small = img.resize((150, 150), Image.LANCZOS)
small.save("assets/fake_small.jpeg", "JPEG", quality=92)
print(f"fake_small.jpeg: {small.size}, {os.path.getsize('assets/fake_small.jpeg')} bytes")

print("Done!")
