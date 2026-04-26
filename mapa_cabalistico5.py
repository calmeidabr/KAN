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

try:
    favicon_img = Image.open(os.path.join("images", "ico_k.png"))
except Exception:
    favicon_img = "🔮"

try:
    header_img = Image.open(os.path.join("images", "kan_logo_lar.png"))
except Exception:
    header_img = "🔮"

st.set_page_config(page_title="Mapa Cabalístico", page_icon=favicon_img, layout="centered")

st.markdown("""
<style>
/* Força o fundo branco e texto escuro nos inputs para bater com a arte */
div[data-baseweb="input"] > div {
    background-color: #FFFFFF !important;
    border-radius: 6px !important;
}
div[data-baseweb="input"] input {
    color: #000000 !important;
}
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border-radius: 6px !important;
}
div[data-baseweb="select"] span {
    color: #000000 !important;
}
/* Cor laranja para a coluna Campo nas tabelas */
table tbody th {
    color: #F18617 !important;
}
/* Cabeçalho das tabelas com fundo laranja e texto lilás/roxo */
table thead th {
    background-color: #F18617 !important;
    color: #401041 !important;
    font-weight: bold !important;
}
/* Congelar primeira coluna (Index) das tabelas ao rolar para a direita */
div[data-testid="stTable"] {
    overflow-x: auto !important;
}
table thead th:first-child {
    position: sticky !important;
    left: 0;
    z-index: 3 !important;
    background-color: #F18617 !important;
}
table tbody th:first-child {
    position: sticky !important;
    left: 0;
    z-index: 2 !important;
    background-color: #401041 !important; /* Cor roxa do fundo */
    border-right: 2px solid #F18617 !important;
}
</style>
""", unsafe_allow_html=True)

# --- CACHED FETCH ---
@st.cache_data(ttl=3600)
def fetch_arcanos():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase_client: Client = create_client(url, key)
        resp = supabase_client.table("arcanos").select("*").execute()
        return {str(int(row['numero'])): {"nome": row['nome'], "descricao": row['descricao']} for row in resp.data if row.get('numero')}
    except Exception:
        return {}

ARCANOS_DB = fetch_arcanos()

@st.cache_data(ttl=3600)
def fetch_fortalezas():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase_client: Client = create_client(url, key)
        resp = supabase_client.table("fortalezas").select("*").execute()
        return {str(int(row['triangulo'])): {"fortaleza": row['fortaleza'], "descricao": row['descricao']} for row in resp.data if row.get('triangulo')}
    except Exception:
        return {}

FORTALEZAS_DB = fetch_fortalezas()

@st.cache_data(ttl=3600)
def fetch_kan():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase_client: Client = create_client(url, key)
        resp = supabase_client.table("kans").select("*").execute()
        return {str(int(row['numero'])): {"kan": row['kan'], "descricao": row['descricao']} for row in resp.data if row.get('numero')}
    except Exception:
        return {}

KAN_DB = fetch_kan()

@st.cache_data(ttl=3600)
def fetch_desafios():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase_client: Client = create_client(url, key)
        resp = supabase_client.table("desafios").select("*").execute()
        return {str(int(row['dia_nascimento'])): {"desafio": row['desafio'], "descricao": row['descricao']} for row in resp.data if row.get('dia_nascimento')}
    except Exception:
        return {}

DESAFIOS_DB = fetch_desafios()

@st.cache_data(ttl=3600)
def fetch_matriz():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase_client: Client = create_client(url, key)
        resp = supabase_client.table("matriz").select("*").execute()
        return {str(row['resultado']): row for row in resp.data}
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
        return {row['atributo'].upper(): row for row in resp.data}
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
        return {str(int(row['repeticao'])): row for row in resp.data}
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
        return {row['perfil'].strip().capitalize(): row['descricao'] for row in resp.data}
    except Exception:
        return {}

PERFIL_DESCRICAO_DB = fetch_perfil_descricao()

@st.cache_data(ttl=3600)
def fetch_lista_categoria():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase_client: Client = create_client(url, key)
        resp = supabase_client.table("lista_categoria").select("*").execute()
        return [row['categoria'] for row in resp.data]
    except Exception:
        return []

LISTA_CATEGORIA_DB = fetch_lista_categoria()

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



def remover_acentos(texto):
    texto_str = str(texto).replace('º', 'o').replace('ª', 'a')
    texto_str = texto_str.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'").replace('–', '-').replace('—', '-')
    norm = ''.join(c for c in unicodedata.normalize('NFD', texto_str) if unicodedata.category(c) != 'Mn')
    return norm.encode('latin-1', 'ignore').decode('latin-1')

def gerar_pdf(nome, data_nasc_str, dados, titulo="Mapa Numerologico Cabalistico"):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, remover_acentos(titulo), ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 8, f"Nome: {remover_acentos(nome)}", ln=True)
    pdf.cell(190, 8, f"Data de Nascimento: {data_nasc_str}", ln=True)
    pdf.ln(5)
    
    col1 = 65
    col2 = 125
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(col1, 8, "Campo", 1)
    pdf.cell(col2, 8, "Resultado", 1, 1)
    
    for row in dados:
        campo = str(row['Campo'])
        resultado = str(row['Resultado'])
        
        if len(resultado) > 55:
            pdf.set_font("Arial", '', 7)
        elif len(resultado) > 40:
            pdf.set_font("Arial", '', 8)
        else:
            pdf.set_font("Arial", '', 10)
            
        pdf.cell(col1, 8, campo, 1)
        pdf.cell(col2, 8, resultado, 1, 1)
        
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

    if "password_correct" not in st.session_state:
        render_login_header()
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password")
        st.button("Entrar", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        render_login_header()
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password")
        st.button("Entrar", on_click=password_entered)
        st.error("Usuário ou senha incorretos. Tente novamente.")
        return False
    else:
        return True

if not check_password():
    st.stop()

if header_img != "🔮":
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image(header_img, use_container_width=True)
    with col2:
        st.title("Mapa e Perfil Comportamental")
else:
    st.title("Mapa e Perfil Comportamental")
st.markdown("Descubra a sua potencialidade.")

# --- FETCH CLIENTES DO BANCO DE DADOS ---
clientes_salvos = {}
supabase_client = None
try:
    from supabase import create_client, Client
    url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
    key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
    supabase_client: Client = create_client(url, key)
    
    response = supabase_client.table("mapas_salvos").select("*").execute()
    for row in response.data:
        clientes_salvos[row['nome']] = {
            'data_nascimento': row['data_nascimento'],
            'cargo': row.get('cargo', ''),
            'empresa': row.get('empresa', ''),
            'foto_base64': row.get('foto_base64', '')
        }
except Exception:
    pass

opcoes_clientes = ["-- Novo Cliente --"] + sorted(list(clientes_salvos.keys()))
cliente_selecionado = st.selectbox("Selecione um nome já cadastrado ou crie um novo:", opcoes_clientes)

if 'fotos' not in st.session_state:
    st.session_state['fotos'] = {}

submit_mapa = False
submit_perfil = False

if cliente_selecionado == "-- Novo Cliente --":
    with st.form("numerologia_form"):
        nome = st.text_input("Digite o seu nome completo, como se escreve, idêntico ao que consta na sua certidão de nascimento (incluir acentos e números se houver).")
        data_str_input = st.text_input("Data de Nascimento (dd/mm/yyyy):", placeholder="Ex: 25/12/1980")
        
        col_cargo, col_empresa = st.columns(2)
        with col_cargo:
            cargo = st.text_input("Cargo/Profissão:")
        with col_empresa:
            empresa = st.text_input("Empresa/Grupo:")
            
        foto_upload = st.file_uploader("Foto da Pessoa (Opcional)", type=["png", "jpg", "jpeg"])
        
        col1, col2 = st.columns(2)
        with col1:
            submit_mapa = st.form_submit_button("Calcular Mapa Numerológico")
        with col2:
            submit_perfil = st.form_submit_button("Calcular Perfil Comportamental")
            
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
        
    st.session_state['show_mapa'] = True
    st.session_state['show_perfil'] = True

if (st.session_state.get('show_mapa') or st.session_state.get('show_perfil')) and nome:
    hoje = datetime.date.today()
    data_atual = (hoje.day, hoje.month, hoje.year)
    nascimento = (data_input.day, data_input.month, data_input.year)
    
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

    add_row("Expressão", expressao)
    add_row("Motivação", motivacao)
    add_row("Impressão", impressao)
    add_row("Destino", destino)
    add_row("Arcano Atual", f"{arcano_atual_res} | Período: {arcano_atual_periodo}")
    add_row("Triângulo da Vida (Base)", triangulo_base)
    add_row("Triângulo da Vida (Repetições)", triangulo_reps)
    add_row("Dia Pessoal", dia_pessoal)
    add_row("Mês Pessoal", mes_pess)
    add_row("Ano Pessoal", ano_pess)
    add_row("Missão", missao)

    dividas_str = ', '.join(str(d) for d in dividas_carmicas) if dividas_carmicas else "Não há"
    add_row("Dívidas Cármicas", dividas_str)

    licoes_str = ', '.join(str(l) for l in licoes_carmicas) if licoes_carmicas else "Não há"
    add_row("Lições Cármicas", licoes_str)

    tendencias_str = ', '.join(str(t) for t in tendencias_ocultas) if tendencias_ocultas else "Não há"
    add_row("Tendências Ocultas", tendencias_str)

    if tendencias_ocultas:
        add_row("Soma das Tendências Ocultas", soma_tendencias)

    add_row("Resposta Subconsciente", resposta_subconsciente)
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
    
    num_dia_puro = nascimento[0]
    num_dia_reduzido = reduce_number(nascimento[0])
    def extract_num(s):
        if not s: return None
        try: return s.split(' - ')[0]
        except: return str(s)
        
    valores_originais_score = {
        "Motivação": motivacao, "Impressão": impressao, "Expressão": expressao, "Destino": destino, "Missão": missao,
        "Dia Natalício": num_dia_puro, "Triângulo": triangulo_base, "No Psiquico": num_dia_reduzido,
        "Estrutural": estrutural, "Direcionamento": direcionamento, "REPETIÇÃO 1": extract_num(rep1), "REPETIÇÃO 2": extract_num(rep2)
    }
    
    score_df_calc = pd.DataFrame(0, index=perfis_list, columns=colunas_score)
    for campo_s in colunas_score:
        val_s = valores_originais_score[campo_s]
        if val_s is None: continue
        perfil_enc = None
        if campo_s in mapa_col_matriz:
            col_m = mapa_col_matriz[campo_s]
            row_m = MATRIZ_DB.get(str(val_s))
            if row_m:
                attr_t = str(row_m.get(col_m, "")).upper()
                if attr_t:
                    ai = ATRIBUTOS_DB.get(attr_t)
                    if ai: perfil_enc = ai.get('perfil')
        else:
            ri = REPETICAO_DB.get(str(val_s))
            if ri: perfil_enc = ri.get('perfil')
        
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
        # Consulta via Matriz -> Atributos (coluna categoria)
        col_m_cat = mapa_col_matriz.get(campo_c)
        if col_m_cat:
            row_m_cat = MATRIZ_DB.get(str(val_c))
            if row_m_cat:
                attr_t_cat = str(row_m_cat.get(col_m_cat, "")).upper()
                if attr_t_cat:
                    ai_cat = ATRIBUTOS_DB.get(attr_t_cat)
                    if ai_cat: cat_encontrada = ai_cat.get('categoria')
        else:
            # Estrutural / Direcionamento
            ri_cat = REPETICAO_DB.get(str(val_c))
            if ri_cat: cat_encontrada = ri_cat.get('categoria')
            
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
        attr_dia = str(row_dia.get('dia_natalicio', "")).upper()
        if attr_dia:
            ai_dia = ATRIBUTOS_DB.get(attr_dia)
            if ai_dia: cat_dia_natalicio = str(ai_dia.get('categoria', "")).strip().capitalize()
            
    # Lógica de seleção de categoria (será finalizada abaixo com o widget)
    # --- FIM DO CÁLCULO DO SCORE PERFIL E CATEGORIA ---

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
        
    k_data = KAN_DB.get(str(kan), {"kan": "Não Encontrado", "descricao": ""})
    add_row_perfil_split("KAN", str(kan), f"{k_data['kan']} - {k_data['descricao']}" if k_data['descricao'] else k_data['kan'])
    
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
        d = PERFIL_DESCRICAO_DB.get(p, "")
        if d: perfil_desc_list.append(f"<b>{p}</b>: {d}")
    
    add_row_perfil_split("Perfil", perfil_val, "<br>".join(perfil_desc_list) if perfil_desc_list else "")
    
    # Categoria
    modo_corte_cat = st.session_state.get('corte_categoria_modo', 'Calculo')
    if modo_corte_cat == 'Dia Natalicio':
        categoria_selecionada = cat_dia_natalicio
    else:
        totais_cat = score_cat_df['TOTAL'].sort_values(ascending=False)
        totais_cat = totais_cat[totais_cat > 0]
        categoria_selecionada = totais_cat.index[0] if not totais_cat.empty else ""
        
    add_row_perfil_split("Categoria", categoria_selecionada, "")
    
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
            
            # Update cache to show in dropdown immediately
            clientes_salvos[nome] = {
                'data_nascimento': data_str_to_save,
                'cargo': cargo,
                'empresa': empresa,
                'foto_base64': insert_data.get('foto_base64', '')
            }
        except Exception as e:
            st.toast(f"⚠️ Erro ao salvar automaticamente: {e}")

    if st.session_state.get('show_mapa'):
        st.subheader("Mapa")
        df = pd.DataFrame(dados)
        st.table(df.set_index('Campo'))

        st.markdown("---")
        st.subheader("Salvar Resultados do Mapa")
        col1, col2 = st.columns(2)

        nome_limpo = remover_acentos(nome).replace(' ', '_')
        
        with col1:
            csv = df.to_csv(sep=';', index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar Mapa como CSV",
                data=csv,
                file_name=f"mapa_cabalistico_{nome_limpo}.csv",
                mime="text/csv",
            )

        with col2:
            data_str = data_input.strftime('%d/%m/%Y')
            pdf_bytes = gerar_pdf(nome, data_str, dados, titulo="Mapa Numerologico Cabalistico")
            st.download_button(
                label="📄 Baixar Mapa como PDF",
                data=pdf_bytes,
                file_name=f"mapa_cabalistico_{nome_limpo}.pdf",
                mime="application/pdf",
            )

    if st.session_state.get('show_perfil'):
        st.subheader("Perfil Comportamental")
        
        # Renderização Customizada com Divisão de Célula (Valor Laranja / Descrição)
        html_perfil = """<style>
.perfil-custom-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
.perfil-custom-table th { background-color: #F18617; color: #401041; padding: 10px; text-align: left; }
.perfil-custom-table td { border: 1px solid rgba(255,255,255,0.1); vertical-align: top; padding: 0; }
.p-label { color: #F18617; font-weight: bold; padding: 10px; }
.p-value { background-color: #F18617; color: #401041; padding: 5px; font-weight: bold; text-align: center; }
.p-desc { padding: 10px; color: white; font-size: 0.95em; line-height: 1.4; }
</style>
<table class="perfil-custom-table">
<thead><tr><th>Campo</th><th>Resultado</th></tr></thead>
<tbody>"""
        for item in dados_perfil:
            html_perfil += f"""<tr>
<td style="width: 25%;"><div class="p-label">{item['Campo']}</div></td>
<td>
<div class="p-value">{item['Valor']}</div>
<div class="p-desc">{item['Descricao']}</div>
</td>
</tr>"""
        html_perfil += "</tbody></table>"
        st.markdown(html_perfil, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Salvar Perfil Comportamental")
        col1, col2 = st.columns(2)

        nome_limpo = remover_acentos(nome).replace(' ', '_')
        
        df_perfil = pd.DataFrame(dados_perfil)
        with col1:
            csv_perfil = df_perfil.to_csv(sep=';', index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar Perfil como CSV",
                data=csv_perfil,
                file_name=f"perfil_comportamental_{nome_limpo}.csv",
                mime="text/csv",
            )

        with col2:
            data_str = data_input.strftime('%d/%m/%Y')
            pdf_bytes_perfil = gerar_pdf(nome, data_str, dados_perfil, titulo="Perfil Comportamental KAN")
            st.download_button(
                label="📄 Baixar Perfil como PDF",
                data=pdf_bytes_perfil,
                file_name=f"perfil_comportamental_{nome_limpo}.pdf",
                mime="application/pdf",
            )

        # --- SCORE PERFIL (Exibição da Tabela) ---
        st.markdown("---")
        st.header("Score Perfil")
        
        # O slider agora controla o resultado em tempo real (st.rerun acontece no fundo)
        corte = st.slider("Corte", 1.0, 2.0, 1.8, 0.1, key="score_perfil_corte_slider")
        
        # Usar o DataFrame já calculado anteriormente
        st.table(score_df_calc)
        
        # Resultado Final (já calculado para a tabela principal, mas exibimos aqui também)
        st.subheader("Resultado Final do Perfil")
        final_res_df = pd.DataFrame([", ".join(perfis_escolhidos)], columns=["Perfis Identificados"], index=["Perfil"])
        st.table(final_res_df)

        # --- SCORE CATEGORIA ---
        st.markdown("---")
        st.header("Score Categoria")
        
        corte_cat = st.selectbox("Corte (Categoria)", ["Dia Natalicio", "Calculo"], 
                               index=1 if modo_corte_cat == 'Calculo' else 0,
                               key="corte_categoria_modo")
        
        st.table(score_cat_df)
        
        st.subheader("Categoria Selecionada")
        final_cat_df = pd.DataFrame([categoria_selecionada], columns=["Categoria"], index=["Resultado"])
        st.table(final_cat_df)


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
