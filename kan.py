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
import base64

def remover_acentos(texto):
    if texto is None: return ""
    texto_str = str(texto).replace('º', 'o').replace('ª', 'a')
    texto_str = texto_str.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'").replace('–', '-').replace('—', '-')
    norm = ''.join(c for c in unicodedata.normalize('NFD', texto_str) if unicodedata.category(c) != 'Mn')
    return norm.encode('latin-1', 'ignore').decode('latin-1')

def normalize_key(k):
    if k is None: return ""
    # Remove acentos, espaços, underscores, hífens, parênteses e pontos
    n = remover_acentos(k).lower()
    for char in [' ', '_', '-', '(', ')', '.', 'º', 'o', 'ª', 'a']:
        n = n.replace(char, '')
    return n

def get_from_row(row, key):
    # Busca ultra-robusta: ignora case, acentos, espaços, underscores e hífens
    if not row: return None
    search_key = normalize_key(key)
    for k in row.keys():
        if normalize_key(k) == search_key:
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
st.set_page_config(page_title="KAN Perfil Comportamental", layout="wide", page_icon=favicon_img)

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

# --- CACHED FETCH ---

@st.cache_data(ttl=3600)
def fetch_arcanos():
    try:
        resp = supabase_client.table("arcanos").select("*").execute()
        return {str(int(get_from_row(row, 'numero'))): {"nome": get_from_row(row, 'nome'), "descricao": get_from_row(row, 'descricao')} for row in resp.data if get_from_row(row, 'numero') is not None}
    except Exception:
        return {}

ARCANOS_DB = fetch_arcanos()

@st.cache_data(ttl=3600)
def fetch_fortalezas():
    try:
        resp = supabase_client.table("fortalezas").select("*").execute()
        return {str(int(get_from_row(row, 'triangulo'))): {"fortaleza": get_from_row(row, 'fortaleza'), "descricao": get_from_row(row, 'descricao')} for row in resp.data if get_from_row(row, 'triangulo') is not None}
    except Exception:
        return {}

FORTALEZAS_DB = fetch_fortalezas()

@st.cache_data(ttl=3600)
def fetch_kan():
    try:
        resp = supabase_client.table("kans").select("*").execute()
        return {str(int(get_from_row(row, 'numero'))): {"kan": get_from_row(row, 'kan'), "descricao": get_from_row(row, 'descricao')} for row in resp.data if get_from_row(row, 'numero') is not None}
    except Exception:
        return {}

KAN_DB = fetch_kan()

@st.cache_data(ttl=3600)
def fetch_desafios():
    try:
        resp = supabase_client.table("desafios").select("*").execute()
        return {str(int(get_from_row(row, 'dia_nascimento'))): {"desafio": get_from_row(row, 'desafio'), "descricao": get_from_row(row, 'descricao')} for row in resp.data if get_from_row(row, 'dia_nascimento') is not None}
    except Exception:
        return {}

DESAFIOS_DB = fetch_desafios()

def get_supabase():
    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

def fetch_matriz():
    try:
        client = get_supabase()
        if client:
            resp = client.table("matriz").select("*").execute()
            if resp.data:
                res_dict = {}
                for row in resp.data:
                    num_val = get_from_row(row, 'numero') or get_from_row(row, 'Resultado')
                    if num_val is not None:
                        try:
                            # Tenta normalizar para string de inteiro (ex: "29.0" -> "29")
                            key_str = str(int(float(num_val)))
                        except:
                            key_str = str(num_val).strip()
                        res_dict[key_str] = row
                if res_dict:
                    return res_dict
    except Exception:
        pass
        
    try:
        df = pd.read_csv("Tabela Matriz.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("Tabela Matriz.csv", sep=",")
        resultado = {}
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            num_val = row_dict.get('Resultado', row_dict.get('numero', ''))
            if pd.notna(num_val):
                try:
                    num_val_str = str(int(float(num_val)))
                except:
                    num_val_str = str(num_val).strip()
                
                if num_val_str:
                    cleaned_row = {remover_acentos(k): v for k, v in row_dict.items()}
                    resultado[num_val_str] = cleaned_row
        return resultado
    except Exception:
        return {}

MATRIZ_DB = fetch_matriz()

def fetch_atributos():
    try:
        client = get_supabase()
        if client:
            resp = client.table("atributos").select("*").execute()
            if resp.data:
                res_dict = {}
                for row in resp.data:
                    attr_val = str(get_from_row(row, 'atributo') or get_from_row(row, 'ATRIBUTOS') or '').upper()
                    if attr_val:
                        res_dict[attr_val] = row
                if res_dict:
                    return res_dict
    except Exception:
        pass
        
    try:
        df = pd.read_csv("Atributos.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("Atributos.csv", sep=",")
        resultado = {}
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            attr_val = str(get_from_row(row_dict, 'atributo') or get_from_row(row_dict, 'ATRIBUTOS') or '').upper()
            if attr_val:
                resultado[attr_val] = row_dict
        return resultado
    except Exception:
        return {}

ATRIBUTOS_DB = fetch_atributos()

def fetch_repeticao():
    try:
        client = get_supabase()
        if client:
            resp = None
            try:
                resp = client.table("repeticao").select("*").execute()
            except:
                resp = client.table("repeticao_descricao").select("*").execute()
            
            if resp and resp.data:
                res_dict = {}
                for row in resp.data:
                    rep_val = get_from_row(row, 'repeticao')
                    if rep_val is not None:
                        res_dict[str(int(float(rep_val)))] = row
                if res_dict:
                    return res_dict
    except Exception:
        pass
        
    try:
        df = pd.read_csv("Repeticao.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("Repeticao.csv", sep=",")
        resultado = {}
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            rep_val = str(int(float(get_from_row(row_dict, 'repeticao')))) if get_from_row(row_dict, 'repeticao') else ''
            if rep_val:
                resultado[rep_val] = row_dict
        return resultado
    except Exception:
        return {}

REPETICAO_DB = fetch_repeticao()

@st.cache_data(ttl=3600)
def fetch_peso():
    try:
        client = get_supabase()
        if client:
            resp = client.table("peso").select("*").execute()
            if resp.data:
                res_dict = {row['campo']: row['peso'] for row in resp.data}
                if res_dict:
                    return res_dict
    except Exception:
        pass
        
    try:
        df = pd.read_csv("peso.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("peso.csv", sep=",")
        return {row['campo']: row['peso'] for _, row in df.iterrows()}
    except Exception:
        return {}

PESO_DB = fetch_peso()

@st.cache_data(ttl=3600)
def fetch_perfis():
    try:
        client = get_supabase()
        if client:
            resp = client.table("perfis").select("*").execute()
            if resp.data:
                return [row['perfil'] for row in resp.data]
    except Exception:
        pass
        
    try:
        df = pd.read_csv("perfil.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("perfil.csv", sep=",")
        return [row['perfil'] for _, row in df.iterrows() if 'perfil' in row]
    except Exception:
        return ["Lider", "Criativo", "Executor", "Resultado", "Vendedor", "Influenciador", "Comunicador"]

PERFIS_DB = fetch_perfis()

@st.cache_data(ttl=3600)
def fetch_perfil_descricao():
    try:
        client = get_supabase()
        if client:
            resp = client.table("perfil_descricao").select("*").execute()
            if resp.data:
                return {str(get_from_row(row, 'perfil')).strip().capitalize(): get_from_row(row, 'descricao') for row in resp.data}
    except Exception:
        pass
        
    try:
        df = pd.read_csv("perfil_descricao.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("perfil_descricao.csv", sep=",")
        return {str(get_from_row(row.to_dict(), 'perfil')).strip().capitalize(): get_from_row(row.to_dict(), 'descricao') for _, row in df.iterrows()}
    except Exception:
        return {}

PERFIL_DESCRICAO_DB = fetch_perfil_descricao()

@st.cache_data(ttl=3600)
def fetch_qualidades():
    try:
        client = get_supabase()
        if client:
            resp = client.table("qualidades").select("*").execute()
            if resp.data:
                return {str(get_from_row(row, 'qualidade')).strip().capitalize(): get_from_row(row, 'descricao') for row in resp.data}
    except Exception:
        pass
        
    try:
        df = pd.read_csv("Qualidades.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("Qualidades.csv", sep=",")
        return {str(get_from_row(row.to_dict(), 'qualidade')).strip().capitalize(): get_from_row(row.to_dict(), 'descricao') for _, row in df.iterrows()}
    except Exception:
        return {}

QUALIDADES_DB = fetch_qualidades()

@st.cache_data(ttl=3600)
def fetch_lista_categoria():
    try:
        client = get_supabase()
        if client:
            resp = client.table("lista_categoria").select("*").execute()
            if resp.data:
                return [get_from_row(row, 'categoria') for row in resp.data]
    except Exception:
        pass
        
    try:
        df = pd.read_csv("lista_categoria.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("lista_categoria.csv", sep=",")
        return [get_from_row(row.to_dict(), 'categoria') for _, row in df.iterrows()]
    except Exception:
        return []

LISTA_CATEGORIA_DB = fetch_lista_categoria()

@st.cache_data(ttl=3600)
def fetch_categoria_descricao():
    try:
        client = get_supabase()
        if client:
            resp = client.table("categoria_descricao").select("*").execute()
            if resp.data:
                return {str(get_from_row(row, 'categoria')).strip().capitalize(): get_from_row(row, 'descricao') for row in resp.data}
    except Exception:
        pass
        
    try:
        df = pd.read_csv("categoria_descricao.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("categoria_descricao.csv", sep=",")
        return {str(get_from_row(row.to_dict(), 'categoria')).strip().capitalize(): get_from_row(row.to_dict(), 'descricao') for _, row in df.iterrows()}
    except Exception:
        return {}

CATEGORIA_DESCRICAO_DB = fetch_categoria_descricao()

@st.cache_data(ttl=3600)
def fetch_peso_categoria():
    try:
        client = get_supabase()
        if client:
            resp = client.table("peso_categoria").select("*").execute()
            if resp.data:
                return {row['campo']: row['peso'] for row in resp.data}
    except Exception:
        pass
        
    try:
        df = pd.read_csv("peso_categoria.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("peso_categoria.csv", sep=",")
        return {row['campo']: row['peso'] for _, row in df.iterrows()}
    except Exception:
        return {}

@st.cache_data(ttl=3600)
def fetch_campo_definicao():
    """Busca as definições conceituais dos campos na tabela campo_definicao."""
    try:
        client = get_supabase()
        if client:
            resp = client.table("campo_definicao").select("*").execute()
            if resp.data:
                # Retorna dicionário {campo: explicacao}
                return {str(get_from_row(row, 'campo')): get_from_row(row, 'explicacao') for row in resp.data}
    except Exception:
        pass

    try:
        df = pd.read_csv("campo_definicao.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("campo_definicao.csv", sep=",")
        return {row['CAMPO']: row['EXPLICACAO'] for _, row in df.iterrows()}
    except Exception:
        return {}

CAMPO_DEFINICAO_DB = fetch_campo_definicao()
PESO_CATEGORIA_DB = fetch_peso_categoria()

@st.cache_data(ttl=3600)
def fetch_diferenciais_descricao():
    try:
        client = get_supabase()
        if client:
            resp = client.table("diferenciais_descricao").select("*").execute()
            if resp.data:
                return {str(get_from_row(row, 'no')): {'diferencial': get_from_row(row, 'diferencial'), 'descricao': get_from_row(row, 'descricao')} for row in resp.data}
    except Exception:
        pass
        
    try:
        df = pd.read_csv("diferenciais_descricao.csv", sep=";")
        if df.shape[1] <= 1:
            df = pd.read_csv("diferenciais_descricao.csv", sep=",")
        return {str(get_from_row(row.to_dict(), 'no')): {'diferencial': get_from_row(row.to_dict(), 'diferencial'), 'descricao': get_from_row(row.to_dict(), 'descricao')} for _, row in df.iterrows()}
    except Exception:
        return {}

DIFERENCIAIS_DESC_DB = fetch_diferenciais_descricao()

@st.cache_data(ttl=3600)
def fetch_descricoes_mapa():
    """Busca o dicionário de descrições numerológicas da tabela descricoes_mapa."""
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
        {'categoria': '1º Ciclo de Vida', 'valor': '1', 'descricao': 'O 1 (um) no primeiro Ciclo de Vida indica um período difícil. Quando criança, a pessoa necessita aprender a desenvolver sua individualidade, pois caso contrário, na juventude e adolescência ou mesmo até à entrada do 2º Ciclo, terá problemas emocionais e grande dificuldade de se estabilizar profissionalmente. O ideal é que a criança nesse Ciclo tenha liberdade acima do normal e não frear os seus instintos em hipótese alguma. No caso de pessoa maior de 18 anos e que ainda esteja no primeiro Ciclo e tenha sido reprimida, ou seja, não tenha tido educação condizente, que absorva estes ensinamentos e os coloque em prática imediatamente.'}, {'categoria': '1º Ciclo de Vida', 'valor': '2', 'descricao': 'O 2 (dois) no primeiro Ciclo de Vida, indica uma criança extremamente mimada, que possivelmente sofreu grande influência da mãe ou dos avós. É natural que na adolescência, em vista da possessiveness familiar, pense em casar-se o mais cedo possível e isso é muito comum, principalmente entre os homens.'}, {'categoria': '1º Ciclo de Vida', 'valor': '3', 'descricao': 'O 3 (três) indica uma infância e adolescência feliz, despreocupada e com muitos amigos. Não é um período particularmente favorável ao aprendizado, que deverá ocorrer a partir do segundo Ciclo, mas haverá provavelmente muitas oportunidades para a expressão de idéias e emoções, após os 18 anos (alguns com menos idade), através das artes em geral, da música, do teatro e escrita. Não é um bom período para contrair matrimônio.'}, {'categoria': '1º Ciclo de Vida', 'valor': '5', 'descricao': 'O 5 (cinco) no primeiro Ciclo de Vida indica muitas mudanças e uma liberdade que às vezes é demasiado grande para que se possa lidar com ela de maneira construtiva. Sem orientação adequada, o jovem nesse período pode ter problemas causados por envolvimentos precoces com sexo, álcool e drogas. É um péssimo período para o casamento e normalmente quando isso acontece, dura pouco. Também no lado profissional a pessoa tem dificuldade de se assentar, mudando continuamente de emprego ou atividade, que só terá término quando da entrada no segundo Ciclo.'}, {'categoria': '1º Ciclo de Vida', 'valor': '6', 'descricao': 'O 6 (seis) indica infância e juventude restritiva, cheia de deveres e responsabilidades e, para fugir dessa restrição, normalmente casa-se cedo e muitas vezes esse casamento é um completo fracasso, pois não é escorado em bases sólidas do amor e sim como uma fuga. Tem, também, dificuldades em se ajustar à sociedade, pois é incompreendido nos seus planos e objetivos.'}, {'categoria': '1º Ciclo de Vida', 'valor': '7', 'descricao': 'O 7 (sete) no primeiro Ciclo de Vida indica um período muito difícil. A criança e o jovem conservam-se retraídos e podem sofrer com a falta de compreensão dos pais, professores e amigos. Tal incompreensão leva, invariavelmente, ao isolamento, retraimento e até medo de encarar a vida nessa fase. Na faixa dos 20 anos, em virtude dessa retração, pode desenvolver complexos de culpa e falta de autoconfiança, restringindo o seu progresso pessoal e profissional.'}, {'categoria': '1º Ciclo de Vida', 'valor': '8', 'descricao': 'O 8 (oito) no primeiro Ciclo de Vida indica um período de realizações. É extraordinário para o aprendizado acerca dos aspectos materiais da vida. É nesse período que se forjam os homens de negócios, comércio, políticos, advogados e todos aqueles que pensam mais no material do que no espiritual.'}, {'categoria': '2º Ciclo de Vida', 'valor': '1', 'descricao': 'O 1 (um) no segundo Ciclo de Vida mostra um período de ambições, um grande desejo de realizações e também de sucesso relativo. A pessoa necessita desenvolver seus próprios recursos, estudando e se dedicando o máximo possível, além de lutar para tornar-se independente e chegar ao terceiro Ciclo já com definição profissional, social e financeira.'}, {'categoria': '2º Ciclo de Vida', 'valor': '2', 'descricao': 'O 2 (dois) neste período é indicador de sociabilidade e receptividade. É necessário cultivar a paciência, o tato, a diplomacia e a capacidade de perceber os sentimentos alheios. Pode indicar ainda, uma carreira diplomática, ser juiz, médico, professor ou consultor.'}, {'categoria': '2º Ciclo de Vida', 'valor': '3', 'descricao': 'O 3 (três) nos mostra uma fase agradável na vida, com certa despreocupação. É a fase da sociabilidade, na qual a criatividade e a originalidade podem exteriorizar suas idéias e sentimentos através de algum tipo de arte: pintura, música, teatro, escrita, etc. É um magnífico período para se desenvolver a criatividade, porém, não deve despender demasiada energia, principalmente em coisas fúteis.'}, {'categoria': '2º Ciclo de Vida', 'valor': '4', 'descricao': 'O 4 (quatro) é sinônimo de trabalho duro, de produtividade e de construção do alicerce que deverá se apoiar no futuro. É um período em que a pessoa necessita aprender a aceitar a rotina e a trabalhar em algo produtivo, sólido e a fazer grande economia.'}, {'categoria': '2º Ciclo de Vida', 'valor': '5', 'descricao': 'O 5 (cinco) é indicativo de um período de expansão de horizontes, época propícia a viagens, mudanças, romances, liberdade, de novas atividades e também novos amigos. Quase sempre, neste período, a pessoa terá de encontrar as suas oportunidades, longe do domicílio. Precisa aprender a se adaptar, a procurar novas maneiras de ver as coisas e a evitar a tendência para fixar-se num determinado lugar. Em resumo, é um período de grande movimentação, de grandes mudanças e de novos horizontes.'}, {'categoria': '2º Ciclo de Vida', 'valor': '6', 'descricao': 'O 6 (seis) neste Ciclo nos mostra um período de ajustes e de responsabilidades nos assuntos domésticos em geral. É um bom momento para se contrair matrimônio, ter filhos e solidificar a família. Em suma, é um período familiar, de colocar a casa em ordem, de viver mais para a família, e deixar de ser tanto individualista.'}, {'categoria': '2º Ciclo de Vida', 'valor': '7', 'descricao': 'O 7 (sete) indica um período de crescimento tranquilo, de estudos e de meditação. A menos que esteja casado, este não é um bom Ciclo para se contrair matrimônio, pois a pessoa necessita desenvolver seus recursos interiores e a incompreensão quase sempre aparece nesse período.'}, {'categoria': '2º Ciclo de Vida', 'valor': '8', 'descricao': 'O 8 (oito) neste Ciclo mostra um período de preocupação com os aspectos materiais da vida. Normalmente a pessoa tem tendência a adquirir riqueza e poder material. Existe, ainda, a grande possibilidade de realizações no mundo dos negócios, a ganhar muito dinheiro com o trabalho e também através de especulações.'}, {'categoria': '2º Ciclo de Vida', 'valor': '9', 'descricao': 'O 9 (nove) neste Ciclo traz a possibilidade de sucesso na vida pública. É um período altamente espiritual e a pessoa necessita aprender a cultivar a tolerância, o amor à humanidade, o altruísmo e o controle emocional. Dificilmente um romance é bem sucedido e os casamentos tendem a pouca duração caso sejam realizados neste período e também é indício de alguma perda, seja ela material, afetiva ou social.'}, {'categoria': '2º Ciclo de Vida', 'valor': '11', 'descricao': 'O 11 (onze) nos mostra um período de ideais, de revelações, de grandeza e, possivelmente, de fama. Aconselha- se que a pessoa se mantenha longe de empreendimentos comerciais ou de especulações, sejam elas financeiras ou imobiliárias. É o momento de desenvolver a mente, de especializar-se em alguma coisa, de estudar, ensinar e também de inspirar as outras pessoas através do seu próprio exemplo.'}, {'categoria': '2º Ciclo de Vida', 'valor': '22', 'descricao': 'O 22 (vinte e dois) no Segundo Ciclo é indício de grandes realizações e de liderança em alto nível. O objetivo primordial da pessoa neste Ciclo deve ser o de beneficiar a humanidade como um todo. Em virtude do grande poder deste número, os nervos e as emoções serão testados durante todo o período e a pessoa deve se manter o mais calmo possível e seguir a orientação da sua intuição.'}, {'categoria': '3º Ciclo de Vida', 'valor': '1', 'descricao': 'O 1 (um) nos indica um final de vida solitário. A pessoa precisa permanecer ativa e independente e contar com seus próprios recursos.'}, {'categoria': '3º Ciclo de Vida', 'valor': '2', 'descricao': 'O 2 (dois) mostra um período de amor sincero e de amigos íntimos. A pessoa se sentirá impelida a colecionar coisas, tais como selos, moedas, antiguidades ou qualquer coisa extravagante.'}, {'categoria': '3º Ciclo de Vida', 'valor': '3', 'descricao': 'O 3 (três) no terceiro Ciclo de Vida indica um período de expressão de idéias e sentimentos através de diversas formas de arte, música, teatro e literatura. A criatividade vai se desenvolver. Haverá muitos amigos e grande atividade social.'}, {'categoria': '3º Ciclo de Vida', 'valor': '4', 'descricao': 'O 4 (quatro) neste Ciclo nos mostra que a pessoa, mesmo aposentada, deverá continuar trabalhando, seja por necessidade, seja por escolha, pois o 4 não o deixará levar uma vida monótona e rotineira.'}, {'categoria': '3º Ciclo de Vida', 'valor': '5', 'descricao': 'O 5 (cinco) é o período da liberdade pessoal, de viagens, mudanças, de novas atividades e variedade, seja de amigos, de atividades ou de residência.'}, {'categoria': '3º Ciclo de Vida', 'valor': '6', 'descricao': 'O 6 (seis) poderá ser o mais agradável de todos os terceiros ciclos de vida - uma fase de felicidade e harmonia no lar - se a pessoa tiver aprendido a adaptar-se e assumir responsabilidades. Caso não tenha aprendido estas coisas, ela poderá ser sobrecarregada com muitos problemas domésticos.'}, {'categoria': '3º Ciclo de Vida', 'valor': '7', 'descricao': 'O 7 (sete) indica um período de isolamento ou de semi - isolamento. Trata-se de uma fase tranquila, apropriada para se estudar em casa e adquirir sabedoria e conhecimento.'}, {'categoria': '3º Ciclo de Vida', 'valor': '8', 'descricao': 'O 8 (oito) neste Ciclo mostra que a pessoa precisa agir com sabedoria, trabalhar e estudar duramente nos dois primeiros, quando terá grande possibilidade de ficar rico neste e ter poder e sucesso ilimitados no mundo dos negócios.'}, {'categoria': '3º Ciclo de Vida', 'valor': '9', 'descricao': 'O 9 (nove) mostra um período de retiro para o estudo e o aprendizado. A pessoa precisa cultivar a tolerância e o amor pela humanidade. Neste Ciclo geralmente há alguma espécie de perda.'}, {'categoria': '3º Ciclo de Vida', 'valor': '22', 'descricao': 'O 22 (vinte e dois) no terceiro ciclo de vida talvez torne a pessoa tensa e nervosa. Ela deve procurar manter-se ativa durante esse período e dedicar-se a um hobby, tal como a escultura, a pintura, as artes divinatórias, etc.'}, {'categoria': 'Desafio', 'valor': '1', 'descricao': 'Desafio 1 - O consulente precisará aprender a se situar num meio termo entre um sentimento excessivo ou insuficiente de sua própria personalidade ou importância. Precisa aprender a ser firme, positivo independente e autoconfiante, sem impor sua vontade às outras pessoas ou esperar que tudo gire em torno de si.'}, {'categoria': 'Desafio', 'valor': '2', 'descricao': 'Desafio 2 - Poderá tender a ser tão sensível em relação aos seus próprios sentimentos e a passar tanto tempo pensando neles, que acabará não tomando conhecimento dos sentimentos dos outros. Pequenas coisas são ampliadas fora de qualquer proporção e nunca esquecidas ou perdoadas. O consulente precisa aprender a cuidar de si mesmo, a cultivar uma atitude mais liberal e tolerante em relação à vida e a parar de utilizar seus próprios sentimentos e emoções como ponto de referência para tudo.'}, {'categoria': 'Desafio', 'valor': '3', 'descricao': 'Desafio 3 - Precisará aprender a situar-se num meio termo, entre ter medo de contatos sociais e ser por demais festeiro. Tem de aprender a ser sociável e a exprimir suas idéias e sentimentos sem dispersar suas energias ou comportar-se como pessoa fútil.'}, {'categoria': 'Desafio', 'valor': '4', 'descricao': 'Desafio 4 - É o mais fácil de todos os desafios, visto que não há nenhum conflito envolvido. Precisa aprender a situar-se num meio termo entre agir como um “burro de carga” ou ser preguiçoso.'}, {'categoria': 'Desafio', 'valor': '5', 'descricao': 'Desafio 5 - Precisa aprender a situar-se num meio- termo entre desejar uma liberdade excessiva e ter um receio injustiçado dela - entre uma ânsia exagerada de experiências sensuais e o medo de tentar coisas novas. Precisa aprender a não buscar sexo, álcool e drogas e - o mais difícil de tudo - precisa aprender quando e como renunciar a pessoas ou coisas cuja presença na sua vida não tem mais razão de ser.'}, {'categoria': 'Desafio', 'valor': '6', 'descricao': 'Desafio 6- Precisa aprender a situar-se num meio termo entre comportar-se como um “capacho” ou ser demasiado exigente e dominador. Precisa aprender a aceitar as pessoas como elas são sem esperar que elas vivam de acordo com os seus padrões; respeitar os pontos de vista de todos e não estabelecer regras além de você mesmo.'}, {'categoria': 'Desafio', 'valor': '7', 'descricao': 'Desafio 7 - Precisará aprender a situar-se num meio termo entre o orgulho excessivo e a modéstia exagerada. Deveria tomar cuidado para não se refugiar dentro de si mesmo e nem tentar escapar das coisas desagradáveis da vida, recorrendo ao álcool e às drogas. É particularmente uma boa educação, aprender a compreender o que se passa no mundo à sua volta e - acima de tudo - ter fé.'}, {'categoria': 'Desafio', 'valor': '8', 'descricao': 'Desafio 8 - Precisará aprender a situar-se num meio termo entre uma preocupação excessiva com as questões materiais, e um desinteresse exagerado em relação a esse assunto. Precisa aprender a utilizar corretamente o dinheiro e o poder e a voltar seu pensamento para outras coisas que não o dinheiro e o que ele poderá fazer por você.'}, {'categoria': 'Momento Decisivo', 'valor': '1', 'descricao': 'MOMENTO DECISIVO 1 - Não é um período fácil; exige coragem, determinação e muita força de vontade. É o momento propício para se “cultivar” a individualidade, a independência e a engenhosidade. Inúmeros acasos e situações inesperadas forçarão a pessoa a enfrentar a vida pensando e agindo por si mesma. Um Momento Decisivo 1 no primeiro Ciclo de Vida, indica uma criança agitada, voluntariosa e por vezes complicada, que será difícil controlar e compreender.'}, {'categoria': 'Momento Decisivo', 'valor': '2', 'descricao': 'MOMENTO DECISIVO 2 - Traz consigo a oportunidade para “cultivar” o tato e a compreensão. Se for amigo, companheiro e atencioso com seus semelhantes, este será um período de amizades sinceras e de relacionamentos duradouros. Excelente fase para se contrair matrimônio. Se for impaciente e desatencioso, poderá ser uma fase de relacionamentos difíceis, de grandes incompreensões, brigas, discussões, em que você poderá causar graves prejuízos às pessoas que o cercam. Um Momento Decisivo 2 no primeiro Ciclo de Vida, é indício de uma “mãe” forte e dominadora, ou pai ausente (por motivo de trabalho, morte ou separação). A criança, nesse caso, pode se tornar excessivamente sensível e ter reflexos dessa sensibilidade na juventude e adolescência, obstruindo dessa maneira, as possibilidades de progresso.'}, {'categoria': 'Momento Decisivo', 'valor': '3', 'descricao': 'MOMENTO DECISIVO 3 - É o momento de expandir a vida social e “cultivar” os próprios talentos. Trata-se de uma fase apropriada para a auto-expressão, novas amizades, romance e fertilidade. A manifestação descuidada das emoções poderá ter consequências desagradáveis, pois existe, nesse estado, tendência ao desmando: vícios, brigas, discórdias. Cuidado com os “amigos”, pois apesar de serem necessários, por vezes são más companhias. Um Momento Decisivo 3 no primeiro Ciclo de Vida, geralmente indica uma criança com dificuldade de se adaptar aos estudos. Indica, também, oportunidades artísticas que se não alimentadas e direcionadas condizentemente, poderão ser desperdiçadas, fazendo com que a pessoa já adulta venha a se lamentar dessa negligência dos pais ou educadores.'}, {'categoria': 'Momento Decisivo', 'valor': '4', 'descricao': 'MOMENTO DECISIVO 4 - Este Momento Decisivo traz a oportunidade de se construir um sólido alicerce para o futuro. É um período de trabalho duro e até de algumas restrições e é necessário “cultivar” a paciência e os bons hábitos de trabalho. Neste período, poderá haver alguns problemas econômicos, que serão superados com inteligência, trabalho e dedicação ao projeto final. A família e os parentes por afinidade podem se transformar num peso e a pessoa terá de ajudá-los, tanto financeiramente, como prestando ajuda humanitária, em uma doença, por exemplo. As recompensas sempre aparecem a partir da aplicação dos preceitos corretos de vida e do esforço para se obter os resultados positivos. Um Momento Decisivo 4 no primeiro Ciclo de Vida, frequentemente indica que a pessoa poderá começar a trabalhar muito nova e a assumir grandes responsabilidades ainda na juventude.'}, {'categoria': 'Momento Decisivo', 'valor': '5', 'descricao': 'MOMENTO DECISIVO 5 - Traz oportunidades para viagens, para experimentar novas sensações, novos empreendimentos e para se livrar de tudo que está obsoleto ou que já não nos faz falta. É uma fase de liberdade, de mudanças e de desenvolvimento pessoal, principalmente se vier após um Momento decisivo 4 ou 6. Um Momento Decisivo 5 no primeiro Ciclo de Vida, indica uma criança ousada, inquieta, esperta e pouco constante. Geralmente empreende mudanças súbitas, ora gostando disto, ora daquilo, sem esperar as recompensas resultantes de um esforço ou trabalho empreendido.'}, {'categoria': 'Momento Decisivo', 'valor': '6', 'descricao': 'MOMENTO DECISIVO 6 - É o momento dos ajustes e das responsabilidades familiares. Caso tenha consciência disso, este é o Momento de grande afetividade, de amor e de felicidade doméstica, além de sucesso e segurança material. Do contrário, ou seja, caso seja dispersivo ou inconstante, poderá ser um período de desgostos, discussões, brigas e graves problemas domésticos e até indício de separação. Um Momento Decisivo 6 no primeiro Ciclo de Vida, geralmente indica casamento precoce ou a responsabilidade de tomar conta dos pais ou de algum familiar. Quando o 6 for o último Momento Decisivo, ele poderá trazer o reconhecimento do trabalho já feito. Caso a pessoa esteja solteira, este Momento trará a oportunidade para um novo amor e para o materialismo.'}, {'categoria': 'Momento Decisivo', 'valor': '7', 'descricao': 'MOMENTO DECISIVO 7 - É uma fase de introspecção, de meditação e estudo do significado último da vida. Caso não esteja casado, desaconselhamos o matrimônio nesta fase. Velhos relacionamentos que não produzem mais frutos, podem e devem ser deixados para trás. A pessoa normalmente sente vontade de se retirar para dentro de si mesma, o que de certa forma poderá causar problemas de relacionamento, tanto a nível pessoal como familiar. Um Momento Decisivo 7 no primeiro Ciclo de Vida, nos indica uma criança retraída, solitária, pensativa e muito estuda. Quando os pais são excessivamente rígidos e severos, a criança poderá, pela regressão de suas idéias e projetos, contrair algum tipo de doença psicossomática ou mesmo depressão, ser temperamental e desenvolver algum tipo de complexo.'}, {'categoria': 'Momento Decisivo', 'valor': '8', 'descricao': 'MOMENTO DECISIVO 8 - É um período de grandes realizações no mundo dos negócios. As despesas são altas, não obstante, é uma excelente fase para se correr atrás dos objetivos, de conquistar poder, fama e sucesso material. Com dedicação, estudo e trabalho sistemático, com objetivo definido e com colaboradores aptos e interessados, a pessoa dificilmente deixa de conseguir tudo o que deseja. Um Momento Decisivo 8 no primeiro Ciclo de Vida, indica que a pessoa começará ainda jovem a se dedicar aos negócios, a trabalhar para se sustentar e também sustentar algum membro da família.'}, {'categoria': 'Momento Decisivo', 'valor': '9', 'descricao': 'MOMENTO DECISIVO 9 - Traz a oportunidade para se “cultivar” o amor, a solidariedade, o altruísmo e para se viajar para o exterior. Poderá haver algum tipo de perda e até desapontamentos, principalmente entre amigos. Um bom investimento para o consulente é fazer obras humanitárias durante este período, pois os frutos dessa plantação são certos, e o sucesso e a fama se farão presentes. Um Momento Decisivo 9 no primeiro Ciclo de Vida, normalmente não é dos mais afortunados, pois quase sempre a criança é incompreendida por colegas, amigos e até familiares, que por causa dessa incompreensão exigem muito e retribuem pouco, o que faz com que o jovem se retraia e fique tímido e introspectivo.'}, {'categoria': 'Momento Decisivo', 'valor': '11', 'descricao': 'MOMENTO DECISIVO 11 - Por ser um número altamente espiritual e elevado, a pessoa nesse período sente-se tensa e muito nervosa. É uma excelente fase para estudar esoterismo, espiritualismo e expandir seus horizons. Este momento traz inspiração, iluminação e, quase sempre, fama e prestígio nacional e até internacional. Não faça nada nem diga por trás o que não teria coragem de dizer ou fazer na frente das pessoas.'}, {'categoria': 'Momento Decisivo', 'valor': '22', 'descricao': 'MOMENTO DECISIVO 22 - É, sem dúvida alguma, o número e o Momento mais pode-roso. A pessoa fica altamente criativa e neste estado tornam-se possíveis todas as realizações. É uma fase de interesses pelos problemas mundiais e de grande expansão da consciência.'}]
    
    resultado = {}
    
    # Preenche inicialmente com o fallback local
    for item in REMAINING_DESCRIPTIONS:
        cat = item['categoria']
        val = str(item['valor'])
        desc = item['descricao']
        if cat not in resultado:
            resultado[cat] = {}
        resultado[cat][val] = desc

    try:
        from supabase import create_client, Client
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase_client: Client = create_client(url, key)
        
        # Tenta fazer upsert dos dados locais
        try:
            check_resp = supabase_client.table("descricoes_mapa").select("id").eq("categoria", "Desafio").limit(1).execute()
            if not check_resp.data:
                supabase_client.table("descricoes_mapa").upsert(REMAINING_DESCRIPTIONS).execute()
        except Exception:
            pass

        # Sobrescreve com o que está no banco de dados
        resp = supabase_client.table("descricoes_mapa").select("*").execute()
        for row in resp.data:
            cat = get_from_row(row, 'categoria') or ""
            val = str(get_from_row(row, 'valor') or "")
            desc = get_from_row(row, 'descricao') or ""
            res = get_from_row(row, 'resumo') or ""
            if cat:
                if cat not in resultado:
                    resultado[cat] = {}
                resultado[cat][val] = {"descricao": desc, "resumo": res}
    except Exception:
        pass
        
    return resultado

DESCRICOES_MAPA_DB = fetch_descricoes_mapa()

def get_desc_mapa(categoria, valor):
    """Retorna a descrição resumida (ou completa se o resumo não existir)."""
    if not DESCRICOES_MAPA_DB:
        return ""
    cat_data = DESCRICOES_MAPA_DB.get(categoria, {})
    entry = cat_data.get(str(valor), "")
    
    if isinstance(entry, dict):
        # Prioriza o resumo, se não houver, usa a descrição
        return entry.get("resumo") if str(entry.get("resumo")).strip() else entry.get("descricao", "")
    return entry


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
    while n > 9 and n not in [11, 22]:
        n = sum(int(d) for d in str(n))
    return n

letter_values = {
    'A':1, 'B':2, 'C':3, 'D':4, 'E':5, 'F':8, 'G':3, 'H':5, 'I':1, 'J':1, 'K':2,
    'L':3, 'M':4, 'N':5, 'O':7, 'P':8, 'Q':1, 'R':2, 'S':3, 'T':4, 'U':6, 'V':6,
    'W':6, 'X':6, 'Y':1, 'Z':7, 'Ç':6, 'Ê':3, 'É':7, 'Í':3, 'Ó':9, 'Á':3, 'Ú':8,
    'Ã':4, 'Å':8, 'Ñ':8, 'Ù':3, 'Û':4, 'À':2, 'Ö':5, 'Ô':5, 'È':1, 'Â':8, 'Ì':2, 'Ï':2
}

def reduce_number(n):
    while n > 9 and n not in (11, 22):
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
        user = st.session_state.get("username", "")
        pwd = st.session_state.get("password", "")
        if user in USUARIOS and USUARIOS[user] == pwd:
            st.session_state["password_correct"] = True
            if "password" in st.session_state:
                del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    def render_login_header():
        if header_img != "🔮":
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.image(header_img, use_container_width=True)
        st.markdown("<h4 style='text-align: center;'>Diagnóstico comportamental instantâneo. Sem testes. Sem manipulação.</h4>", unsafe_allow_html=True)
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

# --- CABEÇALHO ---
# --- CABEÇALHO ---
col_logo, col_empty = st.columns([1, 4])
with col_logo:
    if header_img != "🔮":
        st.image(header_img, width=150)
    else:
        st.markdown("<h3 style='margin:0; color: #F18617;'>🔮 KAN</h3>", unsafe_allow_html=True)

def get_base64_of_bin_file(bin_file):
    if not os.path.exists(bin_file):
        return ""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def render_home():
    # Caminhos padrão (Arquivos locais na pasta PROG)
    banner1_path = "banner1.png"
    banner2_path = "banner2.png"
    banner3_path = "banner3.png"


    if 'carousel_index' not in st.session_state:
        st.session_state.carousel_index = 0
    
    # Inicializa dados dos banners se não existirem
    if 'banners_data' not in st.session_state:
        st.session_state.banners_data = [
            {"title": "Diagnóstico Inteligente", "subtitle": "Análise comportamental profunda e instantânea.", "accent": "#F18617", "cta": "Explorar Diagnósticos", "link": "#", "img_path": banner1_path},
            {"title": "Gestão de Talentos", "subtitle": "Dados precisos para equipes de alta performance.", "accent": "#00d2ff", "cta": "Ver Equipes", "link": "#", "img_path": banner2_path},
            {"title": "Inovação Humana", "subtitle": "A inteligência por trás do comportamento.", "accent": "#39ff14", "cta": "Saiba Mais", "link": "#", "img_path": banner3_path}
        ]
    
    current_b = st.session_state.banners_data[st.session_state.carousel_index]
    
    # Carrega imagem (base64 customizada ou do path padrão)
    if current_b.get('b64_custom'):
        img_b64 = current_b['b64_custom']
    else:
        img_b64 = get_base64_of_bin_file(current_b.get('img_path', ""))

    # Injeção de CSS para o Carrossel Moderno
    st.markdown(f"""
    <style>
    .main-hero {{
        position: relative;
        width: 100%;
        height: 500px;
        background-color: #111;
        background-image: url('data:image/png;base64,{img_b64}');
        background-size: cover;
        background-position: center;
        border-radius: 30px;
        overflow: hidden;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        padding: 60px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.5);
        transition: all 0.8s ease;
    }}
    .hero-overlay {{
        background: linear-gradient(90deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.4) 50%, rgba(0,0,0,0) 100%);
        position: absolute;
        top:0; left:0; width:100%; height:100%;
        z-index: 1;
    }}
    .hero-content {{
        position: relative;
        z-index: 10;
        max-width: 600px;
    }}
    .hero-label {{
        background-color: {current_b['accent']};
        color: black;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9em;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 20px;
    }}
    .hero-title {{
        font-size: 4.2em;
        font-weight: 900;
        color: white;
        margin-bottom: 15px;
        line-height: 1.05;
        letter-spacing: -2px;
    }}
    .hero-subtitle {{
        font-size: 1.6em;
        color: rgba(255,255,255,0.8);
        margin-bottom: 35px;
        line-height: 1.3;
    }}
    .hero-cta {{
        background-color: white;
        color: black;
        padding: 15px 40px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 1.1em;
        text-decoration: none;
        display: inline-block;
        transition: 0.3s;
    }}
    .hero-cta:hover {{
        background-color: {current_b['accent']};
        transform: translateY(-3px);
    }}
    </style>
    
    <div class='main-hero'>
        <div class='hero-overlay'></div>
        <div class='hero-content'>
            <div class='hero-label'>Mundo KAN</div>
            <div class='hero-title'>{current_b['title']}</div>
            <div class='hero-subtitle'>{current_b['subtitle']}</div>
            <a href='{current_b['link']}' class='hero-cta'>{current_b['cta']}</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navegação do Carrossel
    col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])
    with col_nav2:
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("❮", key="prev_home"):
                st.session_state.carousel_index = (st.session_state.carousel_index - 1) % len(st.session_state.banners_data)
                st.rerun()
        with c2:
            st.markdown(f"<p style='text-align: center; margin-top: 10px; opacity: 0.5;'>{st.session_state.carousel_index + 1} / {len(st.session_state.banners_data)}</p>", unsafe_allow_html=True)
        with c3:
            if st.button("❯", key="next_home"):
                st.session_state.carousel_index = (st.session_state.carousel_index + 1) % len(st.session_state.banners_data)
                st.rerun()


def render_admin_panel():

    st.title("Painel de Controle Administrativo")
    
    # Login automático se já estiver logado como adminkan no app principal
    if st.session_state.get("username") == "adminkan":
        st.session_state["admin_authenticated"] = True

    if "admin_authenticated" not in st.session_state:
        st.session_state["admin_authenticated"] = False

        
    if not st.session_state["admin_authenticated"]:
        st.warning("Área restrita. Identifique-se para acessar o Painel.")
        col_auth1, col_auth2 = st.columns(2)
        with col_auth1:
            user_admin = st.text_input("Usuário de Administrador", key="admin_user_input")
        with col_auth2:
            pass_admin = st.text_input("Senha de Administrador", type="password", key="admin_pass_input")
            
        if st.button("Validar Acesso Administrativo"):
            if user_admin == "adminkan" and pass_admin == "K@nAdmin#2026*":
                st.session_state["admin_authenticated"] = True
                st.session_state["admin_user"] = user_admin
                st.success(f"Bem-vindo, {user_admin}!")
                st.rerun()
            else:
                st.error("Usuário ou Senha incorretos!")
        return
    
    st.info("Central de comando administrativa do sistema KAN.")
    
    t_tab1, t_tab2, t_tab3, t_tab4, t_tab5 = st.tabs(["Tabelas", "Base", "Usuários", "Empresas", "Banners"])
    
    with t_tab1:
        st.subheader("Editor de Configurações (Tabelas)")
        
        with st.expander("Inserção em Lote (Upload de Perfis via CSV)", expanded=False):
            st.markdown("""
            **Instruções:** Carregue um arquivo CSV com as seguintes colunas:
            `Nome completo`, `Data de Nascimento`, `Cargo/Profissao`, `Empresa/Grupo`.
            """)
            arquivo_csv = st.file_uploader("Escolha o arquivo CSV:", type=["csv"])
            if arquivo_csv is not None:
                try:
                    df_lote = pd.read_csv(arquivo_csv, sep=";")
                    if df_lote.shape[1] <= 1:
                        df_lote = pd.read_csv(arquivo_csv, sep=",")
                    
                    colunas_obrigatorias = ["Nome completo", "Data de Nascimento", "Cargo/Profissao", "Empresa/Grupo"]
                    colunas_validas = True
                    for col in colunas_obrigatorias:
                        if col not in df_lote.columns:
                            colunas_validas = False
                            st.error(f"Coluna obrigatória ausente no CSV: `{col}`")
                    
                    if colunas_validas:
                        st.dataframe(df_lote, use_container_width=True)
                        if st.button("Confirmar Inserção em Lote"):
                            with st.spinner("Gravando perfis no Supabase..."):
                                sucessos = 0
                                for _, row in df_lote.iterrows():
                                    n_nome = str(row["Nome completo"]).strip()
                                    n_data = str(row["Data de Nascimento"]).strip()
                                    n_cargo = str(row["Cargo/Profissao"]).strip()
                                    n_empresa = str(row["Empresa/Grupo"]).strip()
                                    
                                    if n_nome and n_data:
                                        try:
                                            if supabase_client:
                                                resp_chk = supabase_client.table("mapas_salvos").select("id").eq("nome", n_nome).execute()
                                                if resp_chk.data:
                                                    supabase_client.table("mapas_salvos").update({
                                                        "data_nascimento": n_data,
                                                        "cargo": n_cargo,
                                                        "empresa": n_empresa
                                                    }).eq("nome", n_nome).execute()
                                                else:
                                                    supabase_client.table("mapas_salvos").insert({
                                                        "nome": n_nome,
                                                        "data_nascimento": n_data,
                                                        "cargo": n_cargo,
                                                        "empresa": n_empresa
                                                    }).execute()
                                                sucessos += 1
                                        except Exception as ex:
                                            st.error(f"Erro ao inserir `{n_nome}`: {ex}")
                                st.success(f"Processamento concluído! {sucessos} perfis integrados.")
                                st.cache_data.clear()
                except Exception as e:
                    st.error(f"Erro ao ler CSV: {e}")

        st.markdown("---")
        tabelas_config = ["matriz", "atributos", "repeticao", "peso", "perfis", "lista_categoria", "qualidades", "categoria_descricao", "descricoes_mapa", "campo_definicao"]
        tab_selecionada = st.selectbox("Selecione a tabela para editar:", tabelas_config)
        
        if supabase_client:
            try:
                res_tab = supabase_client.table(tab_selecionada).select("*").execute()
                df_edit = pd.DataFrame(res_tab.data)
                
                if df_edit.empty and tab_selecionada == "descricoes_mapa":
                    dict_mapa = fetch_descricoes_mapa()
                    flat_data = []
                    for cat, subdict in dict_mapa.items():
                        for val, desc in subdict.items():
                            flat_data.append({"categoria": cat, "valor": val, "descricao": desc})
                    df_edit = pd.DataFrame(flat_data)
                
                if not df_edit.empty or tab_selecionada == "descricoes_mapa":
                    st.write(f"Editando: `{tab_selecionada}`")
                    if df_edit.empty:
                        df_edit = pd.DataFrame(columns=["categoria", "valor", "descricao"])
                    
                    disabled_cols = []
                    if tab_selecionada == "descricoes_mapa":
                        disabled_cols = [c for c in df_edit.columns if c not in ["descricao", "resumo"]]
                    elif tab_selecionada == "campo_definicao":
                        disabled_cols = [c for c in df_edit.columns if c not in ["explicacao"]]
                    else:
                        disabled_cols = [c for c in ["id", "categoria", "valor", "campo"] if c in df_edit.columns]
                    
                    edited_df = st.data_editor(df_edit, use_container_width=True, disabled=disabled_cols, num_rows="dynamic")
                    
                    if st.button(f"Salvar Alterações em {tab_selecionada}"):
                        with st.spinner("Sincronizando com Supabase..."):
                            try:
                                supabase_client.table(tab_selecionada).delete().neq("id", -1).execute() 
                                novos_dados = edited_df.to_dict(orient='records')
                                cleaned_dados = []
                                for d in novos_dados:
                                    d_clean = {k: v for k, v in d.items() if not (k == 'id' and pd.isna(v))}
                                    cleaned_dados.append(d_clean)
                                if cleaned_dados:
                                    supabase_client.table(tab_selecionada).insert(cleaned_dados).execute()
                                st.success(f"Tabela `{tab_selecionada}` atualizada com sucesso!")
                                st.cache_data.clear() 
                            except Exception as e:
                                st.error(f"Erro ao salvar: {e}")
                else:
                    st.warning("Tabela vazia ou não encontrada.")
            except Exception as e:
                st.error(f"Erro ao carregar tabela: {e}")
                
    with t_tab2:
        st.subheader("Visualização da Base de Mapas Salvos")
        if supabase_client:
            try:
                res_mapas = supabase_client.table("mapas_salvos").select("id, nome, data_nascimento, cargo, empresa, usuario").order("id", desc=True).execute()
                if res_mapas.data:
                    df_view = pd.DataFrame(res_mapas.data)
                    st.dataframe(df_view, use_container_width=True)
                else:
                    st.info("Nenhum mapa salvo encontrado.")
            except Exception as e:
                st.error(f"Erro ao carregar mapas: {e}")

    with t_tab3:
        st.subheader("Gerenciamento de Usuários")
        # Reutiliza lógica de render_contas_master mas com filtro de roles simplificado
        if "usuarios_data" not in st.session_state:
            st.session_state.usuarios_data = [
                {"usuario": "adminkan", "tipo": "admin", "status": "Ativo"},
                {"usuario": "cristiano", "tipo": "admin", "status": "Ativo"},
                {"usuario": "maria", "tipo": "user", "status": "Ativo"}
            ]
        
        for i, user in enumerate(st.session_state.usuarios_data):
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 2, 2])
                with c1:
                    st.write(f"**Usuário:** {user['usuario']}")
                with c2:
                    n_tipo = st.selectbox("Direitos", ["admin", "user"], 
                                         index=["admin", "user"].index(user['tipo']),
                                         key=f"user_tipo_{i}", disabled=(user['usuario'] == "adminkan"))
                with c3:
                    n_status = st.selectbox("Status", ["Ativo", "Desabilitado"], 
                                           index=0 if user['status'] == "Ativo" else 1,
                                           key=f"user_status_{i}", disabled=(user['usuario'] == "adminkan"))
                if user['usuario'] != "adminkan":
                    if st.button("Salvar", key=f"user_save_{i}"):
                        st.session_state.usuarios_data[i]['tipo'] = n_tipo
                        st.session_state.usuarios_data[i]['status'] = n_status
                        st.success(f"Usuário {user['usuario']} atualizado!")

    with t_tab4:
        st.subheader("Gerenciamento de Empresas (SaaS)")
        render_empresas()

    with t_tab5:
        st.subheader("Gerenciamento de Banners da Home")
        # Caminhos padrão para garantir inicialização (Pasta PROG)
        b1_p = "banner1.png"
        b2_p = "banner2.png"
        b3_p = "banner3.png"


        if "banners_data" not in st.session_state:
             st.session_state.banners_data = [
                {"title": "Diagnóstico Inteligente", "subtitle": "Análise comportamental profunda e instantânea.", "accent": "#F18617", "cta": "Explorar Diagnósticos", "link": "#", "img_path": b1_p},
                {"title": "Gestão de Talentos", "subtitle": "Dados precisos para equipes de alta performance.", "accent": "#00d2ff", "cta": "Ver Equipes", "link": "#", "img_path": b2_p},
                {"title": "Inovação Humana", "subtitle": "A inteligência por trás do comportamento.", "accent": "#39ff14", "cta": "Saiba Mais", "link": "#", "img_path": b3_p}
            ]
        
        for i, b in enumerate(st.session_state.banners_data):
            with st.expander(f"Banner {i+1}: {b['title']}"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    st.session_state.banners_data[i]['title'] = st.text_input("Título", value=b['title'], key=f"b_title_{i}")
                    st.session_state.banners_data[i]['subtitle'] = st.text_area("Subtítulo", value=b['subtitle'], key=f"b_sub_{i}")
                with col_e2:
                    st.session_state.banners_data[i]['cta'] = st.text_input("Texto do Botão", value=b['cta'], key=f"b_cta_{i}")
                    st.session_state.banners_data[i]['link'] = st.text_input("Link do Botão", value=b['link'], key=f"b_link_{i}")
                    st.session_state.banners_data[i]['accent'] = st.color_picker("Cor de Destaque", value=b['accent'], key=f"b_acc_{i}")
                
                img_file = st.file_uploader(f"Nova Imagem (Banner {i+1})", type=["png", "jpg", "jpeg"], key=f"b_img_{i}")
                if img_file:
                    b64 = base64.b64encode(img_file.read()).decode()
                    st.session_state.banners_data[i]['b64_custom'] = b64
                    st.success("Imagem atualizada!")

        if st.button("💾 Salvar Configurações de Banners"):
            st.success("Configurações aplicadas com sucesso!")
            st.rerun()

def render_empresas():
    st.title("Gestão de Empresas (Tenants)")
    st.info("Aqui você poderá gerenciar os clientes e entidades do sistema KAN.")
    
    # Placeholder para lista de empresas
    empresas_mock = ["Empresa Exemplo A", "Empresa Exemplo B"]
    for emp in empresas_mock:
        with st.expander(emp):
            st.write(f"Configurações para {emp}")
            st.button(f"Editar {emp}", key=f"edit_{emp}")

def render_contas_master():
    st.title("Contas Master")
    st.info("Gerencie os acessos administrativos e permissões do sistema.")
    
    # Inicializa estado das contas se não existir (Mock)
    if "contas_master_data" not in st.session_state:
        st.session_state.contas_master_data = [
            {"usuario": "adminkan", "senha": "K@nAdmin#2026*", "tipo": "Administrador Master", "status": "Ativo"},
            {"usuario": "cristiano", "senha": "password123", "tipo": "Administrador Empresa", "status": "Ativo"},
            {"usuario": "maria", "senha": "password456", "tipo": "Usuário", "status": "Ativo"}
        ]
    
    for i, conta in enumerate(st.session_state.contas_master_data):
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            
            with col1:
                st.write(f"**Usuário:** {conta['usuario']}")
                st.write(f"**Tipo:** {conta['tipo']}")
            
            with col2:
                # Toggle de visualização de senha
                ver_senha = st.checkbox("Ver Senha", key=f"ver_{i}")
                if ver_senha:
                    st.text_input("Senha", value=conta['senha'], key=f"senha_{i}", disabled=(conta['usuario'] == "adminkan"))
                else:
                    st.text_input("Senha", value="********", key=f"senha_hide_{i}", disabled=True)
            
            with col3:
                # Direitos
                n_tipo = st.selectbox("Direitos", ["Administrador Master", "Administrador Empresa", "Usuário"], 
                                     index=["Administrador Master", "Administrador Empresa", "Usuário"].index(conta['tipo']),
                                     key=f"tipo_{i}", disabled=(conta['usuario'] == "adminkan"))
            
            with col4:
                # Status e Logs
                status_opt = ["Ativo", "Desabilitado"]
                n_status = st.selectbox("Status", status_opt, index=status_opt.index(conta['status']), 
                                       key=f"status_{i}", disabled=(conta['usuario'] == "adminkan"))
                if st.button("Ver Logs", key=f"log_{i}"):
                    st.toast(f"Gerando logs para {conta['usuario']}...")
            
            # Se não for adminkan, permite salvar alterações
            if conta['usuario'] != "adminkan":
                if st.button("Salvar Alterações", key=f"save_{i}"):
                    st.session_state.contas_master_data[i]['tipo'] = n_tipo
                    st.session_state.contas_master_data[i]['status'] = n_status
                    st.success(f"Alterações para {conta['usuario']} salvas!")

# --- CONFIGURAÇÃO DO MENU LATERAL ---
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2 style='color: #F18617; margin-bottom: 0;'>Mundo KAN</h2>
        <p style='font-size: 0.8em; color: rgba(255,255,255,0.6);'>Diagnóstico Inteligente</p>
    </div>
    """, unsafe_allow_html=True)
    
    menu_opcoes = [
        "Home",
        "Conta", 
        "Estrutura da Empresa", 
        "Colaboradores", 
        "Equipes", 
        "Diagnósticos", 
        "Mapas", 
        "Analytics",
        "Configurações"
    ]
    
    # Painel de Controle apenas para adminkan
    if st.session_state.get("username") == "adminkan":
        menu_opcoes.append("Painel de Controle")


    escolha = st.radio("", menu_opcoes, index=0) # Home por padrão


    
    st.markdown("---")
    if st.button("Sair", use_container_width=True):
        st.session_state["password_correct"] = False
        st.rerun()
    
    if st.button("Recarregar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# --- LÓGICA DE PÁGINAS ---

if escolha == "Home":
    render_home()
    st.stop()

if escolha == "Conta":
    st.title("Minha Conta")
    st.info("Funcionalidade em desenvolvimento.")
    st.stop()



elif escolha == "Estrutura da Empresa":
    st.title("Estrutura da Empresa")
    st.info("Funcionalidade em desenvolvimento.")
    st.stop()

elif escolha == "Colaboradores":
    st.title("Colaboradores")
    st.info("Funcionalidade em desenvolvimento.")
    st.stop()

elif escolha == "Equipes":
    st.title("Equipes")
    st.info("Funcionalidade em desenvolvimento.")
    st.stop()

elif escolha == "Analytics":
    st.title("Analytics")
    st.info("Funcionalidade em desenvolvimento.")
    st.stop()

elif escolha == "Configurações":
    st.title("Configurações")
    st.info("Funcionalidade em desenvolvimento.")
    st.stop()


elif escolha == "Painel de Controle":
    render_admin_panel()
    st.stop()

elif escolha in ["Diagnósticos", "Mapas"]:
    # O conteúdo atual do app vai aqui
    if escolha == "Diagnósticos":
        st.markdown("<h2 style='text-align: left; margin-bottom: 5px;'>Diagnóstico Comportamental</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.1em; color: rgba(255,255,255,0.7); margin-bottom: 20px;'>Diagnóstico comportamental instantâneo. Sem testes. Sem manipulação.</p>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align: left; margin-bottom: 5px;'>Mapas Detalhados</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.1em; color: rgba(255,255,255,0.7); margin-bottom: 20px;'>Visualização completa de dados numerológicos e arquétipos.</p>", unsafe_allow_html=True)


# --- FETCH CLIENTES DO BANCO DE DADOS ---
@st.cache_data(ttl=3600)
def calcular_perfil_faltante(nome, data_str, _matriz, _atributos, _repeticao, _peso, _perfis, _lista_cat, _qualidades):
    try:
        partes_data = str(data_str).split('/')
        if len(partes_data) != 3: return "", "", "", ""
        dia, mes, ano = int(partes_data[0]), int(partes_data[1]), int(partes_data[2])
        nascimento = (dia, mes, ano)
        data_atual = (datetime.date.today().day, datetime.date.today().month, datetime.date.today().year)
        
        resultados = calcular_numerologia(nome, nascimento, data_atual)
        expressao, motivacao, impressao, destino = resultados[0], resultados[1], resultados[2], resultados[3]
        missao, desafio1, desafio2, desafio_principal = resultados[7], resultados[13], resultados[14], resultados[15]
        ciclos_vida, momentos_decisivos, triangulo_base = resultados[16], resultados[17], resultados[18]
        
        estrutural, direcionamento, kan, rep1, rep2 = calcular_perfil_comportamental(
            expressao, motivacao, impressao, dia,
            destino, missao, ciclos_vida['ciclo2']['numero'], momentos_decisivos['momento3']['numero'],
            triangulo_base
        )
        
        def extract_num(s):
            if not s: return None
            try: return str(s).split(' - ')[0]
            except: return str(s)
        
        todos_numeros_mapa = []
        for v in [expressao, motivacao, impressao, destino, missao, dia]:
            if isinstance(v, int): todos_numeros_mapa.append(v)
            elif isinstance(v, str) and str(v).isdigit(): todos_numeros_mapa.append(int(v))
        for v in [desafio1, desafio2, desafio_principal]:
            if isinstance(v, int): todos_numeros_mapa.append(v)
            elif isinstance(v, str) and str(v).isdigit(): todos_numeros_mapa.append(int(v))
        for c_key in ciclos_vida:
            num_c = ciclos_vida[c_key].get('numero')
            if isinstance(num_c, int): todos_numeros_mapa.append(num_c)
        for m_key in momentos_decisivos:
            num_m = momentos_decisivos[m_key].get('numero')
            if isinstance(num_m, int): todos_numeros_mapa.append(num_m)
        num_psiquico = reduce_number(dia)
        todos_numeros_mapa.append(num_psiquico)
        if isinstance(triangulo_base, int): todos_numeros_mapa.append(triangulo_base)
        
        c_total = Counter(todos_numeros_mapa)
        r_totais = sorted([(num, ct) for num, ct in c_total.items()], key=lambda x: (-x[1], x[0]))
        num_repeticao_mapa = r_totais[0][0] if r_totais else 0
        rep2_val = str(num_repeticao_mapa)
        
        perfis_list = _perfis if _perfis else ["Lider", "Criativo", "Executor", "Resultado", "Vendedor", "Influenciador", "Comunicador"]
        colunas_score = ["Motivação", "Impressão", "Expressão", "Destino", "Missão", "Dia Natalício", "Triângulo", "No Psiquico", "Estrutural", "Direcionamento", "REPETIÇÃO 1", "REPETIÇÃO 2"]
        mapa_col_matriz = {"Motivação": "motivacao", "Impressão": "impressao", "Expressão": "expressao", "Destino": "destino", "Missão": "missao", "Dia Natalício": "dia_natalicio", "Triângulo": "triangulo", "No Psiquico": "no_psiquico"}
        
        valores_originais_score = {
            "Motivação": extract_num(motivacao), "Impressão": extract_num(impressao), "Expressão": extract_num(expressao), "Destino": extract_num(destino), "Missão": extract_num(missao),
            "Dia Natalício": dia, "Triângulo": triangulo_base, "No Psiquico": num_psiquico,
            "Estrutural": estrutural, "Direcionamento": direcionamento, "REPETIÇÃO 1": extract_num(rep1), "REPETIÇÃO 2": int(rep2_val) if str(rep2_val).isdigit() else 0
        }
        
        score_df_calc = pd.DataFrame(0, index=perfis_list, columns=colunas_score)
        for campo_s in colunas_score:
            val_s = valores_originais_score.get(campo_s)
            if val_s is None: continue
            perfil_enc = None
            if campo_s in mapa_col_matriz:
                row_m = _matriz.get(str(val_s))
                if row_m:
                    attr_t = str(get_from_row(row_m, campo_s) or "").upper()
                    if (not attr_t or attr_t == "NAN") and str(val_s).isdigit() and int(val_s) in (11, 22, 33):
                        num_reduz = sum(int(d) for d in str(val_s))
                        row_m_reduz = _matriz.get(str(num_reduz))
                        if row_m_reduz:
                            attr_t = str(get_from_row(row_m_reduz, campo_s) or "").upper()
                            
                    if attr_t and attr_t != "NAN":
                        ai = _atributos.get(attr_t)
                        if ai: perfil_enc = get_from_row(ai, 'perfil')
            else:
                ri = _repeticao.get(str(val_s))
                if ri: perfil_enc = get_from_row(ri, 'perfil')
            
            if perfil_enc:
                pn = str(perfil_enc).strip().capitalize()
                if pn in score_df_calc.index:
                    pv = _peso.get(campo_s, 0)
                    score_df_calc.at[pn, campo_s] = int(pv)

        score_df_calc['TOTAL'] = score_df_calc.sum(axis=1)
        totais_s = score_df_calc['TOTAL'].sort_values(ascending=False)
        totais_s = totais_s[totais_s > 0]
        perfis_escolhidos = []
        if not totais_s.empty:
            max_score = totais_s.iloc[0]
            for p, s in totais_s.items():
                if max_score / s <= 1.8: perfis_escolhidos.append(p)
                else: break
        perfil_val = ", ".join(perfis_escolhidos)
        
        lista_cat = _lista_cat if _lista_cat else ["Justo"]
        score_cat_df = pd.DataFrame(0, index=lista_cat, columns=colunas_score)
        
        for campo_c in colunas_score:
            val_c = valores_originais_score.get(campo_c)
            if val_c is None: continue
            
            cat_encontrada = None
            if campo_c in mapa_col_matriz:
                row_m_cat = _matriz.get(str(val_c))
                if row_m_cat:
                    attr_t_cat = str(get_from_row(row_m_cat, campo_c)).upper()
                    if attr_t_cat and attr_t_cat != "NAN":
                        ai_cat = _atributos.get(attr_t_cat)
                        if ai_cat: cat_encontrada = get_from_row(ai_cat, 'categoria')
            else:
                ri_cat = _repeticao.get(str(val_c))
                if ri_cat: cat_encontrada = get_from_row(ri_cat, 'categoria')
                
            if cat_encontrada:
                cn = str(cat_encontrada).strip().capitalize()
                if cn in score_cat_df.index:
                    # Usar _peso pois não tem PESO_CATEGORIA_DB_CACHE no escopo
                    pv_cat = _peso.get(campo_c, 0)
                    score_cat_df.at[cn, campo_c] = int(pv_cat)

        score_cat_df['TOTAL'] = score_cat_df.sum(axis=1)
        totais_cat = score_cat_df['TOTAL'].sort_values(ascending=False)
        totais_cat = totais_cat[totais_cat > 0]
        categoria_selecionada = totais_cat.index[0] if not totais_cat.empty else ""
        
        lista_quals = list(_qualidades.keys()) if _qualidades else ["Relacionamento"]
        score_qual_df = pd.DataFrame(0, index=lista_quals, columns=colunas_score)
        for campo_q in colunas_score:
            val_q = valores_originais_score.get(campo_q)
            if val_q is None: continue
            
            qual_encontrada = None
            if campo_q in mapa_col_matriz:
                row_m_q = _matriz.get(str(val_q))
                if row_m_q:
                    attr_t_q = str(get_from_row(row_m_q, campo_q) or "").upper()
                    if attr_t_q and attr_t_q != "NAN":
                        ai_q = _atributos.get(attr_t_q)
                        if ai_q: qual_encontrada = get_from_row(ai_q, 'qualidades')
            else:
                ri_q = _repeticao.get(str(val_q))
                if ri_q: qual_encontrada = get_from_row(ri_q, 'qualidade')

            if qual_encontrada:
                # qualidades can be comma separated
                quals = [x.strip().capitalize() for x in str(qual_encontrada).split(',')]
                for q_name in quals:
                    if q_name in score_qual_df.index:
                        score_qual_df.at[q_name, campo_q] = 1

        score_qual_df['TOTAL'] = score_qual_df.sum(axis=1)
        totais_q = score_qual_df['TOTAL'].sort_values(ascending=False)
        totais_q = totais_q[totais_q > 0]
        qual_val = ", ".join(list(totais_q.index)[:2])
        
        return perfil_val, categoria_selecionada, qual_val, str(kan)
    except Exception as e:
        import traceback
        return f"ERRO: {e} | {traceback.format_exc()}", "ERRO", "ERRO", "ERRO"

def realizar_calculos_completos(nome, nascimento, data_atual, cargo, empresa):
    try:
        # Re-importações necessárias para dentro do escopo se necessário ou usar globais
        import json
        from collections import Counter
        
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
        
        # Substitui REPETIÇÃO 2 por REPETICAO MAPA
        todos_numeros_mapa = []
        for v in [expressao, motivacao, impressao, destino, missao, nascimento[0]]:
            if isinstance(v, int): todos_numeros_mapa.append(v)
            elif isinstance(v, str) and str(v).isdigit(): todos_numeros_mapa.append(int(v))
            
        for v in [desafio1, desafio2, desafio_principal]:
            if isinstance(v, int): todos_numeros_mapa.append(v)
            elif isinstance(v, str) and str(v).isdigit(): todos_numeros_mapa.append(int(v))
            
        for c_key in ciclos_vida:
            num_c = ciclos_vida[c_key].get('numero')
            if isinstance(num_c, int): todos_numeros_mapa.append(num_c)
            
        for m_key in momentos_decisivos:
            num_m = momentos_decisivos[m_key].get('numero')
            if isinstance(num_m, int): todos_numeros_mapa.append(num_m)
            
        num_psiquico = reduce_number(nascimento[0])
        todos_numeros_mapa.append(num_psiquico)
        
        if isinstance(triangulo_base, int): todos_numeros_mapa.append(triangulo_base)
        
        c_total = Counter(todos_numeros_mapa)
        r_totais = sorted([(n, c) for n, c in c_total.items()], key=lambda x: (-x[1], x[0]))
        
        num_repeticao_mapa = r_totais[0][0] if r_totais else 0
        perfil_rep_mapa = REPETICAO_DB.get(str(num_repeticao_mapa), {"perfil": ""}).get("perfil", "")
        repeticao_mapa = f"{num_repeticao_mapa} - {perfil_rep_mapa}" if perfil_rep_mapa else str(num_repeticao_mapa)
        
        num_repeticao_2_mapa = r_totais[1][0] if len(r_totais) > 1 else 0
        perfil_rep_2_mapa = REPETICAO_DB.get(str(num_repeticao_2_mapa), {"perfil": ""}).get("perfil", "")
        repeticao_2_mapa = f"{num_repeticao_2_mapa} - {perfil_rep_2_mapa}" if perfil_rep_2_mapa else str(num_repeticao_2_mapa)
        
        num_repeticao_3_mapa = r_totais[2][0] if len(r_totais) > 2 else 0
        perfil_rep_3_mapa = REPETICAO_DB.get(str(num_repeticao_3_mapa), {"perfil": ""}).get("perfil", "")
        repeticao_3_mapa = f"{num_repeticao_3_mapa} - {perfil_rep_3_mapa}" if perfil_rep_3_mapa else str(num_repeticao_3_mapa)
        
        rep2 = repeticao_mapa
        rep3 = repeticao_2_mapa
        rep4 = repeticao_3_mapa

        dados = []
        def add_row(campo, valor_str, explicacao=""):
            if not explicacao or str(explicacao).strip() == "":
                explicacao = get_expl(campo)
            dados.append({"Campo": campo, "Resultado": valor_str, "Explicacao": explicacao})

        num_dia_puro = nascimento[0]
        num_dia_reduzido = reduce_number(nascimento[0])

        def extract_num(s):
            if not s: return None
            try: return s.split(' - ')[0]
            except: return str(s)

        def get_expl(campo_nome):
            base_name = campo_nome.split(" - ")[0]
            search = normalize_key(base_name)
            if "psiquico" in search: search = "nopsiquico"
            if "triangulodavida" in search and "repeticao" not in search: search = "triangulodavida"
            if "repeticao" in search: search = "triangulodavidarepeticoes"
            for k, v in CAMPO_DEFINICAO_DB.items():
                if normalize_key(k) == search: return v
            for k, v in CAMPO_DEFINICAO_DB.items():
                if normalize_key(k) in search or search in normalize_key(k):
                    if len(normalize_key(k)) > 3: return v
            return ""

        def add_row_com_desc(campo, valor_str, categoria_mapa, valor_num):
            desc = get_desc_mapa(categoria_mapa, str(valor_num))
            expl = get_expl(campo)
            if desc: add_row(f"{campo} - {valor_num}", desc, expl)
            else: add_row(campo, valor_str, expl)

        add_row_com_desc("Expressão", expressao, "Expressao", extract_num(expressao) if expressao else expressao)
        add_row_com_desc("Motivação", motivacao, "Motivacao", extract_num(motivacao) if motivacao else motivacao)
        add_row_com_desc("Impressão", impressao, "Impressao", extract_num(impressao) if impressao else impressao)
        add_row_com_desc("Destino", destino, "Destino", extract_num(destino) if destino else destino)
        add_row_com_desc("Número Psíquico", num_dia_reduzido, "Numero Psiquico", num_dia_reduzido)
        add_row("Arcano Atual", f"{arcano_atual_res} | Período: {arcano_atual_periodo}")
        add_row("Triângulo da Vida (Base)", triangulo_base)
        add_row("Triângulo da Vida (Repetições)", triangulo_reps)
        add_row_com_desc("Dia Pessoal", dia_pessoal, "Dia Pessoal", extract_num(dia_pessoal) if dia_pessoal else dia_pessoal)
        add_row_com_desc("Mês Pessoal", mes_pess, "Mes Pessoal", extract_num(mes_pess) if mes_pess else mes_pess)
        add_row_com_desc("Ano Pessoal", ano_pess, "Ano Pessoal", extract_num(ano_pess) if ano_pess else ano_pess)
        add_row_com_desc("Missão", missao, "Missao", extract_num(missao) if missao else missao)

        if dividas_carmicas:
            dividas_str = ', '.join(str(d) for d in dividas_carmicas)
            dividas_parts = []
            for d in dividas_carmicas:
                desc_d = get_desc_mapa("Divida Carmica", str(d))
                dividas_parts.append(f"<b>{d}</b>: {desc_d}" if desc_d else str(d))
            add_row(f"Dívidas Cármicas - {dividas_str}", ' | '.join(dividas_parts))
        else: add_row("Dívidas Cármicas", "Não há")

        if licoes_carmicas:
            licoes_str = ', '.join(str(l) for l in licoes_carmicas)
            licoes_parts = []
            for l in licoes_carmicas:
                desc_l = get_desc_mapa("Licao Carmica", str(l))
                licoes_parts.append(f"<b>{l}</b>: {desc_l}" if desc_l else str(l))
            add_row(f"Lições Cármicas - {licoes_str}", ' | '.join(licoes_parts))
        else: add_row("Lições Cármicas", "Não há")

        if tendencias_ocultas:
            tend_str = ', '.join(str(t) for t in tendencias_ocultas)
            tend_parts = []
            for t in tendencias_ocultas:
                desc_t = get_desc_mapa("Tendencia Oculta", str(t))
                tend_parts.append(f"<b>{t}</b>: {desc_t}" if desc_t else str(t))
            add_row(f"Tendências Ocultas - {tend_str}", ' | '.join(tend_parts))
        else: add_row("Tendências Ocultas", "Não há")

        desc_resp = get_desc_mapa("Resposta Subconsciente", str(extract_num(resposta_subconsciente) if resposta_subconsciente else ""))
        add_row(f"Resposta Subconsciente - {resposta_subconsciente}", desc_resp if desc_resp else "")
        desc_dia_nat = get_desc_mapa("Dia Natalicio", str(nascimento[0]))
        add_row(f"Dia Natalício - {nascimento[0]}", desc_dia_nat if desc_dia_nat else "")
        desc_des1 = get_desc_mapa("Desafio", str(desafio1))
        add_row(f"1º Desafio - {desafio1}", desc_des1 if desc_des1 else "")
        desc_des2 = get_desc_mapa("Desafio", str(desafio2))
        add_row(f"2º Desafio - {desafio2}", desc_des2 if desc_des2 else "")
        desc_des_princ = get_desc_mapa("Desafio", str(desafio_principal))
        add_row(f"Desafio Principal - {desafio_principal}", desc_des_princ if desc_des_princ else "")

        c1_num = ciclos_vida['ciclo1']['numero']
        c1_periodo = f"{ciclos_vida['ciclo1']['inicio']} a {ciclos_vida['ciclo1']['fim']}"
        desc_c1 = get_desc_mapa("1º Ciclo de Vida", str(c1_num))
        add_row(f"1º Ciclo de Vida - {c1_num}", f"<b>Período: {c1_periodo}</b><br>{desc_c1}" if desc_c1 else c1_periodo)
        c2_num = ciclos_vida['ciclo2']['numero']
        c2_periodo = f"{ciclos_vida['ciclo2']['inicio']} a {ciclos_vida['ciclo2']['fim']}"
        desc_c2 = get_desc_mapa("2º Ciclo de Vida", str(c2_num))
        add_row(f"2º Ciclo de Vida - {c2_num}", f"<b>Período: {c2_periodo}</b><br>{desc_c2}" if desc_c2 else c2_periodo)
        c3_num = ciclos_vida['ciclo3']['numero']
        c3_periodo = f"A partir de {ciclos_vida['ciclo3']['inicio']}"
        desc_c3 = get_desc_mapa("3º Ciclo de Vida", str(c3_num))
        add_row(f"3º Ciclo de Vida - {c3_num}", f"<b>Período: {c3_periodo}</b><br>{desc_c3}" if desc_c3 else c3_periodo)

        m1_num = momentos_decisivos['momento1']['numero']
        m1_periodo = f"{momentos_decisivos['momento1']['inicio']} a {momentos_decisivos['momento1']['fim']}"
        desc_m1 = get_desc_mapa("Momento Decisivo", str(m1_num))
        add_row(f"1º Momento Decisivo - {m1_num}", f"<b>Período: {m1_periodo}</b><br>{desc_m1}" if desc_m1 else m1_periodo)
        m2_num = momentos_decisivos['momento2']['numero']
        m2_periodo = f"{momentos_decisivos['momento2']['inicio']} a {momentos_decisivos['momento2']['fim']}"
        desc_m2 = get_desc_mapa("Momento Decisivo", str(m2_num))
        add_row(f"2º Momento Decisivo - {m2_num}", f"<b>Período: {m2_periodo}</b><br>{desc_m2}" if desc_m2 else m2_periodo)
        m3_num = momentos_decisivos['momento3']['numero']
        m3_periodo = f"{momentos_decisivos['momento3']['inicio']} a {momentos_decisivos['momento3']['fim']}"
        desc_m3 = get_desc_mapa("Momento Decisivo", str(m3_num))
        add_row(f"3º Momento Decisivo - {m3_num}", f"<b>Período: {m3_periodo}</b><br>{desc_m3}" if desc_m3 else m3_periodo)
        m4_num = momentos_decisivos['momento4']['numero']
        m4_periodo = f"A partir de {momentos_decisivos['momento4']['inicio']}"
        desc_m4 = get_desc_mapa("Momento Decisivo", str(m4_num))
        add_row(f"4º Momento Decisivo - {m4_num}", f"<b>Período: {m4_periodo}</b><br>{desc_m4}" if desc_m4 else m4_periodo)

        perfis_list = PERFIS_DB if PERFIS_DB else ["Lider"]
        colunas_score = ["Motivação", "Impressão", "Expressão", "Destino", "Missão", "Dia Natalício", "Triângulo", "No Psiquico", "Estrutural", "Direcionamento", "REPETIÇÃO 1", "REPETIÇÃO 2"]
        mapa_col_matriz = {"Motivação": "motivacao", "Impressão": "impressao", "Expressão": "expressao", "Destino": "destino", "Missão": "missao", "Dia Natalício": "dia_natalicio", "Triângulo": "triangulo", "No Psiquico": "no_psiquico"}
        valores_originais_score = {"Motivação": extract_num(motivacao), "Impressão": extract_num(impressao), "Expressão": extract_num(expressao), "Destino": extract_num(destino), "Missão": extract_num(missao), "Dia Natalício": num_dia_puro, "Triângulo": triangulo_base, "No Psiquico": num_dia_reduzido, "Estrutural": estrutural, "Direcionamento": direcionamento, "REPETIÇÃO 1": extract_num(rep1), "REPETIÇÃO 2": extract_num(rep2)}
        score_df_calc = pd.DataFrame(0, index=perfis_list, columns=colunas_score)
        for campo_s in colunas_score:
            val_s = valores_originais_score[campo_s]
            if val_s is None: continue
            perfil_enc = None
            if campo_s in mapa_col_matriz:
                row_m = MATRIZ_DB.get(str(val_s))
                if row_m:
                    attr_t = str(get_from_row(row_m, campo_s) or "").upper()
                    if (not attr_t or attr_t == "NAN") and str(val_s).isdigit() and int(val_s) in (11, 22, 33):
                        num_reduz = sum(int(d) for d in str(val_s)); row_m_reduz = MATRIZ_DB.get(str(num_reduz))
                        if row_m_reduz: attr_t = str(get_from_row(row_m_reduz, campo_s) or "").upper()
                    if attr_t and attr_t != "NAN":
                        ai = ATRIBUTOS_DB.get(attr_t)
                        if ai: perfil_enc = get_from_row(ai, 'perfil')
            else:
                ri = REPETICAO_DB.get(str(val_s))
                if ri: perfil_enc = get_from_row(ri, 'perfil')
            if perfil_enc:
                pn = str(perfil_enc).strip().capitalize()
                if pn in score_df_calc.index: score_df_calc.at[pn, campo_s] = int(PESO_DB.get(campo_s, 0))
        score_df_calc['TOTAL'] = score_df_calc.sum(axis=1)

        lista_cat = LISTA_CATEGORIA_DB if LISTA_CATEGORIA_DB else ["Justo"]
        score_cat_df = pd.DataFrame(0, index=lista_cat, columns=colunas_score)
        for campo_c in colunas_score:
            val_c = valores_originais_score[campo_c]
            if val_c is None: continue
            cat_en = None
            if campo_c in mapa_col_matriz:
                row_m_cat = MATRIZ_DB.get(str(val_c))
                if row_m_cat:
                    attr_t_cat = str(get_from_row(row_m_cat, campo_c)).upper()
                    if attr_t_cat:
                        ai_cat = ATRIBUTOS_DB.get(attr_t_cat)
                        if ai_cat: cat_en = get_from_row(ai_cat, 'categoria')
            else:
                ri_cat = REPETICAO_DB.get(str(val_c))
                if ri_cat: cat_en = get_from_row(ri_cat, 'categoria')
            if cat_en:
                cn = str(cat_en).strip().capitalize()
                if cn in score_cat_df.index: score_cat_df.at[cn, campo_c] = int(PESO_CATEGORIA_DB.get(campo_c, 0))
        score_cat_df['TOTAL'] = score_cat_df.sum(axis=1)
        
        cat_dia_natalicio = ""
        row_dia = MATRIZ_DB.get(str(valores_originais_score["Dia Natalício"]))
        if row_dia:
            attr_dia = str(get_from_row(row_dia, 'Dia Natalício')).upper()
            if attr_dia:
                ai_dia = ATRIBUTOS_DB.get(attr_dia)
                if ai_dia: cat_dia_natalicio = str(get_from_row(ai_dia, 'categoria') or "").strip().capitalize()

        lista_qual = list(QUALIDADES_DB.keys()) if QUALIDADES_DB else ["Relacionamento"]
        score_qual_df = pd.DataFrame(0, index=lista_qual, columns=colunas_score)
        dados_auditoria_qual = []
        for campo_q in colunas_score:
            val_q = valores_originais_score[campo_q]; qual_en = None; attr_t_q = None; p_v = "N/A"; c_v = "N/A"
            if campo_q in mapa_col_matriz:
                row_m_q = MATRIZ_DB.get(str(val_q))
                if row_m_q:
                    attr_t_q = str(get_from_row(row_m_q, campo_q) or "").upper()
                    if (not attr_t_q or attr_t_q == "NAN") and str(val_q).isdigit() and int(val_q) in (11, 22, 33):
                        num_reduz = sum(int(d) for d in str(val_q)); row_m_reduz = MATRIZ_DB.get(str(num_reduz))
                        if row_m_reduz: attr_t_q = str(get_from_row(row_m_reduz, campo_q) or "").upper()
                    if attr_t_q and attr_t_q != "NAN":
                        ai_q = ATRIBUTOS_DB.get(attr_t_q)
                        if ai_q:
                            p_v = get_from_row(ai_q, 'perfil') or "N/A"; c_v = get_from_row(ai_q, 'categoria') or "N/A"
                            qual_en = (get_from_row(ai_q, 'qualidade') or get_from_row(ai_q, 'area de suporte') or get_from_row(ai_q, 'categoria') or get_from_row(ai_q, 'perfil'))
            else:
                ri_q = REPETICAO_DB.get(str(val_q))
                if ri_q:
                    p_v = get_from_row(ri_q, 'perfil') or "N/A"; c_v = get_from_row(ri_q, 'categoria') or "N/A"
                    qual_en = (get_from_row(ri_q, 'qualidade') or get_from_row(ri_q, 'area de suporte') or get_from_row(ri_q, 'categoria') or get_from_row(ri_q, 'perfil'))
                    attr_t_q = "Tabela Repetição"
            if qual_en:
                qn = remover_acentos(str(qual_en).strip()).upper()
                for idx_name in score_qual_df.index:
                    if remover_acentos(idx_name).upper() == qn: score_qual_df.at[idx_name, campo_q] += int(PESO_DB.get(campo_q, 0)); break
            dados_auditoria_qual.append({"Campo": campo_q, "Valor": val_q, "Matriz": attr_t_q if attr_t_q else "N/A", "Perfil": p_v, "Categoria": c_v, "Qualidade": qual_en if qual_en else "N/A"})
        score_qual_df['TOTAL'] = score_qual_df.sum(axis=1)

        dados_perfil = []
        def add_row_perfil_split(campo, valor, descricao):
            desc_limpa = descricao.replace("<b>", "").replace("</b>", "").replace("<br>", " | ")
            dados_perfil.append({"Campo": campo, "Valor": valor, "Descricao": descricao, "Resultado": f"{valor} - {desc_limpa}" if desc_limpa else valor})
        
        k_data = KAN_DB.get(str(kan), {"kan": str(kan), "descricao": ""})
        add_row_perfil_split("KAN", k_data['kan'], k_data['descricao'])
        
        totais_s = score_df_calc['TOTAL'].sort_values(ascending=False); perfis_escolhidos = []
        if not totais_s[totais_s > 0].empty:
            max_s = totais_s.iloc[0]
            for p, s in totais_s[totais_s > 0].items():
                if max_s / s <= st.session_state.get('score_perfil_corte_slider', 1.8): perfis_escolhidos.append(p)
                else: break
        perfil_val = ", ".join(perfis_escolhidos); p_desc_list = []
        for p in perfis_escolhidos:
            d = ""; pn = remover_acentos(p).upper()
            for k_desc, v_desc in PERFIL_DESCRICAO_DB.items():
                if remover_acentos(k_desc).upper() == pn: d = v_desc; break
            if d: p_desc_list.append(d)
        add_row_perfil_split("Perfil", perfil_val, "<br><br>".join(p_desc_list) if p_desc_list else "")
        
        modo_corte_cat = st.session_state.get('corte_categoria_modo', 'Calculo')
        cat_sel = cat_dia_natalicio if modo_corte_cat == 'Dia Natalicio' else (score_cat_df['TOTAL'].sort_values(ascending=False).index[0] if not score_cat_df['TOTAL'].empty else "")
        cat_d = ""; cn = remover_acentos(cat_sel).upper()
        for k_desc, v_desc in CATEGORIA_DESCRICAO_DB.items():
            if remover_acentos(k_desc).upper() == cn: cat_d = v_desc; break
        add_row_perfil_split("Categoria", cat_sel, cat_d)
        
        campos_para_dif = [extract_num(motivacao), extract_num(impressao), extract_num(expressao), extract_num(destino), extract_num(missao), str(nascimento[0]), str(triangulo_base), str(num_dia_reduzido)]
        dif_ativos = []; dif_d_list = []
        for v_dif in ["11", "22"]:
            if v_dif in campos_para_dif:
                d_dif = DIFERENCIAIS_DESC_DB.get(v_dif)
                if d_dif: dif_ativos.append(d_dif['diferencial']); dif_d_list.append(f"<b>{d_dif['diferencial']}</b>: {d_dif['descricao']}")
        if dif_ativos: add_row_perfil_split("Diferenciais", ", ".join(dif_ativos), "<br><br>".join(dif_d_list))
        
        totais_q = score_qual_df['TOTAL'].sort_values(ascending=False); q_escolhidas = list(totais_q[totais_q > 0].index)[:2]; q_d_list = []
        for q in q_escolhidas:
            d = ""; qn = remover_acentos(q).upper()
            for k_desc, v_desc in QUALIDADES_DB.items():
                if remover_acentos(k_desc).upper() == qn: d = v_desc; break
            if d: q_d_list.append(f"<b>{q}</b>: {d}")
        add_row_perfil_split("Qualidades", ", ".join(q_escolhidas), "<br>".join(q_d_list) if q_d_list else "")
        
        user_name_key = f"diag_{nome}"
        desc_diag = st.session_state.get("ai_diagnosis", {}).get(user_name_key) or (clientes_salvos.get(nome, {}).get('ai_diagnosis')) or "Clique no botão ao final da página para gerar o Diagnóstico com Inteligência Artificial."
        add_row_perfil_split("Diagnóstico", "Análise de Performance", desc_diag)
        f_data = FORTALEZAS_DB.get(str(triangulo_base), {"fortaleza": "N/E", "descricao": ""}); add_row_perfil_split("Fortaleza", f_data['fortaleza'], f_data['descricao'])
        d_data = DESAFIOS_DB.get(str(nascimento[0]), {"desafio": "N/E", "descricao": ""}); add_row_perfil_split("Desafio", d_data['desafio'], d_data['descricao'])
        
        return dados, dados_perfil, kan, estrutural, direcionamento, rep1, rep2, score_df_calc, score_cat_df, score_qual_df, pd.DataFrame(dados_auditoria_qual)
    except Exception as e:
        st.error(f"Erro nos cálculos: {e}"); return [], [], None, None, None, None, None, None, None, None, None

def salvar_na_base_dados(nome, dados_perfil, dados, estrutural, direcionamento, rep1, rep2):
    if not supabase_client:
        st.error("Erro: Cliente Supabase não inicializado.")
        return
    try:
        import json
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
        supabase_client.table("mapas_salvos").update({"perfil_json": perfil_json_str}).eq("nome", nome).execute()
        st.toast("✅ Dados sincronizados com sucesso!")
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")


clientes_salvos = {}
if supabase_client:
    try:
        MATRIZ_DB_CACHE = fetch_matriz()
        ATRIBUTOS_DB_CACHE = fetch_atributos()
        REPETICAO_DB_CACHE = fetch_repeticao()
        PESO_DB_CACHE = fetch_peso()
        PERFIS_DB_CACHE = fetch_perfis()
        QUALIDADES_DB_CACHE = fetch_qualidades()
        LISTA_CATEGORIA_DB_CACHE = fetch_lista_categoria()
        
        response = supabase_client.table("mapas_salvos").select("*").execute()
        for row in response.data:
            kan_val = ""
            perfil_val = ""
            categoria_val = ""
            qualidades_val = ""
            fortaleza_val = ""
            desafio_val = ""
            
            p_json = row.get('perfil_json')
            if p_json:
                if isinstance(p_json, str):
                    try:
                        p_json = json.loads(p_json)
                    except:
                        p_json = []
                        
                if isinstance(p_json, list):
                    for item in p_json:
                        if isinstance(item, dict):
                            raw_val = item.get('Valor')
                            if raw_val is None or raw_val == "":
                                res_str = str(item.get('Resultado', ''))
                                if ' - ' in res_str:
                                    raw_val = res_str.split(' - ')[0].strip()
                                elif ':' in res_str:
                                    raw_val = res_str.split(':')[0].strip()
                                else:
                                    raw_val = res_str.strip()
                            
                            campo_orig = str(item.get('Campo', ''))
                            campo_norm = remover_acentos(campo_orig).lower().strip()
                            if campo_norm == 'kan': kan_val = raw_val
                            elif campo_norm == 'perfil': perfil_val = raw_val
                            elif campo_norm == 'categoria': categoria_val = raw_val
                            elif campo_norm == 'qualidades': qualidades_val = raw_val
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

            if not perfil_val or not kan_val:
                perfil_val, categoria_val, qualidades_val, kan_val = calcular_perfil_faltante(
                    row['nome'], row['data_nascimento'],
                    MATRIZ_DB_CACHE, ATRIBUTOS_DB_CACHE, REPETICAO_DB_CACHE, PESO_DB_CACHE, PERFIS_DB_CACHE, LISTA_CATEGORIA_DB_CACHE, QUALIDADES_DB_CACHE
                )

            clientes_salvos[row['nome']] = {
                'data_nascimento': row['data_nascimento'],
                'cargo': row.get('cargo', ''),
                'empresa': row.get('empresa', ''),
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
                'has_json': True if p_json else False
            }
            if row.get('ai_diagnosis'):
                if "ai_diagnosis" not in st.session_state:
                    st.session_state["ai_diagnosis"] = {}
                st.session_state["ai_diagnosis"][f"diag_{row['nome']}"] = row['ai_diagnosis']
    except Exception:
        pass

opcoes_clientes = ["-- Novo Cliente --"] + sorted(list(clientes_salvos.keys()))

col_top1, col_top2_area = st.columns([3, 1])
with col_top1:
    cliente_selecionado = st.selectbox("Selecione um nome já cadastrado ou crie um novo:", opcoes_clientes)
col_top2 = col_top2_area.empty()

# --- INICIALIZAÇÃO DE VARIÁVEIS ---
nome = ""
data_str = ""
data_input = datetime.date.today()
submit_mapa = False
submit_perfil = False
dados_perfil = []
dados = []

# --- PRÉ-CÁLCULO PARA CLIENTE EXISTENTE (para permitir botão no topo) ---
if cliente_selecionado != "-- Novo Cliente --":
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
    
    # Realiza cálculos básicos silenciosamente para o botão de salvar
    hoje = datetime.date.today()
    data_atual_tup = (hoje.day, hoje.month, hoje.year)
    nascimento_tup = (data_input.day, data_input.month, data_input.year)
    
    # Executa cálculos completos para ter os dados prontos para o botão
    res_calc = realizar_calculos_completos(nome, nascimento_tup, data_atual_tup, cargo, empresa)
    dados, dados_perfil, kan, estrutural, direcionamento, rep1, rep2, score_df_calc, score_cat_df, score_qual_df, auditoria_qual_df = res_calc
    
    st.session_state['last_calc_results'] = res_calc # Cache para evitar re-calculo imediato no mesmo loop
    
    # O botão de salvar será renderizado mais abaixo, após o processamento de todos os casos (Novo/Existente)
    pass
if 'fotos' not in st.session_state:
    st.session_state['fotos'] = {}

if cliente_selecionado == "-- Novo Cliente --":
    col_c1, col_c2, col_c3 = st.columns([1, 6, 1])
    with col_c2:
        with st.container(border=True):
            st.markdown("### Novo Cadastro")
            nome = st.text_input("Nome Completo (Conforme certidão):", value=st.session_state.get('ocr_nome', ''))
            
            col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
            with col_f1:
                data_str_input = st.text_input("Data de Nascimento:", placeholder="dd/mm/yyyy", value=st.session_state.get('ocr_data_nascimento', ''))
            with col_f2:
                foto_upload = st.file_uploader("Foto (Opcional)", type=["png", "jpg", "jpeg"])
            with col_f3:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("Ativar Câmera", use_container_width=True):
                    st.session_state['camera_aberta'] = True
                st.caption("Leitura de Documento")
            
            if st.session_state.get('camera_aberta', False):
                foto_doc = st.camera_input("Tire uma foto legível do seu documento")
                if foto_doc:
                    with st.spinner("Extraindo dados do documento..."):
                        try:
                            api_key = st.secrets["gemini"]["api_key"]
                            genai.configure(api_key=api_key)
                            
                            imagem_pil = Image.open(foto_doc)
                            model = genai.GenerativeModel('models/gemini-2.5-flash')
                            
                            prompt = """
                            Você é um especialista em OCR. Extraia as seguintes informações deste documento de identidade brasileiro:
                            1. Nome completo (campo Nome).
                            2. Data de nascimento (campo Data de Nascimento).
                            
                            Retorne EXCLUSIVAMENTE um objeto JSON válido no padrão a seguir, sem textos adicionais, formatações markdown ou comentários:
                            {"nome": "NOME COMPLETO", "data_nascimento": "DD/MM/AAAA"}
                            """
                            
                            resposta_ia = model.generate_content([prompt, imagem_pil])
                            texto_ia = resposta_ia.text.strip().replace("```json", "").replace("```", "")
                            
                            dados_json = json.loads(texto_ia)
                            if "nome" in dados_json:
                                st.session_state['ocr_nome'] = str(dados_json['nome']).upper().strip()
                            if "data_nascimento" in dados_json:
                                st.session_state['ocr_data_nascimento'] = str(dados_json['data_nascimento']).strip()
                                
                            st.session_state['camera_aberta'] = False
                            st.success("Dados preenchidos! Atualizando formulário.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro na leitura: {e}")

            col_f4, col_f5, col_f6 = st.columns([1, 1, 1])
            with col_f4:
                cargo = st.text_input("Cargo/Profissão:")
            with col_f5:
                empresa = st.text_input("Empresa/Grupo:")
            with col_f6:
                linkedin = st.text_input("LinkedIn (URL):")
                
            experiencias = st.text_area("Experiências Profissionais / Bio", 
                                    placeholder="Resumo profissional para a IA...",
                                    height=80)
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_diag = st.button("Gerar Diagnóstico")

            
    if submit_diag:
        try:
            dia, mes, ano = map(int, data_str_input.split('/'))
            data_input = datetime.date(ano, mes, dia)
            data_str = data_str_input
            if foto_upload:
                st.session_state['fotos'][nome] = foto_upload.getvalue()
            if submit_diag:
                st.session_state['show_mapa'] = True
                st.session_state['show_perfil'] = True
                nascimento_tup = (data_input.day, data_input.month, data_input.year)
                hoje = datetime.date.today()
                data_atual_tup = (hoje.day, hoje.month, hoje.year)
                
                # Executa cálculos para novo cliente
                res_calc = realizar_calculos_completos(nome, nascimento_tup, data_atual_tup, cargo, empresa)
                dados, dados_perfil, kan, estrutural, direcionamento, rep1, rep2, score_df_calc, score_cat_df, score_qual_df, auditoria_qual_df = res_calc
                st.session_state['last_calc_results'] = res_calc
        except:
            st.error("Formato de data inválido! Use dd/mm/yyyy (ex: 25/12/1980).")
            submit_mapa = False
            submit_perfil = False
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
        
    # --- RENDERIZAÇÃO DO BOTÃO DE SALVAR NO TOPO (Pós-processamento) ---
if nome and dados_perfil:
    with col_top2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("💾 Salvar na Base de Dados", key=f"save_top_{nome}", use_container_width=True):
            salvar_na_base_dados(nome, dados_perfil, dados, estrutural, direcionamento, rep1, rep2)

    with st.expander("📝 Editar dados", expanded=False):
        col_edit1, col_edit2 = st.columns(2)
        with col_edit1:
            new_nome = st.text_input("Nome", value=nome, key=f"edit_nome_{nome}")
            new_data = st.text_input("Data de Nascimento (dd/mm/yyyy)", value=data_str, key=f"edit_data_{nome}")
            new_cargo = st.text_input("Cargo/Profissão", value=cargo if pd.notna(cargo) and str(cargo) != 'nan' else "", key=f"edit_cargo_{nome}")
        with col_edit2:
            new_empresa = st.text_input("Empresa/Grupo", value=empresa if pd.notna(empresa) and str(empresa) != 'nan' else "", key=f"edit_emp_{nome}")
            new_linkedin = st.text_input("LinkedIn (URL)", value=linkedin if pd.notna(linkedin) and str(linkedin) != 'nan' else "", key=f"edit_link_{nome}")
            new_experiencias = st.text_area("Experiências Profissionais / Bio", value=experiencias if pd.notna(experiencias) and str(experiencias) != 'nan' else "", key=f"edit_exp_{nome}", height=68)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Salvar Alterações", key=f"btn_save_edit_{nome}"):
            if supabase_client:
                try:
                    supabase_client.table("mapas_salvos").update({
                        "nome": new_nome,
                        "data_nascimento": new_data,
                        "cargo": new_cargo,
                        "empresa": new_empresa,
                        "linkedin_url": new_linkedin,
                        "experiencias": new_experiencias
                    }).eq("nome", nome).execute()
                    st.toast("✅ Informações atualizadas!")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao atualizar: {e}")

    st.markdown("---")
    st.session_state['show_mapa'] = True
    st.session_state['show_perfil'] = True
    
    # Executa cálculos completos imediatamente para carregar dados
    res_calc = realizar_calculos_completos(nome, nascimento_tup, data_atual_tup, cargo, empresa)
    dados, dados_perfil, kan, estrutural, direcionamento, rep1, rep2, score_df_calc, score_cat_df, score_qual_df, auditoria_qual_df = res_calc

if (st.session_state.get('show_mapa') or st.session_state.get('show_perfil')) and nome:
    # Recupera resultados calculados anteriormente no loop
    if 'last_calc_results' in st.session_state:
        dados, dados_perfil, kan, estrutural, direcionamento, rep1, rep2, score_df_calc, score_cat_df, score_qual_df, auditoria_qual_df = st.session_state['last_calc_results']
    
    col_res1, col_res2, col_res3 = st.columns([1, 10, 1])
    with col_res2:
        st.markdown("---")
        info_parts = [nome, data_str]
        for p in [cargo, empresa]:
            if p and str(p).lower() != "nan" and str(p).strip() != "":
                info_parts.append(str(p))
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

        if cliente_selecionado == "-- Novo Cliente --" and (submit_mapa or submit_perfil) and supabase_client:
            try:
                import json
                # Preparar perfil_json completo para salvar (igual ao botão de cima)
                dados_para_salvar = list(dados_perfil)
                for label, val in [("Estrutural", estrutural), ("Direcionamento", direcionamento), 
                                   ("REPETIÇÃO 1", rep1), ("REPETIÇÃO 2", rep2)]:
                    dados_para_salvar.append({
                        "Campo": label, "Valor": str(val), "Descricao": "", "Resultado": str(val)
                    })
                for item in dados:
                    campo_full = item.get('Campo', '')
                    if ' - ' in campo_full:
                        partes = campo_full.split(' - ')
                        campo_simples = partes[0]
                        valor_simples = partes[1]
                    else:
                        campo_simples = campo_full
                        valor_simples = item.get('Resultado', '')
                        if len(str(valor_simples)) > 50: valor_simples = "Ver Mapa"
                    
                    dados_para_salvar.append({
                        "Campo": f"Mapa: {campo_simples}", "Valor": valor_simples, "Descricao": "", "Resultado": valor_simples
                    })

                perfil_json_str = json.dumps(dados_para_salvar, ensure_ascii=False)
                mapa_json_str = json.dumps(dados, ensure_ascii=False)
                
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
                    "mapa_json": mapa_json_str,
                    "perfil_json": perfil_json_str
                }
                if nome in st.session_state['fotos']:
                    import base64
                    insert_data["foto_base64"] = base64.b64encode(st.session_state['fotos'][nome]).decode()
                    
                supabase_client.table("mapas_salvos").insert(insert_data).execute()
                st.toast("✅ Cadastro salvo na nuvem!")
                st.cache_data.clear()
            except Exception as e:
                st.toast(f"⚠️ Erro ao salvar cadastro: {e}")

        # --- EXIBIÇÃO DOS RESULTADOS DO MAPA ---
        if st.session_state.get('show_mapa'):
            st.subheader("Mapa")
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

                explicacao_html = ""
                if item.get("Explicacao"):
                    explicacao_html = f"<div style='font-size: 0.78em; color: rgba(255,255,255,0.6); padding: 0 14px 10px 14px; font-style: italic;'>{item['Explicacao']}</div>"

                html_mapa += (
                    f"<tr>"
                    f"<td><div class='mapa-campo'>{label_campo}{numero_badge}</div>{explicacao_html}</td>"
                    f"<td>{cel_resultado}</td>"
                    f"</tr>"
                )
            html_mapa += "</tbody></table>"
            st.markdown(html_mapa, unsafe_allow_html=True)

            st.markdown("---")
            st.subheader("Baixar Resultados do Mapa")
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
                    
                    # Montar o contexto para a IA (Extraindo dados do Mapa e Perfil)
                    mapa_texto = "\n".join([f"- {item['Campo']}: {item['Resultado']}" for item in dados])
                    perfil_texto = "\n".join([f"- {item['Campo']}: {item['Resultado']}" for item in dados_perfil if item['Campo'] != "Diagnóstico"])
                    info_prof = f"- LinkedIn: {linkedin}\n- Experiências: {experiencias}" if (linkedin or experiencias) else ""
                    
                    contexto = f"""
                    Você é um Especialista em Recrutamento e Seleção (RH) de alta performance e Consultor de Carreira.
                    Sua tarefa é analisar o perfil completo de {nome} e gerar um Diagnóstico de Performance com foco em contratação corporativa.
                    
                    DADOS BRUTOS DO PERFIL E TENDÊNCIAS COMPORTAMENTAIS:
                    {mapa_texto}
                    
                    DADOS DO PERFIL KAN (Forças, Estilo de Trabalho e Qualidades):
                    {perfil_texto}
                    
                    INFORMAÇÕES PROFISSIONAIS ADICIONAIS:
                    {info_prof}
                    
                    DIRETRIZES ESTRITAS PARA A REDAÇÃO:
                    1. Use puramente linguagem corporativa, psicológica e de RH (Foco em soft skills, competências, fit cultural e desafios de gestão).
                    2. PROIBIDO MENCIONAR TERMOS NUMEROLÓGICOS: NUNCA escreva palavras como "Mapa", "Numerologia", "Expressão 1", "Destino 8", "Motivação", "Dívidas Cármicas", etc. Você deve APENAS absorver o significado psicológico desses itens e transformá-los em análise de competência profissional.
                    3. NUNCA use a expressão "tendências numerológicas". Se precisar, use "tendências comportamentais", "análise de perfil" ou "mapeamento".
                    4. O texto não pode, em hipótese alguma, parecer uma consulta esotérica. Deve soar como uma avaliação técnica, profunda e baseada em dados analíticos de RH.
                    5. O texto deve ser formatado em exatamente 3 parágrafos curtos, diretos e objetivos.
                    """
                    
                    with st.spinner("IA analisando perfil com visão de RH (Alta Performance)..."):
                        # Usando os modelos modernos disponíveis na chave do usuário (2026)
                        texto_ia = ""
                        try:
                            # Tenta o modelo ultra-rápido moderno
                            model = genai.GenerativeModel('models/gemini-2.5-flash')
                            response = model.generate_content(contexto)
                            texto_ia = response.text.replace("\n", "<br>")
                        except Exception as e1:
                            try:
                                # Fallback para o modelo Pro 3.1 de última geração
                                model = genai.GenerativeModel('models/gemini-3.1-pro-preview')
                                response = model.generate_content(contexto)
                                texto_ia = response.text.replace("\n", "<br>")
                            except Exception as e2:
                                try:
                                    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                                    modelos_str = ", ".join(modelos)
                                    texto_ia = f"<b>Aviso de Sistema:</b> Não foi possível acessar os modelos de IA modernos.<br>Erro: {e1}<br><br><b>Modelos disponíveis na sua chave:</b> {modelos_str}"
                                except Exception as e3:
                                    texto_ia = f"<b>Erro na IA:</b> Não foi possível conectar ao Google Gemini. Verifique se a chave da API em st.secrets é válida.<br>Erro original: {e1}"
                        
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
            col_p1, col_p2, col_p3 = st.columns(3)
            df_perfil = pd.DataFrame(dados_perfil)
            nome_limpo_p = remover_acentos(nome).replace(' ', '_')
            with col_p1:
                csv_p = df_perfil.to_csv(sep=';', index=False).encode('utf-8')
                st.download_button("📥 Baixar Perfil como CSV", data=csv_p, file_name=f"perfil_{nome_limpo_p}.csv", mime="text/csv", key="dl_p_csv")
            with col_p2:
                pdf_p = gerar_pdf(nome, data_str, dados_perfil, titulo="Perfil Comportamental KAN")
                st.download_button("📄 Baixar Perfil como PDF", data=pdf_p, file_name=f"perfil_{nome_limpo_p}.pdf", mime="application/pdf", key="dl_p_pdf")
            with col_p3:
                if st.button("💾 Salvar na Base de Dados", key=f"save_bottom_{nome}", use_container_width=True):
                    salvar_na_base_dados(nome, dados_perfil, dados, estrutural, direcionamento, rep1, rep2)
            # --- BUSCA DE PERFIS (AUDITORIA) ---

            with st.expander("🔍 Busca de Perfis Cadastrados (Auditoria)", expanded=False):
                st.markdown("### Selecione os filtros desejados")
                st.caption("Você pode escolher mais de uma opção em cada filtro ou deixá-los em branco para buscar todos.")
                
                kan_display_map = {"3": "CRIAÇÃO", "6": "MOVIMENTO", "9": "FINALIDADE"}
                all_kans_raw = sorted([str(k) for k in KAN_DB.keys()], key=lambda x: int(x)) if KAN_DB else ['1', '2', '3', '4', '5', '6', '7', '8', '9', '11', '22']
                all_kans = [kan_display_map.get(k, k) for k in all_kans_raw]
                
                # Normaliza e remove vazios
                def limpa_lista(lst):
                    return sorted(list(set(str(x).strip() for x in lst if x and str(x).strip())))
                
                # Perfis
                perfis_db_lista = PERFIS_DB if PERFIS_DB else ["Lider", "Criativo", "Executor", "Resultado", "Vendedor", "Influenciador", "Comunicador"]
                all_perfis = limpa_lista(perfis_db_lista)
                
                # Categorias
                cats_db_lista = LISTA_CATEGORIA_DB if LISTA_CATEGORIA_DB else ["Justo", "Inovador", "Diplomático", "Realizador", "Versátil", "Visionário", "Magnético", "Analítico", "Organizado", "Harmônico", "Comunicativo", "Intuitivo", "Conhecimento"]
                all_cats = limpa_lista(cats_db_lista)
                
                # Qualidades
                quals_db_lista = list(QUALIDADES_DB.keys()) if QUALIDADES_DB else ["Relacionamento", "Execução", "Análise", "Coletividade", "Justiça", "Praticidade e disciplina", "Comunicação", "Versatilidade", "Intuição", "Organização", "Serviço"]
                all_quals = limpa_lista(quals_db_lista)
                
                # Cargos e Empresas
                all_cargos = limpa_lista([c.get('cargo', '') for c in clientes_salvos.values()])
                all_empresas = limpa_lista([c.get('empresa', '') for c in clientes_salvos.values()])
                
                col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                with col_b1:
                    filtro_kan = st.multiselect("KAN", options=all_kans)
                with col_b2:
                    filtro_perfil = st.multiselect("PERFIL", options=all_perfis)
                with col_b3:
                    filtro_cat = st.multiselect("Categoria", options=all_cats)
                with col_b4:
                    filtro_qual = st.multiselect("Qualidades", options=all_quals)
                
                col_b5, col_b6 = st.columns(2)
                with col_b5:
                    filtro_cargo = st.multiselect("Cargo/Profissão", options=all_cargos)
                with col_b6:
                    filtro_empresa = st.multiselect("Empresa/Grupo", options=all_empresas)
                
                if st.button("🔎 Realizar Busca de Perfis"):
                    resultados_busca = []
                    for n, c in clientes_salvos.items():
                        match_kan = True
                        if filtro_kan:
                            inv_kan_map = {v: k for k, v in kan_display_map.items()}
                            f_kan_raw = [inv_kan_map.get(f, f) for f in filtro_kan]
                            f_kan_norm = [str(f).strip() for f in f_kan_raw]
                            match_kan = str(c.get('kan')).strip() in f_kan_norm
                        
                        match_perfil = True
                        if filtro_perfil:
                            f_perfis_norm = [remover_acentos(str(f)).upper().strip() for f in filtro_perfil]
                            c_perfis = [remover_acentos(str(p)).upper().strip() for p in str(c.get('perfil', '')).split(',')]
                            match_perfil = any(p in f_perfis_norm for p in c_perfis)
                            
                        match_cat = True
                        if filtro_cat:
                            f_cats_norm = [remover_acentos(str(f)).upper().strip() for f in filtro_cat]
                            c_cats = [remover_acentos(str(p)).upper().strip() for p in str(c.get('categoria', '')).split(',')]
                            match_cat = any(p in f_cats_norm for p in c_cats)
                            
                        match_qual = True
                        if filtro_qual:
                            f_quals_norm = [remover_acentos(str(f)).upper().strip() for f in filtro_qual]
                            c_quals = [remover_acentos(str(q)).upper().strip() for q in str(c.get('qualidades', '')).split(',')]
                            match_qual = any(q in f_quals_norm for q in c_quals)
                        
                        match_cargo = True
                        if filtro_cargo:
                            match_cargo = str(c.get('cargo', '')).strip() in filtro_cargo
                            
                        match_empresa = True
                        if filtro_empresa:
                            match_empresa = str(c.get('empresa', '')).strip() in filtro_empresa
                            
                        if match_kan and match_perfil and match_cat and match_qual and match_cargo and match_empresa:
                            # Prepara dado base
                            row_res = {
                                "Nome": n,
                                "Data Nasc.": c.get('data_nascimento', ''),
                                "KAN": kan_display_map.get(str(c.get('kan')), str(c.get('kan'))),
                                "Perfil": c.get('perfil', ''),
                                "Categoria": c.get('categoria', ''),
                                "Qualidades": c.get('qualidades', ''),
                                "Estrutural": c.get('estrutural', ''),
                                "Direcionamento": c.get('direcionamento', ''),
                                "REPETIÇÃO 1": c.get('repeticao_1', ''),
                                "REPETIÇÃO 2": c.get('repeticao_2', ''),
                                "Fortaleza": c.get('fortaleza', ''),
                                "Desafio": c.get('desafio', '')
                            }
                            # Adiciona campos do mapa detalhado ao final
                            if c.get('mapa_detalhado'):
                                for k_mapa, v_mapa in c['mapa_detalhado'].items():
                                    row_res[k_mapa] = v_mapa
                            
                            resultados_busca.append(row_res)
                    
                    if resultados_busca:
                        st.success(f"{len(resultados_busca)} perfil(is) encontrado(s)!")
                        df_final = pd.DataFrame(resultados_busca)
                        st.dataframe(df_final, use_container_width=True, column_config={"Nome": st.column_config.Column(pinned=True)})
                    else:
                        st.warning("Nenhum perfil encontrado com os critérios selecionados.")

            # --- EXIBIÇÃO DOS SCORES TÉCNICOS ---
            with st.expander("📊 Ver Scores Técnicos (Auditoria)", expanded=False):
                p_val = next((item['Valor'] for item in dados_perfil if item['Campo'] == 'Perfil'), '')
                c_val = next((item['Valor'] for item in dados_perfil if item['Campo'] == 'Categoria'), '')
                q_val = next((item['Valor'] for item in dados_perfil if item['Campo'] == 'Qualidades'), '')

                st.header("Score Perfil")
                st.table(score_df_calc)
                st.info(f"**Perfil Selecionado:** {p_val}")
                
                st.header("Score Categoria")
                st.table(score_cat_df)
                st.info(f"**Categoria Selecionada:** {c_val}")
                
                st.header("Score Qualidades")
                st.table(score_qual_df)
                st.info(f"**Qualidades Selecionadas:** {q_val}")
                
                st.header("Detalhamento dos Atributos")
                st.table(auditoria_qual_df)
                
                st.header("Plano KAN")
                rep3 = ""
                rep4 = ""
                df_plano_kan = pd.DataFrame({
                    "Campo": ["KAN", "ESTRUTURAL", "DIRECIONAMENTO", "REPETIÇÃO 1", "REPETICAO MAPA", "REPETICAO 2 MAPA", "REPETICAO 3 MAPA"],
                    "Valor": [
                        kan, 
                        estrutural, 
                        direcionamento, 
                        str(rep1).split(" - ")[0] if " - " in str(rep1) else str(rep1), 
                        str(rep2).split(" - ")[0] if " - " in str(rep2) else str(rep2),
                        str(rep3).split(" - ")[0] if " - " in str(rep3) else str(rep3),
                        str(rep4).split(" - ")[0] if " - " in str(rep4) else str(rep4)
                    ]
                })
                st.table(df_plano_kan)
                
                st.header("Triângulo Harmônico")
                
                def clean_val(v):
                    if v is None: return None
                    s = str(v).split(" - ")[0]
                    return int(s) if s.isdigit() else None

                k_val = clean_val(kan)
                e_val = clean_val(estrutural)
                d_val = clean_val(direcionamento)
                r1_val = clean_val(rep1)
                r2_val = clean_val(rep2)
                r3_val = clean_val(rep3)
                r4_val = clean_val(rep4)
                
                todos_campos = [
                    {"campo": "KAN", "valor": k_val},
                    {"campo": "ESTRUTURAL", "valor": e_val},
                    {"campo": "DIRECIONAMENTO", "valor": d_val},
                    {"campo": "REPETIÇÃO 1", "valor": r1_val},
                    {"campo": "REPETICAO MAPA", "valor": r2_val},
                    {"campo": "REPETICAO 2 MAPA", "valor": r3_val},
                    {"campo": "REPETICAO 3 MAPA", "valor": r4_val}
                ]
                
                vertices = []
                valores_adicionados = set()
                
                for item in todos_campos:
                    val = item["valor"]
                    if val is not None and val not in [11, 22] and val not in valores_adicionados:
                        vertices.append(item)
                        valores_adicionados.add(val)
                    if len(vertices) == 3:
                        break
                        
                valores_finais = [v["valor"] for v in vertices]
                df_triangulo = pd.DataFrame({
                    "Vértice": [v["campo"] for v in vertices],
                    "Valor": [v["valor"] for v in vertices]
                })
                st.table(df_triangulo)
                
                if len(set(valores_finais)) == 3:
                    try:
                        from PIL import Image, ImageDraw
                        import os
                        
                        path_fundo = os.path.join("images", "plano_kan_fundo.jpg")
                        if os.path.exists(path_fundo):
                            fundo_img = Image.open(path_fundo).convert("RGBA")
                            draw_layer = Image.new("RGBA", fundo_img.size, (255, 255, 255, 0))
                            draw = ImageDraw.Draw(draw_layer)
                            
                            # Coordenadas conhecidas dos números (ajustadas ao centro das áreas)
                            coords_map = {
                                1: (794, 176),
                                2: (1037, 243),
                                3: (960, 380),
                                4: (794, 585),
                                5: (486, 585),
                                6: (320, 380),
                                7: (243, 243),
                                8: (486, 176),
                                9: (640, 120),
                                11: (1037, 243),
                                22: (794, 585)
                            }
                            
                            poly_points = []
                            for v in vertices:
                                val_num = int(v["valor"])
                                if val_num in coords_map:
                                    poly_points.append(coords_map[val_num])
                                else:
                                    val_reduz = sum(int(d) for d in str(val_num))
                                    if val_reduz in coords_map:
                                        poly_points.append(coords_map[val_reduz])
                                        
                            if len(poly_points) == 3:
                                draw.polygon(poly_points, fill=(255, 255, 255, 140))
                                img_final = Image.alpha_composite(fundo_img, draw_layer)
                                st.image(img_final.convert("RGB"), caption="Visualização do Triângulo Harmônico", use_container_width=True)
                                
                                st.markdown("### 👥 Adicionar perfil para comparação")
                                
                                # Helper para extrair vértices de outro perfil
                                def obter_vertices_triangulo(nome_comp, data_nasc_str):
                                    def clean_val(v):
                                        if v is None: return None
                                        s = str(v).split(" - ")[0]
                                        return int(s) if s.isdigit() else None
                                    try:
                                        from datetime import datetime, date
                                        if isinstance(data_nasc_str, (datetime, date)):
                                            nasc_dt = data_nasc_str
                                        elif isinstance(data_nasc_str, str):
                                            try:
                                                nasc_dt = datetime.strptime(data_nasc_str, "%d/%m/%Y")
                                            except ValueError:
                                                nasc_dt = datetime.strptime(data_nasc_str, "%Y-%m-%d")
                                        else:
                                            raise ValueError("Data em formato desconhecido")
                                        nasc_tuple = (nasc_dt.day, nasc_dt.month, nasc_dt.year)
                                        now_dt = datetime.now()
                                        data_at = (now_dt.day, now_dt.month, now_dt.year)
                                        
                                        res = calcular_numerologia(nome_comp, nasc_tuple, data_at)
                                        (expressao, motivacao, impressao, destino, _, _, _, missao, _, _, 
                                         _, _, _, _, _, _, ciclos_vida, momentos_decisivos, triangulo_base, _, _, _) = res
                                        
                                        estrutural, direcionamento, kan, rep1, rep2 = calcular_perfil_comportamental(
                                            expressao, motivacao, impressao, nasc_tuple[0],
                                            destino, missao, ciclos_vida['ciclo2']['numero'], momentos_decisivos['momento3']['numero'],
                                            triangulo_base
                                        )
                                        
                                        todos_num = []
                                        for v_it in [expressao, motivacao, impressao, destino, missao, nasc_tuple[0]]:
                                            if isinstance(v_it, int): todos_num.append(v_it)
                                            elif isinstance(v_it, str) and str(v_it).isdigit(): todos_num.append(int(v_it))
                                            
                                        for c_key in ciclos_vida:
                                            num_c = ciclos_vida[c_key].get('numero')
                                            if isinstance(num_c, int): todos_num.append(num_c)
                                            
                                        for m_key in momentos_decisivos:
                                            num_m = momentos_decisivos[m_key].get('numero')
                                            if isinstance(num_m, int): todos_num.append(num_m)
                                            
                                        num_ps = reduce_number(nasc_tuple[0])
                                        todos_num.append(num_ps)
                                        
                                        if isinstance(triangulo_base, int): todos_num.append(triangulo_base)
                                        
                                        c_tot = Counter(todos_num)
                                        r_tot = sorted([(n, c) for n, c in c_tot.items()], key=lambda x: (-x[1], x[0]))
                                        
                                        r2_v = r_tot[0][0] if r_tot else 0
                                        r3_v = r_tot[1][0] if len(r_tot) > 1 else 0
                                        r4_v = r_tot[2][0] if len(r_tot) > 2 else 0
                                        
                                        k_v = clean_val(kan)
                                        e_v = clean_val(estrutural)
                                        d_v = clean_val(direcionamento)
                                        r1_v = clean_val(rep1)
                                        
                                        todos_comp = [
                                            {"campo": "KAN", "valor": k_v},
                                            {"campo": "ESTRUTURAL", "valor": e_v},
                                            {"campo": "DIRECIONAMENTO", "valor": d_v},
                                            {"campo": "REPETIÇÃO 1", "valor": r1_v},
                                            {"campo": "REPETICAO MAPA", "valor": r2_v},
                                            {"campo": "REPETICAO 2 MAPA", "valor": r3_v},
                                            {"campo": "REPETICAO 3 MAPA", "valor": r4_v}
                                        ]
                                        
                                        vertices_comp = []
                                        vals_comp = set()
                                        for it in todos_comp:
                                            v_it = it["valor"]
                                            if v_it is not None and v_it not in [11, 22] and v_it not in vals_comp:
                                                vertices_comp.append(v_it)
                                                vals_comp.add(v_it)
                                            if len(vertices_comp) == 3:
                                                break
                                                
                                        if len(vertices_comp) == 3:
                                            return vertices_comp
                                    except Exception as ex:
                                        st.error(f"Erro ao processar {nome_comp}: {ex}")
                                    return None

                                perfis_disp = sorted([n for n in clientes_salvos.keys() if n != nome])
                                perfis_selecionados = st.multiselect("Pesquise e selecione os perfis:", options=perfis_disp)
                                
                                if perfis_selecionados:
                                    from PIL import ImageFont
                                    try:
                                        font_label = ImageFont.truetype("arial.ttf", 34)
                                    except:
                                        font_label = ImageFont.load_default()

                                    # Camada para o triângulo original
                                    layer_base = Image.new("RGBA", fundo_img.size, (255, 255, 255, 0))
                                    draw_base = ImageDraw.Draw(layer_base)
                                    draw_base.polygon(poly_points, fill=(255, 255, 255, 140))
                                    
                                    img_multi_final = Image.alpha_composite(fundo_img, layer_base)
                                    
                                    # Camada para anotações (nomes e vértices KAN)
                                    layer_notes = Image.new("RGBA", fundo_img.size, (255, 255, 255, 0))
                                    draw_notes = ImageDraw.Draw(layer_notes)
                                    
                                    # Anotações do perfil principal
                                    if len(poly_points) == 3:
                                        k_base = poly_points[0]
                                        draw_notes.ellipse((k_base[0]-4, k_base[1]-4, k_base[0]+4, k_base[1]+4), fill=(60, 60, 60))
                                        
                                        cx_b = sum(p[0] for p in poly_points) // 3
                                        cy_b = sum(p[1] for p in poly_points) // 3
                                        draw_notes.text((cx_b - 15, cy_b - 10), str(nome).split()[0], fill=(60, 60, 60), font=font_label)
                                    
                                    for idx, p_nome in enumerate(perfis_selecionados):
                                        p_dados = clientes_salvos[p_nome]
                                        p_vertices = obter_vertices_triangulo(p_nome, p_dados['data_nascimento'])
                                        if p_vertices and len(p_vertices) == 3:
                                            p_points = []
                                            for val in p_vertices:
                                                if int(val) in coords_map:
                                                    p_points.append(coords_map[int(val)])
                                                else:
                                                    val_red = sum(int(d) for d in str(val))
                                                    if val_red in coords_map:
                                                        p_points.append(coords_map[val_red])
                                            if len(p_points) == 3:
                                                layer_comp = Image.new("RGBA", fundo_img.size, (255, 255, 255, 0))
                                                draw_comp = ImageDraw.Draw(layer_comp)
                                                draw_comp.polygon(p_points, fill=(255, 255, 255, 140))
                                                
                                                img_multi_final = Image.alpha_composite(img_multi_final, layer_comp)
                                                
                                                # Anotações do perfil comparado
                                                k_comp = p_points[0]
                                                draw_notes.ellipse((k_comp[0]-4, k_comp[1]-4, k_comp[0]+4, k_comp[1]+4), fill=(60, 60, 60))
                                                
                                                cx_c = sum(p[0] for p in p_points) // 3
                                                cy_c = sum(p[1] for p in p_points) // 3
                                                draw_notes.text((cx_c - 15, cy_c - 10), str(p_nome).split()[0], fill=(60, 60, 60), font=font_label)
                                                
                                    img_multi_final = Image.alpha_composite(img_multi_final, layer_notes)
                                    st.image(img_multi_final.convert("RGB"), caption="Comparativo de Triângulos Harmônicos", use_container_width=True)
                                    
                    except Exception as e:
                        st.error(f"Erro ao gerar triângulo visual: {e}")
                else:
                    st.warning("⚠️ O triângulo harmônico não foi formado.")


elif (submit_diag) and not nome:
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
