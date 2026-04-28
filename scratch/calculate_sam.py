import sys
sys.path.append(".")

from mapa_cabalistico5 import calcular_numerologia, calcular_perfil_comportamental, reduce_number

def extract_num(s):
    if not s: return None
    try: return str(s).split(' - ')[0]
    except: return str(s)

nome = "Samuel Harris Altman"
nascimento = (22, 4, 1985)
data_atual = (28, 4, 2026)

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

num_dia_puro = nascimento[0]
num_dia_reduzido = reduce_number(nascimento[0])

print(f"Motivação: {extract_num(motivacao)}")
print(f"Impressão: {extract_num(impressao)}")
print(f"Expressão: {extract_num(expressao)}")
print(f"Destino: {extract_num(destino)}")
print(f"Missão: {extract_num(missao)}")
print(f"Dia Natalício: {num_dia_puro}")
print(f"Triângulo: {triangulo_base}")
print(f"No Psiquico: {num_dia_reduzido}")
print(f"Estrutural: {estrutural}")
print(f"Direcionamento: {direcionamento}")
print(f"REPETIÇÃO 1: {extract_num(rep1)}")
print(f"REPETIÇÃO 2: {extract_num(rep2)}")
