import os
import sys
import datetime
from collections import Counter

# Adiciona o diretório raiz ao path do python para que possamos importar os módulos locais
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Evita erros de codificação de caracteres no terminal Windows (UnicodeEncodeError)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(errors='replace')

# Inicializa patches e carregadores básicos

from models.database import get_supabase_admin
from services.numerologia import calcular_numerologia
from services.perfil import reduce_number

def extrair_digitos(s):
    if not s:
        return ""
    return "".join(ch for ch in str(s) if ch.isdigit())

def formatar_lista(lst):
    if not lst:
        return ""
    return ", ".join(str(x) for x in lst if x is not None)

def calcular_e_salvar_mapas():
    client = get_supabase_admin()
    if not client:
        print("Erro: Supabase client não configurado.")
        return False
        
    print("Buscando talentos cadastrados em mapas_salvos...")
    try:
        response = client.table("mapas_salvos").select("nome, data_nascimento").execute()
    except Exception as e:
        print(f"Erro ao consultar mapas_salvos: {e}")
        return False
        
    talentos = response.data
    if not talentos:
        print("Nenhum talento encontrado na base de dados.")
        return True
        
    print(f"Total de {len(talentos)} talentos encontrados. Iniciando processamento...")
    
    rows_to_insert = []
    
    for idx, t in enumerate(talentos):
        nome = t.get("nome")
        data_nascimento_str = t.get("data_nascimento")
        
        if not nome or not data_nascimento_str:
            print(f"[{idx+1}/{len(talentos)}] Ignorando registro com dados nulos: {t}")
            continue
            
        print(f"[{idx+1}/{len(talentos)}] Processando {nome} ({data_nascimento_str})...")
        
        try:
            # Parse da data
            dia, mes, ano = map(int, data_nascimento_str.split('/'))
            nascimento_tup = (dia, mes, ano)
        except Exception:
            print(f"      Erro ao decodificar data de nascimento '{data_nascimento_str}' para {nome}. Pulando.")
            continue
            
        hoje = datetime.date.today()
        data_atual_tup = (hoje.day, hoje.month, hoje.year)
        
        try:
            # Calcular numerologia pura
            resultados = calcular_numerologia(nome, nascimento_tup, data_atual_tup)
            (expressao, motivacao, impressao, destino, dia_pessoal, mes_pess,
             ano_pess, missao, dividas_carmicas, licoes_carmicas,
             tendencias_ocultas, soma_tendencias, resposta_subconsciente,
             desafio1, desafio2, desafio_principal, ciclos_vida, momentos_decisivos,
             triangulo_base, triangulo_reps, arcano_atual_res, arcano_atual_periodo) = resultados
             
            # Calcular as repetições da mesma forma que na perfil.py
            todos_numeros = []
            for v in [expressao, motivacao, impressao, destino, missao, nascimento_tup[0]]:
                if isinstance(v, int): todos_numeros.append(v)
                elif isinstance(v, str) and str(v).isdigit(): todos_numeros.append(int(v))
                
            for v in [desafio1, desafio2, desafio_principal]:
                if isinstance(v, int): todos_numeros.append(v)
                elif isinstance(v, str) and str(v).isdigit(): todos_numeros.append(int(v))
                
            for c_key in ciclos_vida:
                num_c = ciclos_vida[c_key].get('numero')
                if isinstance(num_c, int): todos_numeros.append(num_c)
                
            for m_key in momentos_decisivos:
                num_m = momentos_decisivos[m_key].get('numero')
                if isinstance(num_m, int): todos_numeros.append(num_m)
                
            num_psiquico = reduce_number(nascimento_tup[0])
            todos_numeros.append(num_psiquico)
            if isinstance(triangulo_base, int): todos_numeros.append(triangulo_base)
            
            c_total = Counter(todos_numeros)
            r_totais = sorted([(n, c) for n, c in c_total.items()], key=lambda x: (-x[1], x[0]))
            
            num_rep1 = r_totais[0][0] if r_totais else None
            num_rep2 = r_totais[1][0] if len(r_totais) > 1 else None
            num_rep3 = r_totais[2][0] if len(r_totais) > 2 else None
            
            # Montar payload do row
            row = {
                "nome": nome,
                "data_nascimento": data_nascimento_str,
                "motivacao": int(extrair_digitos(motivacao)) if motivacao else None,
                "impressao": int(extrair_digitos(impressao)) if impressao else None,
                "expressao": int(extrair_digitos(expressao)) if expressao else None,
                "dia_natalicio": nascimento_tup[0],
                "numero_psiquico": num_psiquico,
                "destino": int(extrair_digitos(destino)) if destino else None,
                "missao": int(extrair_digitos(missao)) if missao else None,
                "dividas_carmicas": formatar_lista(dividas_carmicas),
                "licoes_carmicas": formatar_lista(licoes_carmicas),
                "tendencias_ocultas": formatar_lista(tendencias_ocultas),
                "resposta_subconsciente": int(extrair_digitos(resposta_subconsciente)) if resposta_subconsciente else None,
                "desafio_1": desafio1,
                "desafio_2": desafio2,
                "desafio_principal": desafio_principal,
                "ciclo_1": ciclos_vida['ciclo1'].get('numero'),
                "ciclo_2": ciclos_vida['ciclo2'].get('numero'),
                "ciclo_3": ciclos_vida['ciclo3'].get('numero'),
                "momento_1": momentos_decisivos['momento1'].get('numero'),
                "momento_2": momentos_decisivos['momento2'].get('numero'),
                "momento_3": momentos_decisivos['momento3'].get('numero'),
                "momento_4": momentos_decisivos['momento4'].get('numero'),
                "ano_pessoal": ano_pess,
                "mes_pessoal": mes_pess,
                "dia_pessoal": dia_pessoal,
                "triangulo_harmonico": triangulo_base,
                "arcano_atual": extrair_digitos(arcano_atual_res),
                "arcano_atual_periodo": arcano_atual_periodo,
                "repeticao_mapa": num_rep1,
                "repeticao_mapa_2": num_rep2,
                "repeticao_mapa_3": num_rep3
            }
            rows_to_insert.append(row)
        except Exception as ex:
            print(f"      Erro ao processar cálculos para {nome}: {ex}")
            
    # Remove duplicados por nome no payload para evitar erro de conflito no mesmo insert
    dict_unicos = {}
    for r in rows_to_insert:
        dict_unicos[r["nome"]] = r
    rows_to_insert = list(dict_unicos.values())

    if not rows_to_insert:
        print("Nenhum registro válido processado para inserção.")
        return True
        
    print(f"\nTentando inserir/atualizar {len(rows_to_insert)} registros únicos na tabela 'mapa_numerologico_salvo'...")
    try:
        # Usamos upsert baseado na constraint unique do nome
        res = client.table("mapa_numerologico_salvo").upsert(rows_to_insert, on_conflict="nome").execute()
        print("Sincronização concluída com sucesso no Supabase!")
        return True
    except Exception as e:
        print(f"Erro crítico no salvamento/upsert do Supabase: {e}")
        print("Verifique se a tabela 'mapa_numerologico_salvo' foi criada corretamente com o SQL DDL correspondente.")
        return False

if __name__ == "__main__":
    calcular_e_salvar_mapas()
