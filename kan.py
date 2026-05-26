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

    /* --- ESTRUTURA E RESPONSIVIDADE GLOBAL (DESKTOP E MOBILE) --- */
    
    [data-testid="stSidebar"] {
        transition: all 0.2s ease-in-out !important;
    }
    
    [data-testid="stMain"] {
        transition: padding-left 0.2s ease-in-out !important;
    }

    /* CONFIG DESKTOP: Telas maiores ou iguais a 992px */
    @media (min-width: 992px) {
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
        .stApp:has([data-testid="stSidebar"][data-collapsed="false"]) [data-testid="stMain"] {
            padding-left: 340px !important;
        }
        .stApp:has([data-testid="stSidebar"][data-collapsed="true"]) [data-testid="stMain"] {
            padding-left: 0px !important;
        }
    }

    /* CONFIG MOBILE: Telas menores que 992px */
    @media (max-width: 991px) {
        /* Sidebar como overlay de tela cheia */
        [data-testid="stSidebar"][data-collapsed="false"] {
            width: 100vw !important;
            min-width: 100vw !important;
            max-width: 100vw !important;
            background: var(--sidebar-bg) !important;
            z-index: 999999 !important;
        }

        [data-testid="stSidebar"][data-collapsed="false"] > div:first-child {
            width: 100vw !important;
        }

        /* No mobile, o conteúdo principal não deve ter padding-left */
        [data-testid="stMain"] {
            padding-left: 0px !important;
        }
        .stApp:has([data-testid="stSidebar"][data-collapsed="false"]) [data-testid="stMain"] {
            padding-left: 0px !important;
        }
        .stApp:has([data-testid="stSidebar"][data-collapsed="true"]) [data-testid="stMain"] {
            padding-left: 0px !important;
        }

        /* Estilização do Botão Hambúrguer para Abrir o Menu */
        [data-testid="collapsedControl"] button, 
        [data-testid="stSidebarCollapseButton"] button {
            background-color: #F18617 !important;
            border-radius: 12px !important;
            width: 46px !important;
            height: 46px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 4px 15px rgba(241, 134, 23, 0.45) !important;
            border: none !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            position: fixed !important;
            top: 12px !important;
            left: 12px !important;
            z-index: 99999 !important;
        }

        [data-testid="collapsedControl"] button:hover, 
        [data-testid="stSidebarCollapseButton"] button:hover {
            background-color: #D97706 !important;
            transform: scale(1.05) !important;
        }

        /* Esconde o ícone SVG de chevron original no botão de abrir */
        [data-testid="collapsedControl"] button svg, 
        [data-testid="stSidebarCollapseButton"] button svg {
            display: none !important;
        }

        /* Cria as 3 linhas do menu hambúrguer */
        [data-testid="collapsedControl"] button::before,
        [data-testid="stSidebarCollapseButton"] button::before {
            content: "" !important;
            display: block !important;
            width: 20px !important;
            height: 2px !important;
            background-color: #FFFFFF !important;
            box-shadow: 0 6px 0 #FFFFFF, 0 -6px 0 #FFFFFF !important;
            transition: all 0.2s ease !important;
        }

        /* Estilo específico do botão de fechar quando o sidebar está expandido */
        [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button,
        [data-testid="stSidebar"] [data-testid="collapsedControl"] button {
            background-color: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 8px !important;
            width: 38px !important;
            height: 38px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: #FFFFFF !important;
            position: absolute !important;
            top: 15px !important;
            right: 15px !important;
            z-index: 9999999 !important;
        }

        /* Remove o hambúrguer no botão de fechar */
        [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button::before,
        [data-testid="stSidebar"] [data-testid="collapsedControl"] button::before {
            display: none !important;
        }

        /* Exibe o SVG original (seta de colapsar) no botão de fechar */
        [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button svg,
        [data-testid="stSidebar"] [data-testid="collapsedControl"] button svg {
            display: block !important;
            fill: #FFFFFF !important;
        }

        /* Força colunas na área principal a empilharem verticalmente no celular */
        [data-testid="stMain"] [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 16px !important;
        }
        [data-testid="stMain"] [data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
        }

        /* Adaptação Hero Banner do Home */
        .main-hero {
            height: 240px !important;
            padding: 24px !important;
            border-radius: 18px !important;
            margin-bottom: 18px !important;
            background-image: linear-gradient(180deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.6) 100%), url('data:image/png;base64,{img_b64}') !important;
            align-items: flex-end !important;
        }
        .hero-title {
            font-size: 2.0em !important;
            margin-bottom: 8px !important;
        }
        .hero-subtitle {
            font-size: 0.95em !important;
        }
        
        /* Ajuste do container em Mobile */
        div[data-testid="stContainer"] {
            padding: 14px !important;
            margin-bottom: 14px !important;
        }
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

    /* Highlight lilac translúcido para os botões dos menus principais */
    .st-key-sidehome button,
    .st-key-grpcadastros button,
    .st-key-grpanalises button,
    .st-key-grpconfiguracoes button,
    .st-key-grpadmin button,
    .st-key-menusaas button {
        background-color: rgba(139, 92, 246, 0.14) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.08) !important;
        font-weight: 700 !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-size: 0.9em !important;
    }

    .st-key-sidehome button:hover,
    .st-key-grpcadastros button:hover,
    .st-key-grpanalises button:hover,
    .st-key-grpconfiguracoes button:hover,
    .st-key-grpadmin button:hover,
    .st-key-menusaas button:hover {
        background-color: rgba(139, 92, 246, 0.22) !important;
        border-color: rgba(139, 92, 246, 0.5) !important;
        color: #FFFFFF !important;
        transform: translateX(3px) !important;
        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.15) !important;
    }

    /* Item ativo selecionado nos menus principais */
    .st-key-sidehome button[data-testid="baseButton-primary"],
    .st-key-grpcadastros button[data-testid="baseButton-primary"],
    .st-key-grpanalises button[data-testid="baseButton-primary"],
    .st-key-grpconfiguracoes button[data-testid="baseButton-primary"],
    .st-key-grpadmin button[data-testid="baseButton-primary"],
    .st-key-menusaas button[data-testid="baseButton-primary"] {
        background-color: rgba(139, 92, 246, 0.22) !important;
        color: var(--accent) !important;
        border: 1px solid var(--accent) !important;
        border-left: 4px solid var(--accent) !important;
        border-radius: 0 8px 8px 0 !important;
        font-weight: 700 !important;
        box-shadow: none !important;
    }

    /* Submenus Aninhados - Estilo Limpo e Compacto */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button {
        border: none !important;
        border-left: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 0 !important;
        padding: 8px 12px 8px 24px !important;
        margin-left: 20px !important;
        font-size: 0.86em !important;
        font-weight: 500 !important;
        color: rgba(255,255,255,0.6) !important;
        background: transparent !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }
    
    /* Hover nos Submenus */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        border: none !important;
        border-left: 1px solid rgba(139, 92, 246, 0.6) !important;
        background: rgba(255, 255, 255, 0.03) !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
        color: #FFFFFF !important;
        transform: translateX(2px) !important;
    }

    /* Submenu Ativo Aninhado */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button[data-testid="baseButton-primary"] {
        border: none !important;
        border-left: 2px solid var(--accent) !important;
        background: transparent !important;
        background-color: transparent !important;
        color: var(--accent) !important;
        font-weight: 700 !important;
        box-shadow: none !important;
    }

    /* Ajuste de layout específico do SaaS Multi-Tenant para alinhar com os menus principais */
    section[data-testid="stSidebar"] .st-key-menusaas button {
        margin-left: 0 !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        font-size: 0.9em !important;
        font-weight: 700 !important;
        background-color: rgba(139, 92, 246, 0.14) !important;
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] .st-key-menusaas button:hover {
        background-color: rgba(139, 92, 246, 0.22) !important;
        border-color: rgba(139, 92, 246, 0.5) !important;
        transform: translateX(3px) !important;
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] .st-key-menusaas button[data-testid="baseButton-primary"] {
        background-color: rgba(139, 92, 246, 0.22) !important;
        color: var(--accent) !important;
        border: 1px solid var(--accent) !important;
        border-left: 4px solid var(--accent) !important;
        border-radius: 0 8px 8px 0 !important;
        font-weight: 700 !important;
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
