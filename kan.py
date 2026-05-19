import streamlit as st
from PIL import Image
import os

# 1. Configuração da Página
try:
    favicon_img = Image.open(os.path.join("images", "kan_logo_peq.png"))
except Exception:
    favicon_img = "🔮"

st.set_page_config(page_title="KAN Perfil Comportamental", layout="wide", page_icon=favicon_img)

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
    section[data-testid="stSidebar"] {
        width: 310px !important;
        min-width: 310px !important;
        max-width: 310px !important;
        background-color: #270828 !important;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    section[data-testid="stSidebar"] > div,
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
        background-color: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
    }
    [data-testid="stSidebarContent"]::-webkit-scrollbar-thumb:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }

    /* Container do Perfil do Usuário no rodapé */
    .user-profile-card {
        background: rgba(255, 255, 255, 0.03) !important;
        padding: 12px 14px !important;
        border-radius: 12px !important;
        margin-top: 15px !important;
        margin-bottom: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }
    .user-profile-card:hover {
        background: rgba(255, 255, 255, 0.06) !important;
        border-color: rgba(241, 134, 23, 0.3) !important;
        box-shadow: 0 6px 20px rgba(241, 134, 23, 0.08) !important;
    }

    /* Botões Gerais do Sidebar */
    .stApp section[data-testid="stSidebar"] div.stButton > button {
        border: none !important;
        background-color: transparent !important;
        color: rgba(255,255,255,0.7) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        font-weight: 600 !important;
        box-shadow: none !important;
        font-size: 0.9em !important;
    }

    /* Hover nos botões gerais */
    .stApp section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #FFFFFF !important;
        transform: translateX(2px) !important;
    }

    /* Item Selecionado Geral */
    .stApp section[data-testid="stSidebar"] div.stButton > button[kind="primary"],
    .stApp section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(90deg, rgba(241, 134, 23, 0.15) 0%, rgba(255, 255, 255, 0.02) 100%) !important;
        color: #F18617 !important;
        font-weight: 700 !important;
        border-left: 3px solid #F18617 !important;
        border-radius: 0 8px 8px 0 !important;
    }

    /* Submenus Aninhados (dentro de containers internos do sidebar) */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button {
        border-left: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 0 !important;
        padding: 8px 12px 8px 24px !important;
        margin-left: 20px !important;
        font-size: 0.86em !important;
        font-weight: 500 !important;
        color: rgba(255,255,255,0.55) !important;
    }
    
    /* Hover específico nos Submenus Aninhados */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        border-left: 1px solid rgba(255, 255, 255, 0.25) !important;
        background-color: rgba(255, 255, 255, 0.04) !important;
        color: #FFFFFF !important;
    }

    /* Submenu Ativo Aninhado */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button[data-testid="baseButton-primary"] {
        border-left: 2px solid #F18617 !important;
        background: linear-gradient(90deg, rgba(241, 134, 23, 0.12) 0%, rgba(255, 255, 255, 0.02) 100%) !important;
        color: #F18617 !important;
        font-weight: 700 !important;
    }

    /* Botões de Ação no Rodapé (Sair / Reset) dentro de colunas */
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div.stButton > button {
        font-size: 0.8em !important;
        padding: 8px 10px !important;
        border-radius: 8px !important;
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        color: rgba(255, 255, 255, 0.8) !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        font-weight: 600 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(241, 134, 23, 0.3) !important;
        color: #F18617 !important;
        transform: translateY(-1px) !important;
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
