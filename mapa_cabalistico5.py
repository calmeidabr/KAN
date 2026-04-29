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
                res_dict = {str(row['numero']): row for row in resp.data if row.get('numero')}
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
                res_dict = {str(get_from_row(row, 'atributo')).upper(): row for row in resp.data}
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
            resp = client.table("repeticao").select("*").execute()
            if resp.data:
                res_dict = {str(int(get_from_row(row, 'repeticao'))): row for row in resp.data}
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
    REMAINING_DESCRIPTIONS = [{'categoria': '1º Ciclo de Vida', 'valor': '1', 'descricao': 'O 1 (um) no primeiro Ciclo de Vida indica um período difícil. Quando criança, a pessoa necessita aprender a desenvolver sua individualidade, pois caso contrário, na juventude e adolescência ou mesmo até à entrada do 2º Ciclo, terá problemas emocionais e grande dificuldade de se estabilizar profissionalmente. O ideal é que a criança nesse Ciclo tenha liberdade acima do normal e não frear os seus instintos em hipótese alguma. No caso de pessoa maior de 18 anos e que ainda esteja no primeiro Ciclo e tenha sido reprimida, ou seja, não tenha tido educação condizente, que absorva estes ensinamentos e os coloque em prática imediatamente.'}, {'categoria': '1º Ciclo de Vida', 'valor': '2', 'descricao': 'O 2 (dois) no primeiro Ciclo de Vida, indica uma criança extremamente mimada, que possivelmente sofreu grande influência da mãe ou dos avós. É natural que na adolescência, em vista da possessiveness familiar, pense em casar-se o mais cedo possível e isso é muito comum, principalmente entre os homens.'}, {'categoria': '1º Ciclo de Vida', 'valor': '3', 'descricao': 'O 3 (três) indica uma infância e adolescência feliz, despreocupada e com muitos amigos. Não é um período particularmente favorável ao aprendizado, que deverá ocorrer a partir do segundo Ciclo, mas haverá provavelmente muitas oportunidades para a expressão de idéias e emoções, após os 18 anos (alguns com menos idade), através das artes em geral, da música, do teatro e escrita. Não é um bom período para contrair matrimônio.'}, {'categoria': '1º Ciclo de Vida', 'valor': '5', 'descricao': 'O 5 (cinco) no primeiro Ciclo de Vida indica muitas mudanças e uma liberdade que às vezes é demasiado grande para que se possa lidar com ela de maneira construtiva. Sem orientação adequada, o jovem nesse período pode ter problemas causados por envolvimentos precoces com sexo, álcool e drogas. É um péssimo período para o casamento e normalmente quando isso acontece, dura pouco. Também no lado profissional a pessoa tem dificuldade de se assentar, mudando continuamente de emprego ou atividade, que só terá término quando da entrada no segundo Ciclo.'}, {'categoria': '1º Ciclo de Vida', 'valor': '6', 'descricao': 'O 6 (seis) indica infância e juventude restritiva, cheia de deveres e responsabilidades e, para fugir dessa restrição, normalmente casa-se cedo e muitas vezes esse casamento é um completo fracasso, pois não é escorado em bases sólidas do amor e sim como uma fuga. Tem, também, dificuldades em se ajustar à sociedade, pois é incompreendido nos seus planos e objetivos.'}, {'categoria': '1º Ciclo de Vida', 'valor': '7', 'descricao': 'O 7 (sete) no primeiro Ciclo de Vida indica um período muito difícil. A criança e o jovem conservam-se retraídos e podem sofrer com a falta de compreensão dos pais, professores e amigos. Tal incompreensão leva, invariavelmente, ao isolamento, retraimento e até medo de encarar a vida nessa fase. Na faixa dos 20 anos, em virtude dessa retração, pode desenvolver complexos de culpa e falta de autoconfiança, restringindo o seu progresso pessoal e profissional.'}, {'categoria': '1º Ciclo de Vida', 'valor': '8', 'descricao': 'O 8 (oito) no primeiro Ciclo de Vida indica um período de realizações. É extraordinário para o aprendizado acerca dos aspectos materiais da vida. É nesse período que se forjam os homens de negócios, comércio, políticos, advogados e todos aqueles que pensam mais no material do que no espiritual.'}, {'categoria': '2º Ciclo de Vida', 'valor': '1', 'descricao': 'O 1 (um) no segundo Ciclo de Vida mostra um período de ambições, um grande desejo de realizações e também de sucesso relativo. A pessoa necessita desenvolver seus próprios recursos, estudando e se dedicando o máximo possível, além de lutar para tornar-se independente e chegar ao terceiro Ciclo já com definição profissional, social e financeira.'}, {'categoria': '2º Ciclo de Vida', 'valor': '2', 'descricao': 'O 2 (dois) neste período é indicador de sociabilidade e receptividade. É necessário cultivar a paciência, o tato, a diplomacia e a capacidade de perceber os sentimentos alheios. Pode indicar ainda, uma carreira diplomática, ser juiz, médico, professor ou consultor.'}, {'categoria': '2º Ciclo de Vida', 'valor': '3', 'descricao': 'O 3 (três) nos mostra uma fase agradável na vida, com certa despreocupação. É a fase da sociabilidade, na qual a criatividade e a originalidade podem exteriorizar suas idéias e sentimentos através de algum tipo de arte: pintura, música, teatro, escrita, etc. É um magnífico período para se desenvolver a criatividade, porém, não deve despender demasiada energia, principalmente em coisas fúteis.'}, {'categoria': '2º Ciclo de Vida', 'valor': '4', 'descricao': 'O 4 (quatro) é sinônimo de trabalho duro, de produtividade e de construção do alicerce que deverá se apoiar no futuro. É um período em que a pessoa necessita aprender a aceitar a rotina e a trabalhar em algo produtivo, sólido e a fazer grande economia.'}, {'categoria': '2º Ciclo de Vida', 'valor': '5', 'descricao': 'O 5 (cinco) é indicativo de um período de expansão de horizontes, época propícia a viagens, mudanças, romances, liberdade, de novas atividades e também novos amigos. Quase sempre, neste período, a pessoa terá de encontrar as suas oportunidades, longe do domicílio. Precisa aprender a se adaptar, a procurar novas maneiras de ver as coisas e a evitar a tendência para fixar-se num determinado lugar. Em resumo, é um período de grande movimentação, de grandes mudanças e de novos horizontes.'}, {'categoria': '2º Ciclo de Vida', 'valor': '6', 'descricao': 'O 6 (seis) neste Ciclo nos mostra um período de ajustes e de responsabilidades nos assuntos domésticos em geral. É um bom momento para se contrair matrimônio, ter filhos e solidificar a família. Em suma, é um período familiar, de colocar a casa em ordem, de viver mais para a família, e deixar de ser tanto individualista.'}, {'categoria': '2º Ciclo de Vida', 'valor': '7', 'descricao': 'O 7 (sete) indica um período de crescimento tranquilo, de estudos e de meditação. A menos que esteja casado, este não é um bom Ciclo para se contrair matrimônio, pois a pessoa necessita desenvolver seus recursos interiores e a incompreensão quase sempre aparece nesse período.'}, {'categoria': '2º Ciclo de Vida', 'valor': '8', 'descricao': 'O 8 (oito) neste Ciclo mostra um período de preocupação com os aspectos materiais da vida. Normalmente a pessoa tem tendência a adquirir riqueza e poder material. Existe, ainda, a grande possibilidade de realizações no mundo dos negócios, a ganhar muito dinheiro com o trabalho e também através de especulações.'}, {'categoria': '2º Ciclo de Vida', 'valor': '9', 'descricao': 'O 9 (nove) neste Ciclo traz a possibilidade de sucesso na vida pública. É um período altamente espiritual e a pessoa necessita aprender a cultivar a tolerância, o amor à humanidade, o altruísmo e o controle emocional. Dificilmente um romance é bem sucedido e os casamentos tendem a pouca duração caso sejam realizados neste período e também é indício de alguma perda, seja ela material, afetiva ou social.'}, {'categoria': '2º Ciclo de Vida', 'valor': '11', 'descricao': 'O 11 (onze) nos mostra um período de ideais, de revelações, de grandeza e, possivelmente, de fama. Aconselha- se que a pessoa se mantenha longe de empreendimentos comerciais ou de especulações, sejam elas financeiras ou imobiliárias. É o momento de desenvolver a mente, de especializar-se em alguma coisa, de estudar, ensinar e também de inspirar as outras pessoas através do seu próprio exemplo.'}, {'categoria': '2º Ciclo de Vida', 'valor': '22', 'descricao': 'O 22 (vinte e dois) no Segundo Ciclo é indício de grandes realizações e de liderança em alto nível. O objetivo primordial da pessoa neste Ciclo deve ser o de beneficiar a humanidade como um todo. Em virtude do grande poder deste número, os nervos e as emoções serão testados durante todo o período e a pessoa deve se manter o mais calmo possível e seguir a orientação da sua intuição.'}, {'categoria': '3º Ciclo de Vida', 'valor': '1', 'descricao': 'O 1 (um) nos indica um final de vida solitário. A pessoa precisa permanecer ativa e independente e contar com seus próprios recursos.'}, {'categoria': '3º Ciclo de Vida', 'valor': '2', 'descricao': 'O 2 (dois) mostra um período de amor sincero e de amigos íntimos. A pessoa se sentirá impelida a colecionar coisas, tais como selos, moedas, antiguidades ou qualquer coisa extravagante.'}, {'categoria': '3º Ciclo de Vida', 'valor': '3', 'descricao': 'O 3 (três) no terceiro Ciclo de Vida indica um período de expressão de idéias e sentimentos através de diversas formas de arte, música, teatro e literatura. A criatividade vai se desenvolver. Haverá muitos amigos e grande atividade social.'}, {'categoria': '3º Ciclo de Vida', 'valor': '4', 'descricao': 'O 4 (quatro) neste Ciclo nos mostra que a pessoa, mesmo aposentada, deverá continuar trabalhando, seja por necessidade, seja por escolha, pois o 4 não o deixará levar uma vida monótona e rotineira.'}, {'categoria': '3º Ciclo de Vida', 'valor': '5', 'descricao': 'O 5 (cinco) é o período da liberdade pessoal, de viagens, mudanças, de novas atividades e variedade, seja de amigos, de atividades ou de residência.'}, {'categoria': '3º Ciclo de Vida', 'valor': '6', 'descricao': 'O 6 (seis) poderá ser o mais agradável de todos os terceiros ciclos de vida - uma fase de felicidade e harmonia no lar - se a pessoa tiver aprendido a adaptar-se e assumir responsabilidades. Caso não tenha aprendido estas coisas, ela poderá ser sobrecarregada com muitos problemas domésticos.'}, {'categoria': '3º Ciclo de Vida', 'valor': '7', 'descricao': 'O 7 (sete) indica um período de isolamento ou de semi - isolamento. Trata-se de uma fase tranquila, apropriada para se estudar em casa e adquirir sabedoria e conhecimento.'}, {'categoria': '3º Ciclo de Vida', 'valor': '8', 'descricao': 'O 8 (oito) neste Ciclo mostra que a pessoa precisa agir com sabedoria, trabalhar e estudar duramente nos dois primeiros, quando terá grande possibilidade de ficar rico neste e ter poder e sucesso ilimitados no mundo dos negócios.'}, {'categoria': '3º Ciclo de Vida', 'valor': '9', 'descricao': 'O 9 (nove) mostra um período de retiro para o estudo e o aprendizado. A pessoa precisa cultivar a tolerância e o amor pela humanidade. Neste Ciclo geralmente há alguma espécie de perda.'}, {'categoria': '3º Ciclo de Vida', 'valor': '22', 'descricao': 'O 22 (vinte e dois) no terceiro ciclo de vida talvez torne a pessoa tensa e nervosa. Ela deve procurar manter-se ativa durante esse período e dedicar-se a um hobby, tal como a escultura, a pintura, as artes divinatórias, etc.'}, {'categoria': 'Desafio', 'valor': '1', 'descricao': 'Desafio 1 - O consulente precisará aprender a se situar num meio termo entre um sentimento excessivo ou insuficiente de sua própria personalidade ou importância. Precisa aprender a ser firme, positivo independente e autoconfiante, sem impor sua vontade às outras pessoas ou esperar que tudo gire em torno de si.'}, {'categoria': 'Desafio', 'valor': '2', 'descricao': 'Desafio 2 - Poderá tender a ser tão sensível em relação aos seus próprios sentimentos e a passar tanto tempo pensando neles, que acabará não tomando conhecimento dos sentimentos dos outros. Pequenas coisas são ampliadas fora de qualquer proporção e nunca esquecidas ou perdoadas. O consulente precisa aprender a cuidar de si mesmo, a cultivar uma atitude mais liberal e tolerante em relação à vida e a parar de utilizar seus próprios sentimentos e emoções como ponto de referência para tudo.'}, {'categoria': 'Desafio', 'valor': '3', 'descricao': 'Desafio 3 - Precisará aprender a situar-se num meio termo, entre ter medo de contatos sociais e ser por demais festeiro. Tem de aprender a ser sociável e a exprimir suas idéias e sentimentos sem dispersar suas energias ou comportar-se como pessoa fútil.'}, {'categoria': 'Desafio', 'valor': '4', 'descricao': 'Desafio 4 - É o mais fácil de todos os desafios, visto que não há nenhum conflito envolvido. Precisa aprender a situar-se num meio termo entre agir como um “burro de carga” ou ser preguiçoso.'}, {'categoria': 'Desafio', 'valor': '5', 'descricao': 'Desafio 5 - Precisa aprender a situar-se num meio- termo entre desejar uma liberdade excessiva e ter um receio injustiçado dela - entre uma ânsia exagerada de experiências sensuais e o medo de tentar coisas novas. Precisa aprender a não buscar sexo, álcool e drogas e - o mais difícil de tudo - precisa aprender quando e como renunciar a pessoas ou coisas cuja presença na sua vida não tem mais razão de ser.'}, {'categoria': 'Desafio', 'valor': '6', 'descricao': 'Desafio 6- Precisa aprender a situar-se num meio termo entre comportar-se como um “capacho” ou ser demasiado exigente e dominador. Precisa aprender a aceitar as pessoas como elas são sem esperar que elas vivam de acordo com os seus padrões; respeitar os pontos de vista de todos e não estabelecer regras além de você mesmo.'}, {'categoria': 'Desafio', 'valor': '7', 'descricao': 'Desafio 7 - Precisará aprender a situar-se num meio termo entre o orgulho excessivo e a modéstia exagerada. Deveria tomar cuidado para não se refugiar dentro de si mesmo e nem tentar escapar das coisas desagradáveis da vida, recorrendo ao álcool e às drogas. É particularmente uma boa educação, aprender a compreender o que se passa no mundo à sua volta e - acima de tudo - ter fé.'}, {'categoria': 'Desafio', 'valor': '8', 'descricao': 'Desafio 8 - Precisará aprender a situar-se num meio termo entre uma preocupação excessiva com as questões materiais, e um desinteresse exagerado em relação a esse assunto. Precisa aprender a utilizar corretamente o dinheiro e o poder e a voltar seu pensamento para outras coisas que não o dinheiro e o que ele poderá fazer por você.'}, {'categoria': 'Momento Decisivo', 'valor': '1', 'descricao': 'MOMENTO DECISIVO 1 - Não é um período fácil; exige coragem, determinação e muita força de vontade. É o momento propício para se “cultivar” a individualidade, a independência e a engenhosidade. Inúmeros acasos e situações inesperadas forçarão a pessoa a enfrentar a vida pensando e agindo por si mesma. Um Momento Decisivo 1 no primeiro Ciclo de Vida, indica uma criança agitada, voluntariosa e por vezes complicada, que será difícil controlar e compreender.'}, {'categoria': 'Momento Decisivo', 'valor': '2', 'descricao': 'MOMENTO DECISIVO 2 - Traz consigo a oportunidade para “cultivar” o tato e a compreensão. Se for amigo, companheiro e atencioso com seus semelhantes, este será um período de amizades sinceras e de relacionamentos duradouros. Excelente fase para se contrair matrimônio. Se for impaciente e desatencioso, poderá ser uma fase de relacionamentos difíceis, de grandes incompreensões, brigas, discussões, em que você poderá causar graves prejuízos às pessoas que o cercam. Um Momento Decisivo 2 no primeiro Ciclo de Vida, é indício de uma “mãe” forte e dominadora, ou pai ausente (por motivo de trabalho, morte ou separação). A criança, nesse caso, pode se tornar excessivamente sensível e ter reflexos dessa sensibilidade na juventude e adolescência, obstruindo dessa maneira, as possibilidades de progresso.'}, {'categoria': 'Momento Decisivo', 'valor': '3', 'descricao': 'MOMENTO DECISIVO 3 - É o momento de expandir a vida social e “cultivar” os próprios talentos. Trata-se de uma fase apropriada para a auto-expressão, novas amizades, romance e fertilidade. A manifestação descuidada das emoções poderá ter consequências desagradáveis, pois existe, nesse estado, tendência ao desmando: vícios, brigas, discórdias. Cuidado com os “amigos”, pois apesar de serem necessários, por vezes são más companhias. Um Momento Decisivo 3 no primeiro Ciclo de Vida, geralmente indica uma criança com dificuldade de se adaptar aos estudos. Indica, também, oportunidades artísticas que se não alimentadas e direcionadas condizentemente, poderão ser desperdiçadas, fazendo com que a pessoa já adulta venha a se lamentar dessa negligência dos pais ou educadores.'}, {'categoria': 'Momento Decisivo', 'valor': '4', 'descricao': 'MOMENTO DECISIVO 4 - Este Momento Decisivo traz a oportunidade de se construir um sólido alicerce para o futuro. É um período de trabalho duro e até de algumas restrições e é necessário “cultivar” a paciência e os bons hábitos de trabalho. Neste período, poderá haver alguns problemas econômicos, que serão superados com inteligência, trabalho e dedicação ao projeto final. A família e os parentes por afinidade podem se transformar num peso e a pessoa terá de ajudá-los, tanto financeiramente, como prestando ajuda humanitária, em uma doença, por exemplo. As recompensas sempre aparecem a partir da aplicação dos preceitos corretos de vida e do esforço para se obter os resultados positivos. Um Momento Decisivo 4 no primeiro Ciclo de Vida, frequentemente indica que a pessoa poderá começar a trabalhar muito nova e a assumir grandes responsabilidades ainda na juventude.'}, {'categoria': 'Momento Decisivo', 'valor': '5', 'descricao': 'MOMENTO DECISIVO 5 - Traz oportunidades para viagens, para experimentar novas sensações, novos empreendimentos e para se livrar de tudo que está obsoleto ou que já não nos faz falta. É uma fase de liberdade, de mudanças e de desenvolvimento pessoal, principalmente se vier após um Momento decisivo 4 ou 6. Um Momento Decisivo 5 no primeiro Ciclo de Vida, indica uma criança ousada, inquieta, esperta e pouco constante. Geralmente empreende mudanças súbitas, ora gostando disto, ora daquilo, sem esperar as recompensas resultantes de um esforço ou trabalho empreendido.'}, {'categoria': 'Momento Decisivo', 'valor': '6', 'descricao': 'MOMENTO DECISIVO 6 - É o momento dos ajustes e das responsabilidades familiares. Caso tenha consciência disso, este é o Momento de grande afetividade, de amor e de felicidade doméstica, além de sucesso e segurança material. Do contrário, ou seja, caso seja dispersivo ou inconstante, poderá ser um período de desgostos, discussões, brigas e graves problemas domésticos e até indício de separação. Um Momento Decisivo 6 no primeiro Ciclo de Vida, geralmente indica casamento precoce ou a responsabilidade de tomar conta dos pais ou de algum familiar. Quando o 6 for o último Momento Decisivo, ele poderá trazer o reconhecimento do trabalho já feito. Caso a pessoa esteja solteira, este Momento trará a oportunidade para um novo amor e para o materialismo.'}, {'categoria': 'Momento Decisivo', 'valor': '7', 'descricao': 'MOMENTO DECISIVO 7 - É uma fase de introspecção, de meditação e estudo do significado último da vida. Caso não esteja casado, desaconselhamos o matrimônio nesta fase. Velhos relacionamentos que não produzem mais frutos, podem e devem ser deixados para trás. A pessoa normalmente sente vontade de se retirar para dentro de si mesma, o que de certa forma poderá causar problemas de relacionamento, tanto a nível pessoal como familiar. Um Momento Decisivo 7 no primeiro Ciclo de Vida, nos indica uma criança retraída, solitária, pensativa e muito estuda. Quando os pais são excessivamente rígidos e severos, a criança poderá, pela regressão de suas idéias e projetos, contrair algum tipo de doença psicossomática ou mesmo depressão, ser temperamental e desenvolver algum tipo de complexo.'}, {'categoria': 'Momento Decisivo', 'valor': '8', 'descricao': 'MOMENTO DECISIVO 8 - É um período de grandes realizações no mundo dos negócios. As despesas são altas, não obstante, é uma excelente fase para se correr atrás dos objetivos, de conquistar poder, fama e sucesso material. Com dedicação, estudo e trabalho sistemático, com objetivo definido e com colaboradores aptos e interessados, a pessoa dificilmente deixa de conseguir tudo o que deseja. Um Momento Decisivo 8 no primeiro Ciclo de Vida, indica que a pessoa começará ainda jovem a se dedicar aos negócios, a trabalhar para se sustentar e também sustentar algum membro da família.'}, {'categoria': 'Momento Decisivo', 'valor': '9', 'descricao': 'MOMENTO DECISIVO 9 - Traz a oportunidade para se “cultivar” o amor, a solidariedade, o altruísmo e para se viajar para o exterior. Poderá haver algum tipo de perda e até desapontamentos, principalmente entre amigos. Um bom investimento para o consulente é fazer obras humanitárias durante este período, pois os frutos dessa plantação são certos, e o sucesso e a fama se farão presentes. Um Momento Decisivo 9 no primeiro Ciclo de Vida, normalmente não é dos mais afortunados, pois quase sempre a criança é incompreendida por colegas, amigos e até familiares, que por causa dessa incompreensão exigem muito e retribuem pouco, o que faz com que o jovem se retraia e fique tímido e introspectivo.'}, {'categoria': 'Momento Decisivo', 'valor': '11', 'descricao': 'MOMENTO DECISIVO 11 - Por ser um número altamente espiritual e elevado, a pessoa nesse período sente-se tensa e muito nervosa. É uma excelente fase para estudar esoterismo, espiritualismo e expandir seus horizons. Este momento traz inspiração, iluminação e, quase sempre, fama e prestígio nacional e até internacional. Não faça nada nem diga por trás o que não teria coragem de dizer ou fazer na frente das pessoas.'}, {'categoria': 'Momento Decisivo', 'valor': '22', 'descricao': 'MOMENTO DECISIVO 22 - É, sem dúvida alguma, o número e o Momento mais pode-roso. A pessoa fica altamente criativa e neste estado tornam-se possíveis todas as realizações. É uma fase de interesses pelos problemas mundiais e de grande expansão da consciência.'}]
    
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
            cat = row.get('categoria', '')
            val = str(row.get('valor', ''))
            desc = row.get('descricao', '')
            if cat not in resultado:
                resultado[cat] = {}
            resultado[cat][val] = desc
    except Exception:
        pass
        
    return resultado

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
        "diferenciais_descricao", "peso_categoria", "atributos", "matriz", "qualidades",
        "descricoes_mapa"
    ]
    
    tab_selecionada = st.selectbox("Selecione a Tabela para Editar", tabelas)
    
    if supabase_client:
        try:
            # Busca dados atuais
            res = supabase_client.table(tab_selecionada).select("*").execute()
            df_edit = pd.DataFrame(res.data)
            
            # Se descricoes_mapa estiver vazia no banco, puxa os dados do fallback local
            if df_edit.empty and tab_selecionada == "descricoes_mapa":
                dict_mapa = fetch_descricoes_mapa()
                flat_data = []
                for cat, subdict in dict_mapa.items():
                    for val, desc in subdict.items():
                        flat_data.append({"categoria": cat, "valor": val, "descricao": desc})
                df_edit = pd.DataFrame(flat_data)
            
            if not df_edit.empty or tab_selecionada == "descricoes_mapa":
                st.write(f"Editando: `{tab_selecionada}`")
                
                # Garante colunas mínimas caso venha vazio
                if df_edit.empty:
                    df_edit = pd.DataFrame(columns=["categoria", "valor", "descricao"])
                
                # Editor de dados com altura limitada
                edited_df = st.data_editor(df_edit, num_rows="dynamic", use_container_width=True, hide_index=True, height=450)
                
                if st.button(f"💾 Salvar Alterações em {tab_selecionada}"):
                    with st.spinner("Sincronizando com Supabase..."):
                        try:
                            # Tenta deletar se houver RLS permissivo ou ignorar
                            supabase_client.table(tab_selecionada).delete().neq("id", -1).execute() 
                            novos_dados = edited_df.to_dict(orient='records')
                            
                            # Limpa campos nulos de ID para não quebrar no banco
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
        with st.container(border=True):
            st.markdown("### 👤 Novo Cadastro")
            nome = st.text_input("Nome Completo (Conforme certidão):", value=st.session_state.get('ocr_nome', ''))
            
            col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
            with col_f1:
                data_str_input = st.text_input("Data de Nascimento:", placeholder="dd/mm/yyyy", value=st.session_state.get('ocr_data_nascimento', ''))
            with col_f2:
                foto_upload = st.file_uploader("Foto (Opcional)", type=["png", "jpg", "jpeg"])
            with col_f3:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("📷 Ativar Câmera", use_container_width=True):
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
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
            with col_btn1:
                submit_mapa = st.button("🏁 Gerar Mapa")
            with col_btn2:
                submit_perfil = st.button("🧠 Gerar Perfil")
            
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
        
        rep2 = repeticao_mapa
        rep3 = repeticao_2_mapa

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
            dividas_str = ', '.join(str(d) for d in dividas_carmicas)
            dividas_parts = []
            for d in dividas_carmicas:
                desc_d = get_desc_mapa("Divida Carmica", str(d))
                dividas_parts.append(f"<b>{d}</b>: {desc_d}" if desc_d else str(d))
            add_row(f"Dívidas Cármicas - {dividas_str}", ' | '.join(dividas_parts))
        else:
            add_row("Dívidas Cármicas", "Não há")

        # Lições Cármicas com descrições
        if licoes_carmicas:
            licoes_str = ', '.join(str(l) for l in licoes_carmicas)
            licoes_parts = []
            for l in licoes_carmicas:
                desc_l = get_desc_mapa("Licao Carmica", str(l))
                licoes_parts.append(f"<b>{l}</b>: {desc_l}" if desc_l else str(l))
            add_row(f"Lições Cármicas - {licoes_str}", ' | '.join(licoes_parts))
        else:
            add_row("Lições Cármicas", "Não há")

        # Tendências Ocultas com descrições
        if tendencias_ocultas:
            tend_str = ', '.join(str(t) for t in tendencias_ocultas)
            tend_parts = []
            for t in tendencias_ocultas:
                desc_t = get_desc_mapa("Tendencia Oculta", str(t))
                tend_parts.append(f"<b>{t}</b>: {desc_t}" if desc_t else str(t))
            add_row(f"Tendências Ocultas - {tend_str}", ' | '.join(tend_parts))
            add_row("Soma das Tendências Ocultas", soma_tendencias)
        else:
            add_row("Tendências Ocultas", "Não há")

        # Resposta Subconsciente com descrição
        desc_resp = get_desc_mapa("Resposta Subconsciente", str(extract_num(resposta_subconsciente) if resposta_subconsciente else ""))
        add_row(f"Resposta Subconsciente - {resposta_subconsciente}", desc_resp if desc_resp else "")

        # Dia Natalício com descrição (usa o dia bruto 1-31)
        desc_dia_nat = get_desc_mapa("Dia Natalicio", str(nascimento[0]))
        add_row(f"Dia Natalício - {nascimento[0]}", desc_dia_nat if desc_dia_nat else "")

        # Desafios com descrição
        desc_des1 = get_desc_mapa("Desafio", str(desafio1))
        add_row(f"1º Desafio - {desafio1}", desc_des1 if desc_des1 else "")

        desc_des2 = get_desc_mapa("Desafio", str(desafio2))
        add_row(f"2º Desafio - {desafio2}", desc_des2 if desc_des2 else "")

        desc_des_princ = get_desc_mapa("Desafio", str(desafio_principal))
        add_row(f"Desafio Principal - {desafio_principal}", desc_des_princ if desc_des_princ else "")

        # Ciclos de Vida
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

        # Momentos Decisivos
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

        # Recarrega configurações dinamicamente
        MATRIZ_DB = fetch_matriz()
        ATRIBUTOS_DB = fetch_atributos()
        REPETICAO_DB = fetch_repeticao()
        PESO_DB = fetch_peso()

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
                    attr_t = str(get_from_row(row_m, campo_s) or "").upper()
                    
                    if (not attr_t or attr_t == "NAN") and str(val_s).isdigit() and int(val_s) in (11, 22, 33):
                        num_reduz = sum(int(d) for d in str(val_s))
                        row_m_reduz = MATRIZ_DB.get(str(num_reduz))
                        if row_m_reduz:
                            attr_t = str(get_from_row(row_m_reduz, campo_s) or "").upper()
                            
                    if attr_t and attr_t != "NAN":
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
        dados_auditoria_qual = []
        
        for campo_q in colunas_qual:
            val_q = valores_originais_score[campo_q]
            if val_q is None: continue
            
            qual_encontrada = None
            attr_t_q = None
            if campo_q in mapa_col_matriz:
                row_m_q = MATRIZ_DB.get(str(val_q))
                if row_m_q:
                    attr_t_q = str(get_from_row(row_m_q, campo_q) or "").upper()
                    
                    if (not attr_t_q or attr_t_q == "NAN") and str(val_q).isdigit() and int(val_q) in (11, 22, 33):
                        num_reduz = sum(int(d) for d in str(val_q))
                        row_m_reduz = MATRIZ_DB.get(str(num_reduz))
                        if row_m_reduz:
                            attr_t_q = str(get_from_row(row_m_reduz, campo_q) or "").upper()
                            
                    if attr_t_q and attr_t_q != "NAN":
                        ai_q = ATRIBUTOS_DB.get(attr_t_q)
                        if ai_q:
                            qual_encontrada = get_from_row(ai_q, 'qualidade') or get_from_row(ai_q, 'area de suporte')
            else:
                ri_q = REPETICAO_DB.get(str(val_q))
                if ri_q:
                    qual_encontrada = get_from_row(ri_q, 'qualidade') or get_from_row(ri_q, 'area de suporte')
                    attr_t_q = "Tabela Repetição"
                
            if qual_encontrada:
                qn = remover_acentos(str(qual_encontrada).strip()).upper()
                # Busca insensível a maiúsculas/minúsculas e acentos no index
                for idx_name in score_qual_df.index:
                    if remover_acentos(idx_name).upper() == qn:
                        pv_qual = PESO_DB.get(campo_q, 0)
                        score_qual_df.at[idx_name, campo_q] += int(pv_qual)
                        break
            
            dados_auditoria_qual.append({
                "Campo": campo_q,
                "Valor": val_q,
                "Matriz": attr_t_q if attr_t_q else "N/A",
                "Qualidade": qual_encontrada if qual_encontrada else "N/A"
            })
                    
        score_qual_df['TOTAL'] = score_qual_df.sum(axis=1)
        auditoria_qual_df = pd.DataFrame(dados_auditoria_qual)
        
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
        qualidades_escolhidas = list(totais_q.index)[:2]
        
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
                
                st.header("Detalhamento dos Atributos")
                st.table(auditoria_qual_df)
                
                st.header("Plano KAN")
                df_plano_kan = pd.DataFrame({
                    "Campo": ["KAN", "ESTRUTURAL", "DIRECIONAMENTO", "REPETIÇÃO 1", "REPETICAO MAPA", "REPETICAO 2 MAPA"],
                    "Valor": [
                        kan, 
                        estrutural, 
                        direcionamento, 
                        str(rep1).split(" - ")[0] if " - " in str(rep1) else str(rep1), 
                        str(rep2).split(" - ")[0] if " - " in str(rep2) else str(rep2),
                        str(rep3).split(" - ")[0] if " - " in str(rep3) else str(rep3)
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
                
                vertices = [
                    {"campo": "KAN", "valor": k_val},
                    {"campo": "ESTRUTURAL", "valor": e_val},
                    {"campo": "DIRECIONAMENTO", "valor": d_val}
                ]
                
                pool = []
                if r1_val is not None and r1_val not in [11, 22]:
                    pool.append({"campo": "REPETIÇÃO 1", "valor": r1_val})
                if r2_val is not None and r2_val not in [11, 22]:
                    pool.append({"campo": "REPETICAO MAPA", "valor": r2_val})
                if r3_val is not None and r3_val not in [11, 22]:
                    pool.append({"campo": "REPETICAO 2 MAPA", "valor": r3_val})
                    
                # Passo 1: Invalidar 11 e 22
                for i in range(3):
                    if vertices[i]["valor"] in [11, 22, None]:
                        if pool:
                            sub = pool.pop(0)
                            vertices[i]["campo"] = f"{vertices[i]['campo']} ({sub['campo']})"
                            vertices[i]["valor"] = sub["valor"]
                        else:
                            vertices[i]["valor"] = None
                            
                # Passo 2: Duplicatas
                valores_atuais = [v["valor"] for v in vertices]
                if len(set([v for v in valores_atuais if v is not None])) < len([v for v in valores_atuais if v is not None]):
                    counts = Counter(valores_atuais)
                    for i in range(3):
                        val = vertices[i]["valor"]
                        if val is not None and counts[val] > 1:
                            if pool:
                                sub = pool.pop(0)
                                vertices[i]["campo"] = f"{vertices[i]['campo']} ({sub['campo']})"
                                vertices[i]["valor"] = sub["valor"]
                                counts = Counter([v["valor"] for v in vertices])
                            else:
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
                                5: (558, 585),
                                6: (243, 579),
                                7: (243, 360),
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
                                        
                                        k_v = clean_val(kan)
                                        e_v = clean_val(estrutural)
                                        d_v = clean_val(direcionamento)
                                        r1_v = clean_val(rep1)
                                        
                                        v_list = [
                                            {"campo": "KAN", "valor": k_v},
                                            {"campo": "ESTRUTURAL", "valor": e_v},
                                            {"campo": "DIRECIONAMENTO", "valor": d_v}
                                        ]
                                        
                                        pool_comp = []
                                        if r1_v is not None and r1_v not in [11, 22]:
                                            pool_comp.append(r1_v)
                                        if r2_v is not None and r2_v not in [11, 22]:
                                            pool_comp.append(r2_v)
                                        if r3_v is not None and r3_v not in [11, 22]:
                                            pool_comp.append(r3_v)
                                            
                                        for i in range(3):
                                            if v_list[i]["valor"] in [11, 22, None]:
                                                if pool_comp:
                                                    v_list[i]["valor"] = pool_comp.pop(0)
                                                else:
                                                    v_list[i]["valor"] = None
                                                    
                                        valores_atuais = [v["valor"] for v in v_list]
                                        if len(set([v for v in valores_atuais if v is not None])) < len([v for v in valores_atuais if v is not None]):
                                            counts = Counter(valores_atuais)
                                            for i in range(3):
                                                val = v_list[i]["valor"]
                                                if val is not None and counts[val] > 1:
                                                    if pool_comp:
                                                        v_list[i]["valor"] = pool_comp.pop(0)
                                                        counts = Counter([v["valor"] for v in v_list])
                                                    else:
                                                        break
                                                    
                                        if len(set([v["valor"] for v in v_list])) == 3:
                                            return [v["valor"] for v in v_list]
                                    except Exception as ex:
                                        st.error(f"Erro ao processar {nome_comp}: {ex}")
                                    return None

                                perfis_disp = sorted([n for n in clientes_salvos.keys() if n != nome])
                                perfis_selecionados = st.multiselect("Pesquise e selecione os perfis:", options=perfis_disp)
                                
                                if perfis_selecionados:
                                    # Camada para o triângulo original
                                    layer_base = Image.new("RGBA", fundo_img.size, (255, 255, 255, 0))
                                    draw_base = ImageDraw.Draw(layer_base)
                                    draw_base.polygon(poly_points, fill=(255, 255, 255, 140))
                                    
                                    img_multi_final = Image.alpha_composite(fundo_img, layer_base)
                                    
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
                                                
                                    st.image(img_multi_final.convert("RGB"), caption="Comparativo de Triângulos Harmônicos", use_container_width=True)
                                    
                    except Exception as e:
                        st.error(f"Erro ao gerar triângulo visual: {e}")
                else:
                    st.warning("⚠️ O triângulo harmônico não foi formado.")


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
