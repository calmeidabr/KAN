import itertools
from collections import defaultdict, Counter

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

def reduce_kan(n):
    while n > 9 and n not in [11, 22]:
        n = sum(int(d) for d in str(n))
    return n

def calcular_numeros_nome(nome_completo):
    nome = nome_completo.upper().replace(' ', '')
    expressao_total = sum(letter_values.get(ch, 0) for ch in nome)
    vogais = set('AEIOUYÀÁÂÃÄÅÆÉÈÊËÍÎÏÓÒÔÕÖÚÙÛÜ')
    motivacao_total = sum(letter_values.get(ch, 0) for ch in nome if ch in vogais)
    consoantes_total = sum(letter_values.get(ch, 0) for ch in nome if ch not in vogais)

    impressao_reduzida = reduce_number(consoantes_total)
    while impressao_reduzida > 9:
        impressao_reduzida = sum(int(d) for d in str(impressao_reduzida))

    return (reduce_number(expressao_total), reduce_number(motivacao_total), impressao_reduzida)

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
    return base

def calcular_momentos_decisivos_base(dia, mes, ano, destino):
    ciclo1_num = mes
    while ciclo1_num > 9:
        ciclo1_num = sum(int(d) for d in str(ciclo1_num))
    ciclo1_periodo_anos = 37 - destino
    ciclo2_num = dia
    while ciclo2_num > 9:
        ciclo2_num = sum(int(d) for d in str(ciclo2_num))
        
    momento1 = dia + mes
    if momento1 not in (11, 22): momento1 = reduce_number(momento1)
    
    ano_reduzido = reduce_number(ano)
    momento2 = dia + ano_reduzido
    if momento2 not in (11, 22): momento2 = reduce_number(momento2)
    
    soma_12 = momento1 + momento2
    if soma_12 in (11, 22): momento3 = soma_12
    else: momento3 = reduce_number(soma_12)
    
    return ciclo2_num, momento3

nome = "Samuel Harris Altman"
dia, mes, ano = 22, 4, 1985

expressao, motivacao, impressao = calcular_numeros_nome(nome)
destino_total = sum(int(d) for d in str(dia) + str(mes) + str(ano))
destino = reduce_number(destino_total)
missao = reduce_number(destino + expressao)
num_dia_puro = dia
num_dia_reduzido = reduce_number(dia)
triangulo_base = calcular_triangulo_vida(nome)

ciclo2_num, momento3_num = calcular_momentos_decisivos_base(dia, mes, ano, destino)

estrutural = reduce_kan(motivacao + impressao + expressao + reduce_number(dia))
direcionamento = reduce_kan(destino + missao + ciclo2_num + momento3_num)

nums = [motivacao, impressao, expressao, destino, missao, num_dia_puro, triangulo_base, num_dia_reduzido]
counts = Counter(nums)
reps = sorted([(num, count) for num, count in counts.items() if count >= 2], key=lambda x: (-x[1], x[0]))

def get_rep_info(idx):
    if idx < len(reps):
        return reps[idx][0]
    return "N/A"

rep1 = get_rep_info(0)
rep2 = get_rep_info(1)

print(f"Motivação: {motivacao}")
print(f"Impressão: {impressao}")
print(f"Expressão: {expressao}")
print(f"Destino: {destino}")
print(f"Missão: {missao}")
print(f"Dia Natalício: {num_dia_puro}")
print(f"Triângulo: {triangulo_base}")
print(f"No Psiquico: {num_dia_reduzido}")
print(f"Estrutural: {estrutural}")
print(f"Direcionamento: {direcionamento}")
print(f"REPETIÇÃO 1: {rep1}")
print(f"REPETIÇÃO 2: {rep2}")
