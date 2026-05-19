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
    
    /* Perfil Card e Containers */
    .user-profile-card {
        background: rgba(0,0,0,0.25);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 14px;
        margin-top: 15px;
    }
    
    div[data-testid="stContainer"] {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
        padding: 20px;
        margin-bottom: 20px;
    }
    
    div[data-testid="stSidebar"] {
        background-color: #270828 !important;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
</style>
""", unsafe_allow_html=True)

# 3. Inicialização e Execução do Roteador Central
from app import App

app = App()
app.run()
