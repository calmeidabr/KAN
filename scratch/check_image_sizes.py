from PIL import Image
import os

img1 = Image.open(os.path.join("images", "plano_kan_fundo.jpg"))
img2 = Image.open(os.path.join("images", "plano_kan_cristiano.jpg"))

print(f"plano_kan_fundo.jpg size: {img1.size}")
print(f"plano_kan_cristiano.jpg size: {img2.size}")
