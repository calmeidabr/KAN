# --- PATCH PARA COMPATIBILIDADE COM PYTHON 3.14-DEV E CHAVES SUPABASE NÃO-JWT ---
import builtins
import typing
import re

original_setattr = builtins.setattr
def safe_setattr(obj, name, value):
    try:
        original_setattr(obj, name, value)
    except AttributeError as e:
        if name == "__module__":
            pass
        else:
            raise e
builtins.setattr = safe_setattr

original_eval_type = getattr(typing, "_eval_type", None)
if original_eval_type:
    import inspect
    try:
        sig = inspect.signature(original_eval_type)
        if 'prefer_fwd_module' not in sig.parameters:
            def patched_eval_type(t, globalns, localns, *args, **kwargs):
                kwargs.pop('prefer_fwd_module', None)
                return original_eval_type(t, globalns, localns, *args, **kwargs)
            typing._eval_type = patched_eval_type
    except Exception:
        pass

original_match = re.match
def patched_match(pattern, string, flags=0):
    if pattern == r"^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$":
        if string:
            class MockMatch:
                pass
            return MockMatch()
    return original_match(pattern, string, flags)
re.match = patched_match
# --------------------------------------------------------------------------------

import streamlit as st
from PIL import Image
import os

# 1. Configuração da Página
try:
    favicon_img = os.path.join("images", "ico_k_laranja.jpg")
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
        --app-bg: #EEF1F5;
        --content-bg: #F5F7FA;
        --sidebar-bg: #FCFCFD;
        --panel-bg: #FFFFFF;
        --panel-border: rgba(22, 26, 34, 0.10);
        --panel-border-medium: rgba(22, 26, 34, 0.14);
        --divider: rgba(22, 26, 34, 0.08);
        --text-main: #161A22;
        --text-soft: #5E6675;
        --text-muted: #8891A1;
        --text-disabled: #A7AFBD;
        --input-bg: #FAFBFC;
        --hover-bg: #ECEFF3;
        --accent: #F08A00;
        --accent-hover: #FF9D1F;
        --accent-active: #D97800;
        --sidebar-item-hover: #ECEFF3;
        --sidebar-item-active-bg: #FFF4E8;
        --sidebar-item-active-text: #161A22;
        --sidebar-container-bg: #FCFCFD;
        --sidebar-text: rgba(22, 26, 34, 0.7);
        --sidebar-text-hover: #161A22;
        --sidebar-icon-color: rgba(22, 26, 34, 0.6);
        --card-shadow: 0 4px 12px rgba(22, 26, 34, 0.05);
        --radius: 14px;
        /* Novas superfícies específicas do redesenho Light Mode */
        --card-secondary: #F7F4EF;
        --panel-neutral: #F2F4F7;
        --selected-subtle: #FFF4E8;
        --header-bg: #F7F8FB;
        --header-border: rgba(22, 26, 34, 0.08);
        --button-primary-text: #1A1A1A;
        --button-secondary-bg: #F7F4EF;
        --button-secondary-text: #2A3140;
        --button-secondary-border: rgba(22, 26, 34, 0.10);
        --button-secondary-hover: #EFE9E1;

        /* Card design tokens (Light Mode overrides) */
        --card-border-top-color: #9B30B3;
        --card-bg: linear-gradient(180deg, #FFFFFF 0%, #F5F7FA 100%);
        --card-border-color: rgba(22, 26, 34, 0.08);
        --card-glow: radial-gradient(circle at 96% -26%, rgba(155, 48, 179, 0.04) 0%, rgba(155, 48, 179, 0) 35%);
        --card-shadow: 0 12px 30px rgba(22, 26, 34, 0.06);
        
        --card-hover-bg: linear-gradient(180deg, #F9FBFC 0%, #EEF1F5 100%);
        --card-hover-border-color: rgba(22, 26, 34, 0.15);
        --card-hover-glow: radial-gradient(circle at 96% -26%, rgba(155, 48, 179, 0.06) 0%, rgba(155, 48, 179, 0) 40%);
        --card-hover-shadow: 0 16px 35px rgba(22, 26, 34, 0.10);
        
        --card-selected-border-color: rgba(155, 48, 179, 0.6);
        --card-selected-shadow: 0 12px 35px rgba(155, 48, 179, 0.15);
        
        --card-text-main: #161A22;
        --card-text-soft: #5E6675;
        --card-divider-color: rgba(22, 26, 34, 0.08);
    }
    .st-key-btn_theme_toggle button::before { content: "\\e11e" !important; } /* moon icon */
    """
else:
    theme_variables = """
    :root {
        --app-bg: #15161A;
        --content-bg: #15161A;
        --sidebar-bg: #121318;
        --panel-bg: #1B1D24;
        --panel-border: rgba(255, 255, 255, 0.08);
        --panel-border-medium: rgba(255, 255, 255, 0.15);
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
        /* Equivalentes para Dark Mode */
        --card-secondary: #23252E;
        --panel-neutral: #1E2028;
        --selected-subtle: rgba(240, 138, 0, 0.08);
        --header-bg: transparent;
        --header-border: transparent;
        --button-primary-text: #121318;
        --button-secondary-bg: #1B1D24;
        --button-secondary-text: #F5F7FA;
        --button-secondary-border: rgba(255, 255, 255, 0.08);
        --button-secondary-hover: #232632;

        /* Card design tokens (Dark Mode overrides) */
        --card-border-top-color: #5B1463;
        --card-bg: linear-gradient(180deg, #141824 0%, #0D1016 100%);
        --card-border-color: rgba(255, 255, 255, 0.05);
        --card-glow: radial-gradient(circle at 96% -26%, rgba(122, 43, 138, 0.06) 0%, rgba(122, 43, 138, 0) 35%);
        --card-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
        
        --card-hover-bg: linear-gradient(180deg, #171B2A 0%, #0E121C 100%);
        --card-hover-border-color: rgba(255, 255, 255, 0.1);
        --card-hover-glow: radial-gradient(circle at 96% -26%, rgba(122, 43, 138, 0.09) 0%, rgba(122, 43, 138, 0) 40%);
        --card-hover-shadow: 0 16px 35px rgba(0, 0, 0, 0.5);
        
        --card-selected-border-color: rgba(122, 43, 138, 0.6);
        --card-selected-shadow: 0 12px 35px rgba(122, 43, 138, 0.25);
        
        --card-text-main: #F4F7FB;
        --card-text-soft: #AAB3C5;
        --card-divider-color: rgba(255, 255, 255, 0.06);
    }
    .st-key-btn_theme_toggle button::before { content: "\\e178" !important; } /* sun icon */
    """

st.markdown(f"<style>{theme_variables}</style>", unsafe_allow_html=True)

# Injetar CSS de Cards do Design System
from utils.helpers import load_text_file
card_css_path = os.path.join("frontend", "card.css")
card_css = load_text_file(card_css_path)
if card_css:
    st.markdown(f"<style>{card_css}</style>", unsafe_allow_html=True)

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
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-main) !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stHeader"] {
        background-color: var(--header-bg) !important;
        border-bottom: 1px solid var(--header-border) !important;
        transition: all 0.25s ease !important;
    }
    
    [data-testid="stHeader"] button,
    [data-testid="stHeader"] a,
    [data-testid="stHeader"] svg {
        color: var(--text-main) !important;
        fill: var(--text-main) !important;
    }
    
    p, span, label, li {
        font-family: 'Inter', sans-serif;
        color: var(--text-soft) !important;
    }
    
    small {
        color: var(--text-muted) !important;
    }
    
    /* Botões Primários do Streamlit */
    .stButton > button[data-testid="baseButton-primary"] {
        background: var(--accent) !important;
        color: var(--button-primary-text) !important;
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
        color: var(--button-primary-text) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(240, 138, 0, 0.3) !important;
    }
    .stButton > button[data-testid="baseButton-primary"]:active {
        background: var(--accent-active) !important;
    }
    
    /* Botões Secundários/Outros */
    .stButton > button[data-testid="baseButton-secondary"],
    .stButton > button:not([data-testid="baseButton-primary"]):not([class*="st-key-btn_d_eq_"]):not([class*="st-key-btn_rem_"]):not([class*="st-key-btn_delete_"]):not([class*="st-key-btn_excluir_"]) {
        background: var(--button-secondary-bg) !important;
        color: var(--button-secondary-text) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        border: 1px solid var(--button-secondary-border) !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        transition: all 0.2s ease;
    }
    .stButton > button[data-testid="baseButton-secondary"]:hover,
    .stButton > button:not([data-testid="baseButton-primary"]):not([class*="st-key-btn_d_eq_"]):not([class*="st-key-btn_rem_"]):not([class*="st-key-btn_delete_"]):not([class*="st-key-btn_excluir_"]):hover {
        background: var(--button-secondary-hover) !important;
        border-color: var(--button-secondary-border) !important;
        color: var(--button-secondary-text) !important;
    }
    
    /* Botão Destrutivo (Lixeira / Delete) */
    div[class*="st-key-btn_d_eq_"] button,
    div[class*="st-key-btn_rem_"] button,
    div[class*="st-key-btn_delete_"] button,
    div[class*="st-key-btn_excluir_"] button {
        background: #FFF1F1 !important;
        background-color: #FFF1F1 !important;
        border: 1px solid rgba(220, 38, 38, 0.12) !important;
        color: #B42318 !important;
        transition: all 0.2s ease !important;
    }
    div[class*="st-key-btn_d_eq_"] button:hover,
    div[class*="st-key-btn_rem_"] button:hover,
    div[class*="st-key-btn_delete_"] button:hover,
    div[class*="st-key-btn_excluir_"] button:hover {
        background: #FEE4E2 !important;
        background-color: #FEE4E2 !important;
        border-color: rgba(220, 38, 38, 0.24) !important;
        color: #B42318 !important;
    }
    
    /* --- SIDEBAR ENTERPRISE UI --- */
    [data-testid="stSidebar"] {
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--panel-border) !important;
    }
    
    [data-testid="stMain"] {
        transition: padding-left 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background-color: var(--content-bg) !important;
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
        font-family: system-ui, -apple-system, sans-serif !important;
        margin-left: auto;
        font-size: 11px !important;
        color: var(--sidebar-icon-color) !important;
        font-style: normal !important;
        transition: color 0.2s ease;
        line-height: 1 !important;
    }
    .stApp section[data-testid="stSidebar"] div.stButton > button[class*="st-key-grp"]:hover::after {
        color: var(--sidebar-text-hover) !important;
    }

    /* Mapeamento de Ícones */
    .st-key-sidehome button::before { content: "\\e0f5" !important; } /* home */
    .st-key-grpcadastros button::before { content: "\\e172" !important; } /* square-pen */
    .st-key-grpanalises button::before { content: "\\e038" !important; } /* activity */
    .st-key-grpconfiguracoes button::before { content: "\\e154" !important; } /* settings */
    .st-key-grpadmin button::before { content: "\\e687" !important; } /* user-star */
    div[class*="st-key-grp"][class*="_open"] button::after { content: "▲" !important; } /* chevron-up */
    div[class*="st-key-grp"][class*="_closed"] button::after { content: "▼" !important; } /* chevron-down */

    /* Chevrons Gerais */
    div[class*="_open_"] button::after, div[class*="_closed_"] button::after {
        font-family: system-ui, -apple-system, sans-serif !important;
        margin-left: 8px;
        font-size: 11px !important;
        line-height: 1 !important;
    }
    div[class*="_open_"] button::after { content: "▲" !important; }
    div[class*="_closed_"] button::after { content: "▼" !important; }

    /* Itens de Cadastro */
    .st-key-menutalentos button::before { content: "\\e46c" !important; } /* user-round-plus */
    .st-key-menuvagas button::before { content: "\\e062" !important; } /* briefcase */
    .st-key-menuhierarquiadeptos button::before { content: "\\e125" !important; } /* network */
    .st-key-menuempresaeorganograma button::before { content: "\\e125" !important; } /* network */
    .st-key-menuequipes button::before { content: "\\e342" !important; } /* user-cog */
    .st-key-menuempresas button::before { content: "\\e290" !important; } /* building-2 */
    .st-key-menusaas button::before { content: "\\e0e8" !important; } /* globe */

    /* Itens de Análise */
    .st-key-menudiagnosticos button::before { content: "\\e09b" !important; } /* compass */
    .st-key-menumapas button::before { content: "\\e09b" !important; } /* compass */
    .st-key-menuanalytics button::before { content: "\\e06b" !important; } /* pie-chart */
    .st-key-menuprocessoseletivo button::before { content: "\\e1a0" !important; } /* user-check */

    /* Itens de Configuração */
    .st-key-menuempresa button::before { content: "\\e154" !important; } /* settings */
    .st-key-menuusuarios button::before { content: "\\e1a4" !important; } /* users */
    .st-key-menupaineldecontrole button::before { content: "\\e687" !important; } /* user-star */

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

    /* Rodapé da Sidebar - Ações Rápidas */
    .st-key-btn_logout_side button,
    .st-key-btn_theme_toggle button {
        font-size: 0.8em !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        background-color: var(--sidebar-container-bg) !important;
        border: 1px solid var(--panel-border) !important;
        color: var(--sidebar-text) !important;
        justify-content: center !important;
        margin-top: 6px !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
    }
    .st-key-btn_logout_side button:hover,
    .st-key-btn_theme_toggle button:hover {
        background-color: var(--hover-bg) !important;
        border-color: var(--accent) !important;
        color: var(--sidebar-text-hover) !important;
    }
    .st-key-btn_logout_side button::before,
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
    .st-key-btn_logout_side button:hover::before,
    .st-key-btn_theme_toggle button:hover::before {
        color: var(--sidebar-text-hover) !important;
    }
    .st-key-btn_logout_side button::before { content: "\\e10e" !important; }

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
    div[class*="st-key-btn_d_eq_"] button::before, div[class*="st-key-btn_rem_"] button::before, div[class*="st-key-btn_delete_"] button::before { content: "\\e18d" !important; }
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
    div[data-testid="stTextInput"] div[data-baseweb="input"], 
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stSelectbox"] select,
    div[data-testid="stSelectbox"] div[role="combobox"],
    div[data-testid="stMultiSelect"] div[role="combobox"] {
        background-color: var(--input-bg) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--panel-border) !important;
        border-radius: 12px !important;
    }
    /* Resetar borda e sombra no elemento input interno para evitar duplo contorno */
    div[data-testid="stTextInput"] input {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    div[data-testid="stTextInput"] input::placeholder, 
    div[data-testid="stTextArea"] textarea::placeholder {
        color: var(--text-muted) !important;
        opacity: 0.8 !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within, 
    div[data-testid="stTextArea"] textarea:focus,
    div[data-testid="stSelectbox"] div[role="combobox"]:focus-within {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(240, 138, 0, 0.15) !important;
        outline: none !important;
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
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stContainer"] {
        background: var(--card-bg) !important;
        border: var(--card-border-width) solid var(--card-border-color) !important;
        border-top: var(--card-border-top-width) solid var(--card-border-top-color) !important;
        border-radius: var(--card-radius) !important;
        padding: 20px !important;
        box-shadow: var(--card-shadow) !important;
        position: relative !important;
        overflow: hidden !important;
        transition: var(--card-transition) !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]::before,
    div[data-testid="stContainer"]::before {
        content: "" !important;
        position: absolute !important;
        top: 0 !important;
        right: 0 !important;
        width: 100% !important;
        height: 100% !important;
        background: var(--card-glow) !important;
        pointer-events: none !important;
        z-index: 1 !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"] > div,
    div[data-testid="stContainer"] > div {
        position: relative !important;
        z-index: 2 !important;
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
        background: var(--card-secondary) !important;
        border: 1px solid var(--panel-border) !important;
        border-radius: 12px !important;
        box-shadow: var(--card-shadow) !important;
        transition: all 0.2s ease !important;
    }
    .talent-member-card img, .talent-member-avatar {
        border-color: var(--accent) !important;
    }
    .talent-member-avatar {
        background: var(--hover-bg) !important;
    }
    .hierarquia-card {
        background: var(--card-secondary) !important;
        border: 1px solid var(--panel-border) !important;
        border-radius: 12px !important;
        box-shadow: var(--card-shadow) !important;
        transition: all 0.2s ease !important;
    }
    .hierarquia-card img, .hierarquia-card-avatar {
        border-color: var(--accent) !important;
    }
    .hierarquia-card-avatar {
        background: var(--hover-bg) !important;
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
    
    /* File Uploader Custom Styling */
    [data-testid="stFileUploader"] section {
        background-color: var(--panel-neutral) !important;
        border: 1px dashed var(--panel-border-medium) !important;
        border-radius: 12px !important;
        padding: 20px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stFileUploader"] section:hover {
        background-color: var(--hover-bg) !important;
        border-color: var(--accent) !important;
    }
    [data-testid="stFileUploader"] section * {
        color: var(--text-soft) !important;
    }
    [data-testid="stFileUploader"] section strong {
        color: var(--text-main) !important;
    }
    [data-testid="stFileUploader"] section button {
        background-color: var(--panel-bg) !important;
        color: transparent !important; /* Esconde o texto original */
        font-size: 0 !important; /* Reseta tamanho para evitar sobreposição física */
        line-height: 0 !important; /* Evita quebra de layout */
        border: 1px solid var(--panel-border) !important;
        border-radius: 8px !important;
        padding: 6px 14px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        position: relative !important;
        width: 140px !important;
        height: 38px !important;
        overflow: hidden !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    /* Forçar todos os filhos do botão a ficarem transparentes e invisíveis (evita wildcard overrides) */
    [data-testid="stFileUploader"] section button * {
        color: transparent !important;
        font-size: 0 !important;
        line-height: 0 !important;
        display: none !important; /* Oculta qualquer tag interna como span, div, p */
    }
    [data-testid="stFileUploader"] section button::before {
        content: "Fazer Upload" !important;
        color: var(--text-main) !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 0.85rem !important;
        font-family: inherit !important;
        font-weight: 500 !important;
        pointer-events: none !important;
    }
    [data-testid="stFileUploader"] section button:hover {
        background-color: var(--hover-bg) !important;
        border-color: var(--panel-border-medium) !important;
    }
    [data-testid="stFileUploader"] section button:hover::before {
        color: var(--accent) !important;
    }
    
    /* Custom Alert/Notification Backgrounds (Light Mode specific) */
    div[data-testid="stNotification"] {
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(22, 26, 34, 0.02) !important;
        border: 1px solid var(--panel-border) !important;
        background-color: var(--panel-neutral) !important;
    }
    
    /* Info Box */
    div[data-testid="stNotification"]:has(path[d*="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"]),
    div[data-testid="stNotification"]:has(svg) {
        background-color: var(--header-bg) !important;
        border: 1px solid var(--panel-border-medium) !important;
    }
    
    /* Success Box */
    div[data-testid="stNotification"]:has(path[d*="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"]) {
        background-color: #ECFDF3 !important;
        border: 1px solid rgba(22, 163, 74, 0.16) !important;
    }
    
    /* Warning Box */
    div[data-testid="stNotification"]:has(path[d*="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"]) {
        background-color: #FFF7E6 !important;
        border: 1px solid rgba(217, 119, 6, 0.16) !important;
    }
    
    /* Error Box */
    div[data-testid="stNotification"]:has(path[d*="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"]) {
        background-color: #FEF3F2 !important;
        border: 1px solid rgba(220, 38, 38, 0.16) !important;
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

    /* Correção do bug visual dos ícones do st.expander que vazam/sobrepõem como texto bruto */
    [data-testid="stExpander"] details summary {
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        cursor: pointer !important;
    }

    [data-testid="stExpander"] details summary [data-testid="stIconMaterial"] {
        font-size: 0px !important; /* Esconde o texto da ligature (ex: _arrow_right) */
        color: transparent !important;
        text-shadow: none !important;
        width: 20px !important;
        height: 20px !important;
        min-width: 20px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative !important;
        overflow: hidden !important;
    }

    /* Insere um chevron desenhado pelo Lucide (que está em cache/carregado localmente) */
    [data-testid="stExpander"] details summary [data-testid="stIconMaterial"]::before {
        font-family: "lucide" !important;
        font-size: 18px !important;
        color: var(--text-soft) !important;
        display: inline-block !important;
        line-height: 1 !important;
        font-style: normal !important;
        font-weight: normal !important;
        position: absolute !important;
        left: 50% !important;
        top: 50% !important;
        transform: translate(-50%, -50%) !important;
        transition: color 0.2s ease, transform 0.2s ease !important;
    }

    /* Define chevron para a direita no expander fechado */
    [data-testid="stExpander"] details:not([open]) summary [data-testid="stIconMaterial"]::before {
        content: "\\e06f" !important; /* chevron-right */
    }

    /* Define chevron para baixo no expander aberto */
    [data-testid="stExpander"] details[open] summary [data-testid="stIconMaterial"]::before {
        content: "\\e06d" !important; /* chevron-down */
    }

    [data-testid="stExpander"] details summary:hover [data-testid="stIconMaterial"]::before {
        color: var(--accent) !important;
    }

    /* Prevenção de overlap do label e alinhamento vertical centralizado */
    [data-testid="stExpander"] details summary span,
    [data-testid="stExpander"] details summary p,
    [data-testid="stExpander"] details summary div {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.4 !important;
        display: inline-block !important;
        vertical-align: middle !important;
    }
</style>
<script>
    // Força o idioma da página como português para evitar o prompt de tradução automática do navegador
    document.documentElement.lang = 'pt';
    document.documentElement.setAttribute('lang', 'pt');

    // Aplica a classe 'notranslate' nos file uploaders, expanders e SVGs para evitar corrupção de texto/icones (ex: "_arrow_right", "uploadpload") caso a tradução esteja ativa
    function aplicarNoTranslate() {
        // File Uploaders
        document.querySelectorAll('[data-testid="stFileUploader"], [data-testid="stFileUploader"] button').forEach(function(el) {
            if (!el.classList.contains('notranslate')) {
                el.classList.add('notranslate');
                el.setAttribute('translate', 'no');
            }
        });

        // Expanders (Headers, Icons, Toggle Buttons e Ícones Material)
        document.querySelectorAll('[data-testid="stExpander"], [data-testid="stExpander"] button, [data-testid="stExpander"] summary, [data-testid="stIconMaterial"]').forEach(function(el) {
            if (!el.classList.contains('notranslate')) {
                el.classList.add('notranslate');
                el.setAttribute('translate', 'no');
            }
        });

        // Elementos SVG (ícones) para evitar injeção de texto traduzido
        document.querySelectorAll('svg').forEach(function(el) {
            if (!el.classList.contains('notranslate')) {
                el.classList.add('notranslate');
                el.setAttribute('translate', 'no');
            }
        });
    }

    aplicarNoTranslate();
    setInterval(aplicarNoTranslate, 500);

    // Usa MutationObserver para capturar novos elementos inseridos no DOM imediatamente e evitar delay de tradução
    const observer = new MutationObserver(function() {
        aplicarNoTranslate();
    });
    observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)


# 3. Inicialização e Execução do Roteador Central
from app import App

app = App()
app.run()
