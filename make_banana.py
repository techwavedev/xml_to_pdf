from PIL import Image
import os, shutil

src = "/Users/elton/.gemini/antigravity-ide/brain/988d0139-c487-40b8-8be7-4e8002ec3a97/nano_banana_profile_1785318837191.png"

img = Image.open(src).convert("RGB")

# Versão grande (1820x2557) - mesma proporção da image7.jpeg original
large = img.resize((1820, 2557), Image.LANCZOS)
large.save("assets/banana_large.jpeg", "JPEG", quality=92)
print(f"banana_large.jpeg: {large.size}")

# Versão pequena (150x150) - mesma que large_foto.jpeg original
small = img.resize((150, 150), Image.LANCZOS)
small.save("assets/banana_small.jpeg", "JPEG", quality=92)
print(f"banana_small.jpeg: {small.size}")

print("Done! Banana photos ready.")
