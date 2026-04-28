import streamlit as st
import pandas as pd
import datetime
import unicodedata
import json
import calendar
import tempfile
from collections import Counter
from PIL import Image
import os
import google.generativeai as genai

def remover_acentos(texto):
    if texto is None: return ""
    texto_str = str(texto).replace('º', 'o').replace('ª', 'a')
    texto_str = texto_str.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'").replace('–', '-').replace('—', '-')
    norm = ''.join(c for c in unicodedata.normalize('NFD', texto_str) if unicodedata.category(c) != 'Mn')
    return norm.encode('latin-1', 'ignore').decode('latin-1')

def get_from_row(row, key):
    # Tenta buscar ignorando acentos e case
    if not row: return None
    search_key = remover_acentos(key).lower()
    for k in row.keys():
        if remover_acentos(k).lower() == search_key:
            return row[k]
    return None

try:
    favicon_img = Image.open(os.path.join("images", "ico_k.png"))
except Exception:
    favicon_img = "🔮"

try:
    header_img = Image.open(os.path.join("images", "kan_logo_lar.png"))
except Exception:
    header_img = "🔮"

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Mapa Numerológico Cabalístico KAN", layout="wide", page_icon=favicon_img)

st.markdown("""
<style>
    /* Restaurando Identidade KAN */
    .stApp {
        background-color: #401041 !important;
        color: #FFFFFF !important;
    }
    
    /* Inputs com fundo semi-transparente e texto BRANCO */
    div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(241, 134, 23, 0.5) !important;
        border-radius: 8px !important;
    }
    input, textarea, span {
        color: #FFFFFF !important;
    }
    /* Cor do cursor (caret) também em branco */
    input {
        caret-color: white !important;
    }
    
    /* Labels em branco para leitura sobre o roxo */
    label, .stMarkdown p, h3 {
        color: #FFFFFF !important;
    }

    /* Inputs limitados para não ficarem muito longos e centralizados */
    .stTextInput, .stTextArea, .stFileUploader, .stSelectbox {
        max-width: 500px !important;
    }
    /* Forçar o alinhamento dentro das colunas */
    [data-testid="stForm"] {
        max-width: 800px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    /* Em colunas, permite ocupar a largura da coluna */
    [data-testid="column"] .stTextInput, [data-testid="column"] .stTextArea {
        max-width: 100% !important;
    }

    /* Botão Laranja KAN */
    .stButton > button, .stFormSubmitButton > button {
        background-color: #F18617 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
    }

    /* Tabelas com as cores originais */
    table thead th {
        background-color: #F18617 !important;
        color: #401041 !important;
    }
    table tbody th {
        color: #F18617 !important;
    }
    
    /* Ajuste para o expander ficar visível */
    div[data-testid="stExpander"] {
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid #F18617 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO CLIENTE SUPABASE (GLOBAL) ---
supabase_client = None
try:
    from supabase import create_client, Client
    url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
    key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
    supabase_client: Client = create_client(url, key)
except Exception as e:
    st.error(f"Erro ao conectar ao Supabase: {e}")

# Botão para limpar cache
if st.sidebar.button("🔄 Recarregar Dados do Banco"):
    st.cache_data.clear()
    st.rerun()

# --- CACHED FETCH ---
@st.cache_data(ttl=3600)
def fetch_arcanos():
    try:
        resp = supabase_client.table("arcanos").select("*").execute()
        return {str(int(row['numero'])): {"nome": row['nome'], "descricao": row['descricao']} for row in resp.data if row.get('numero')}
    except Exception:
        return {}

ARCANOS_DB = fetch_arcanos()

@st.cache_data(ttl=3600)
def fetch_fortalezas():
    try:
        resp = supabase_client.table("fortalezas").select("*").execute()
        return {str(int(row['triangulo'])): {"fortaleza": row['fortaleza'], "descricao": row['descricao']} for row in resp.data if row.get('triangulo')}
    except Exception:
        return {}

FORTALEZAS_DB = fetch_fortalezas()

@st.cache_data(ttl=3600)
def fetch_kan():
    try:
        resp = supabase_client.table("kans").select("*").execute()
        return {str(int(row['numero'])): {"kan": row['kan'], "descricao": row['descricao']} for row in resp.data if row.get('numero')}
    except Exception:
        return {}

KAN_DB = fetch_kan()

@st.cache_data(ttl=3600)
def fetch_desafios():
    try:
        resp = supabase_client.table("desafios").select("*").execute()
        return {str(int(row['dia_nascimento'])): {"desafio": row['desafio'], "descricao": row['descricao']} for row in resp.data if row.get('dia_nascimento')}
    except Exception:
        return {}

DESAFIOS_DB = fetch_desafios()

@st.cache_data(ttl=3600)
def fetch_matriz():
    try:
        resp = supabase_client.table("matriz").select("*").execute()
        return {str(row['numero']): row for row in resp.data if row.get('numero')}
    except Exception:
        return {}
        resp = supabase_client.table("matriz").select("*").execute()
        return {str(get_from_row(row, 'resultado')): row for row in resp.data}
    except Exception:
        return {}

MATRIZ_DB = fetch_matriz()

@st.cache_data(ttl=3600)
def fetch_atributos():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase_client: Client = create_client(url, key)
        resp = supabase_client.table("atributos").select("*").execute()
        return {str(get_from_row(row, 'atributo')).upper(): row for row in resp.data}
    except Exception:
        return {}

ATRIBUTOS_DB = fetch_atributos()

@st.cache_data(ttl=3600)
def fetch_repeticao():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase_client: Client = create_client(url, key)
        resp = supabase_client.table("repeticao").select("*").execute()
        return {str(int(get_from_row(row, 'repeticao'))): row for row in resp.data}
    except Exception:
        return {}

REPETICAO_DB = fetch_repeticao()

@st.cache_data(ttl=3600)
def fetch_peso():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase_client: Client = create_client(url, key)
        resp = supabase_client.table("peso").select("*").execute()
        return {row['campo']: row['peso'] for row in resp.data}
    except Exception:
        return {}

PESO_DB = fetch_peso()

@st.cache_data(ttl=3600)
def fetch_perfis():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase_client: Client = create_client(url, key)
        resp = supabase_client.table("perfis").select("*").execute()
        return [row['perfil'] for row in resp.data]
    except Exception:
        return []

PERFIS_DB = fetch_perfis()

@st.cache_data(ttl=3600)
def fetch_perfil_descricao():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase_client: Client = create_client(url, key)
        resp = supabase_client.table("perfil_descricao").select("*").execute()
        return {str(get_from_row(row, 'perfil')).strip().capitalize(): get_from_row(row, 'descricao') for row in resp.data}
    except Exception:
        return {}

PERFIL_DESCRICAO_DB = fetch_perfil_descricao()

@st.cache_data(ttl=3600)
def fetch_qualidades():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase_client: Client = create_client(url, key)
        resp = supabase_client.table("qualidades").select("*").execute()
        return {str(get_from_row(row, 'qualidade')).strip().capitalize(): get_from_row(row, 'descricao') for row in resp.data}
    except Exception:
        return {}

QUALIDADES_DB = fetch_qualidades()

@st.cache_data(ttl=3600)
def fetch_lista_categoria():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase_client: Client = create_client(url, key)
        resp = supabase_client.table("lista_categoria").select("*").execute()
        return [get_from_row(row, 'categoria') for row in resp.data]
    except Exception:
        return []

LISTA_CATEGORIA_DB = fetch_lista_categoria()

@st.cache_data(ttl=3600)
def fetch_categoria_descricao():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase_client: Client = create_client(url, key)
        resp = supabase_client.table("categoria_descricao").select("*").execute()
        return {str(get_from_row(row, 'categoria')).strip().capitalize(): get_from_row(row, 'descricao') for row in resp.data}
    except Exception:
        return {}

CATEGORIA_DESCRICAO_DB = fetch_categoria_descricao()

@st.cache_data(ttl=3600)
def fetch_peso_categoria():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase_client: Client = create_client(url, key)
        resp = supabase_client.table("peso_categoria").select("*").execute()
        return {row['campo']: row['peso'] for row in resp.data}
    except Exception:
        return {}

PESO_CATEGORIA_DB = fetch_peso_categoria()

@st.cache_data(ttl=3600)
def fetch_diferenciais_descricao():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase_client: Client = create_client(url, key)
        resp = supabase_client.table("diferenciais_descricao").select("*").execute()
        # Retorna dicionário { '11': {diferencial, descricao}, '22': ... }
        return {str(get_from_row(row, 'no')): {'diferencial': get_from_row(row, 'diferencial'), 'descricao': get_from_row(row, 'descricao')} for row in resp.data}
    except Exception:
        return {}

DIFERENCIAIS_DESC_DB = fetch_diferenciais_descricao()

@st.cache_data(ttl=3600)
def fetch_descricoes_mapa():
    """Busca o dicionário de descrições numerológicas da tabela descricoes_mapa."""
    try:
        resp = supabase_client.table("descricoes_mapa").select("*").execute()
        # Retorna dict aninhado: {categoria: {valor: descricao}}
        resultado = {}
        for row in resp.data:
            cat = row.get('categoria', '')
            val = str(row.get('valor', ''))
            desc = row.get('descricao', '')
            if cat not in resultado:
                resultado[cat] = {}
            resultado[cat][val] = desc
        return resultado
    except Exception:
        return {}

DESCRICOES_MAPA_DB = fetch_descricoes_mapa()

def get_desc_mapa(categoria, valor):
    """Retorna a descrição numerológica para uma categoria e valor."""
    if not DESCRICOES_MAPA_DB:
        return ""
    cat_data = DESCRICOES_MAPA_DB.get(categoria, {})
    return cat_data.get(str(valor), "")


def calcular_numeros_nome(nome_completo):
    nome = nome_completo.upper().replace(' ', '')
    expressao_total = sum(letter_values.get(ch, 0) for ch in nome)
    vogais = set('AEIOUYÀÁÂÃÄÅÆÉÈÊËÍÎÏÓÒÔÕÖÚÙÛÜ')
    motivacao_total = sum(letter_values.get(ch, 0) for ch in nome if ch in vogais)
    consoantes_total = sum(letter_values.get(ch, 0) for ch in nome if ch not in vogais)

    impressao_reduzida = reduce_number(consoantes_total)
    while impressao_reduzida > 9:
        impressao_reduzida = sum(int(d) for d in str(impressao_reduzida))

    return (reduce_number(expressao_total), reduce_number(motivacao_total), impressao_reduzida,
            expressao_total, motivacao_total, consoantes_total)

def soma_numeros(n):
    while n > 9 and n not in [11, 22, 33]:
        n = sum(int(d) for d in str(n))
    return n

letter_values = {
    'A':1, 'B':2, 'C':3, 'D':4, 'E':5, 'F':8, 'G':3, 'H':5, 'I':1, 'J':1, 'K':2,
    'L':3, 'M':4, 'N':5, 'O':7, 'P':8, 'Q':1, 'R':2, 'S':3, 'T':4, 'U':6, 'V':6,
    'W':6, 'X':6, 'Y':1, 'Z':7, 'Ç':6, 'Ê':3, 'É':7, 'Í':3, 'Ó':9, 'Á':3, 'Ú':8,
    'Ã':4, 'Å':8, 'Ñ':8, 'Ù':3, 'Û':4, 'À':2, 'Ö':5, 'Ô':5, 'È':1, 'Â':8, 'Ì':2, 'Ï':2
}

def reduce_number(n):
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(i) for i in str(n))
    return n

# Cálculo dos Momentos Decisivos considerando números mestres
def calcular_momento_decisivo(a, b):
    soma = a + b
    if soma in (11, 22):
        return soma
    return reduce_number(soma)

def calcular_momentos_decisivos(dia, mes, ano, ciclos_vida):
    # 1º Momento Decisivo: Dia + Mês (sem reduzir 11 e 22)
    momento1 = calcular_momento_decisivo(dia, mes)
    inicio1 = ciclos_vida['ciclo1']['inicio']
    fim1 = ciclos_vida['ciclo1']['fim']

    # 2º Momento: Dia + Ano
    ano_reduzido = reduce_number(ano)
    momento2 = calcular_momento_decisivo(dia, ano_reduzido)
    inicio2 = fim1
    fim2 = inicio2 + 9

    # 3º Momento: soma 1º e 2º Momento
    soma_12 = momento1 + momento2
    if soma_12 in (11, 22):
        momento3 = soma_12
    else:
        momento3 = reduce_number(soma_12)
    inicio3 = fim2
    fim3 = inicio3 + 9

    # 4º Momento: Mês + Ano
    momento4 = calcular_momento_decisivo(mes, ano_reduzido)
    inicio4 = fim3
    fim4 = None  # Até o fim da vida

    return {
        'momento1': {'numero': momento1, 'inicio': inicio1, 'fim': fim1},
        'momento2': {'numero': momento2, 'inicio': inicio2, 'fim': fim2},
        'momento3': {'numero': momento3, 'inicio': inicio3, 'fim': fim3},
        'momento4': {'numero': momento4, 'inicio': inicio4, 'fim': fim4},
    }

# (O restante do código permanece igual, ajuste para chamar calcular_momentos_decisivos e imprimir resultados)

# Abaixo trecho adaptado da função calcular_numerologia para incluir momentos decisivos

def calcular_ciclos_vida(dia, mes, ano, destino):
    ciclo1_num = mes
    while ciclo1_num > 9:
        ciclo1_num = sum(int(d) for d in str(ciclo1_num))
        
    ciclo1_ano_inicio = ano
    ciclo1_periodo_anos = 37 - destino
    ciclo1_ano_fim = ciclo1_ano_inicio + ciclo1_periodo_anos
    
    ciclo2_num = dia
    while ciclo2_num > 9:
        ciclo2_num = sum(int(d) for d in str(ciclo2_num))
        
    ciclo2_ano_inicio = ciclo1_ano_fim
    ciclo2_ano_fim = ciclo2_ano_inicio + 27

    ano_reduzido = reduce_number(ano)
    if ano_reduzido in [11, 22]:
        ciclo3_num = ano_reduzido
    else:
        ciclo3_num = ano_reduzido
    ciclo3_ano_inicio = ciclo2_ano_fim

    return {
        'ciclo1': {'numero': ciclo1_num, 'inicio': ciclo1_ano_inicio, 'fim': ciclo1_ano_fim},
        'ciclo2': {'numero': ciclo2_num, 'inicio': ciclo2_ano_inicio, 'fim': ciclo2_ano_fim},
        'ciclo3': {'numero': ciclo3_num, 'inicio': ciclo3_ano_inicio, 'fim': None}
    }

def ano_pessoal(dia, mes, ano_atual):
    total = dia + mes + ano_atual
    while total > 9:
        total = sum(int(d) for d in str(total))
    return total

def calcular_missao(destino, expressao):
    return reduce_number(destino + expressao)

def calcular_dividas_carmicas(dia, motivacao_total, expressao_total, impressao_total, destino_total):
    dividas = []
    
    # Função para buscar dívidas durante o processo de redução
    def extrair_dividas(n):
        if n in (13, 14, 16, 19):
            dividas.append(n)
        while n > 9 and n not in (11, 22, 33):
            n = sum(int(i) for i in str(n))
            if n in (13, 14, 16, 19):
                dividas.append(n)

    # O dia do nascimento é analisado puro
    if dia in (13, 14, 16, 19):
        dividas.append(dia)
        
    extrair_dividas(motivacao_total)
    extrair_dividas(expressao_total)
    extrair_dividas(impressao_total)
    extrair_dividas(destino_total)
    
    return sorted(list(set(dividas)))

def calcular_licoes_carmicas(nome_completo):
    nome_simplificado = nome_completo.upper().replace(' ', '')
    letras_presentes = set(nome_simplificado)
    numeros_presentes = set(letter_values.get(ch, 0) for ch in letras_presentes)
    todas_licoes = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    return sorted(list(todas_licoes - numeros_presentes))

def calcular_tendencias_ocultas(nome_completo):
    nome_simplificado = nome_completo.upper().replace(' ', '')
    contagem = Counter(letter_values.get(ch, 0) for ch in nome_simplificado if ch in letter_values)
    return sorted([num for num, count in contagem.items() if count >= 3])

def soma_tendencias_ocultas(tendencias_ocultas):
    return sum(tendencias_ocultas)

def calcular_resposta_subconsciente(licoes_carmicas):
    return 9 - len(licoes_carmicas)

def calcular_desafios(dia, mes, ano):
    d1 = reduce_number(dia)
    m1 = reduce_number(mes)
    a1 = reduce_number(ano)
    
    desafio1 = abs(d1 - m1)
    desafio2 = abs(d1 - a1)
    desafio_principal = abs(desafio1 - desafio2)
    return desafio1, desafio2, desafio_principal

def calcular_arcano_atual(nome_completo, nascimento, data_atual):
    arcanos_dict = ARCANOS_DB

    nome = nome_completo.upper().replace(' ', '')
    numeros = [str(letter_values.get(ch, 0)) for ch in nome]
    seq_str = ''.join(numeros)
    
    total_arcanos = len(seq_str) - 1
    if total_arcanos <= 0:
        return "N/A", "N/A"
        
    arcanos = [int(seq_str[i:i+2]) for i in range(total_arcanos)]
    dia_nasc, mes_nasc, ano_nasc = nascimento
    total_meses = 90 * 12
    duracao_meses_por_arcano = total_meses / total_arcanos
    
    periodos = []
    for i in range(total_arcanos):
        meses_para_somar = int(i * duracao_meses_por_arcano)
        mes_index = (mes_nasc - 1) + meses_para_somar
        ano = ano_nasc + (mes_index // 12)
        mes = (mes_index % 12) + 1
        
        ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
        dia = min(dia_nasc, ultimo_dia_mes)
        
        data_inicio = datetime.date(ano, mes, dia)
        periodos.append({
            'arcano': arcanos[i],
            'inicio': data_inicio
        })
        
    hoje = datetime.date(*data_atual[::-1])
    
    arcano_atual_idx = 0
    for i in range(total_arcanos):
        if hoje >= periodos[i]['inicio']:
            arcano_atual_idx = i
        else:
            break
            
    arc = periodos[arcano_atual_idx]['arcano']
    arc_data = arcanos_dict.get(str(arc), {"nome": f"Carta {arc}", "descricao": ""})
    nome_arcano = arc_data["nome"]
    descricao = arc_data["descricao"]
    data_inicio_str = periodos[arcano_atual_idx]['inicio'].strftime('%d/%m/%Y')
    
    if arcano_atual_idx < total_arcanos - 1:
        data_fim_str = periodos[arcano_atual_idx + 1]['inicio'].strftime('%d/%m/%Y')
    else:
        meses_para_somar = int(total_arcanos * duracao_meses_por_arcano)
        mes_index = (mes_nasc - 1) + meses_para_somar
        ano = ano_nasc + (mes_index // 12)
        mes = (mes_index % 12) + 1
        ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
        dia = min(dia_nasc, ultimo_dia_mes)
        data_fim_str = datetime.date(ano, mes, dia).strftime('%d/%m/%Y')
        
    resultado = f"Nº {arc} ({nome_arcano})"
    if descricao and str(descricao).lower() != "nan":
        resultado += f" - {descricao}"
    periodo = f"{data_inicio_str} a {data_fim_str}"
    
    return resultado, periodo

import itertools
from collections import defaultdict

def calcular_triangulo_vida(nome_completo):
    nome = nome_completo.upper().replace(' ', '')
    arr = [letter_values.get(ch, 0) for ch in nome]
    linhas = [arr]
    
    while len(arr) > 1:
        new_arr = []
        for i in range(len(arr) - 1):
            s = arr[i] + arr[i+1]
            while s > 9:
                s = sum(int(d) for d in str(s))
            new_arr.append(s)
        arr = new_arr
        linhas.append(arr)
        
    base = arr[0] if arr else 0
    seq_counts = defaultdict(int)
    
    for row in linhas:
        for num, group in itertools.groupby(row):
            count = sum(1 for _ in group)
            if count >= 3:
                seq_str = str(num) * count
                seq_counts[seq_str] += 1
                
    if not seq_counts:
        reps = "Não há"
    else:
        reps = ", ".join(f"{seq} ({qtd} vez{'es' if qtd > 1 else ''})" for seq, qtd in seq_counts.items())
        
    return base, reps

def calcular_numerologia(nome_completo, nascimento, data_atual):
    dia, mes, ano = nascimento
    dia_atual, mes_atual, ano_atual = data_atual

    resultados_nome = calcular_numeros_nome(nome_completo)
    expressao, motivacao, impressao = resultados_nome[0:3]

    # O total bruto do Destino é a soma individual dos algarismos da data de nascimento (para uso geral)
    destino_total = sum(int(d) for d in str(dia) + str(mes) + str(ano))
    destino = reduce_number(destino_total)

    ano_pess = ano_pessoal(dia, mes, ano_atual)

    mes_pess = mes_atual + ano_pess
    while mes_pess > 9:
        mes_pess = sum(int(d) for d in str(mes_pess))

    dia_pessoal = dia_atual + mes_pess
    while dia_pessoal > 9:
        dia_pessoal = sum(int(d) for d in str(dia_pessoal))

    # --- CÁLCULO ESPECÍFICO PARA DÍVIDAS CÁRMICAS ---
    # As dívidas cármicas exigem que a redução ocorra por blocos (cada nome/cada parte da data) antes da soma final
    def reduce_single(n):
        while n > 9:
            n = sum(int(d) for d in str(n))
        return n

    carmica_des = reduce_single(dia) + reduce_single(mes) + reduce_single(ano)

    vogais = set('AEIOUÀÁÂÃÄÅÆÉÈÊËÍÎÏÓÒÔÕÖÚÙÛÜ')
    carmica_mot = 0
    carmica_imp = 0
    carmica_exp = 0

    for palavra in nome_completo.upper().split():
        v = sum(letter_values.get(c, 0) for c in palavra if c in vogais)
        c = sum(letter_values.get(c, 0) for c in palavra if c not in vogais)
        e = sum(letter_values.get(c, 0) for c in palavra)
        carmica_mot += reduce_single(v)
        carmica_imp += reduce_single(c)
        carmica_exp += reduce_single(e)

    missao = calcular_missao(destino, expressao)
    dividas_carmicas = calcular_dividas_carmicas(dia, carmica_mot, carmica_exp, carmica_imp, carmica_des)
    licoes_carmicas = calcular_licoes_carmicas(nome_completo)
    tendencias_ocultas = calcular_tendencias_ocultas(nome_completo)
    soma_tendencias = soma_tendencias_ocultas(tendencias_ocultas)
    resposta_subconsciente = calcular_resposta_subconsciente(licoes_carmicas)
    desafio1, desafio2, desafio_principal = calcular_desafios(dia, mes, ano)

    ciclos_vida = calcular_ciclos_vida(dia, mes, ano, destino)
    momentos_decisivos = calcular_momentos_decisivos(dia, mes, ano, ciclos_vida)
    triangulo_base, triangulo_reps = calcular_triangulo_vida(nome_completo)
    arcano_atual_res, arcano_atual_periodo = calcular_arcano_atual(nome_completo, nascimento, data_atual)

    return (expressao, motivacao, impressao, destino, dia_pessoal, mes_pess,
            ano_pess, missao, dividas_carmicas, licoes_carmicas,
            tendencias_ocultas, soma_tendencias, resposta_subconsciente,
            desafio1, desafio2, desafio_principal, ciclos_vida, momentos_decisivos,
            triangulo_base, triangulo_reps, arcano_atual_res, arcano_atual_periodo)




def gerar_pdf(nome, data_nasc_str, dados, titulo="Mapa Numerologico Cabalistico"):
    from fpdf import FPDF
    import tempfile
    
    def clean_text(s):
        if not s: return ""
        s = str(s).replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'").replace('–', '-').replace('—', '-')
        s = s.replace("<b>", "").replace("</b>", "").replace("<br>", "\n")
        return s.encode('latin-1', 'replace').decode('latin-1')

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, clean_text(titulo), ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(190, 7, f"Nome: {clean_text(nome)}", ln=True)
    pdf.cell(190, 7, f"Data de Nascimento: {data_nasc_str}", ln=True)
    pdf.ln(5)
    
    col1 = 60
    col2 = 130
    
    # Cabeçalho da Tabela
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(col1, 8, clean_text("Campo"), 1, 0, 'L', True)
    pdf.cell(col2, 8, clean_text("Resultado"), 1, 1, 'L', True)
    
    pdf.set_font("Arial", '', 9)
    for row in dados:
        campo = clean_text(row['Campo'])
        resultado = clean_text(row['Resultado'])
        
        # Estimar altura (aproximada) para decidir se pula de página
        # Cada linha no multi_cell tem ~5mm de altura. 
        # Calculamos quantas linhas o texto vai ocupar (130mm de largura / ~2mm por char)
        linhas_estimadas = max(1, (len(resultado) // 80) + 1)
        altura_linha = linhas_estimadas * 6
        
        # Se não houver espaço na página (A4 tem ~297mm, deixamos margem)
        if pdf.get_y() + altura_linha > 275:
            pdf.add_page()
            # Repete cabeçalho da tabela na nova página
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(col1, 8, clean_text("Campo"), 1, 0, 'L', True)
            pdf.cell(col2, 8, clean_text("Resultado"), 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9)

        start_y = pdf.get_y()
        # Desenha a coluna do Resultado primeiro para saber a altura real
        pdf.set_x(col1 + 10) # 10 é a margem padrão esquerda
        pdf.multi_cell(col2, 6, resultado, 1)
        end_y = pdf.get_y()
        altura_final = end_y - start_y
        
        # Volta para desenhar o Campo com a mesma altura
        pdf.set_y(start_y)
        pdf.multi_cell(col1, altura_final, campo, 1)
        pdf.set_y(end_y)
        
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, 'rb') as f:
            return f.read()

# --- CÁLCULOS DO PERFIL COMPORTAMENTAL ---
def calcular_perfil_comportamental(expressao, motivacao, impressao, dia, destino, missao, ciclo2_num, momento3_num, triangulo_base):
    def reduce_kan(n):
        while n > 9 and n not in [11, 22]:
            n = sum(int(d) for d in str(n))
        return n
        
    estrutural = reduce_kan(motivacao + impressao + expressao + reduce_number(dia))
    direcionamento = reduce_kan(destino + missao + ciclo2_num + momento3_num)
    kan = reduce_kan(estrutural + direcionamento)

    # Dia Natalício (puro, ex: 21) e No Psiquico (reduzido, ex: 3)
    num_dia_puro = dia
    num_dia_reduzido = reduce_number(dia)
    
    # Campos solicitados: Motivação, Impressão, Expressão, Destino, Missão, Dia Natalício, Triângulo, No Psiquico
    nums = [motivacao, impressao, expressao, destino, missao, num_dia_puro, triangulo_base, num_dia_reduzido]
    counts = Counter(nums)
    
    # Filtra números que repetem 2 ou mais vezes, ordenando por frequência (maior primeiro)
    reps = sorted([(num, count) for num, count in counts.items() if count >= 2], key=lambda x: (-x[1], x[0]))
    
    def get_rep_info(idx):
        if idx < len(reps):
            n = reps[idx][0]
            r_data = REPETICAO_DB.get(str(n), {"perfil": ""})
            perfil = r_data.get('perfil', '')
            return f"{n} - {perfil}" if perfil else str(n)
        return ""

    rep1 = get_rep_info(0)
    rep2 = get_rep_info(1)
    
    return estrutural, direcionamento, kan, rep1, rep2

# --- SISTEMA DE LOGIN ---
USUARIOS = {
    "admin": "admin123",
    "adminkan": "K@nAdmin#2026*",
    "cristiano": "kan2026",
    "maria": "maria2026"
}

def check_password():
    def password_entered():
        user = st.session_state["username"]
        pwd = st.session_state["password"]
        if user in USUARIOS and USUARIOS[user] == pwd:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    def render_login_header():
        if header_img != "🔮":
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.image(header_img, use_container_width=True)
        st.markdown("<h4 style='text-align: center;'>Descubra sua potencialidade</h4>", unsafe_allow_html=True)
        st.write("")

    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        render_login_header()
        col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
        with col_l2:
            st.text_input("Usuário", key="username")
            st.text_input("Senha", type="password", key="password")
            st.button("Entrar", on_click=password_entered)
            if st.session_state.get("password_correct") == False:
                st.error("Usuário ou senha incorretos. Tente novamente.")
        return False
    else:
        return True

if not check_password():
    st.stop()

# --- CABEÇALHO E NAVEGAÇÃO SUPERIOR ---
col_logo, col_space, col_nav = st.columns([1.5, 4, 1.5])

with col_logo:
    if header_img != "🔮":
        st.image(header_img, use_container_width=True)
    else:
        st.markdown("<h2 style='margin:0;'>🔮 KAN</h2>", unsafe_allow_html=True)

with col_nav:
    st.markdown("<div style='padding-top: 10px;'>", unsafe_allow_html=True)
    menu_opt = st.selectbox("Menu", ["Mapa", "Painel de Controle"], label_visibility="collapsed", key="top_nav_menu")
    st.markdown("</div>", unsafe_allow_html=True)

if menu_opt == "Painel de Controle":
    st.title("⚙️ Painel de Controle Administrativo")
    
    # Proteção extra: Somente adminkan
    if "admin_authenticated" not in st.session_state:
        st.session_state["admin_authenticated"] = False
        
    if not st.session_state["admin_authenticated"]:
        st.warning("⚠️ Área restrita. Identifique-se para acessar o Painel.")
        
        col_auth1, col_auth2 = st.columns(2)
        with col_auth1:
            user_admin = st.text_input("Usuário de Administrador", key="admin_user_input")
        with col_auth2:
            pass_admin = st.text_input("Senha de Administrador", type="password", key="admin_pass_input")
            
        if st.button("🚀 Validar Acesso Administrativo"):
            if user_admin == "adminkan" and pass_admin == "K@nAdmin#2026*":
                st.session_state["admin_authenticated"] = True
                st.session_state["admin_user"] = user_admin
                st.success(f"Bem-vindo, {user_admin}!")
                st.rerun()
            else:
                st.error("Usuário ou Senha incorretos!")
        st.stop()
    
    st.info("Aqui você pode editar as tabelas do banco de dados diretamente. As alterações são salvas no Supabase.")
    
    tabelas = [
        "categoria_descricao", "perfil_descricao", "repeticao_descricao", 
        "diferenciais_descricao", "peso_categoria", "atributos", "matriz", "qualidades"
    ]
    
    tab_selecionada = st.selectbox("Selecione a Tabela para Editar", tabelas)
    
    if supabase_client:
        try:
            # Busca dados atuais
            res = supabase_client.table(tab_selecionada).select("*").execute()
            df_edit = pd.DataFrame(res.data)
            
            if not df_edit.empty:
                st.write(f"Editando: `{tab_selecionada}`")
                
                # Editor de dados com altura limitada
                edited_df = st.data_editor(df_edit, num_rows="dynamic", use_container_width=True, hide_index=True, height=450)
                
                if st.button(f"💾 Salvar Alterações em {tab_selecionada}"):
                    with st.spinner("Sincronizando com Supabase..."):
                        try:
                            supabase_client.table(tab_selecionada).delete().neq("id", -1).execute() 
                            novos_dados = edited_df.to_dict(orient='records')
                            if novos_dados:
                                supabase_client.table(tab_selecionada).insert(novos_dados).execute()
                            st.success(f"Tabela `{tab_selecionada}` atualizada com sucesso!")
                            st.cache_data.clear() 
                        except Exception as e:
                            st.error(f"Erro ao salvar: {e}")
            else:
                st.warning("Tabela vazia ou não encontrada.")
        except Exception as e:
            st.error(f"Erro ao carregar tabela: {e}")
    
    if st.button("Sair do Painel"):
        st.session_state["admin_authenticated"] = False
        st.rerun()
        
    st.stop() 

# --- TITULO DA PAGINA DE MAPAS ---
st.markdown("<h2 style='text-align: left; margin-bottom: 20px;'>Mapa e Perfil Comportamental</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.1em; color: rgba(255,255,255,0.7);'>Descubra a sua potencialidade através da numerologia cabalística.</p>", unsafe_allow_html=True)

# --- FETCH CLIENTES DO BANCO DE DADOS ---
clientes_salvos = {}
# --- FETCH CLIENTES DO BANCO DE DADOS ---
clientes_salvos = {}
if supabase_client:
    try:
        response = supabase_client.table("mapas_salvos").select("*").execute()
        for row in response.data:
            clientes_salvos[row['nome']] = {
                'data_nascimento': row['data_nascimento'],
                'cargo': row.get('cargo', ''),
                'empresa': row.get('empresa', ''),
                'linkedin_url': row.get('linkedin_url', ''),
                'experiencias': row.get('experiencias', ''),
                'foto_base64': row.get('foto_base64', ''),
                'ai_diagnosis': row.get('ai_diagnosis', '')
            }
            if row.get('ai_diagnosis'):
                if "ai_diagnosis" not in st.session_state:
                    st.session_state["ai_diagnosis"] = {}
                st.session_state["ai_diagnosis"][f"diag_{row['nome']}"] = row['ai_diagnosis']
    except Exception:
        pass

opcoes_clientes = ["-- Novo Cliente --"] + sorted(list(clientes_salvos.keys()))
cliente_selecionado = st.selectbox("Selecione um nome já cadastrado ou crie um novo:", opcoes_clientes)

if 'fotos' not in st.session_state:
    st.session_state['fotos'] = {}

# --- INICIALIZAÇÃO DE VARIÁVEIS ---
nome = ""
data_str = ""
data_input = datetime.date.today()
submit_mapa = False
submit_perfil = False

if cliente_selecionado == "-- Novo Cliente --":
    col_c1, col_c2, col_c3 = st.columns([1, 6, 1])
    with col_c2:
        with st.form("numerologia_form"):
            st.markdown("### 👤 Novo Cadastro")
            nome = st.text_input("Nome Completo (Conforme certidão):")
            
            col_f1, col_f2 = st.columns([1, 1])
            with col_f1:
                data_str_input = st.text_input("Data de Nascimento:", placeholder="dd/mm/yyyy")
            with col_f2:
                foto_upload = st.file_uploader("Foto (Opcional)", type=["png", "jpg", "jpeg"])

            col_f3, col_f4, col_f5 = st.columns([1, 1, 1])
            with col_f3:
                cargo = st.text_input("Cargo/Profissão:")
            with col_f4:
                empresa = st.text_input("Empresa/Grupo:")
            with col_f5:
                linkedin = st.text_input("LinkedIn (URL):")
                
            experiencias = st.text_area("Experiências Profissionais / Bio", 
                                    placeholder="Resumo profissional para a IA...",
                                    height=80)
            
            st.markdown("<br>", unsafe_allow_html=True)
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
            with col_btn1:
                submit_mapa = st.form_submit_button("🏁 Gerar Mapa")
            with col_btn2:
                submit_perfil = st.form_submit_button("🧠 Gerar Perfil")
            
    if submit_mapa or submit_perfil:
        try:
            dia, mes, ano = map(int, data_str_input.split('/'))
            data_input = datetime.date(ano, mes, dia)
            data_str = data_str_input
            if foto_upload:
                st.session_state['fotos'][nome] = foto_upload.getvalue()
            if submit_mapa:
                st.session_state['show_mapa'] = True
            if submit_perfil:
                st.session_state['show_perfil'] = True
        except:
            st.error("Formato de data inválido! Use dd/mm/yyyy (ex: 25/12/1980).")
            submit_mapa = False
            submit_perfil = False
else:
    nome = cliente_selecionado
    info_cliente = clientes_salvos[nome]
    data_str = info_cliente['data_nascimento']
    cargo = info_cliente['cargo']
    empresa = info_cliente['empresa']
    linkedin = info_cliente.get('linkedin_url', '')
    experiencias = info_cliente.get('experiencias', '')
    try:
        dia, mes, ano = map(int, data_str.split('/'))
        data_input = datetime.date(ano, mes, dia)
    except:
        data_input = datetime.date.today()
        
    tem_foto = bool(info_cliente.get('foto_base64')) or (nome in st.session_state['fotos'])
    if not tem_foto:
        foto_upload_existente = st.file_uploader("Carregar Foto (Opcional)", type=["png", "jpg", "jpeg"], key=f"foto_existente_{nome}")
        if foto_upload_existente:
            foto_bytes = foto_upload_existente.getvalue()
            st.session_state['fotos'][nome] = foto_bytes
            import base64
            encoded = base64.b64encode(foto_bytes).decode()
            if supabase_client:
                try:
                    supabase_client.table("mapas_salvos").update({"foto_base64": encoded}).eq("nome", nome).execute()
                    info_cliente['foto_base64'] = encoded
                    st.rerun()
                except:
                    pass
        
    # --- CAMPOS DE EDIÇÃO PARA CLIENTE EXISTENTE ---
    with st.expander("📝 Editar Informações Profissionais", expanded=False):
        col_edit1, col_edit2 = st.columns([2, 1])
        with col_edit1:
            new_linkedin = st.text_input("LinkedIn (URL)", value=linkedin, key=f"edit_link_{nome}")
            new_experiencias = st.text_area("Experiências Profissionais / Bio", value=experiencias, key=f"edit_exp_{nome}", height=100)
        
        with col_edit2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button("💾 Salvar Alterações"):
                if supabase_client:
                    try:
                        supabase_client.table("mapas_salvos").update({
                            "linkedin_url": new_linkedin,
                            "experiencias": new_experiencias
                        }).eq("nome", nome).execute()
                        st.toast("✅ Informações atualizadas!")
                        clientes_salvos[nome]['linkedin_url'] = new_linkedin
                        clientes_salvos[nome]['experiencias'] = new_experiencias
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao atualizar: {e}")

    st.markdown("---")
    st.session_state['show_mapa'] = True
    st.session_state['show_perfil'] = True

if (st.session_state.get('show_mapa') or st.session_state.get('show_perfil')) and nome:
    hoje = datetime.date.today()
    data_atual = (hoje.day, hoje.month, hoje.year)
    nascimento = (data_input.day, data_input.month, data_input.year)
    
    col_res1, col_res2, col_res3 = st.columns([1, 10, 1])
    with col_res2:
        st.markdown("---")
        info_parts = [nome, data_str]
        if cargo:
            info_parts.append(cargo)
        if empresa:
            info_parts.append(empresa)
        info_text = " | ".join(info_parts)
        
        foto_b64 = None
        if nome in st.session_state['fotos']:
            import base64
            foto_b64 = base64.b64encode(st.session_state['fotos'][nome]).decode()
        elif clientes_salvos.get(nome) and clientes_salvos[nome].get('foto_base64'):
            foto_b64 = clientes_salvos[nome]['foto_base64']
        
        if foto_b64:
            html = f'''
            <div style="display: flex; align-items: center; margin-bottom: 25px;">
                <img src="data:image/png;base64,{foto_b64}" style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; margin-right: 25px; border: 3px solid #F18617; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);">
                <h3 style="margin: 0; color: #FFFFFF; font-weight: bold;">{info_text}</h3>
            </div>
            '''
            st.markdown(html, unsafe_allow_html=True)
        else:
            html = f'''
            <div style="display: flex; align-items: center; margin-bottom: 25px;">
                <h3 style="margin: 0; color: #FFFFFF; font-weight: bold;">{info_text}</h3>
            </div>
            '''
            st.markdown(html, unsafe_allow_html=True)

        resultados = calcular_numerologia(nome, nascimento, data_atual)
        (expressao, motivacao, impressao, destino, dia_pessoal, mes_pess,
         ano_pess, missao, dividas_carmicas, licoes_carmicas,
         tendencias_ocultas, soma_tendencias, resposta_subconsciente,
         desafio1, desafio2, desafio_principal, ciclos_vida, momentos_decisivos,
         triangulo_base, triangulo_reps, arcano_atual_res, arcano_atual_periodo) = resultados

        estrutural, direcionamento, kan, rep1, rep2 = calcular_perfil_comportamental(
            expressao, motivacao, impressao, nascimento[0],
            destino, missao, ciclos_vida['ciclo2']['numero'], momentos_decisivos['momento3']['numero'],
            triangulo_base
        )

        dados = []
        def add_row(campo, valor):
            dados.append({"Campo": remover_acentos(campo), "Resultado": remover_acentos(valor)})

        # Helpers de extração e descrição
        num_dia_puro = nascimento[0]
        num_dia_reduzido = reduce_number(nascimento[0])

        def extract_num(s):
            if not s: return None
            try: return s.split(' - ')[0]
            except: return str(s)

        # Helper: campo com número no label + descrição separada
        def add_row_com_desc(campo, valor_str, categoria_mapa, valor_num):
            desc = get_desc_mapa(categoria_mapa, str(valor_num))
            if desc:
                # Campo recebe "NomeCampo - NUMERO" e Resultado recebe apenas a descrição
                add_row(f"{campo} - {valor_num}", desc)
            else:
                add_row(campo, valor_str)

        add_row_com_desc("Expressão", expressao, "Expressao", extract_num(expressao) if expressao else expressao)
        add_row_com_desc("Motivação", motivacao, "Motivacao", extract_num(motivacao) if motivacao else motivacao)
        add_row_com_desc("Impressão", impressao, "Impressao", extract_num(impressao) if impressao else impressao)
        add_row_com_desc("Destino", destino, "Destino", extract_num(destino) if destino else destino)
        add_row("Arcano Atual", f"{arcano_atual_res} | Período: {arcano_atual_periodo}")
        add_row("Triângulo da Vida (Base)", triangulo_base)
        add_row("Triângulo da Vida (Repetições)", triangulo_reps)
        add_row_com_desc("Dia Pessoal", dia_pessoal, "Dia Pessoal", extract_num(dia_pessoal) if dia_pessoal else dia_pessoal)
        add_row_com_desc("Mês Pessoal", mes_pess, "Mes Pessoal", extract_num(mes_pess) if mes_pess else mes_pess)
        add_row_com_desc("Ano Pessoal", ano_pess, "Ano Pessoal", extract_num(ano_pess) if ano_pess else ano_pess)
        add_row_com_desc("Missão", missao, "Missao", extract_num(missao) if missao else missao)

        # Dívidas Cármicas com descrições
        if dividas_carmicas:
            dividas_parts = []
            for d in dividas_carmicas:
                desc_d = get_desc_mapa("Divida Carmica", str(d))
                dividas_parts.append(f"{d}: {desc_d}" if desc_d else str(d))
            add_row("Dívidas Cármicas", ' | '.join(dividas_parts))
        else:
            add_row("Dívidas Cármicas", "Não há")

        # Lições Cármicas com descrições
        if licoes_carmicas:
            licoes_parts = []
            for l in licoes_carmicas:
                desc_l = get_desc_mapa("Licao Carmica", str(l))
                licoes_parts.append(f"{l}: {desc_l}" if desc_l else str(l))
            add_row("Lições Cármicas", ' | '.join(licoes_parts))
        else:
            add_row("Lições Cármicas", "Não há")

        # Tendências Ocultas com descrições
        if tendencias_ocultas:
            tend_parts = []
            for t in tendencias_ocultas:
                desc_t = get_desc_mapa("Tendencia Oculta", str(t))
                tend_parts.append(f"{t}: {desc_t}" if desc_t else str(t))
            add_row("Tendências Ocultas", ' | '.join(tend_parts))
            add_row("Soma das Tendências Ocultas", soma_tendencias)
        else:
            add_row("Tendências Ocultas", "Não há")

        # Resposta Subconsciente com descrição
        desc_resp = get_desc_mapa("Resposta Subconsciente", str(extract_num(resposta_subconsciente) if resposta_subconsciente else ""))
        add_row("Resposta Subconsciente", f"{resposta_subconsciente} | {desc_resp}" if desc_resp else resposta_subconsciente)

        # Dia Natalício com descrição (usa o dia bruto 1-31)
        desc_dia_nat = get_desc_mapa("Dia Natalicio", str(nascimento[0]))
        add_row("Dia Natalício", f"{nascimento[0]} | {desc_dia_nat}" if desc_dia_nat else str(nascimento[0]))

        add_row("1º Desafio", desafio1)
        add_row("2º Desafio", desafio2)
        add_row("Desafio Principal", desafio_principal)

        c1 = f"Nº {ciclos_vida['ciclo1']['numero']} ({ciclos_vida['ciclo1']['inicio']} a {ciclos_vida['ciclo1']['fim']})"
        c2 = f"Nº {ciclos_vida['ciclo2']['numero']} ({ciclos_vida['ciclo2']['inicio']} a {ciclos_vida['ciclo2']['fim']})"
        c3 = f"Nº {ciclos_vida['ciclo3']['numero']} (a partir de {ciclos_vida['ciclo3']['inicio']})"
        add_row("1º Ciclo de Vida", c1)
        add_row("2º Ciclo de Vida", c2)
        add_row("3º Ciclo de Vida", c3)

        m1 = f"Nº {momentos_decisivos['momento1']['numero']} ({momentos_decisivos['momento1']['inicio']} a {momentos_decisivos['momento1']['fim']})"
        m2 = f"Nº {momentos_decisivos['momento2']['numero']} ({momentos_decisivos['momento2']['inicio']} a {momentos_decisivos['momento2']['fim']})"
        m3 = f"Nº {momentos_decisivos['momento3']['numero']} ({momentos_decisivos['momento3']['inicio']} a {momentos_decisivos['momento3']['fim']})"
        m4 = f"Nº {momentos_decisivos['momento4']['numero']} (a partir de {momentos_decisivos['momento4']['inicio']})"
        add_row("1º Momento Decisivo", m1)
        add_row("2º Momento Decisivo", m2)
        add_row("3º Momento Decisivo", m3)
        add_row("4º Momento Decisivo", m4)

        # --- CÁLCULO DO SCORE PERFIL (Mover para antes das tabelas para incluir no Resultado) ---
        perfis_list = PERFIS_DB if PERFIS_DB else ["Lider", "Criativo", "Executor", "Resultado", "Vendedor", "Influenciador", "Comunicador"]
        colunas_score = ["Motivação", "Impressão", "Expressão", "Destino", "Missão", "Dia Natalício", "Triângulo", "No Psiquico", "Estrutural", "Direcionamento", "REPETIÇÃO 1", "REPETIÇÃO 2"]
        mapa_col_matriz = {"Motivação": "motivacao", "Impressão": "impressao", "Expressão": "expressao", "Destino": "destino", "Missão": "missao", "Dia Natalício": "dia_natalicio", "Triângulo": "triangulo", "No Psiquico": "no_psiquico"}
        

        valores_originais_score = {
            "Motivação": extract_num(motivacao), "Impressão": extract_num(impressao), "Expressão": extract_num(expressao), "Destino": extract_num(destino), "Missão": extract_num(missao),
            "Dia Natalício": num_dia_puro, "Triângulo": triangulo_base, "No Psiquico": num_dia_reduzido,
            "Estrutural": estrutural, "Direcionamento": direcionamento, "REPETIÇÃO 1": extract_num(rep1), "REPETIÇÃO 2": extract_num(rep2)
        }
        
        score_df_calc = pd.DataFrame(0, index=perfis_list, columns=colunas_score)
        for campo_s in colunas_score:
            val_s = valores_originais_score[campo_s]
            if val_s is None: continue
            perfil_enc = None
            if campo_s in mapa_col_matriz:
                row_m = MATRIZ_DB.get(str(val_s))
                if row_m:
                    attr_t = str(get_from_row(row_m, campo_s)).upper()
                    if attr_t:
                        ai = ATRIBUTOS_DB.get(attr_t)
                        if ai: perfil_enc = get_from_row(ai, 'perfil')
            else:
                ri = REPETICAO_DB.get(str(val_s))
                if ri: perfil_enc = get_from_row(ri, 'perfil')
            
            if perfil_enc:
                pn = str(perfil_enc).strip().capitalize()
                if pn in score_df_calc.index:
                    pv = PESO_DB.get(campo_s, 0)
                    score_df_calc.at[pn, campo_s] = int(pv)
        
        score_df_calc['TOTAL'] = score_df_calc.sum(axis=1)
        
        # --- CÁLCULO DO SCORE CATEGORIA ---
        lista_cat = LISTA_CATEGORIA_DB if LISTA_CATEGORIA_DB else ["Justo", "Inovador", "Diplomático", "Realizador", "Versátil", "Visionário", "Magnético", "Analítico", "Organizado", "Harmônico", "Comunicativo", "Intuitivo", "Conhecimento"]
        colunas_cat = ["Motivação", "Impressão", "Expressão", "Destino", "Missão", "Dia Natalício", "Triângulo", "No Psiquico", "Estrutural", "Direcionamento", "REPETIÇÃO 1", "REPETIÇÃO 2"]
        
        score_cat_df = pd.DataFrame(0, index=lista_cat, columns=colunas_cat)
        
        for campo_c in colunas_cat:
            val_c = valores_originais_score[campo_c]
            if val_c is None: continue
            
            cat_encontrada = None
            if campo_c in mapa_col_matriz:
                row_m_cat = MATRIZ_DB.get(str(val_c))
                if row_m_cat:
                    attr_t_cat = str(get_from_row(row_m_cat, campo_c)).upper()
                    if attr_t_cat:
                        ai_cat = ATRIBUTOS_DB.get(attr_t_cat)
                        if ai_cat: cat_encontrada = get_from_row(ai_cat, 'categoria')
            else:
                ri_cat = REPETICAO_DB.get(str(val_c))
                if ri_cat: cat_encontrada = get_from_row(ri_cat, 'categoria')
                
            if cat_encontrada:
                cn = str(cat_encontrada).strip().capitalize()
                if cn in score_cat_df.index:
                    pv_cat = PESO_CATEGORIA_DB.get(campo_c, 0)
                    score_cat_df.at[cn, campo_c] = int(pv_cat)
                    
        score_cat_df['TOTAL'] = score_cat_df.sum(axis=1)
        
        # Identificar categoria Dia Natalício
        cat_dia_natalicio = ""
        val_dia_natalicio = valores_originais_score["Dia Natalício"]
        row_dia = MATRIZ_DB.get(str(val_dia_natalicio))
        if row_dia:
            attr_dia = str(get_from_row(row_dia, 'Dia Natalício')).upper()
            if attr_dia:
                ai_dia = ATRIBUTOS_DB.get(attr_dia)
                if ai_dia: cat_dia_natalicio = str(get_from_row(ai_dia, 'categoria') or "").strip().capitalize()
                
        # --- CÁLCULO DO SCORE QUALIDADES ---
        lista_qual = list(QUALIDADES_DB.keys()) if QUALIDADES_DB else ["Relacionamento", "Execução", "Análise", "Coletividade", "Justiça", "Praticidade e disciplina", "Comunicação", "Versatilidade", "Intuição", "Organização", "Serviço"]
        colunas_qual = ["Motivação", "Impressão", "Expressão", "Destino", "Missão", "Dia Natalício", "Triângulo", "No Psiquico", "Estrutural", "Direcionamento", "REPETIÇÃO 1", "REPETIÇÃO 2"]
        
        score_qual_df = pd.DataFrame(0, index=lista_qual, columns=colunas_qual)
        
        for campo_q in colunas_qual:
            val_q = valores_originais_score[campo_q]
            if val_q is None: continue
            
            qual_encontrada = None
            if campo_q in mapa_col_matriz:
                row_m_q = MATRIZ_DB.get(str(val_q))
                if row_m_q:
                    attr_t_q = str(get_from_row(row_m_q, campo_q)).upper()
                    if attr_t_q:
                        ai_q = ATRIBUTOS_DB.get(attr_t_q)
                        if ai_q:
                            qual_encontrada = get_from_row(ai_q, 'qualidade') or get_from_row(ai_q, 'area de suporte')
            else:
                ri_q = REPETICAO_DB.get(str(val_q))
                if ri_q:
                    qual_encontrada = get_from_row(ri_q, 'qualidade') or get_from_row(ri_q, 'area de suporte')
                
            if qual_encontrada:
                qn = remover_acentos(str(qual_encontrada).strip()).upper()
                # Busca insensível a maiúsculas/minúsculas e acentos no index
                for idx_name in score_qual_df.index:
                    if remover_acentos(idx_name).upper() == qn:
                        score_qual_df.at[idx_name, campo_q] += 50
                        break
                    
        score_qual_df['TOTAL'] = score_qual_df.sum(axis=1)
        
        # --- FIM DO CÁLCULO DO SCORE PERFIL, CATEGORIA E QUALIDADES ---

        dados_perfil = []
        def add_row_perfil_split(campo, valor, descricao):
            # Texto limpo para o PDF (sem HTML)
            desc_limpa = descricao.replace("<b>", "").replace("</b>", "").replace("<br>", " | ")
            dados_perfil.append({
                "Campo": campo,
                "Valor": valor,
                "Descricao": descricao,
                "Resultado": f"{valor} - {desc_limpa}" if desc_limpa else valor
            })
            
        k_data = KAN_DB.get(str(kan), {"kan": str(kan), "descricao": ""})
        add_row_perfil_split("KAN", k_data['kan'], k_data['descricao'])
        
        # Perfil
        val_corte = st.session_state.get('score_perfil_corte_slider', 1.8)
        totais_s = score_df_calc['TOTAL'].sort_values(ascending=False)
        totais_s = totais_s[totais_s > 0]
        perfis_escolhidos = []
        if not totais_s.empty:
            max_score = totais_s.iloc[0]
            for p, s in totais_s.items():
                if max_score / s <= val_corte:
                    perfis_escolhidos.append(p)
                else:
                    break
        
        perfil_val = ", ".join(perfis_escolhidos)
        perfil_desc_list = []
        for p in perfis_escolhidos:
            # Busca insensível para Perfil
            d = ""
            pn = remover_acentos(p).upper()
            for k_desc, v_desc in PERFIL_DESCRICAO_DB.items():
                if remover_acentos(k_desc).upper() == pn:
                    d = v_desc
                    break
            if d: perfil_desc_list.append(d)
        
        add_row_perfil_split("Perfil", perfil_val, "<br><br>".join(perfil_desc_list) if perfil_desc_list else "")
        
        # Categoria
        modo_corte_cat = st.session_state.get('corte_categoria_modo', 'Calculo')
        if modo_corte_cat == 'Dia Natalicio':
            categoria_selecionada = cat_dia_natalicio
        else:
            totais_cat = score_cat_df['TOTAL'].sort_values(ascending=False)
            totais_cat = totais_cat[totais_cat > 0]
            categoria_selecionada = totais_cat.index[0] if not totais_cat.empty else ""
            
        # Busca insensível para Categoria
        cat_desc = ""
        cn = remover_acentos(categoria_selecionada).upper()
        for k_desc, v_desc in CATEGORIA_DESCRICAO_DB.items():
            if remover_acentos(k_desc).upper() == cn:
                cat_desc = v_desc
                break
                
        add_row_perfil_split("Categoria", categoria_selecionada, cat_desc)
        
        # Diferenciais (11 e 22)
        campos_para_dif = [
            extract_num(motivacao), extract_num(impressao), extract_num(expressao),
            extract_num(destino), extract_num(missao), str(nascimento[0]),
            str(triangulo_base), str(num_dia_reduzido)
        ]
        
        diferenciais_ativos = []
        dif_desc_list = []
        
        # Verifica 11
        if "11" in campos_para_dif:
            d11 = DIFERENCIAIS_DESC_DB.get("11")
            if d11:
                diferenciais_ativos.append(d11['diferencial'])
                dif_desc_list.append(f"<b>{d11['diferencial']}</b>: {d11['descricao']}")
        
        # Verifica 22
        if "22" in campos_para_dif:
            d22 = DIFERENCIAIS_DESC_DB.get("22")
            if d22:
                diferenciais_ativos.append(d22['diferencial'])
                dif_desc_list.append(f"<b>{d22['diferencial']}</b>: {d22['descricao']}")
                
        if diferenciais_ativos:
            add_row_perfil_split("Diferenciais", ", ".join(diferenciais_ativos), "<br><br>".join(dif_desc_list))
        
        # Novo Campo: Qualidades
        totais_q = score_qual_df['TOTAL'].sort_values(ascending=False)
        totais_q = totais_q[totais_q > 0]
        qualidades_escolhidas = list(totais_q.index)
        
        qual_val = ", ".join(qualidades_escolhidas)
        qual_desc_list = []
        for q in qualidades_escolhidas:
            # Busca insensível para Qualidades
            d = ""
            qn = remover_acentos(q).upper()
            for k_desc, v_desc in QUALIDADES_DB.items():
                if remover_acentos(k_desc).upper() == qn:
                    d = v_desc
                    break
            if d: qual_desc_list.append(f"<b>{q}</b>: {d}")
            
        add_row_perfil_split("Qualidades", qual_val, "<br>".join(qual_desc_list) if qual_desc_list else "")
        
        # --- NOVO: DIAGNÓSTICO COM IA (GEMINI) ---
        if "ai_diagnosis" not in st.session_state:
            st.session_state["ai_diagnosis"] = {}

        user_name_key = f"diag_{nome}"
        
        # Se já existir um diagnóstico salvo para este nome na sessão ou no carregamento do banco, usamos ele
        desc_diag = st.session_state["ai_diagnosis"].get(user_name_key)
        if not desc_diag and clientes_salvos.get(nome):
            desc_diag = clientes_salvos[nome].get('ai_diagnosis')
        
        if not desc_diag:
            desc_diag = "Clique no botão ao final da página para gerar o Diagnóstico com Inteligência Artificial."
        
        add_row_perfil_split("Diagnóstico", "Análise de Performance", desc_diag)
        
        f_data = FORTALEZAS_DB.get(str(triangulo_base), {"fortaleza": "Não Encontrado", "descricao": ""})
        add_row_perfil_split("Fortaleza", f_data['fortaleza'], f_data['descricao'])
        
        d_data = DESAFIOS_DB.get(str(nascimento[0]), {"desafio": "Não Encontrado", "descricao": ""})
        add_row_perfil_split("Desafio", d_data['desafio'], d_data['descricao'])

        if cliente_selecionado == "-- Novo Cliente --" and (submit_mapa or submit_perfil) and supabase_client:
            try:
                mapa_json = json.dumps(dados, ensure_ascii=False)
                perfil_json = json.dumps(dados_perfil, ensure_ascii=False)
                data_str_to_save = data_input.strftime('%d/%m/%Y')
                
                agora_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                usuario_logado = st.session_state.get("username", "Desconhecido")
                
                insert_data = {
                    "nome": nome,
                    "data_nascimento": data_str_to_save,
                    "cargo": cargo,
                    "empresa": empresa,
                    "linkedin_url": linkedin,
                    "experiencias": experiencias,
                    "usuario": usuario_logado,
                    "data_inclusao": agora_str,
                    "mapa_json": mapa_json,
                    "perfil_json": perfil_json
                }
                if nome in st.session_state['fotos']:
                    import base64
                    insert_data["foto_base64"] = base64.b64encode(st.session_state['fotos'][nome]).decode()
                    
                supabase_client.table("mapas_salvos").insert(insert_data).execute()
                st.toast("✅ Cálculos salvos automaticamente na nuvem!")
                
                clientes_salvos[nome] = {
                    'data_nascimento': data_str_to_save,
                    'cargo': cargo,
                    'empresa': empresa,
                    'foto_base64': insert_data.get('foto_base64', '')
                }
            except Exception as e:
                st.toast(f"⚠️ Erro ao salvar automaticamente: {e}")

            # --- Tabela do Mapa em HTML customizado ---
            st.markdown("""
            <style>
            .mapa-table { width: 100%; border-collapse: collapse; margin-top: 10px; background: rgba(255,255,255,0.05); }
            .mapa-table th { background-color: #F18617; color: #401041; padding: 10px 14px; text-align: left; font-size: 0.95em; }
            .mapa-table td { border: 1px solid rgba(255,255,255,0.1); vertical-align: top; padding: 0; }
            .mapa-campo { color: #F18617; font-weight: bold; padding: 10px 14px; white-space: nowrap; font-size: 0.9em; }
            .mapa-numero { display: inline-block; background: #F18617; color: #401041;
                           font-weight: bold; font-size: 1.1em; padding: 1px 8px;
                           border-radius: 4px; margin-left: 6px; }
            .mapa-desc { padding: 10px 14px; color: #FFFFFF; font-size: 0.88em;
                         line-height: 1.45; text-align: justify; }
            .mapa-valor { padding: 10px 14px; color: #FFFFFF; font-size: 0.95em; }
            </style>
            """, unsafe_allow_html=True)

            html_mapa = '<table class="mapa-table"><thead><tr><th style="width:18%">Campo</th><th>Resultado</th></tr></thead><tbody>'
            for item in dados:
                campo_raw = item['Campo']
                resultado_raw = item['Resultado']

                # Detecta se o campo tem número embutido (ex: "Expressao - 1")
                if ' - ' in campo_raw:
                    partes_campo = campo_raw.rsplit(' - ', 1)
                    label_campo = partes_campo[0]
                    numero_badge = f"<span class='mapa-numero'>{partes_campo[1]}</span>"
                else:
                    label_campo = campo_raw
                    numero_badge = ""

                # Célula da descrição
                if resultado_raw:
                    cel_resultado = f"<div class='mapa-desc'>{resultado_raw}</div>"
                else:
                    cel_resultado = "<div class='mapa-valor'></div>"

                html_mapa += (
                    f"<tr>"
                    f"<td><div class='mapa-campo'>{label_campo}{numero_badge}</div></td>"
                    f"<td>{cel_resultado}</td>"
                    f"</tr>"
                )
            html_mapa += "</tbody></table>"
            st.markdown(html_mapa, unsafe_allow_html=True)

            st.markdown("---")
            st.subheader("Salvar Resultados do Mapa")
            col1, col2 = st.columns(2)
            nome_limpo = remover_acentos(nome).replace(' ', '_')
            df = pd.DataFrame(dados)
            
            with col1:
                csv = df.to_csv(sep=';', index=False).encode('utf-8')
                st.download_button("📥 Baixar Mapa como CSV", data=csv, file_name=f"mapa_{nome_limpo}.csv", mime="text/csv", key="dl_mapa_csv")
            with col2:
                data_str_pdf = data_input.strftime('%d/%m/%Y')
                pdf_bytes = gerar_pdf(nome, data_str_pdf, dados, titulo="Mapa Numerologico Cabalistico")
                st.download_button("📄 Baixar Mapa como PDF", data=pdf_bytes, file_name=f"mapa_{nome_limpo}.pdf", mime="application/pdf", key="dl_mapa_pdf")

            if st.session_state.get('show_perfil'):
                st.markdown("---")
                st.subheader("Perfil Comportamental")
                
                # Injeta Estilo Separado
                st.markdown("""<style>
                .perfil-custom-table { width: 100%; border-collapse: collapse; margin-top: 10px; background: rgba(255,255,255,0.05); }
                .perfil-custom-table th { background-color: #F18617; color: #401041; padding: 12px; text-align: left; }
                .perfil-custom-table td { border: 1px solid rgba(255,255,255,0.1); vertical-align: top; padding: 0; }
                .p-label { color: #F18617; font-weight: bold; padding: 12px; }
                .p-value { background-color: #F18617; color: #401041; padding: 6px; font-weight: bold; text-align: center; }
                .p-desc { padding: 12px; color: #FFFFFF; font-size: 0.95em; line-height: 1.5; }
                </style>""", unsafe_allow_html=True)
                
                # Constrói Tabela
                html_table = '<table class="perfil-custom-table"><thead><tr><th>Campo</th><th>Resultado</th></tr></thead><tbody>'
                for item in dados_perfil:
                    html_table += f"<tr><td style='width: 25%;'><div class='p-label'>{item['Campo']}</div></td>"
                    html_table += f"<td><div class='p-value'>{item['Valor']}</div><div class='p-desc'>{item['Descricao']}</div></td></tr>"
                html_table += "</tbody></table>"
                
                st.markdown(html_table, unsafe_allow_html=True)
            
            # Botão para Gerar Diagnóstico com IA
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🪄 Gerar Diagnóstico Profissional com IA"):
                try:
                    api_key = st.secrets["gemini"]["api_key"]
                    genai.configure(api_key=api_key)
                    
                    # Montar o contexto para a IA
                    info_prof = f"- LinkedIn: {linkedin}\n- Experiências: {experiencias}" if (linkedin or experiencias) else ""
                    contexto = f"""
                    Analise o perfil de {nome}:
                    - KAN: {k_data['kan']} ({k_data['descricao']})
                    - Perfil: {perfil_val}
                    - Categoria: {categoria_selecionada} ({cat_desc})
                    - Qualidades: {qual_val}
                    {info_prof}
                    
                    Gere um diagnóstico realista e direto em 3 parágrafos curtos.
                    """
                    
                    with st.spinner("Analisando perfil..."):
                        model = genai.GenerativeModel('models/gemini-2.5-flash')
                        response = model.generate_content(contexto)
                        texto_ia = response.text.replace("\n", "<br>")
                        st.session_state["ai_diagnosis"][user_name_key] = texto_ia
                        
                        if supabase_client:
                            supabase_client.table("mapas_salvos").update({"ai_diagnosis": texto_ia}).eq("nome", nome).execute()
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro na IA: {e}")

            # Exibe o consumo de tokens se houver
            if "ai_usage" in st.session_state:
                st.caption(f"📊 {st.session_state['ai_usage']}")

            st.markdown("---")
            st.subheader("Salvar Perfil Comportamental")
            col_p1, col_p2 = st.columns(2)
            df_perfil = pd.DataFrame(dados_perfil)
            nome_limpo_p = remover_acentos(nome).replace(' ', '_')
            with col_p1:
                csv_p = df_perfil.to_csv(sep=';', index=False).encode('utf-8')
                st.download_button("📥 Baixar Perfil como CSV", data=csv_p, file_name=f"perfil_{nome_limpo_p}.csv", mime="text/csv", key="dl_p_csv")
            with col_p2:
                pdf_p = gerar_pdf(nome, data_str, dados_perfil, titulo="Perfil Comportamental KAN")
                st.download_button("📄 Baixar Perfil como PDF", data=pdf_p, file_name=f"perfil_{nome_limpo_p}.pdf", mime="application/pdf", key="dl_p_pdf")

            # --- EXIBIÇÃO DOS SCORES TÉCNICOS ---
            with st.expander("📊 Ver Scores Técnicos (Auditoria)", expanded=False):
                st.header("Score Perfil")
                st.slider("Corte Perfil", 1.0, 2.0, 1.8, 0.1, key="score_perfil_corte_slider")
                st.table(score_df_calc)
                
                st.header("Score Categoria")
                st.selectbox("Corte Categoria", ["Dia Natalicio", "Calculo"], index=1 if modo_corte_cat == 'Calculo' else 0, key="corte_categoria_modo")
                st.table(score_cat_df)
                
                st.header("Score Qualidades")
                st.table(score_qual_df)


elif (submit_mapa or submit_perfil) and not nome:
    st.error("Por favor, digite seu nome completo para calcular!")

# --- RODAPÉ ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("---")
col_footer1, col_footer2 = st.columns([1, 8])

try:
    footer_img = Image.open(os.path.join("images", "logo_mundo_kan_peq_neg2.png"))
    with col_footer1:
        st.image(footer_img)
except Exception:
    pass

with col_footer2:
    st.markdown("<p style='color: white; font-size: 12px; margin: 0; padding-top: 15px;'>Todos os direitos reservados para mundokan. Metodologia exclusiva registrada.</p>", unsafe_allow_html=True)
