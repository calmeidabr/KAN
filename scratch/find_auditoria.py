import sys
with open("c:/Users/calme/OneDrive/Documentos/KAN/PROG/kan.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "busca de perfis" in line.lower() or "scores técnicos" in line.lower() or "auditoria" in line.lower():
        sys.stdout.buffer.write(f"Line {idx+1}: {line.strip()}\n".encode("utf-8", "replace"))
