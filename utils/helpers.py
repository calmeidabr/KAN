import unicodedata
import base64
from PIL import Image
import io
import re

def remover_acentos(texto):
    if texto is None: return ""
    texto_str = str(texto).replace('º', 'o').replace('ª', 'a')
    texto_str = texto_str.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'").replace('–', '-').replace('—', '-')
    norm = ''.join(c for c in unicodedata.normalize('NFD', texto_str) if unicodedata.category(c) != 'Mn')
    return norm.encode('latin-1', 'ignore').decode('latin-1')

def normalize_key(k):
    if k is None: return ""
    n = remover_acentos(k).lower()
    for char in [' ', '_', '-', '(', ')', '.', 'º', 'o', 'ª', 'a']:
        n = n.replace(char, '')
    return n

def get_from_row(row, key):
    if not row or not isinstance(row, dict): return None
    search_key = normalize_key(key)
    for k in row.keys():
        if normalize_key(k) == search_key:
            return row[k]
    return None

import streamlit as st

@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

@st.cache_data
def load_text_file(filepath):
    import os
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return ""

@st.cache_data
def get_base64_logo(logo_path):
    import os
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def compress_image_to_b64(uploaded_file, max_width=1280, quality=75):
    try:
        img = Image.open(uploaded_file)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        width, height = img.size
        if width > max_width:
            ratio = max_width / width
            new_height = int(height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        img.save(output, format="JPEG", quality=quality, optimize=True)
        return base64.b64encode(output.getvalue()).decode("utf-8")
    except Exception as e:
        return ""

def validar_cnpj(cnpj):
    cnpj = re.sub(r'\D', '', str(cnpj))
    if len(cnpj) != 14: return False
    if cnpj == cnpj[0] * 14: return False
    
    tamanhos = [12, 13]
    multiplicadores_base = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    
    for tamanho in tamanhos:
        numeros = [int(digito) for digito in cnpj[:tamanho]]
        multiplicadores = multiplicadores_base[-tamanho:]
        soma = sum(n * m for n, m in zip(numeros, multiplicadores))
        resto = soma % 11
        digito = 0 if resto < 2 else 11 - resto
        if int(cnpj[tamanho]) != digito:
            return False
    return True

def format_vaga_title(nome_vaga, senioridade):
    if not nome_vaga:
        return ""
    nome_vaga = str(nome_vaga).strip()
    if not senioridade or str(senioridade).strip() in ("", "Nenhum", "Não especificado"):
        return nome_vaga
    senioridade = str(senioridade).strip()
    if senioridade.lower() in nome_vaga.lower():
        return nome_vaga
    return f"{nome_vaga} ({senioridade})"

def converter_markdown_para_html(texto):
    if not texto:
        return ""
    # Substitui **texto** por <strong> com cor de destaque do tema (var(--accent)), peso 800 e fonte Outfit
    return re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: var(--accent); font-weight: 800; font-family: Outfit, sans-serif;">\1</strong>', str(texto))

