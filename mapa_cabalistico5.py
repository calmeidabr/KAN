import os

# Este arquivo serve como ponte para o novo nome kan.py
# O Streamlit Cloud exige que o arquivo principal configurado inicialmente exista.
path = os.path.join(os.path.dirname(__file__), "kan.py")
with open(path, "r", encoding="utf-8") as f:
    exec(f.read(), globals())
