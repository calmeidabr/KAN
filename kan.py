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
    
    /* --- DESIGN EXCLUSIVO DO SIDEBAR (KAN V3 PREMIUM) --- */
    section[data-testid="stSidebar"] {
        background-color: #270828 !important;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    section[data-testid="stSidebar"] > div,
    [data-testid="stSidebarContent"], [data-testid="stSidebarHeader"] {
        background: transparent !important;
    }

    /* Container do Perfil do Usuário no rodapé */
    .user-profile-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 12px 14px;
        border-radius: 14px;
        margin-top: 15px;
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .user-profile-card:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(241, 134, 23, 0.4);
    }

    /* Botões do Menu Lateral - Estilo Monocromático & Clean */
    .stApp section[data-testid="stSidebar"] div.stButton > button {
        border: none !important;
        background-color: transparent !important;
        color: rgba(255,255,255,0.75) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 10px 16px !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        filter: grayscale(100%) opacity(0.85);
    }

    .stApp section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #FFFFFF !important;
        transform: translateX(3px) !important;
        filter: grayscale(0%) opacity(1);
    }

    /* Item Selecionado no Sidebar */
    .stApp section[data-testid="stSidebar"] div.stButton > button[kind="primary"],
    .stApp section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(90deg, rgba(241, 134, 23, 0.2) 0%, rgba(255, 255, 255, 0.03) 100%) !important;
        color: #F18617 !important;
        font-weight: 700 !important;
        border-left: 3px solid #F18617 !important;
        border-radius: 3px 10px 10px 3px !important;
        filter: grayscale(0%) opacity(1);
    }
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
