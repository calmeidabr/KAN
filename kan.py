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

# 2. Estilização CSS e Variáveis de Tema (Dark vs. Light)
current_theme = st.session_state.get("theme", "dark")

if current_theme == "light":
    theme_variables = """
    :root {
        --app-bg: #F5F6F8;
        --sidebar-bg: #FFFFFF;
        --panel-bg: #FFFFFF;
        --panel-border: rgba(19, 24, 35, 0.08);
        --divider: rgba(19, 24, 35, 0.06);
        --text-main: #161A22;
        --text-soft: #5F6776;
        --text-muted: #8A93A3;
        --text-disabled: #B0B7C3;
        --input-bg: #FFFFFF;
        --hover-bg: #F0F2F5;
        --accent: #F08A00;
        --accent-hover: #FF9D1F;
        --accent-active: #D97800;
        --sidebar-item-hover: #F0F2F5;
        --sidebar-item-active-bg: #FFF4E8;
        --sidebar-item-active-text: #161A22;
        --sidebar-container-bg: #FFFFFF;
        --sidebar-text: rgba(22, 26, 34, 0.7);
        --sidebar-text-hover: #161A22;
        --sidebar-icon-color: rgba(22, 26, 34, 0.6);
        --card-shadow: 0 2px 8px rgba(19, 24, 35, 0.04);
        --radius: 14px;
    }
    .st-key-btn_theme_toggle button::before { content: "\\e11e" !important; } /* moon icon */
    """
else:
    theme_variables = """
    :root {
        --app-bg: #15161A;
        --sidebar-bg: #121318;
        --panel-bg: #1B1D24;
        --panel-border: rgba(255, 255, 255, 0.08);
        --divider: rgba(255, 255, 255, 0.06);
        --text-main: #F5F7FA;
        --text-soft: #B5BBC8;
        --text-muted: #8C93A3;
        --text-disabled: #5F6776;
        --input-bg: #111318;
        --hover-bg: #232632;
        --accent: #F08A00;
        --accent-hover: #FF9D1F;
        --accent-active: #D97800;
        --sidebar-item-hover: rgba(255, 255, 255, 0.04);
        --sidebar-item-active-bg: rgba(240, 138, 0, 0.08);
        --sidebar-item-active-text: #FFFFFF;
        --sidebar-container-bg: rgba(255, 255, 255, 0.01);
        --sidebar-text: rgba(245, 247, 250, 0.6);
        --sidebar-text-hover: #FFFFFF;
        --sidebar-icon-color: rgba(245, 247, 250, 0.6);
        --card-shadow: none;
        --radius: 14px;
    }
    .st-key-btn_theme_toggle button::before { content: "\\e178" !important; } /* sun icon */
    """

st.markdown(f"<style>{theme_variables}</style>", unsafe_allow_html=True)

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/lucide-static@latest/font/lucide.css">
<style>
    /* Estilos Globais e Tipografia */
    .stApp {
        background-color: var(--app-bg) !important;
        color: var(--text-main) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6, [data-testid="stHeader"] {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-main) !important;
        font-weight: 700 !important;
    }
    
    p, span, label, li {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-soft) !important;
    }
    
    small {
        color: var(--text-muted) !important;
    }
    
    /* Botões Primários do Streamlit */
    .stButton > button[data-testid="baseButton-primary"] {
        background: var(--accent) !important;
        color: #121318 !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 12px rgba(240, 138, 0, 0.2) !important;
        transition: all 0.2s ease;
    }
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background: var(--accent-hover) !important;
        color: #121318 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(240, 138, 0, 0.3) !important;
    }
    .stButton > button[data-testid="baseButton-primary"]:active {
        background: var(--accent-active) !important;
    }
    
    /* Botões Secundários/Outros */
    .stButton > button[data-testid="baseButton-secondary"],
    .stButton > button:not([data-testid="baseButton-primary"]) {
        background: var(--panel-bg) !important;
        color: var(--text-main) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        border: 1px solid var(--panel-border) !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        transition: all 0.2s ease;
    }
    .stButton > button[data-testid="baseButton-secondary"]:hover,
    .stButton > button:not([data-testid="baseButton-primary"]):hover {
        background: var(--hover-bg) !important;
        border-color: var(--panel-border) !important;
        color: var(--text-main) !important;
    }
    
    /* Botão Destrutivo (Lixeira / Delete) */
    div[class*="st-key-btn_d_eq_"] button:hover,
    div[class*="st-key-btn_rem_"] button:hover,
    div[class*="st-key-btn_delete_"] button:hover,
    div[class*="st-key-btn_excluir_"] button:hover {
        background-color: rgba(239, 68, 68, 0.1) !important;
        border-color: rgba(239, 68, 68, 0.3) !important;
        color: #EF4444 !important;
    }
    
    /* --- SIDEBAR ENTERPRISE UI --- */
    [data-testid="stSidebar"] {
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--panel-border) !important;
    }
    
    [data-testid="stMain"] {
        transition: padding-left 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* CONFIG DESKTOP */
    @media (min-width: 992px) {
        [data-testid="stSidebar"][data-collapsed="false"] {
            width: 300px !important;
            min-width: 300px !important;
            max-width: 300px !important;
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
            width: 300px !important;
        }
        .stApp:has([data-testid="stSidebar"][data-collapsed="false"]) [data-testid="stMain"] {
            padding-left: 300px !important;
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
            background-color: var(--accent) !important;
            border-radius: 10px !important;
            width: 40px !important;
            height: 40px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 4px 12px rgba(240, 138, 0, 0.3) !important;
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
            width: 16px !important;
            height: 2px !important;
            background-color: var(--sidebar-bg) !important;
            box-shadow: 0 5px 0 var(--sidebar-bg), 0 -5px 0 var(--sidebar-bg) !important;
        }
        [data-testid="collapsedControl"] button svg, 
        [data-testid="stSidebarCollapseButton"] button svg {
            display: none !important;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button {
            background-color: var(--sidebar-item-hover) !important;
            border: 1px solid var(--panel-border) !important;
            border-radius: 8px !important;
            width: 32px !important;
            height: 32px !important;
            position: absolute !important;
            top: 15px !important;
            right: 15px !important;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button::before {
            display: none !important;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button svg {
            display: block !important;
            fill: var(--text-main) !important;
        }
        [data-testid="stMain"] [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 16px !important;
        }
        [data-testid="stMain"] [data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
        }
    }

    [data-testid="stSidebarContent"], [data-testid="stSidebarHeader"] {
        background: transparent !important;
    }
    
    [data-testid="stSidebarContent"]::-webkit-scrollbar {
        width: 4px;
    }
    [data-testid="stSidebarContent"]::-webkit-scrollbar-thumb {
        background-color: var(--panel-border);
        border-radius: 4px;
    }

    /* Marca KAN (Header do Sidebar) */
    .sb-brand {
        padding: 1rem;
        margin-bottom: 1.2rem;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(240, 138, 0, 0.08), rgba(255, 255, 255, 0.01));
        border: 1px solid var(--panel-border);
        text-align: left;
    }
    .sb-brand-title {
        color: var(--text-main);
        font-size: 1.25rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        font-family: 'Inter', sans-serif;
    }
    .sb-brand-sub {
        color: var(--text-soft);
        font-size: 0.72rem;
        margin-top: 0.25rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-weight: 600;
        opacity: 0.65;
    }

    /* Containers de Navegação st.container(border=True) */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {
        margin-top: 0.6rem !important;
        margin-bottom: 0.6rem !important;
        padding: 0.5rem !important;
        border-radius: 12px !important;
        background-color: var(--sidebar-container-bg) !important;
        border: 1px solid var(--panel-border) !important;
    }

    .sb-label {
        color: var(--text-muted);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 700;
        margin-bottom: 0.5rem;
        padding-left: 4px;
    }

    /* Perfil do Usuário Logado */
    .user-profile-card {
        background: var(--sidebar-container-bg) !important;
        padding: 10px 12px !important;
        border-radius: 12px !important;
        margin-top: 10px !important;
        border: 1px solid var(--panel-border) !important;
        transition: all 0.2s ease !important;
    }
    .user-profile-card:hover {
        background: var(--hover-bg) !important;
        border-color: var(--panel-border) !important;
    }
    .user-profile-avatar {
        background: var(--sidebar-item-hover) !important;
        width: 36px !important;
        height: 36px !important;
        border-radius: 10px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: bold !important;
        color: var(--text-main) !important;
        margin-right: 12px !important;
        font-size: 1.1em !important;
        border: 1px solid var(--panel-border) !important;
    }
    .user-profile-name {
        margin: 0 !important;
        font-size: 0.9em !important;
        font-weight: 700 !important;
        color: var(--text-main) !important;
        white-space: nowrap !important;
        text-overflow: ellipsis !important;
    }
    .user-profile-role {
        margin: 0 !important;
        font-size: 0.7em !important;
        color: var(--text-soft) !important;
    }

    /* Botões da Sidebar */
    .stApp section[data-testid="stSidebar"] div.stButton > button {
        border: 1px solid transparent !important;
        background: transparent !important;
        background-color: transparent !important;
        color: var(--sidebar-text) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 9px 12px !important;
        border-radius: 8px !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        font-size: 0.95em !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
    }
    .stApp section[data-testid="stSidebar"] div.stButton > button:hover {
        background: var(--sidebar-item-hover) !important;
        color: var(--sidebar-text-hover) !important;
        transform: translateX(4px) !important;
    }

    /* Ícones Lucide na Sidebar */
    .stApp section[data-testid="stSidebar"] div.stButton > button::before {
        font-family: "lucide" !important;
        display: inline-block;
        margin-right: 12px;
        font-size: 20px !important;
        font-style: normal !important;
        font-weight: normal !important;
        color: var(--sidebar-icon-color) !important;
        transition: transform 0.2s ease, color 0.2s ease;
        line-height: 1 !important;
    }
    .stApp section[data-testid="stSidebar"] div.stButton > button:hover::before {
        transform: scale(1.08) !important;
        color: var(--sidebar-text-hover) !important;
    }

    /* Accordion Chevrons (::after) */
    .stApp section[data-testid="stSidebar"] div.stButton > button[class*="st-key-grp"]::after {
        font-family: "lucide" !important;
        margin-left: auto;
        font-size: 18px !important;
        color: var(--sidebar-icon-color) !important;
        font-style: normal !important;
        transition: color 0.2s ease;
    }
    .stApp section[data-testid="stSidebar"] div.stButton > button[class*="st-key-grp"]:hover::after {
        color: var(--sidebar-text-hover) !important;
    }

    /* Mapeamento de Ícones */
    .st-key-sidehome button::before { content: "\\e0f5" !important; } /* home */
    .st-key-grpcadastros button::before { content: "\\e0d7" !important; } /* folder */
    .st-key-grpanalises button::before { content: "\\e038" !important; } /* activity */
    .st-key-grpconfiguracoes button::before { content: "\\e154" !important; } /* settings */
    .st-key-grpadmin button::before { content: "\\e10b" !important; } /* lock */
    div[class*="st-key-grp"][class*="_open"] button::after { content: "\\e070" !important; } /* chevron-up */
    div[class*="st-key-grp"][class*="_closed"] button::after { content: "\\e06d" !important; } /* chevron-down */

    /* Chevrons Gerais */
    div[class*="_open_"] button::after, div[class*="_closed_"] button::after {
        font-family: "lucide" !important;
        margin-left: 8px;
        font-size: 14px !important;
    }
    div[class*="_open_"] button::after { content: "\\e070" !important; }
    div[class*="_closed_"] button::after { content: "\\e06d" !important; }

    /* Itens de Cadastro */
    .st-key-menutalentos button::before { content: "\\e1a4" !important; } /* users */
    .st-key-menuvagas button::before { content: "\\e062" !important; } /* briefcase */
    .st-key-menuhierarquiadeptos button::before { content: "\\e125" !important; } /* network */
    .st-key-menuequipes button::before { content: "\\e342" !important; } /* user-cog */
    .st-key-menuempresas button::before { content: "\\e1cc" !important; } /* building */
    .st-key-menusaas button::before { content: "\\e0e8" !important; } /* globe */

    /* Itens de Análise */
    .st-key-menudiagnosticos button::before { content: "\\e0cc" !important; } /* file-text */
    .st-key-menumapas button::before { content: "\\e09b" !important; } /* compass */
    .st-key-menuanalytics button::before { content: "\\e06b" !important; } /* pie-chart */
    .st-key-menuprocessoseletivo button::before { content: "\\e1a0" !important; } /* user-check */

    /* Itens de Configuração */
    .st-key-menuempresa button::before { content: "\\e162" !important; } /* sliders */
    .st-key-menuusuarios button::before { content: "\\e1ff" !important; } /* shield-check */
    .st-key-menupaineldecontrole button::before { content: "\\e1ff" !important; } /* shield-check */

    /* Menu Ativo Selecionado (Tema Enterprise Laranja) */
    .stApp section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-primary"] {
        background-color: var(--sidebar-item-active-bg) !important;
        color: var(--sidebar-item-active-text) !important;
        border: 1px solid rgba(240, 138, 0, 0.15) !important;
        border-left: 4px solid var(--accent) !important;
        border-radius: 0 8px 8px 0 !important;
        font-weight: 700 !important;
        box-shadow: none !important;
    }
    .stApp section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-primary"]::before {
        color: var(--accent) !important;
    }

    /* Submenus Aninhados */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button {
        border-left: 1px solid var(--panel-border) !important;
        border-radius: 0 !important;
        padding: 6px 10px 6px 20px !important;
        margin-left: 14px !important;
        font-size: 0.85em !important;
        color: var(--text-soft) !important;
        width: calc(100% - 14px) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        border-left: 1px solid var(--accent) !important;
        background: var(--sidebar-item-hover) !important;
        color: var(--sidebar-text-hover) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button[data-testid="baseButton-primary"] {
        border: none !important;
        border-left: 2px solid var(--accent) !important;
        background: var(--sidebar-item-active-bg) !important;
        color: var(--sidebar-item-active-text) !important;
        font-weight: 700 !important;
        border-radius: 0 !important;
    }

    /* Rodapé da Sidebar */
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div.stButton > button {
        font-size: 0.8em !important;
        padding: 6px 8px !important;
        border-radius: 8px !important;
        background-color: var(--sidebar-container-bg) !important;
        border: 1px solid var(--panel-border) !important;
        color: var(--sidebar-text) !important;
        justify-content: center !important;
    }
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div.stButton > button::before {
        font-size: 16px !important;
        color: var(--sidebar-icon-color) !important;
        margin-right: 6px !important;
    }
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div.stButton > button:hover {
        background-color: var(--hover-bg) !important;
        border: 1px solid var(--panel-border) !important;
        color: var(--sidebar-text-hover) !important;
    }
    .st-key-btn_logout_side button::before { content: "\\e10e" !important; }
    .st-key-btn_reset_side button::before { content: "\\e145" !important; }

    /* Botão de Toggle de Tema */
    .st-key-btn_theme_toggle button {
        font-size: 0.8em !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        background-color: var(--sidebar-container-bg) !important;
        border: 1px solid var(--panel-border) !important;
        color: var(--sidebar-text) !important;
        justify-content: center !important;
        margin-top: 8px !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
    }
    .st-key-btn_theme_toggle button:hover {
        background-color: var(--hover-bg) !important;
        border-color: var(--accent) !important;
        color: var(--sidebar-text-hover) !important;
    }
    .st-key-btn_theme_toggle button::before {
        font-family: "lucide" !important;
        display: inline-block;
        margin-right: 8px;
        font-size: 16px !important;
        font-style: normal !important;
        font-weight: normal !important;
        color: var(--sidebar-icon-color) !important;
        line-height: 1 !important;
    }
    .st-key-btn_theme_toggle button:hover::before {
        color: var(--sidebar-text-hover) !important;
    }

    /* --- CONTEÚDO PRINCIPAL (BOTOES E ICONES) --- */
    .stApp [data-testid="stMain"] div.stButton > button::before {
        font-family: "lucide" !important;
        display: inline-block;
        margin-right: 8px;
        font-size: 18px !important;
        font-style: normal !important;
        font-weight: normal !important;
        color: inherit;
        line-height: 1 !important;
    }
    div[class*="st-key-btn_busca_aud"] button::before { content: "\\e151" !important; } /* search */
    div[class*="st-key-btn_eq_add_filter_all"] button::before { content: "\\e0dc" !important; } /* filter */
    div[class*="st-key-btn_ia_"] button::before { content: "\\e412" !important; } /* sparkles */
    div[class*="st-key-dl_p_csv_"] button::before, div[class*="st-key-dl_mapa_csv_"] button::before { content: "\\e326" !important; }
    div[class*="st-key-dl_p_pdf_"] button::before, div[class*="st-key-dl_mapa_pdf_"] button::before { content: "\\e0cc" !important; }
    div[class*="st-key-save_bottom_"] button::before, div[class*="st-key-btn_save_"] button::before { content: "\\e14d" !important; }
    div[class*="st-key-btn_add_"] button::before, div[class*="st-key-btn_start_add"] button::before { content: "\\e13d" !important; }
    div[class*="st-key-btn_eq_clear_temp"] button::before, div[class*="st-key-btn_canc_"] button::before { content: "\\e1b2" !important; }
    div[class*="st-key-btn_d_eq_"] button::before, div[class*="st-key-btn_rem_"] button::before, div[class*="st-key-btn_delete_"] button::before { content: "\\e18e" !important; }
    div[class*="st-key-btn_excluir_ed_"] button::before, div[class*="st-key-btn_excluir_"] button::before { content: "\\e1a3" !important; }
    div[class*="st-key-btn_edit_"] button::before { content: "\\e172" !important; }
    div[class*="st-key-btn_qa_diag"] button::before { content: "\\e09b" !important; }
    div[class*="st-key-btn_qa_tal"] button::before { content: "\\e1a4" !important; }
    div[class*="st-key-prev_home"] button::before { content: "\\e06e" !important; font-size: 14px !important; margin-right: 0 !important; }
    div[class*="st-key-next_home"] button::before { content: "\\e06f" !important; font-size: 14px !important; margin-right: 0 !important; }
    div[class*="st-key-btn_saas_logout"] button::before { content: "\\e10e" !important; }
    div[class*="st-key-btn_back_"] button::before { content: "\\e011" !important; }

    /* Ocultar navegação nativa do Streamlit */
    [data-testid="stSidebarNav"] { display: none; }

    /* --- FORMULÁRIOS & INPUTS --- */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stSelectbox"] select,
    div[data-testid="stSelectbox"] div[role="combobox"],
    div[data-testid="stMultiSelect"] div[role="combobox"] {
        background-color: var(--input-bg) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--panel-border) !important;
        border-radius: 10px !important;
    }
    div[data-testid="stTextInput"] input:focus, 
    div[data-testid="stTextArea"] textarea:focus,
    div[data-testid="stSelectbox"] div[role="combobox"]:focus-within {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
    }
    div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background-color: var(--hover-bg) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--panel-border) !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="popover"] div[data-baseweb="menu"],
    div[role="listbox"] {
        background-color: var(--panel-bg) !important;
        border: 1px solid var(--panel-border) !important;
    }
    div[role="option"] {
        color: var(--text-main) !important;
        background-color: var(--panel-bg) !important;
    }
    div[role="option"]:hover, div[role="option"][aria-selected="true"] {
        background-color: var(--hover-bg) !important;
        color: var(--text-main) !important;
    }

    /* --- CARDS & PAINÉIS (REAPROVEITÁVEIS) --- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--panel-bg) !important;
        border: 1px solid var(--panel-border) !important;
        border-radius: 14px !important;
        padding: 20px !important;
        box-shadow: var(--card-shadow) !important;
    }
    
    div[data-testid="stContainer"] {
        background: var(--panel-bg) !important;
        border-radius: 14px !important;
        border: 1px solid var(--panel-border) !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
        box-shadow: var(--card-shadow) !important;
    }

    /* --- DEFENSIVE STYLING PARA STREAMLIT NATIVO --- */
    div[data-testid="stNotification"] p, 
    div[data-testid="stNotification"] span,
    button[data-baseweb="tab"] p,
    button[data-baseweb="tab"] span {
        color: inherit !important;
    }
    button[data-baseweb="tab"] {
        color: var(--text-soft) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--accent) !important;
    }

    /* --- TABELAS E DIVISORES --- */
    table {
        width: 100% !important;
        border-collapse: collapse !important;
        margin: 10px 0 !important;
        color: var(--text-soft) !important;
    }
    th {
        background-color: var(--hover-bg) !important;
        color: var(--text-main) !important;
        font-weight: 600 !important;
        border-bottom: 2px solid var(--panel-border) !important;
        padding: 10px !important;
        text-align: left !important;
    }
    td {
        border-bottom: 1px solid var(--divider) !important;
        padding: 10px !important;
    }
    tr:hover {
        background-color: var(--hover-bg) !important;
    }
    hr {
        border-color: var(--divider) !important;
    }

    /* --- SOBREPOSIÇÃO DE ESTILOS INLINE LEGADOS --- */
    
    /* Substituição de Laranja anterior por Laranja Enterprise */
    [style*="color: #F18617"], [style*="color:#F18617"], 
    [style*="color: rgb(241, 134, 23)"], [style*="color:rgb(241,134,23)"] {
        color: var(--accent) !important;
    }
    
    /* Backgrounds com tons de roxo/laranja legado redirecionados */
    [style*="background: rgba(241,134,23"], [style*="background:rgba(241,134,23"],
    [style*="background-color: rgba(241,134,23"], [style*="background-color:rgba(241,134,23"],
    [style*="background:rgba(241, 134, 23"], [style*="background: rgba(241, 134, 23"],
    [style*="background: rgba(240, 138, 0"], [style*="background:rgba(240, 138, 0"] {
        background: var(--sidebar-item-active-bg) !important;
    }
    [style*="background-color: #1b0520"], [style*="background-color:#1b0520"] {
        background-color: var(--panel-bg) !important;
    }
    
    /* Bordas com laranja e azul legados redirecionadas */
    [style*="border: 2px solid #F18617"], [style*="border:2px solid #F18617"],
    [style*="border: 3px solid #F18617"], [style*="border:3px solid #F18617"],
    [style*="border:2px solid #004BFF"], [style*="border: 2px solid #004BFF"] {
        border-color: var(--accent) !important;
    }
    
    /* Avatar de Fallback das Equipes */
    [style*="background: rgba(0, 75, 255"] {
        background: var(--sidebar-item-active-bg) !important;
        color: var(--accent) !important;
    }

    /* Substituição global de cores textuais brancas inline nas páginas */
    [style*="color: rgba(255,255,255"], [style*="color:rgba(255,255,255"],
    [style*="color: rgba(255, 255, 255"], [style*="color:rgba(255, 255, 255"],
    [style*="color: rgba(245, 247, 250"], [style*="color:rgba(245, 247, 250"],
    [style*="color: #F5F7FA"], [style*="color:#F5F7FA"],
    [style*="color:white"], [style*="color: white"],
    [style*="color:#FFFFFF"], [style*="color: #FFFFFF"] {
        color: var(--text-main) !important;
    }
    [style*="background: rgba(255,255,255,0.04)"], [style*="background: rgba(255,255,255,0.07)"],
    [style*="background:rgba(255,255,255,0.04)"], [style*="background:rgba(255,255,255,0.07)"],
    [style*="background: rgba(255, 255, 255, 0.04)"] {
        background: var(--hover-bg) !important;
    }

    /* Ajustes específicos de classes customizadas das páginas */
    .talent-member-card {
        background: var(--sidebar-item-active-bg) !important;
        border: 1px solid var(--panel-border) !important;
    }
    .talent-member-card img, .talent-member-avatar {
        border-color: var(--accent) !important;
    }
    .talent-member-avatar {
        background: var(--sidebar-item-active-bg) !important;
    }
    .hierarquia-card {
        background: var(--sidebar-item-active-bg) !important;
        border: 1px solid var(--panel-border) !important;
    }
    .hierarquia-card img, .hierarquia-card-avatar {
        border-color: var(--accent) !important;
    }
    .hierarquia-card-avatar {
        background: var(--sidebar-item-active-bg) !important;
    }
    .candidato-card {
        background-color: var(--panel-bg) !important;
        background: var(--panel-bg) !important;
        border: 1px solid var(--panel-border) !important;
        box-shadow: var(--card-shadow) !important;
    }
    .candidato-card strong, .candidato-card span, .candidato-card p, .candidato-card div {
        color: var(--text-main) !important;
    }
    .candidato-card small {
        color: var(--text-muted) !important;
    }
    .kpi-card {
        background: var(--panel-bg) !important;
        border-left: 4px solid var(--accent) !important;
        border-top: 1px solid var(--panel-border) !important;
        border-right: 1px solid var(--panel-border) !important;
        border-bottom: 1px solid var(--panel-border) !important;
        box-shadow: var(--card-shadow) !important;
    }
    .kpi-card:hover {
        background: var(--hover-bg) !important;
    }
    .kpi-title {
        color: var(--text-soft) !important;
    }
    .kpi-value {
        color: var(--text-main) !important;
    }
    .kpi-box {
        background: var(--panel-bg) !important;
        border: 1px solid var(--panel-border) !important;
        box-shadow: var(--card-shadow) !important;
    }
    .kpi-num {
        color: var(--accent) !important;
    }
    .kpi-lbl {
        color: var(--text-soft) !important;
    }
    .perfil-custom-table {
        background: var(--panel-bg) !important;
        border: 1px solid var(--panel-border) !important;
        box-shadow: var(--card-shadow) !important;
    }
    .perfil-custom-table td {
        border-bottom: 1px solid var(--divider) !important;
        color: var(--text-soft) !important;
    }
    .perfil-custom-table th {
        background-color: var(--accent) !important;
        color: #121318 !important;
    }
    .mapa-table {
        background: var(--panel-bg) !important;
        border: 1px solid var(--panel-border) !important;
        box-shadow: var(--card-shadow) !important;
    }
    .mapa-table td {
        border-bottom: 1px solid var(--divider) !important;
    }
    .mapa-table th {
        background-color: var(--accent) !important;
        color: #121318 !important;
    }
    .mapa-campo-titulo {
        color: var(--accent) !important;
    }
    .mapa-numero-destaque {
        color: #121318 !important;
        background: linear-gradient(135deg, var(--accent) 0%, #D97706 100%) !important;
    }
    .mapa-explicacao {
        color: var(--text-soft) !important;
        opacity: 0.8 !important;
    }
    .mapa-desc-cel {
        color: var(--text-main) !important;
    }
    
    /* Estilo de link para botões de talentos para evitar reloads de página */
    div.talent-link-container div.row-widget.stButton > button {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
        color: var(--text-main) !important;
        text-decoration: none !important;
        border-bottom: 1px dashed var(--accent) !important;
        text-align: left !important;
        font-weight: bold !important;
        box-shadow: none !important;
        display: inline !important;
        margin: 0 !important;
        font-size: inherit !important;
        border-radius: 0 !important;
        height: auto !important;
        min-height: 0 !important;
        line-height: inherit !important;
    }
    div.talent-link-container div.row-widget.stButton > button:hover {
        color: var(--accent) !important;
        background: transparent !important;
        border-bottom: 1px solid var(--accent) !important;
    }
</style>
<script>
    // Força o idioma da página como português para evitar o prompt de tradução automática do navegador
    document.documentElement.lang = 'pt';
    document.documentElement.setAttribute('lang', 'pt');

    // Aplica a classe 'notranslate' nos file uploaders para evitar corrupção de texto (ex: "uploadpload") caso a tradução esteja ativa
    function aplicarNoTranslate() {
        document.querySelectorAll('[data-testid="stFileUploader"], [data-testid="stFileUploader"] button').forEach(function(el) {
            if (!el.classList.contains('notranslate')) {
                el.classList.add('notranslate');
                el.setAttribute('translate', 'no');
            }
        });
    }

    aplicarNoTranslate();
    setInterval(aplicarNoTranslate, 1000);
</script>
""", unsafe_allow_html=True)


# 3. Inicialização e Execução do Roteador Central
from app import App

app = App()
app.run()
