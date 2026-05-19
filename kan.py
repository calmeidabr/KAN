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
    
    /* --- DESIGN EXCLUSIVO DO SIDEBAR (KAN V3 SAAS TOTALMENTE ESCURO) --- */
    section[data-testid="stSidebar"] {
        width: 310px !important;
        min-width: 310px !important;
        max-width: 310px !important;
        background-color: #0b020c !important;
        border-right: 1px solid rgba(255,255,255,0.04);
    }
    section[data-testid="stSidebar"] > div,
    [data-testid="stSidebarContent"], [data-testid="stSidebarHeader"] {
        background: transparent !important;
    }
    
    /* Fonte laranja para todos os textos do sidebar */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] label {
        color: #F18617 !important;
    }
    
    /* Scrollbar customizada ultra-fina */
    [data-testid="stSidebarContent"]::-webkit-scrollbar {
        width: 5px;
    }
    [data-testid="stSidebarContent"]::-webkit-scrollbar-track {
        background: transparent;
    }
    [data-testid="stSidebarContent"]::-webkit-scrollbar-thumb {
        background-color: rgba(241, 134, 23, 0.15);
        border-radius: 10px;
    }
    [data-testid="stSidebarContent"]::-webkit-scrollbar-thumb:hover {
        background-color: rgba(241, 134, 23, 0.3);
    }

    /* Container do Perfil do Usuário no rodapé */
    .user-profile-card {
        background: rgba(255, 255, 255, 0.02) !important;
        padding: 12px 14px !important;
        border-radius: 12px !important;
        margin-top: 15px !important;
        margin-bottom: 10px !important;
        border: 1px solid rgba(241, 134, 23, 0.15) !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
    }
    .user-profile-card:hover {
        background: rgba(255, 255, 255, 0.04) !important;
        border-color: rgba(241, 134, 23, 0.4) !important;
        box-shadow: 0 6px 20px rgba(241, 134, 23, 0.1) !important;
    }

    /* Botões Gerais do Sidebar - Sem Contorno e com Fundo Transparente */
    .stApp section[data-testid="stSidebar"] div.stButton > button {
        border: none !important;
        background-color: transparent !important;
        color: rgba(241, 134, 23, 0.75) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 10px 16px !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
        box-shadow: none !important;
    }

    /* Hover nos botões gerais - Fundo Translúcido e Texto Branco (Da Versão Estável) */
    .stApp section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: none !important;
        transform: translateX(3px) !important;
    }

    /* Item Selecionado Geral - Gradiente Laranja Translúcido e Borda Laranja (Da Versão Estável) */
    .stApp section[data-testid="stSidebar"] div.stButton > button[kind="primary"],
    .stApp section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(90deg, rgba(241, 134, 23, 0.2) 0%, rgba(255, 255, 255, 0.03) 100%) !important;
        color: #F18617 !important;
        font-weight: 700 !important;
        border: none !important;
        border-left: 3px solid #F18617 !important;
        border-radius: 3px 10px 10px 3px !important;
        box-shadow: none !important;
    }

    /* Submenus Aninhados - Sem Contorno e Fundo Transparente */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button {
        border: none !important;
        border-left: 1px solid rgba(241, 134, 23, 0.2) !important;
        border-radius: 0 !important;
        padding: 8px 12px 8px 24px !important;
        margin-left: 20px !important;
        font-size: 0.86em !important;
        font-weight: 450 !important;
        color: rgba(241, 134, 23, 0.65) !important;
        box-shadow: none !important;
    }
    
    /* Hover específico nos Submenus Aninhados */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        border-left: 1px solid rgba(255, 255, 255, 0.6) !important;
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #FFFFFF !important;
        box-shadow: none !important;
    }

    /* Submenu Ativo Aninhado */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button[data-testid="baseButton-primary"] {
        border: none !important;
        border-left: 2px solid #F18617 !important;
        background: linear-gradient(90deg, rgba(241, 134, 23, 0.15) 0%, rgba(255, 255, 255, 0.03) 100%) !important;
        color: #F18617 !important;
        font-weight: 650 !important;
        box-shadow: none !important;
    }

    /* Botões de Ação no Rodapé (Sair / Reset) dentro de colunas - Sem Contorno e Fundo Transparente */
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div.stButton > button,
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div.stButton > button:hover {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div.stButton > button {
        font-size: 0.8em !important;
        padding: 8px 10px !important;
        color: rgba(241, 134, 23, 0.85) !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div.stButton > button:hover {
        color: #FFFFFF !important;
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
