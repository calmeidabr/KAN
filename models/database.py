import streamlit as st
import pandas as pd
from utils.helpers import get_from_row, remover_acentos, normalize_key

MENU_PRINCIPAL = [
    "Home", "Talentos", "Vagas", "Diagnósticos", "Analytics",
    "Hierarquia / Deptos", "Equipes", "Empresa", "Usuários"
]

@st.cache_resource
def init_supabase_client():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

@st.cache_resource
def init_supabase_admin_client():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_SERVICE_ROLE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Erro no init_db_admin_client: {e}")
        return None

def get_supabase():
    return init_supabase_client()

def get_supabase_admin():
    return init_supabase_admin_client()

def parse_arcanos_sql():
    arcanos = {}
    try:
        import os
        import re
        filepath = "arcanos.sql"
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            matches = re.findall(r"VALUES\s*\(\s*(\d+)\s*,\s*'([^']*)'\s*,\s*'([^']*)'\s*\)", content)
            for num, nome, desc in matches:
                desc_clean = desc.replace("''", "'")
                arcanos[str(num)] = {"nome": nome, "descricao": desc_clean}
    except Exception:
        pass
    return arcanos

@st.cache_data(ttl=3600)
def fetch_arcanos():
    client = get_supabase_admin()  # Usa o admin client para contornar restrições de RLS do anon client
    try:
        if client:
            resp = client.table("arcanos").select("*").execute()
            if resp.data:
                return {str(int(get_from_row(row, 'numero'))): {"nome": get_from_row(row, 'nome'), "descricao": get_from_row(row, 'descricao')} for row in resp.data if get_from_row(row, 'numero') is not None}
    except Exception:
        pass
    return parse_arcanos_sql()  # Fallback local lendo arcanos.sql

ARCANOS_DB = fetch_arcanos()

@st.cache_data(ttl=3600)
def fetch_fortalezas():
    client = get_supabase()
    try:
        if client:
            resp = client.table("fortalezas").select("*").execute()
            if resp.data:
                res_dict = {}
                for row in resp.data:
                    num_val = get_from_row(row, 'triangulo')
                    if num_val is not None:
                        res_dict[str(int(num_val))] = {"fortaleza": get_from_row(row, 'fortaleza'), "descricao": get_from_row(row, 'descricao')}
                if res_dict: return res_dict
    except Exception:
        pass
        
    try:
        df = pd.read_csv("Fortaleza.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("Fortaleza.csv", sep=",")
        res_dict = {}
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            num_val = get_from_row(row_dict, 'triangulo')
            if num_val is not None:
                try: key_str = str(int(float(num_val)))
                except: key_str = str(num_val).strip()
                res_dict[key_str] = {
                    "fortaleza": get_from_row(row_dict, 'fortaleza'),
                    "descricao": get_from_row(row_dict, 'descricao')
                }
        return res_dict
    except Exception:
        return {}

FORTALEZAS_DB = fetch_fortalezas()

@st.cache_data(ttl=3600)
def fetch_kan():
    client = get_supabase()
    try:
        if client:
            resp = client.table("kans").select("*").execute()
            if resp.data:
                res_dict = {}
                for row in resp.data:
                    num_val = get_from_row(row, 'numero')
                    if num_val is not None:
                        res_dict[str(int(num_val))] = {"kan": get_from_row(row, 'kan'), "descricao": get_from_row(row, 'descricao')}
                if res_dict: return res_dict
    except Exception:
        pass
        
    try:
        df = pd.read_csv("KAN.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("KAN.csv", sep=",")
        res_dict = {}
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            num_val = get_from_row(row_dict, 'numero')
            if num_val is not None:
                try: key_str = str(int(float(num_val)))
                except: key_str = str(num_val).strip()
                res_dict[key_str] = {
                    "kan": get_from_row(row_dict, 'kan'),
                    "descricao": get_from_row(row_dict, 'descricao')
                }
        return res_dict
    except Exception:
        return {}

KAN_DB = fetch_kan()

@st.cache_data(ttl=3600)
def fetch_desafios():
    client = get_supabase()
    try:
        if client:
            resp = client.table("desafios").select("*").execute()
            if resp.data:
                res_dict = {}
                for row in resp.data:
                    num_val = get_from_row(row, 'dia_nascimento')
                    if num_val is not None:
                        res_dict[str(int(num_val))] = {"desafio": get_from_row(row, 'desafio'), "descricao": get_from_row(row, 'descricao')}
                if res_dict: return res_dict
    except Exception:
        pass
        
    try:
        df = pd.read_csv("Desafio.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("Desafio.csv", sep=",")
        res_dict = {}
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            num_val = get_from_row(row_dict, 'dia do nascimento') or get_from_row(row_dict, 'dia_nascimento')
            if num_val is not None and pd.notna(num_val):
                try: key_str = str(int(float(num_val)))
                except: key_str = str(num_val).strip()
                res_dict[key_str] = {
                    "desafio": get_from_row(row_dict, 'desafio'),
                    "descricao": get_from_row(row_dict, 'descricao')
                }
        return res_dict
    except Exception:
        return {}

DESAFIOS_DB = fetch_desafios()

@st.cache_data(ttl=3600)
def fetch_matriz():
    client = get_supabase()
    try:
        if client:
            resp = client.table("matriz").select("*").execute()
            if resp.data:
                res_dict = {}
                for row in resp.data:
                    num_val = get_from_row(row, 'numero') or get_from_row(row, 'Resultado')
                    if num_val is not None:
                        try: key_str = str(int(float(num_val)))
                        except: key_str = str(num_val).strip()
                        res_dict[key_str] = row
                if res_dict: return res_dict
    except Exception: pass
        
    try:
        df = pd.read_csv("Tabela Matriz.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("Tabela Matriz.csv", sep=",")
        resultado = {}
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            num_val = row_dict.get('Resultado', row_dict.get('numero', ''))
            if pd.notna(num_val):
                try: num_val_str = str(int(float(num_val)))
                except: num_val_str = str(num_val).strip()
                if num_val_str:
                    cleaned_row = {remover_acentos(k): v for k, v in row_dict.items()}
                    resultado[num_val_str] = cleaned_row
        return resultado
    except Exception: return {}

MATRIZ_DB = fetch_matriz()

@st.cache_data(ttl=3600)
def fetch_atributos():
    client = get_supabase()
    try:
        if client:
            resp = client.table("atributos").select("*").execute()
            if resp.data:
                res_dict = {}
                for row in resp.data:
                    attr_val = str(get_from_row(row, 'atributo') or get_from_row(row, 'ATRIBUTOS') or '').upper()
                    if attr_val: res_dict[attr_val] = row
                if res_dict: return res_dict
    except Exception: pass
        
    try:
        df = pd.read_csv("Atributos.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("Atributos.csv", sep=",")
        resultado = {}
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            attr_val = str(get_from_row(row_dict, 'atributo') or get_from_row(row_dict, 'ATRIBUTOS') or '').upper()
            if attr_val: resultado[attr_val] = row_dict
        return resultado
    except Exception: return {}

ATRIBUTOS_DB = fetch_atributos()

@st.cache_data(ttl=3600)
def fetch_repeticao():
    client = get_supabase()
    try:
        if client:
            resp = None
            try: resp = client.table("repeticao").select("*").execute()
            except: resp = client.table("repeticao_descricao").select("*").execute()
            if resp and resp.data:
                res_dict = {}
                for row in resp.data:
                    rep_val = get_from_row(row, 'repeticao')
                    if rep_val is not None:
                        res_dict[str(int(float(rep_val)))] = row
                if res_dict: return res_dict
    except Exception: pass
        
    try:
        df = pd.read_csv("Repeticao.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("Repeticao.csv", sep=",")
        resultado = {}
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            rep_val = str(int(float(get_from_row(row_dict, 'repeticao')))) if get_from_row(row_dict, 'repeticao') else ''
            if rep_val: resultado[rep_val] = row_dict
        return resultado
    except Exception: return {}

REPETICAO_DB = fetch_repeticao()

@st.cache_data(ttl=3600)
def fetch_peso():
    client = get_supabase()
    try:
        if client:
            resp = client.table("peso").select("*").execute()
            if resp.data:
                res_dict = {}
                for row in resp.data:
                    c = get_from_row(row, 'campo')
                    p = get_from_row(row, 'peso')
                    if c is not None and p is not None:
                        res_dict[c] = p
                if res_dict: return res_dict
    except Exception: pass
        
    try:
        df = pd.read_csv("peso.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("peso.csv", sep=",")
        res_dict = {}
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            c = get_from_row(row_dict, 'campo')
            p = get_from_row(row_dict, 'peso')
            if c is not None and p is not None:
                res_dict[c] = p
        return res_dict
    except Exception: return {}

PESO_DB = fetch_peso()

@st.cache_data(ttl=3600)
def fetch_perfis():
    client = get_supabase()
    try:
        if client:
            resp = client.table("perfis").select("*").execute()
            if resp.data: return [row['perfil'] for row in resp.data]
    except Exception: pass
        
    try:
        df = pd.read_csv("perfil.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("perfil.csv", sep=",")
        return [row['perfil'] for _, row in df.iterrows() if 'perfil' in row]
    except Exception: return ["Lider", "Criativo", "Executor", "Resultado", "Vendedor", "Influenciador", "Comunicador"]

PERFIS_DB = fetch_perfis()

@st.cache_data(ttl=3600)
def fetch_perfil_descricao():
    client = get_supabase()
    try:
        if client:
            resp = client.table("perfil_descricao").select("*").execute()
            if resp.data:
                return {str(get_from_row(row, 'perfil')).strip().capitalize(): get_from_row(row, 'descricao') for row in resp.data}
    except Exception: pass
        
    try:
        df = pd.read_csv("perfil_descricao.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("perfil_descricao.csv", sep=",")
        return {str(get_from_row(row.to_dict(), 'perfil')).strip().capitalize(): get_from_row(row.to_dict(), 'descricao') for _, row in df.iterrows()}
    except Exception: return {}

PERFIL_DESCRICAO_DB = fetch_perfil_descricao()

@st.cache_data(ttl=3600)
def fetch_qualidades():
    client = get_supabase()
    try:
        if client:
            resp = client.table("qualidades").select("*").execute()
            if resp.data:
                return {str(get_from_row(row, 'qualidade')).strip().capitalize(): get_from_row(row, 'descricao') for row in resp.data}
    except Exception: pass
        
    try:
        df = pd.read_csv("Qualidades.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("Qualidades.csv", sep=",")
        return {str(get_from_row(row.to_dict(), 'qualidade')).strip().capitalize(): get_from_row(row.to_dict(), 'descricao') for _, row in df.iterrows()}
    except Exception: return {}

QUALIDADES_DB = fetch_qualidades()

@st.cache_data(ttl=3600)
def fetch_lista_categoria():
    client = get_supabase()
    try:
        if client:
            resp = client.table("lista_categoria").select("*").execute()
            if resp.data: return [get_from_row(row, 'categoria') for row in resp.data]
    except Exception: pass
        
    try:
        df = pd.read_csv("lista_categoria.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("lista_categoria.csv", sep=",")
        return [get_from_row(row.to_dict(), 'categoria') for _, row in df.iterrows()]
    except Exception: return []

LISTA_CATEGORIA_DB = fetch_lista_categoria()

@st.cache_data(ttl=3600)
def fetch_categoria_descricao():
    client = get_supabase()
    try:
        if client:
            resp = client.table("categoria_descricao").select("*").execute()
            if resp.data:
                return {str(get_from_row(row, 'categoria')).strip().capitalize(): get_from_row(row, 'descricao') for row in resp.data}
    except Exception: pass
        
    try:
        df = pd.read_csv("categoria_descricao.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("categoria_descricao.csv", sep=",")
        return {str(get_from_row(row.to_dict(), 'categoria')).strip().capitalize(): get_from_row(row.to_dict(), 'descricao') for _, row in df.iterrows()}
    except Exception: return {}

CATEGORIA_DESCRICAO_DB = fetch_categoria_descricao()

@st.cache_data(ttl=3600)
def fetch_peso_categoria():
    client = get_supabase()
    try:
        if client:
            resp = client.table("peso_categoria").select("*").execute()
            if resp.data:
                res_dict = {}
                for row in resp.data:
                    c = get_from_row(row, 'campo')
                    p = get_from_row(row, 'peso') or get_from_row(row, 'peso_categoria')
                    if c is not None and p is not None:
                        res_dict[c] = p
                if res_dict: return res_dict
    except Exception: pass
        
    try:
        df = pd.read_csv("peso_categoria.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("peso_categoria.csv", sep=",")
        res_dict = {}
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            c = get_from_row(row_dict, 'campo')
            p = get_from_row(row_dict, 'peso') or get_from_row(row_dict, 'peso_categoria')
            if c is not None and p is not None:
                res_dict[c] = p
        return res_dict
    except Exception: return {}

PESO_CATEGORIA_DB = fetch_peso_categoria()

@st.cache_data(ttl=3600)
def fetch_campo_definicao():
    client = get_supabase()
    try:
        if client:
            resp = client.table("campo_definicao").select("*").execute()
            if resp.data:
                return {str(get_from_row(row, 'campo')): get_from_row(row, 'explicacao') for row in resp.data}
    except Exception: pass

    try:
        df = pd.read_csv("campo_definicao.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("campo_definicao.csv", sep=",")
        return {row['CAMPO']: row['EXPLICACAO'] for _, row in df.iterrows()}
    except Exception: return {}

CAMPO_DEFINICAO_DB = fetch_campo_definicao()

@st.cache_data(ttl=3600)
def fetch_diferenciais_descricao():
    client = get_supabase()
    try:
        if client:
            resp = client.table("diferenciais_descricao").select("*").execute()
            if resp.data:
                return {str(get_from_row(row, 'no')): {'diferencial': get_from_row(row, 'diferencial'), 'descricao': get_from_row(row, 'descricao')} for row in resp.data}
    except Exception: pass
        
    try:
        df = pd.read_csv("diferenciais_descricao.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("diferenciais_descricao.csv", sep=",")
        return {str(get_from_row(row.to_dict(), 'no')): {'diferencial': get_from_row(row.to_dict(), 'diferencial'), 'descricao': get_from_row(row.to_dict(), 'descricao')} for _, row in df.iterrows()}
    except Exception: return {}

DIFERENCIAIS_DESC_DB = fetch_diferenciais_descricao()

@st.cache_data(ttl=3600)
def fetch_descricoes_mapa():
    client = get_supabase()
    REMAINING_DESCRIPTIONS = [
        {'categoria': 'Numero Psiquico', 'valor': '1', 'descricao': 'Independência, pioneirismo, liderança e coragem.'},
        {'categoria': 'Numero Psiquico', 'valor': '2', 'descricao': 'Diplomacia, cooperação, união, intuição e sensibilidade.'},
        {'categoria': 'Numero Psiquico', 'valor': '3', 'descricao': 'Comunicação, expressão, criatividade e natureza artística.'},
        {'categoria': 'Numero Psiquico', 'valor': '4', 'descricao': 'Determinação, persistência, organização, resistência e trabalho.'},
        {'categoria': 'Numero Psiquico', 'valor': '5', 'descricao': 'Adaptação, liberdade, movimento, curiosidade e progresso.'},
        {'categoria': 'Numero Psiquico', 'valor': '6', 'descricao': 'Sensibilidade, harmonia, cuidado, responsabilidade e vínculos.'},
        {'categoria': 'Numero Psiquico', 'valor': '7', 'descricao': 'Perfeccionismo, introspecção, inspiração, intuição e conhecimento.'},
        {'categoria': 'Numero Psiquico', 'valor': '8', 'descricao': 'Liderança, gestão, força prática, autoridade e foco em resultados.'},
        {'categoria': 'Numero Psiquico', 'valor': '9', 'descricao': 'Altruísmo, compaixão, generosidade, intuição e carisma.'},
        {'categoria': 'Numero Psiquico', 'valor': '11', 'descricao': 'Intuição elevada, visão, inspiração e sensibilidade espiritual.'},
        {'categoria': 'Numero Psiquico', 'valor': '22', 'descricao': 'Construção em grande escala, realização, liderança prática e potencial de impacto coletivo.'},
        {'categoria': '1º Ciclo de Vida', 'valor': '1', 'descricao': 'O 1 (um) no primeiro Ciclo de Vida indica um período difícil. Quando criança, a pessoa necessita aprender a desenvolver sua individualidade, pois caso contrário, na juventude e adolescência ou mesmo até à entrada do 2º Ciclo, terá problemas emocionais e grande dificuldade de se estabilizar profissionalmente. O ideal é que a criança nesse Ciclo tenha liberdade acima do normal e não frear os seus instintos em hipótese alguma.'}, {'categoria': '1º Ciclo de Vida', 'valor': '2', 'descricao': 'O 2 (dois) no primeiro Ciclo de Vida, indica uma criança extremamente mimada, que possivelmente sofreu grande influência da mãe ou dos avós.'}, {'categoria': '1º Ciclo de Vida', 'valor': '3', 'descricao': 'O 3 (três) indica uma infância e adolescência feliz, despreocupada e com muitos amigos.'}, {'categoria': '1º Ciclo de Vida', 'valor': '5', 'descricao': 'O 5 (cinco) no primeiro Ciclo de Vida indica muitas mudanças e uma liberdade que às vezes é demasiado grande para que se possa lidar com ela de maneira construtiva.'}, {'categoria': '1º Ciclo de Vida', 'valor': '6', 'descricao': 'O 6 (seis) indica infância e juventude restritiva, cheia de deveres e responsabilidades e, para fugir dessa restrição, normalmente casa-se cedo e muitas vezes esse casamento é um completo fracasso.'}, {'categoria': '1º Ciclo de Vida', 'valor': '7', 'descricao': 'O 7 (sete) no primeiro Ciclo de Vida indica um período muito difícil. A criança e o jovem conservam-se retraídos e podem sofrer com a falta de compreensão dos pais, professores e amigos.'}, {'categoria': '1º Ciclo de Vida', 'valor': '8', 'descricao': 'O 8 (oito) no primeiro Ciclo de Vida indica um período de realizações. É extraordinário para o aprendizado acerca dos aspectos materiais da vida.'}, {'categoria': '2º Ciclo de Vida', 'valor': '1', 'descricao': 'O 1 (um) no segundo Ciclo de Vida mostra um período de ambições, um grande desejo de realizações e também de sucesso relativo.'}, {'categoria': '2º Ciclo de Vida', 'valor': '2', 'descricao': 'O 2 (dois) neste período é indicador de sociabilidade e receptividade. É necessário cultivar a paciência, o tato, a diplomacia e a capacidade de perceber os sentimentos alheios.'}, {'categoria': '2º Ciclo de Vida', 'valor': '3', 'descricao': 'O 3 (três) nos mostra uma fase agradável na vida, com certa despreocupação. É a fase da sociabilidade, na qual a criatividade e a originalidade podem exteriorizar suas idéias e sentimentos através de algum tipo de arte.'}, {'categoria': '2º Ciclo de Vida', 'valor': '4', 'descricao': 'O 4 (quatro) é sinônimo de trabalho duro, de produtividade e de construção do alicerce que deverá se apoiar no futuro.'}, {'categoria': '2º Ciclo de Vida', 'valor': '5', 'descricao': 'O 5 (cinco) é indicativo de um período de expansão de horizontes, época propícia a viagens, mudanças, romances, liberdade, de novas atividades e também novos amigos.'}, {'categoria': '2º Ciclo de Vida', 'valor': '6', 'descricao': 'O 6 (seis) neste Ciclo nos mostra um período de ajustes e de responsabilidades nos assuntos domésticos em geral.'}, {'categoria': '2º Ciclo de Vida', 'valor': '7', 'descricao': 'O 7 (sete) indica um período de crescimento tranquilo, de estudos e de meditação. A menos que esteja casado, este não é um bom Ciclo para se contrair matrimônio.'}, {'categoria': '2º Ciclo de Vida', 'valor': '8', 'descricao': 'O 8 (oito) neste Ciclo mostra um período de preocupação com os aspectos materiais da vida. Normalmente a pessoa tem tendência a adquirir riqueza e poder material.'}, {'categoria': '2º Ciclo de Vida', 'valor': '9', 'descricao': 'O 9 (nove) neste Ciclo traz a possibilidade de sucesso na vida pública. É um período altamente espiritual e a pessoa necessita aprender a cultivar a tolerância, o amor à humanidade, o altruísmo e o controle emocional.'}, {'categoria': '2º Ciclo de Vida', 'valor': '11', 'descricao': 'O 11 (onze) nos mostra um período de ideais, de revelações, de grandeza e, possivelmente, de fama.'}, {'categoria': '2º Ciclo de Vida', 'valor': '22', 'descricao': 'O 22 (vinte e dois) no Segundo Ciclo é indício de grandes realizações e de liderança em alto nível. O objetivo primordial da pessoa neste Ciclo deve ser o de beneficiar a humanidade como um todo.'}, {'categoria': '3º Ciclo de Vida', 'valor': '1', 'descricao': 'O 1 (um) nos indica um final de vida solitário. A pessoa precisa permanecer ativa e independente e contar com seus próprios recursos.'}, {'categoria': '3º Ciclo de Vida', 'valor': '2', 'descricao': 'O 2 (dois) mostra um período de amor sincero e de amigos íntimos.'}, {'categoria': '3º Ciclo de Vida', 'valor': '3', 'descricao': 'O 3 (três) no terceiro Ciclo de Vida indica um período de expressão de idéias e sentimentos através de diversas formas de arte, música, teatro e literatura.'}, {'categoria': '3º Ciclo de Vida', 'valor': '4', 'descricao': 'O 4 (quatro) neste Ciclo nos mostra que a pessoa, mesmo aposentada, deverá continuar trabalhando, seja por necessidade, seja por escolha.'}, {'categoria': '3º Ciclo de Vida', 'valor': '5', 'descricao': 'O 5 (cinco) é o período da liberdade pessoal, de viagens, mudanças, de novas atividades e variedade.'}, {'categoria': '3º Ciclo de Vida', 'valor': '6', 'descricao': 'O 6 (seis) poderá ser o mais agradável de todos os terceiros ciclos de vida - uma fase de felicidade e harmonia no lar - se a pessoa tiver aprendido a adaptar-se e assumir responsabilidades.'}, {'categoria': '3º Ciclo de Vida', 'valor': '7', 'descricao': 'O 7 (sete) indica um período de isolamento ou de semi - isolamento. Trata-se de uma fase tranquila, apropriada para se estudar em casa e adquirir sabedoria e conhecimento.'}, {'categoria': '3º Ciclo de Vida', 'valor': '8', 'descricao': 'O 8 (oito) neste Ciclo mostra que a pessoa precisa agir com sabedoria, trabalhar e estudar duramente nos dois primeiros, quando terá grande possibilidade de ficar rico neste e ter poder e sucesso ilimitados no mundo dos negócios.'}, {'categoria': '3º Ciclo de Vida', 'valor': '9', 'descricao': 'O 9 (nove) mostra um período de retiro para o estudo e o aprendizado. A pessoa precisa cultivar a tolerância e o amor pela humanidade.'}, {'categoria': '3º Ciclo de Vida', 'valor': '22', 'descricao': 'O 22 (vinte e dois) no terceiro ciclo de vida talvez torne a pessoa tensa e nervosa. Ela deve procurar manter-se ativa durante esse período e dedicar-se a um hobby.'}, {'categoria': 'Desafio', 'valor': '1', 'descricao': 'Desafio 1 - O consulente precisará aprender a se situar num meio termo entre um sentimento excessivo ou insuficiente de sua própria personalidade ou importância.'}, {'categoria': 'Desafio', 'valor': '2', 'descricao': 'Desafio 2 - Poderá tender a ser tão sensível em relação aos seus próprios sentimentos e a passar tanto tempo pensando neles, que acabará não tomando conhecimento dos sentimentos dos outros.'}, {'categoria': 'Desafio', 'valor': '3', 'descricao': 'Desafio 3 - Precisará aprender a situar-se num meio termo, entre ter medo de contatos sociais e ser por demais festeiro.'}, {'categoria': 'Desafio', 'valor': '4', 'descricao': 'Desafio 4 - É o mais fácil de todos os desafios, visto que não há nenhum conflito envolvido.'}, {'categoria': 'Desafio', 'valor': '5', 'descricao': 'Desafio 5 - Precisa aprender a situar-se num meio- termo entre desejar uma liberdade excessiva e ter um receio injustiçado dela - entre uma ânsia exagerada de experiências sensuais e o medo de tentar coisas novas.'}, {'categoria': 'Desafio', 'valor': '6', 'descricao': 'Desafio 6- Precisa aprender a situar-se num meio termo entre comportar-se como um “capacho” ou ser demasiado exigente e dominador.'}, {'categoria': 'Desafio', 'valor': '7', 'descricao': 'Desafio 7 - Precisará aprender a situar-se num meio termo entre o orgulho excessivo e a modéstia exagerada.'}, {'categoria': 'Desafio', 'valor': '8', 'descricao': 'Desafio 8 - Precisará aprender a situar-se num meio termo entre uma preocupação excessiva com as questões materiais, e um desinteresse exagerado em relação a esse assunto.'}, {'categoria': 'Momento Decisivo', 'valor': '1', 'descricao': 'MOMENTO DECISIVO 1 - Não é um período fácil; exige coragem, determinação e muita força de vontade.'}, {'categoria': 'Momento Decisivo', 'valor': '2', 'descricao': 'MOMENTO DECISIVO 2 - Traz consigo a oportunidade para “cultivar” o tato e a compreensão.'}, {'categoria': 'Momento Decisivo', 'valor': '3', 'descricao': 'MOMENTO DECISIVO 3 - É o momento de expandir a vida social e “cultivar” os próprios talentos.'}, {'categoria': 'Momento Decisivo', 'valor': '4', 'descricao': 'MOMENTO DECISIVO 4 - Este Momento Decisivo traz a oportunidade de se construir um sólido alicerce para o futuro.'}, {'categoria': 'Momento Decisivo', 'valor': '5', 'descricao': 'MOMENTO DECISIVO 5 - Traz oportunidades para viagens, para experimentar novas sensações, novos empreendimentos e para se livrar de tudo que está obsoleto ou que já não nos faz falta.'}, {'categoria': 'Momento Decisivo', 'valor': '6', 'descricao': 'MOMENTO DECISIVO 6 - É o momento dos ajustes e das responsabilidades familiares.'}, {'categoria': 'Momento Decisivo', 'valor': '7', 'descricao': 'MOMENTO DECISIVO 7 - É uma fase de introspecção, de meditação e estudo do significado último da vida.'}, {'categoria': 'Momento Decisivo', 'valor': '8', 'descricao': 'MOMENTO DECISIVO 8 - É um período de grandes realizações no mundo dos negócios.'}, {'categoria': 'Momento Decisivo', 'valor': '9', 'descricao': 'MOMENTO DECISIVO 9 - Traz a oportunidade para se “cultivar” o amor, a solidariedade, o altruísmo e para se viajar para o exterior.'}, {'categoria': 'Momento Decisivo', 'valor': '11', 'descricao': 'MOMENTO DECISIVO 11 - Por ser um número altamente espiritual e elevado, a pessoa nesse período sente-se tensa e muito nervosa.'}, {'categoria': 'Momento Decisivo', 'valor': '22', 'descricao': 'MOMENTO DECISIVO 22 - É, sem dúvida alguma, o número e o Momento mais poderoso. A pessoa fica altamente criativa e neste estado tornam-se possíveis todas as realizações.'}]
    
    resultado = {}
    for item in REMAINING_DESCRIPTIONS:
        cat = item['categoria']
        val = str(item['valor'])
        desc = item['descricao']
        if cat not in resultado: resultado[cat] = {}
        resultado[cat][val] = desc

    if client:
        try:
            try:
                check_resp = client.table("descricoes_mapa").select("id").eq("categoria", "Desafio").limit(1).execute()
                if not check_resp.data:
                    client.table("descricoes_mapa").upsert(REMAINING_DESCRIPTIONS).execute()
            except Exception: pass

            resp = client.table("descricoes_mapa").select("*").execute()
            for row in resp.data:
                cat = get_from_row(row, 'categoria') or ""
                val = str(get_from_row(row, 'valor') or "")
                desc = get_from_row(row, 'descricao') or ""
                res = get_from_row(row, 'resumo') or ""
                if cat:
                    if cat not in resultado: resultado[cat] = {}
                    resultado[cat][val] = {"descricao": desc, "resumo": res}
        except Exception: pass
    return resultado

DESCRICOES_MAPA_DB = fetch_descricoes_mapa()

def get_desc_mapa(categoria, valor):
    if not DESCRICOES_MAPA_DB: return ""
    cat_data = DESCRICOES_MAPA_DB.get(categoria, {})
    entry = cat_data.get(str(valor), "")
    if isinstance(entry, dict):
        return entry.get("resumo") if str(entry.get("resumo")).strip() else entry.get("descricao", "")
    return entry

@st.cache_data(ttl=60)
def fetch_banners():
    client = get_supabase()
    if not client: return []
    try:
        res = client.table("kan_banners").select("*").order("id").execute()
        return res.data
    except Exception: return []

@st.cache_data(ttl=300)
def fetch_asset_b64(asset_id):
    client = get_supabase()
    if not asset_id or not client: return None
    try:
        res = client.table("kan_assets").select("data_base64").eq("id", asset_id).single().execute()
        return res.data.get('data_base64')
    except Exception: return None

@st.cache_data(ttl=60)
def fetch_assets_list():
    client = get_supabase()
    if not client: return []
    try:
        res = client.table("kan_assets").select("id, nome").order("nome").execute()
        return res.data
    except Exception: return []

@st.cache_data(ttl=300)
def carregar_empresas(somente_ativas=True):
    client = get_supabase()
    if client:
        try:
            res = client.table("empresas").select("*").order("nome_empresa").execute()
            if res.data:
                if somente_ativas:
                    return [emp for emp in res.data if emp.get("status", "Ativa") != "Inativa"]
                return res.data
        except Exception: pass
    if "empresas_local_data" not in st.session_state:
        st.session_state["empresas_local_data"] = [
            {"nome_empresa": "Mundo Kan", "razao_social": "Mundo KAN Tecnologia Ltda", "cnpj": "00.000.000/0001-00", "segmento": "Tecnologia", "num_colaboradores": "50", "site": "https://mundokan.com.br", "telefone": "(11) 99999-9999", "email": "contato@mundokan.com.br", "responsavel_nome": "Administrador KAN", "responsavel_celular": "(11) 99999-9999", "responsavel_email": "adminkan@mundokan.com.br", "status": "Ativa"}
        ]
    local_data = st.session_state["empresas_local_data"]
    if somente_ativas:
        return [emp for emp in local_data if emp.get("status", "Ativa") != "Inativa"]
    return local_data

@st.cache_data(ttl=300)
def carregar_hierarquia(empresa):
    client = get_supabase()
    if client:
        try:
            res = client.table("hierarquia_departamentos").select("*").eq("empresa", empresa).order("ordem").execute()
            if res.data: return res.data
        except Exception: pass
    if "hier_local_" + empresa in st.session_state:
        return st.session_state["hier_local_" + empresa]
    
    padrao = [
        {"departamento_id": "dept_exec", "nome": "Diretoria Executiva", "parent_id": "Nenhum (Nível Mais Alto)", "empresa": empresa, "ordem": 10},
        {"departamento_id": "dept_com", "nome": "Diretoria Comercial", "parent_id": "dept_exec", "empresa": empresa, "ordem": 20},
        {"departamento_id": "dept_ops", "nome": "Diretoria de Operações", "parent_id": "dept_exec", "empresa": empresa, "ordem": 30},
        {"departamento_id": "dept_rh", "nome": "Recursos Humanos", "parent_id": "dept_ops", "empresa": empresa, "ordem": 40},
        {"departamento_id": "dept_ti", "nome": "Tecnologia da Informação", "parent_id": "dept_ops", "empresa": empresa, "ordem": 50}
    ]
    st.session_state["hier_local_" + empresa] = padrao
    return padrao

@st.cache_data(ttl=300)
def _fetch_supabase_clientes():
    client = get_supabase_admin()
    cl_salvos = {}
    if client:
        try:
            response = client.table("mapas_salvos").select("*").execute()
            for row in response.data:
                p_json = row.get('perfil_json')
                perfil_val, categoria_val, qualidades_val, kan_val, fortaleza_val, desafio_val = "", "", "", None, "", ""
                if p_json:
                    try:
                        import json
                        dt = json.loads(p_json)
                        for item in dt:
                            campo_orig = item.get('Campo', '')
                            campo_norm = normalize_key(campo_orig)
                            raw_val = item.get('Resultado', item.get('Valor', ''))
                            if campo_norm == 'perfil': perfil_val = raw_val
                            elif campo_norm == 'categoria': categoria_val = raw_val
                            elif campo_norm == 'qualidades': qualidades_val = raw_val
                            elif campo_norm == 'kan':
                                try: kan_val = int(raw_val)
                                except: kan_val = raw_val
                            elif campo_norm == 'fortaleza': fortaleza_val = raw_val
                            elif campo_norm == 'desafio': desafio_val = raw_val
                            elif campo_norm == 'estrutural': row['estrutural_val'] = raw_val
                            elif campo_norm == 'direcionamento': row['direcionamento_val'] = raw_val
                            elif 'repeticao 1' in campo_norm: row['rep1_val'] = raw_val
                            elif 'repeticao 2' in campo_norm: row['rep2_val'] = raw_val
                            elif "mapa:" in campo_norm:
                                if 'mapa_detalhado' not in row: row['mapa_detalhado'] = {}
                                nome_campo_mapa = campo_orig.split("Mapa:")[1].strip()
                                row['mapa_detalhado'][nome_campo_mapa] = raw_val
                    except Exception: pass

                is_migrated = 'grupo' in row
                grupo_val = row.get('grupo', '') if is_migrated else row.get('empresa', '')
                empresa_val = row.get('empresa', '') if is_migrated else ''
                
                is_migrated_profissao = 'profissao' in row
                profissao_val = row.get('profissao', '') if is_migrated_profissao else row.get('cargo', '')
                cargo_val = row.get('cargo', '') if is_migrated_profissao else ''
                
                cl_salvos[row['nome']] = {
                    'data_nascimento': row['data_nascimento'],
                    'profissao': profissao_val,
                    'cargo': cargo_val,
                    'grupo': grupo_val,
                    'empresa': empresa_val,
                    'departamento': row.get('departamento', ''),
                    'linkedin_url': row.get('linkedin_url', ''),
                    'experiencias': row.get('experiencias', ''),
                    'foto_base64': row.get('foto_base64', ''),
                    'ai_diagnosis': row.get('ai_diagnosis', ''),
                    'kan': kan_val,
                    'perfil': perfil_val,
                    'categoria': categoria_val,
                    'qualidades': qualidades_val,
                    'fortaleza': fortaleza_val,
                    'desafio': desafio_val,
                    'estrutural': row.get('estrutural_val', ''),
                    'direcionamento': row.get('direcionamento_val', ''),
                    'repeticao_1': row.get('rep1_val', ''),
                    'repeticao_2': row.get('rep2_val', ''),
                    'mapa_detalhado': row.get('mapa_detalhado', {}),
                    'lider': bool(row.get('lider', False)),
                    'has_json': True if p_json else False
                }
                if row.get('ai_diagnosis'):
                    if "ai_diagnosis" not in st.session_state: st.session_state["ai_diagnosis"] = {}
                    st.session_state["ai_diagnosis"][f"diag_{row['nome']}"] = row['ai_diagnosis']
        except Exception as e:
            st.error(f"Erro no _fetch_db_clientes: {e}")
    else:
        st.error("Erro: Conexão administrativa retornou None. Verifique as chaves nos Secrets.")
    return cl_salvos

def carregar_todos_clientes():
    cl_salvos = _fetch_supabase_clientes().copy()
    if "clientes_local_data" in st.session_state:
        for nome, data in st.session_state["clientes_local_data"].items():
            cl_salvos[nome] = data
    return cl_salvos

def salvar_na_base_dados(nome, dados_perfil, dados, estrutural, direcionamento, rep1, rep2):
    client = get_supabase_admin()
    
    try:
        import json
        import streamlit as st
        from utils.helpers import normalize_key
        
        dados_para_salvar = list(dados_perfil)
        campos_extra = [("Estrutural", estrutural), ("Direcionamento", direcionamento), 
                       ("REPETIÇÃO 1", rep1), ("REPETIÇÃO 2", rep2)]
        for label, val in campos_extra:
            if not any(item['Campo'] == label for item in dados_para_salvar):
                dados_para_salvar.append({"Campo": label, "Valor": str(val), "Descricao": "", "Resultado": str(val)})
        for item in dados:
            campo_full = item.get('Campo', '')
            if ' - ' in campo_full:
                partes = campo_full.split(' - ')
                campo_simples = partes[0]
                valor_simples = partes[1]
            else:
                campo_simples = campo_full
                valor_simples = item.get('Resultado', '')
            if not any(it['Campo'] == f"Mapa: {campo_simples}" for it in dados_para_salvar):
                if len(str(valor_simples)) > 50: valor_simples = "Ver Mapa"
                dados_para_salvar.append({"Campo": f"Mapa: {campo_simples}", "Valor": valor_simples, "Descricao": "", "Resultado": valor_simples})

        perfil_json_str = json.dumps(dados_para_salvar, ensure_ascii=False)
        
        if client:
            client.table("mapas_salvos").update({"perfil_json": perfil_json_str}).eq("nome", nome).execute()
            st.toast("✅ Dados sincronizados com sucesso!")
            st.cache_data.clear()
        else:
            # Salvar no armazenamento local da sessão
            if "clientes_local_data" in st.session_state and nome in st.session_state["clientes_local_data"]:
                perfil_val, categoria_val, qualidades_val, kan_val, fortaleza_val, desafio_val = "", "", "", None, "", ""
                for item in dados_para_salvar:
                    campo_norm = normalize_key(item.get('Campo', ''))
                    raw_val = item.get('Resultado', item.get('Valor', ''))
                    if campo_norm == 'perfil': perfil_val = raw_val
                    elif campo_norm == 'categoria': categoria_val = raw_val
                    elif campo_norm == 'qualidades': qualidades_val = raw_val
                    elif campo_norm == 'kan':
                        try: kan_val = int(raw_val)
                        except: kan_val = raw_val
                    elif campo_norm == 'fortaleza': fortaleza_val = raw_val
                    elif campo_norm == 'desafio': desafio_val = raw_val
                    elif campo_norm == 'estrutural': st.session_state["clientes_local_data"][nome]['estrutural'] = raw_val
                    elif campo_norm == 'direcionamento': st.session_state["clientes_local_data"][nome]['direcionamento'] = raw_val
                    elif 'repeticao 1' in campo_norm: st.session_state["clientes_local_data"][nome]['repeticao_1'] = raw_val
                    elif 'repeticao 2' in campo_norm: st.session_state["clientes_local_data"][nome]['repeticao_2'] = raw_val
                    elif "mapa:" in campo_norm:
                        nome_campo_mapa = item['Campo'].split("Mapa:")[1].strip()
                        st.session_state["clientes_local_data"][nome]['mapa_detalhado'][nome_campo_mapa] = raw_val
                
                st.session_state["clientes_local_data"][nome]['perfil'] = perfil_val
                st.session_state["clientes_local_data"][nome]['categoria'] = categoria_val
                st.session_state["clientes_local_data"][nome]['qualidades'] = qualidades_val
                st.session_state["clientes_local_data"][nome]['kan'] = kan_val
                st.session_state["clientes_local_data"][nome]['fortaleza'] = fortaleza_val
                st.session_state["clientes_local_data"][nome]['desafio'] = desafio_val
                st.session_state["clientes_local_data"][nome]['has_json'] = True
                st.toast("✅ Dados calculados e salvos localmente na sessão atual!")

    except Exception as e:
        import streamlit as st
        st.error(f"Erro ao salvar: {e}")

CARGOS_LIST_DEFAULT = [
    "Trainee", "Aprendiz", "Auxiliar", "Assistente", "Atendente", "Operador", "Técnico", "Técnico líder",
    "Analista", "Analista júnior", "Analista pleno", "Analista sênior",
    "Especialista", "Especialista júnior", "Especialista pleno", "Especialista sênior", "Especialista líder", "Especialista principal",
    "Principal", "Consultor", "Consultor sênior", "Consultor estratégico", "Assessor", "Assessor sênior",
    "Auditor", "Perito", "Supervisor", "Supervisor de equipe", "Líder de equipe", "Líder de operação",
    "Coordenador", "Coordenador sênior", "Coordenador regional", "Coordenador corporativo", "Coordenador de projetos",
    "Encarregado", "Chefe de área", "Facilitador", "Gestão tática",
    "Gerente", "Gerente júnior", "Gerente pleno", "Gerente sênior", "Gerente de operações", "Gerente de unidade", "Gerente regional", "Gerente executivo",
    "Head", "Head de especialidade", "Head de operações", "Head de produto", "Head de projetos",
    "Diretor adjunto", "Diretor", "Diretor sênior", "Diretor executivo", "Diretor-presidente",
    "Vice-presidente", "Vice-presidente sênior", "Presidente", "CEO", "COO", "CFO", "CIO", "CTO", "CMO", "CHRO", "CRO", "CHO", "CPO",
    "Sócio", "Sócio fundador", "Sócio-diretor", "Sócio-administrador", "Conselheiro", "Membro do conselho", "Chairman",
    "Vendedor", "Vendedor consultivo", "Executivo de vendas", "Executivo de contas", "Key Account Manager", "Account Manager",
    "Pre-sales", "Customer Success", "Customer Success Manager", "Business Development Representative", "Sales Development Representative",
    "Closer", "Farmer", "Hunter"
]

@st.cache_data(ttl=600)
def carregar_cargos():
    client = get_supabase()
    if client:
        try:
            res = client.table("cargos").select("nome").order("nome").execute()
            if res.data:
                return [row["nome"] for row in res.data]
        except Exception:
            pass
    return CARGOS_LIST_DEFAULT

@st.cache_data(ttl=60)
def carregar_equipes():
    client = get_supabase_admin()
    if client:
        try:
            res = client.table("equipes").select("*").order("nome").execute()
            # res.data pode ser [] lista vazia — isso é válido, não é erro
            if res.data is not None:
                return res.data
        except Exception as e:
            st.session_state["equipes_load_error"] = str(e)
    if "equipes_local_data" not in st.session_state:
        st.session_state["equipes_local_data"] = []
    return st.session_state["equipes_local_data"]
