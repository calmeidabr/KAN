import sys
with open("c:/Users/calme/OneDrive/Documentos/KAN/PROG/kan.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "painel de controle" in line.lower() or "render_admin_panel" in line.lower() or "tabelas" in line.lower() and ("base" in line.lower() or "banners" in line.lower()):
        sys.stdout.buffer.write(f"Line {idx+1}: {line.strip()}\n".encode("utf-8", "replace"))
