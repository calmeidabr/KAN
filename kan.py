import streamlit as st
from PIL import Image
import os

# 1. Configuração da Página
try:
    favicon_img = os.path.join("images", "ico_k.png")
    if not os.path.exists(favicon_img):
        favicon_img = "◇"
except Exception:
    favicon_img = "◇"

st.set_page_config(
    page_title="KAN Perfil Comportamental", 
    layout="wide", 
    page_icon=favicon_img,
    initial_sidebar_state="expanded"
)

# 2. Estilização CSS Global
st.markdown("""
<style>
    /* Restaurando Identidade KAN e Base Global */
    .stApp {
        background-color: #401041 !important;
        color: #FFFFFF !important;
    }
    
    h1, h2, h3, h4, h5, h6, .st-emotion-cache-1104g95 {
        color: #FFFFFF !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #F18617 0%, #D97706 100%);
        color: #1b0520 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 12px rgba(241, 134, 23, 0.3) !important;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(241, 134, 23, 0.5) !important;
        filter: brightness(1.1);
    }
    
    /* Botões secundários no menu */
    .stButton > button[data-testid="baseButton-secondary"] {
        background: rgba(255,255,255,0.05) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        box-shadow: none !important;
    }
    
    .stButton > button[data-testid="baseButton-secondary"]:hover {
        background: rgba(255,255,255,0.1) !important;
        border-color: #F18617 !important;
        color: #F18617 !important;
    }
    
    /* --- DESIGN EXCLUSIVO DO SIDEBAR (KAN V3 SAAS PREMIUM) --- */
    :root {
        --sidebar-bg: linear-gradient(180deg, #0b020c 0%, #160318 100%);
        --panel-bg: rgba(255,255,255,0.03);
        --panel-border: rgba(255,255,255,0.06);
        --text-main: #f8fafc;
        --text-soft: #94a3b8;
        --accent: #F18617;
        --radius: 18px;
    }

    [data-testid="stSidebar"][data-collapsed="false"] {
        background: var(--sidebar-bg) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
        width: 340px !important;
        min-width: 340px !important;
        max-width: 340px !important;
    }

    [data-testid="stSidebar"][data-collapsed="true"] {
        width: 0px !important;
        min-width: 0px !important;
        max-width: 0px !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
    }

    [data-testid="stSidebar"][data-collapsed="false"] > div:first-child {
        width: 340px !important;
    }

    /* Ajusta a área principal da página para expandir ou encolher com o sidebar */
    [data-testid="stMain"] {
        transition: padding-left 0.2s ease-in-out !important;
    }
    .stApp:has([data-testid="stSidebar"][data-collapsed="false"]) [data-testid="stMain"] {
        padding-left: 340px !important;
    }
    .stApp:has([data-testid="stSidebar"][data-collapsed="true"]) [data-testid="stMain"] {
        padding-left: 0px !important;
    }

    [data-testid="stSidebarContent"], [data-testid="stSidebarHeader"] {
        background: transparent !important;
    }
    
    /* Scrollbar customizada ultra-fina */
    [data-testid="stSidebarContent"]::-webkit-scrollbar {
        width: 5px;
    }
    [data-testid="stSidebarContent"]::-webkit-scrollbar-track {
        background: transparent;
    }
    [data-testid="stSidebarContent"]::-webkit-scrollbar-thumb {
        background-color: rgba(255, 255, 255, 0.06);
        border-radius: 10px;
    }

    /* Marca / Topo do Sidebar (.sb-brand) */
    .sb-brand {
        padding: 0.9rem 1rem 1.1rem 1rem;
        margin-bottom: 1rem;
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(241,134,23,0.15), rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }
    .sb-brand-title {
        color: var(--text-main);
        font-size: 1.25rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
    }
    .sb-brand-sub {
        color: var(--text-soft);
        font-size: 0.78rem;
        margin-top: 0.35rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        font-weight: 600;
        opacity: 0.8;
    }

    /* Estilo dos containers st.container(border=True) como seções (.sb-section) */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {
        margin-top: 0.8rem !important;
        margin-bottom: 0.8rem !important;
        padding: 0.85rem !important;
        border-radius: var(--radius) !important;
        background-color: var(--panel-bg) !important;
        border: 1px solid var(--panel-border) !important;
        backdrop-filter: blur(8px) !important;
    }

    .sb-label {
        color: var(--text-soft);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 700;
        margin-bottom: 0.65rem;
        padding-left: 4px;
    }

    /* Container do Perfil do Usuário no rodapé */
    .user-profile-card {
        background: var(--panel-bg) !important;
        padding: 12px 14px !important;
        border-radius: 14px !important;
        margin-top: 15px !important;
        margin-bottom: 10px !important;
        border: 1px solid var(--panel-border) !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }
    .user-profile-card:hover {
        background: rgba(255, 255, 255, 0.04) !important;
        border-color: rgba(241, 134, 23, 0.3) !important;
        box-shadow: 0 6px 20px rgba(241, 134, 23, 0.08) !important;
    }

    /* Botões Gerais do Sidebar - Sem Contorno e com Fundo Transparente */
    .stApp section[data-testid="stSidebar"] div.stButton > button {
        border: none !important;
        background: transparent !important;
        background-color: transparent !important;
        background-image: none !important;
        color: var(--text-soft) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        font-size: 0.9em !important;
    }

    /* Hover nos botões gerais - Sem Contorno */
    .stApp section[data-testid="stSidebar"] div.stButton > button:hover {
        background: rgba(255, 255, 255, 0.04) !important;
        background-color: rgba(255, 255, 255, 0.04) !important;
        background-image: none !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: none !important;
        transform: translateX(3px) !important;
    }

    /* Item Selecionado Geral - Fundo Transparente, indicador laranja */
    .stApp section[data-testid="stSidebar"] div.stButton > button[kind="primary"],
    .stApp section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-primary"] {
        background: transparent !important;
        background-color: transparent !important;
        background-image: none !important;
        color: var(--accent) !important;
        font-weight: 700 !important;
        border: none !important;
        border-left: 3px solid var(--accent) !important;
        border-radius: 0 8px 8px 0 !important;
        box-shadow: none !important;
    }

    /* Submenus Aninhados - Sem Contorno */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button {
        border: none !important;
        border-left: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 0 !important;
        padding: 8px 12px 8px 24px !important;
        margin-left: 20px !important;
        font-size: 0.86em !important;
        font-weight: 450 !important;
        color: rgba(255,255,255,0.45) !important;
        box-shadow: none !important;
    }
    
    /* Hover específico nos Submenus Aninhados */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        border: none !important;
        border-left: 1px solid rgba(255, 255, 255, 0.25) !important;
        background: rgba(255, 255, 255, 0.03) !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
        background-image: none !important;
        color: #FFFFFF !important;
        box-shadow: none !important;
    }

    /* Submenu Ativo Aninhado */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button[data-testid="baseButton-primary"] {
        border: none !important;
        border-left: 2px solid var(--accent) !important;
        background: transparent !important;
        background-color: transparent !important;
        background-image: none !important;
        color: var(--accent) !important;
        font-weight: 650 !important;
        box-shadow: none !important;
    }

    /* Botões de Ação no Rodapé (Sair / Reset) dentro de colunas */
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div.stButton > button {
        font-size: 0.82em !important;
        padding: 8px 10px !important;
        border-radius: 8px !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        color: var(--text-main) !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        font-weight: 500 !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #FFFFFF !important;
        transform: translateY(-1px) !important;
        box-shadow: none !important;
    }
    
    [data-testid="stSidebarNav"] { display: none; }
    /* --- FIM DESIGN SIDEBAR --- */
    
    div[data-testid="stContainer"] {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
        padding: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Inicialização e Execução do Roteador Central
from app import App

app = App()
app.run()
