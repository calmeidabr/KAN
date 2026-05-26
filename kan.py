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

# 2. Estilização CSS
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
<style>
    /* --- ESTILOS GLOBAIS & TIPOGRAFIA PREMIUM --- */
    .stApp {
        background-color: #401041 !important;
        color: #FFFFFF !important;
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6, [data-testid="stHeader"] {
        font-family: 'Outfit', sans-serif !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #F18617 0%, #D97706 100%);
        color: #1b0520 !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 12px rgba(241, 134, 23, 0.3) !important;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #ff9d33 0%, #f18617 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(241, 134, 23, 0.45) !important;
        color: #1b0520 !important;
    }
    
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
    
    /* --- DESIGN EXCLUSIVO DO SIDEBAR (GLASSMORPHISM LILÁS PREMIUM) --- */
    :root {
        --sidebar-bg: rgba(22, 6, 26, 0.72);
        --panel-bg: rgba(255, 255, 255, 0.02);
        --panel-border: rgba(139, 92, 246, 0.12);
        --text-main: #f8fafc;
        --text-soft: #94a3b8;
        --accent: #F18617;
        --radius: 16px;
    }

    [data-testid="stSidebar"] {
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background: var(--sidebar-bg) !important;
        backdrop-filter: blur(16px) saturate(140%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(140%) !important;
        border-right: 1px solid var(--panel-border) !important;
    }
    
    [data-testid="stMain"] {
        transition: padding-left 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* CONFIG DESKTOP */
    @media (min-width: 992px) {
        [data-testid="stSidebar"][data-collapsed="false"] {
            width: 320px !important;
            min-width: 320px !important;
            max-width: 320px !important;
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
            width: 320px !important;
        }

        .stApp:has([data-testid="stSidebar"][data-collapsed="false"]) [data-testid="stMain"] {
            padding-left: 320px !important;
        }
        .stApp:has([data-testid="stSidebar"][data-collapsed="true"]) [data-testid="stMain"] {
            padding-left: 0px !important;
        }
    }

    /* CONFIG MOBILE */
    @media (max-width: 991px) {
        [data-testid="stSidebar"][data-collapsed="false"] {
            width: 100vw !important;
            min-width: 100vw !important;
            max-width: 100vw !important;
            z-index: 999999 !important;
        }

        [data-testid="stSidebar"][data-collapsed="false"] > div:first-child {
            width: 100vw !important;
        }

        [data-testid="stMain"] {
            padding-left: 0px !important;
        }
        .stApp:has([data-testid="stSidebar"][data-collapsed="false"]) [data-testid="stMain"] {
            padding-left: 0px !important;
        }

        [data-testid="collapsedControl"] button, 
        [data-testid="stSidebarCollapseButton"] button {
            background-color: #F18617 !important;
            border-radius: 12px !important;
            width: 44px !important;
            height: 44px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 4px 12px rgba(241, 134, 23, 0.4) !important;
            border: none !important;
            position: fixed !important;
            top: 12px !important;
            left: 12px !important;
            z-index: 99999 !important;
        }

        [data-testid="collapsedControl"] button::before,
        [data-testid="stSidebarCollapseButton"] button::before {
            content: "" !important;
            display: block !important;
            width: 18px !important;
            height: 2px !important;
            background-color: #FFFFFF !important;
            box-shadow: 0 5px 0 #FFFFFF, 0 -5px 0 #FFFFFF !important;
        }

        [data-testid="collapsedControl"] button svg, 
        [data-testid="stSidebarCollapseButton"] button svg {
            display: none !important;
        }

        [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button {
            background-color: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 8px !important;
            width: 36px !important;
            height: 36px !important;
            position: absolute !important;
            top: 15px !important;
            right: 15px !important;
        }

        [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button::before {
            display: none !important;
        }

        [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button svg {
            display: block !important;
            fill: #FFFFFF !important;
        }

        [data-testid="stMain"] [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 16px !important;
        }
        [data-testid="stMain"] [data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
        }

        .main-hero {
            height: auto !important;
            padding: 20px !important;
            border-radius: var(--radius) !important;
            margin-bottom: 16px !important;
            background-image: linear-gradient(180deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.6) 100%) !important;
        }
    }

    [data-testid="stSidebarContent"], [data-testid="stSidebarHeader"] {
        background: transparent !important;
    }
    
    /* Scrollbar */
    [data-testid="stSidebarContent"]::-webkit-scrollbar {
        width: 4px;
    }
    [data-testid="stSidebarContent"]::-webkit-scrollbar-track {
        background: transparent;
    }
    [data-testid="stSidebarContent"]::-webkit-scrollbar-thumb {
        background-color: rgba(255, 255, 255, 0.08);
        border-radius: 4px;
    }

    /* Marca KAN (Header do Sidebar) */
    .sb-brand {
        padding: 1rem;
        margin-bottom: 1.2rem;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(255, 255, 255, 0.01));
        border: 1px solid rgba(255,255,255,0.04);
        text-align: left;
    }
    .sb-brand-title {
        color: var(--text-main);
        font-size: 1.3rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        font-family: 'Outfit', sans-serif;
    }
    .sb-brand-sub {
        color: var(--text-soft);
        font-size: 0.74rem;
        margin-top: 0.25rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-weight: 600;
        opacity: 0.7;
    }

    /* Containers de Navegação st.container(border=True) */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {
        margin-top: 0.6rem !important;
        margin-bottom: 0.6rem !important;
        padding: 0.6rem !important;
        border-radius: var(--radius) !important;
        background-color: var(--panel-bg) !important;
        border: 1px solid var(--panel-border) !important;
    }

    .sb-label {
        color: var(--text-soft);
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 700;
        margin-bottom: 0.5rem;
        padding-left: 4px;
    }

    /* Perfil do Usuário Logado */
    .user-profile-card {
        background: rgba(255, 255, 255, 0.02) !important;
        padding: 10px 12px !important;
        border-radius: 12px !important;
        margin-top: 10px !important;
        border: 1px solid var(--panel-border) !important;
        transition: all 0.2s ease !important;
    }
    .user-profile-card:hover {
        background: rgba(255, 255, 255, 0.04) !important;
        border-color: rgba(139, 92, 246, 0.2) !important;
    }

    /* --- ESTILO DOS BOTÕES DO SIDEBAR COM ÍCONES BRANCOS OUTLINED --- */
    
    .stApp section[data-testid="stSidebar"] div.stButton > button {
        border: none !important;
        background: transparent !important;
        background-color: transparent !important;
        color: var(--text-soft) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 9px 12px !important;
        border-radius: 8px !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        font-size: 0.9em !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
    }

    .stApp section[data-testid="stSidebar"] div.stButton > button:hover {
        background: rgba(255, 255, 255, 0.04) !important;
        color: #FFFFFF !important;
        transform: translateX(4px) !important;
    }

    /* Configuração base para os ícones outlined */
    .stApp section[data-testid="stSidebar"] div.stButton > button::before {
        font-family: "bootstrap-icons" !important;
        display: inline-block;
        margin-right: 12px;
        font-size: 1.1em;
        font-weight: normal !important;
        color: #e2e8f0 !important;
        transition: transform 0.2s ease, color 0.2s ease;
    }

    .stApp section[data-testid="stSidebar"] div.stButton > button:hover::before {
        transform: scale(1.1);
        color: var(--accent) !important;
    }

    /* MAPEAMENTO DOS ÍCONES OUTLINED VIA CLASS-KEY */
    
    /* Home */
    .st-key-sidehome button::before { content: "\f425" !important; } /* bi-house */

    /* Grupos de Acordeão */
    .st-key-grpcadastros button::before { content: "\f3c7" !important; } /* bi-folder */
    .st-key-grpanalises button::before { content: "\f6ce" !important; } /* bi-graph-up-arrow */
    .st-key-grpconfiguracoes button::before { content: "\f3e5" !important; } /* bi-gear */
    .st-key-grpadmin button::before { content: "\f483" !important; } /* bi-lock */

    /* Cadastros */
    .st-key-menutalentos button::before { content: "\f4c0" !important; } /* bi-people */
    .st-key-menuvagas button::before { content: "\f1c7" !important; } /* bi-briefcase */
    .st-key-menuhierarquiadeptos button::before { content: "\f30d" !important; } /* bi-diagram-3 */
    .st-key-menuequipes button::before { content: "\f4db" !important; } /* bi-person-badge */
    .st-key-menuempresas button::before { content: "\f1d1" !important; } /* bi-building */
    .st-key-menusaas button::before { content: "\f3e7" !important; } /* bi-globe */

    /* Análises */
    .st-key-menudiagnosticos button::before { content: "\f467" !important; } /* bi-journal-check */
    .st-key-menumapas button::before { content: "\f2ca" !important; } /* bi-compass */
    .st-key-menuanalytics button::before { content: "\f4ea" !important; } /* bi-pie-chart */
    .st-key-menuprocessoseletivo button::before { content: "\f4cf" !important; } /* bi-person-check */

    /* Configurações */
    .st-key-menuempresa button::before { content: "\f57e" !important; } /* bi-sliders */
    .st-key-menuusuarios button::before { content: "\f546" !important; } /* bi-shield-lock */

    /* Admin */
    .st-key-menupaineldecontrole button::before { content: "\f547" !important; } /* bi-shield-shaded */

    /* Ações Rápidas */
    .st-key-btn_logout_side button::before { content: "\f1a6" !important; } /* bi-box-arrow-right */
    .st-key-btn_reset_side button::before { content: "\f110" !important; } /* bi-arrow-clockwise */

    /* Botão Ativo Selecionado */
    .stApp section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-primary"] {
        background-color: rgba(139, 92, 246, 0.16) !important;
        color: var(--accent) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-left: 4px solid var(--accent) !important;
        border-radius: 0 8px 8px 0 !important;
        font-weight: 700 !important;
        box-shadow: none !important;
    }

    .stApp section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-primary"]::before {
        color: var(--accent) !important;
    }

    /* Submenus Aninhados (Compactação Visual) */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button {
        border-left: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 0 !important;
        padding: 6px 10px 6px 20px !important;
        margin-left: 14px !important;
        font-size: 0.85em !important;
        color: rgba(255,255,255,0.5) !important;
        width: calc(100% - 14px) !important;
    }
    
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        border-left: 1px solid rgba(139, 92, 246, 0.6) !important;
        background: rgba(255, 255, 255, 0.02) !important;
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button[data-testid="baseButton-primary"] {
        border: none !important;
        border-left: 2px solid var(--accent) !important;
        background: transparent !important;
        color: var(--accent) !important;
        font-weight: 700 !important;
        border-radius: 0 !important;
    }

    /* Ações Rápidas no Rodapé */
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div.stButton > button {
        font-size: 0.8em !important;
        padding: 6px 8px !important;
        border-radius: 8px !important;
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        color: var(--text-main) !important;
        justify-content: center !important;
    }
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        transform: translateY(-1px) !important;
    }

    [data-testid="stSidebarNav"] { display: none; }

    /* Estilização Geral de Seções Principais */
    div[data-testid="stContainer"] {
        background: rgba(255,255,255,0.02);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Inicialização e Execução do Roteador Central
from app import App

app = App()
app.run()
