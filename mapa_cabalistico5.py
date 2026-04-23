import streamlit as st
import pandas as pd
import datetime
import unicodedata
from collections import Counter

st.set_page_config(page_title="Mapa Cabalístico", page_icon="🔮", layout="centered")

def calcular_numeros_nome(nome_completo):
    nome = nome_completo.upper().replace(' ', '')
    expressao_total = sum(letter_values.get(ch, 0) for ch in nome)
    vogais = set('AEIOUÀÁÂÃÄÅÆÉÈÊËÍÎÏÓÒÔÕÖÚÙÛÜ')
    motivacao_total = sum(letter_values.get(ch, 0) for ch in nome if ch in vogais)
    consoantes_total = sum(letter_values.get(ch, 0) for ch in nome if ch not in vogais)

    return (reduce_number(expressao_total), reduce_number(motivacao_total), reduce_number(consoantes_total),
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
    if mes == 11:
        ciclo1_num = 11
    else:
        ciclo1_num = reduce_number(mes)
    ciclo1_ano_inicio = ano
    ciclo1_periodo_anos = 37 - destino
    ciclo1_ano_fim = ciclo1_ano_inicio + ciclo1_periodo_anos
    
    if dia in [11, 22]:
        ciclo2_num = dia
    else:
        ciclo2_num = reduce_number(dia)
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
    return reduce_number(total)

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

def calcular_numerologia(nome_completo, nascimento, ano_atual):
    dia, mes, ano = nascimento

    resultados_nome = calcular_numeros_nome(nome_completo)
    expressao, motivacao, impressao = resultados_nome[0:3]

    # O total bruto do Destino é a soma individual dos algarismos da data de nascimento (para uso geral)
    destino_total = sum(int(d) for d in str(dia) + str(mes) + str(ano))
    destino = reduce_number(destino_total)

    dia_pessoal = ano_pessoal(dia, mes, ano_atual)
    ano_pess = dia_pessoal

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

    return (expressao, motivacao, impressao, destino, dia_pessoal,
            ano_pess, missao, dividas_carmicas, licoes_carmicas,
            tendencias_ocultas, soma_tendencias, resposta_subconsciente,
            desafio1, desafio2, desafio_principal, ciclos_vida, momentos_decisivos, triangulo_base, triangulo_reps)



def remover_acentos(texto):
    texto_str = str(texto).replace('º', 'o').replace('ª', 'a')
    return ''.join(c for c in unicodedata.normalize('NFD', texto_str) if unicodedata.category(c) != 'Mn')

st.title("🔮 Calculadora de Numerologia Cabalística")
st.markdown("Descubra os números poderosos que regem sua vida com base na numerologia cabalística.")

with st.form("numerologia_form"):
    nome = st.text_input("Digite seu nome completo (Ex: Cristiano Corrêa de Almeida):")
    data_input = st.date_input("Data de Nascimento:", min_value=datetime.date(1900, 1, 1), format="DD/MM/YYYY")
    submit = st.form_submit_button("Calcular Meu Mapa")

if submit and nome:
    ano_atual = datetime.date.today().year
    nascimento = (data_input.day, data_input.month, data_input.year)

    resultados = calcular_numerologia(nome, nascimento, ano_atual)
    (expressao, motivacao, impressao, destino, dia_pessoal,
     ano_pess, missao, dividas_carmicas, licoes_carmicas,
     tendencias_ocultas, soma_tendencias, resposta_subconsciente,
     desafio1, desafio2, desafio_principal, ciclos_vida, momentos_decisivos, triangulo_base, triangulo_reps) = resultados

    st.success(f"Mapa de **{nome}** calculado com sucesso!")
    
    dados = []
    def add_row(campo, valor):
        dados.append({"Campo": remover_acentos(campo), "Resultado": remover_acentos(valor)})
        
    add_row("Expressão", expressao)
    add_row("Motivação", motivacao)
    add_row("Impressão", impressao)
    add_row("Destino", destino)
    add_row("Triângulo da Vida (Base)", triangulo_base)
    add_row("Triângulo da Vida (Repetições)", triangulo_reps)
    add_row("Dia Pessoal", dia_pessoal)
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

    # Exibir a tabela no site
    df = pd.DataFrame(dados)
    st.table(df)

    # Botão de Download CSV
    csv = df.to_csv(sep=';', index=False).encode('utf-8')
    nome_limpo = remover_acentos(nome).replace(' ', '_')
    st.download_button(
        label="📥 Baixar Resultados como CSV",
        data=csv,
        file_name=f"mapa_cabalistico_{nome_limpo}.csv",
        mime="text/csv",
    )
elif submit and not nome:
    st.error("Por favor, digite seu nome completo para calcular!")
