import sys
import os

# Configura stdout/stderr para UTF-8 para evitar UnicodeEncodeError no console do Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

import datetime
import urllib.request
import json

# Adiciona a raiz do projeto ao path para importar modulos locais
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import KAN_DB
from services.perfil import realizar_calculos_completos

def map_kan_name(k):
    res = KAN_DB.get(str(k), {})
    return res.get("kan", str(k))

def carregar_clientes_rest(url, key):
    print("Buscando dados de mapas_salvos via REST API...")
    req_url = f"{url}/rest/v1/mapas_salvos?select=nome,data_nascimento,profissao,cargo,grupo,empresa,departamento,linkedin_url,experiencias,lider,perfil_json"
    req = urllib.request.Request(
        req_url,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}"
        }
    )
    
    with urllib.request.urlopen(req) as response:
        rows = json.loads(response.read().decode())
        
    cl_salvos = {}
    for row in rows:
        nome_cli = row.get('nome')
        if not nome_cli:
            continue
            
        p_json = row.get('perfil_json')
        perfil_val, categoria_val, qualidades_val, kan_val, fortaleza_val, desafio_val = "", "", "", None, "", ""
        estrutural_val, direcionamento_val, rep1_val, rep2_val = "", "", "", ""
        mapa_detalhado = {}
        
        if p_json:
            try:
                dt = json.loads(p_json)
                for item in dt:
                    campo_orig = item.get('Campo', '')
                    campo_norm = campo_orig.lower().replace(" ", "").replace("_", "").replace("-", "")
                    raw_val = item.get('Resultado', item.get('Valor', ''))
                    if campo_norm == 'perfil': perfil_val = raw_val
                    elif campo_norm == 'categoria': categoria_val = raw_val
                    elif campo_norm == 'qualidades': qualidades_val = raw_val
                    elif campo_norm == 'kan':
                        try: kan_val = int(raw_val)
                        except: kan_val = raw_val
                    elif campo_norm == 'fortaleza': fortaleza_val = raw_val
                    elif campo_norm == 'desafio': desafio_val = raw_val
                    elif campo_norm == 'estrutural': estrutural_val = raw_val
                    elif campo_norm == 'direcionamento': direcionamento_val = raw_val
                    elif 'repeticao1' in campo_norm: rep1_val = raw_val
                    elif 'repeticao2' in campo_norm: rep2_val = raw_val
                    elif "mapa:" in campo_norm:
                        nome_campo_mapa = campo_orig.split("Mapa:")[1].strip()
                        mapa_detalhado[nome_campo_mapa] = raw_val
            except Exception: pass

        is_migrated = 'grupo' in row
        grupo_val = row.get('grupo', '') if is_migrated else row.get('empresa', '')
        empresa_val = row.get('empresa', '') if is_migrated else ''
        
        is_migrated_profissao = 'profissao' in row
        profissao_val = row.get('profissao', '') if is_migrated_profissao else row.get('cargo', '')
        cargo_val = row.get('cargo', '') if is_migrated_profissao else ''
        
        cl_salvos[nome_cli] = {
            'data_nascimento': row.get('data_nascimento'),
            'profissao': profissao_val,
            'cargo': cargo_val,
            'grupo': grupo_val,
            'empresa': empresa_val,
            'departamento': row.get('departamento', ''),
            'linkedin_url': row.get('linkedin_url', ''),
            'experiencias': row.get('experiencias', ''),
            'kan': kan_val,
            'perfil': perfil_val,
            'categoria': categoria_val,
            'qualidades': qualidades_val,
            'fortaleza': fortaleza_val,
            'desafio': desafio_val,
            'estrutural': estrutural_val,
            'direcionamento': direcionamento_val,
            'repeticao_1': rep1_val,
            'repeticao_2': rep2_val,
            'mapa_detalhado': mapa_detalhado,
            'lider': bool(row.get('lider', False)),
            'has_json': True if p_json else False
        }
    return cl_salvos

def upsert_valores_rest(url, key, rows):
    print(f"\nEnviando {len(rows)} registros para mapas_salvos_valores via REST API...")
    req_url = f"{url}/rest/v1/mapas_salvos_valores?on_conflict=nome"
    payload = json.dumps(rows).encode('utf-8')
    req = urllib.request.Request(
        req_url,
        data=payload,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        },
        method="POST"
    )
    
    with urllib.request.urlopen(req) as response:
        status = response.status
        print(f"[+] Upsert concluido com status {status}!")

def main():
    print("Iniciando recalculo das tendencias ocultas (REST)...")
    
    import streamlit as st
    try:
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_SERVICE_ROLE_KEY"]
    except Exception as e:
        print(f"Erro ao carregar configuracoes do secrets.toml: {e}")
        sys.exit(1)
        
    clientes_para_calc = carregar_clientes_rest(url, key)
    if not clientes_para_calc:
        print("Nenhum cliente/talento encontrado na base.")
        sys.exit(0)
        
    print(f"Total de {len(clientes_para_calc)} talentos encontrados.")
    rows_to_insert = []
    now_dt = datetime.datetime.now()
    data_atual_tup = (now_dt.day, now_dt.month, now_dt.year)
    
    sucesso = 0
    erros = 0
    
    for n_aud, c_info in clientes_para_calc.items():
        nasc_dt = c_info.get('data_nascimento')
        if not nasc_dt:
            print(f"[-] Ignorando {n_aud}: Sem data de nascimento cadastrada.")
            continue
            
        try:
            if isinstance(nasc_dt, (datetime.datetime, datetime.date)):
                nascimento_tup = (nasc_dt.day, nasc_dt.month, nasc_dt.year)
            elif isinstance(nasc_dt, str):
                try:
                    dt_obj = datetime.datetime.strptime(nasc_dt, "%d/%m/%Y")
                except ValueError:
                    dt_obj = datetime.datetime.strptime(nasc_dt, "%Y-%m-%d")
                nascimento_tup = (dt_obj.day, dt_obj.month, dt_obj.year)
            else:
                print(f"[-] Ignorando {n_aud}: Formato de data invalido.")
                continue
                
            res_calc = realizar_calculos_completos(
                n_aud, 
                nascimento_tup, 
                data_atual_tup, 
                c_info.get('profissao', c_info.get('cargo', '')), 
                c_info.get('grupo')
            )
            dados, dados_perfil, kan, estrutural, direcionamento, rep1, rep2, rep3, rep4, _, _, _, _ = res_calc
            
            def ext_val(label):
                for d in dados:
                    if str(d.get("Campo")).startswith(label):
                        return str(d.get("Valor"))
                return ""
                
            def ext_perfil(label, just_value=False):
                for d in dados_perfil:
                    if str(d.get("Campo")).lower() == label.lower():
                        if just_value:
                            return str(d.get("Valor", ""))
                        return str(d.get("Resultado", d.get("Valor", "")))
                return ""

            row_val = {
                "nome": n_aud,
                "data_nascimento": nasc_dt if isinstance(nasc_dt, str) else nasc_dt.strftime('%Y-%m-%d'),
                "kan": str(map_kan_name(kan)),
                "perfil": ext_perfil("perfil", just_value=True),
                "categoria": ext_perfil("categoria", just_value=True),
                "qualidades": ext_perfil("qualidades", just_value=True),
                "diferenciais": ext_perfil("diferenciais", just_value=True),
                "motivacao": ext_val("Motivação"),
                "impressao": ext_val("Impressão"),
                "expressao": ext_val("Expressão"),
                "dia_natalicio": ext_val("Dia Natalício"),
                "numero_psiquico": ext_val("Número Psíquico"),
                "destino": ext_val("Destino"),
                "missao": ext_val("Missão"),
                "direcionamento": str(direcionamento),
                "estrutural": str(estrutural),
                "repeticao_1": str(rep1),
                "repeticao_2": str(rep2),
                "repeticao_mapa": ext_val("Repetição Mapa"),
                "repeticao_mapa_2": ext_val("Repetição 2 Mapa"),
                "vertice_triangulo_1": "",
                "vertice_triangulo_2": "",
                "vertice_triangulo_3": ext_val("Triângulo Harmônico"),
                "dividas_carmicas": ext_val("Dívidas Cármicas"),
                "licoes_carmicas": ext_val("Lições Cármicas"),
                "tendencias_ocultas": ext_val("Tendências Ocultas"),
                "resposta_subconsciente": ext_val("Resposta Subconsciente")
            }
            rows_to_insert.append(row_val)
            print(f"[+] Processado: {n_aud} -> Tendencias: {row_val['tendencias_ocultas']}")
            sucesso += 1
            
        except Exception as e:
            print(f"[!] Erro ao processar {n_aud}: {e}")
            erros += 1

    if rows_to_insert:
        try:
            upsert_valores_rest(url, key, rows_to_insert)
        except Exception as e:
            print(f"[!] Erro na chamada do PostgREST Supabase: {e}")
            sys.exit(1)
    else:
        print("Nenhum registro a ser atualizado.")
        
    print(f"\nRelatorio final:")
    print(f"  - Sucesso: {sucesso}")
    print(f"  - Erros: {erros}")

if __name__ == "__main__":
    main()
