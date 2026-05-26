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
<link rel="stylesheet" href="https://unpkg.com/lucide-static@latest/font/lucide.css">
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
        color: rgba(255, 255, 255, 0.6) !important; /* Branco translúcido em estado neutro */
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
        background: rgba(255, 255, 255, 0.05) !important; /* Realce leve no hover */
        color: #FFFFFF !important; /* Branco pleno */
        transform: translateX(4px) !important;
    }

    /* Configuração base para os ícones outlined Lucide */
    .stApp section[data-testid="stSidebar"] div.stButton > button::before {
        font-family: "lucide" !important;
        display: inline-block;
        margin-right: 12px;
        font-size: 24px !important; /* Tamanho 24px para navegação/sidebar */
        font-style: normal !important;
        font-weight: normal !important;
        color: rgba(255, 255, 255, 0.6) !important; /* Branco translúcido em estado neutro */
        transition: transform 0.2s ease, color 0.2s ease;
        line-height: 1 !important;
    }

    .stApp section[data-testid="stSidebar"] div.stButton > button:hover::before {
        transform: scale(1.08) !important;
        color: #FFFFFF !important; /* Branco pleno no hover */
    }

    /* Accordion Chevrons (::after) */
    .stApp section[data-testid="stSidebar"] div.stButton > button[class*="st-key-grp"]::after {
        font-family: "lucide" !important;
        margin-left: auto;
        font-size: 20px !important;
        color: rgba(255, 255, 255, 0.5) !important;
        font-style: normal !important;
        transition: color 0.2s ease;
    }
    .stApp section[data-testid="stSidebar"] div.stButton > button[class*="st-key-grp"]:hover::after {
        color: #FFFFFF !important;
    }

    /* MAPEAMENTO DOS ÍCONES OUTLINED VIA CLASS-KEY */
    
    /* Home */
    .st-key-sidehome button::before { content: "\e0f5" !important; } /* home */

    /* Grupos de Acordeão */
    .st-key-grpcadastros button::before { content: "\e0d7" !important; } /* folder */
    .st-key-grpanalises button::before { content: "\e038" !important; } /* activity */
    .st-key-grpconfiguracoes button::before { content: "\e154" !important; } /* settings */
    .st-key-grpadmin button::before { content: "\e10b" !important; } /* lock */

    /* Accordion Chevrons dinâmicos */
    div[class*="st-key-grp"][class*="_open"] button::after { content: "\e070" !important; } /* chevron-up */
    div[class*="st-key-grp"][class*="_closed"] button::after { content: "\e06d" !important; } /* chevron-down */

    /* Chevrons dinâmicos gerais no Main */
    div[class*="_open_"] button::after {
        font-family: "lucide" !important;
        content: "\e070" !important; /* chevron-up */
        margin-left: 8px;
        font-size: 16px !important;
    }
    div[class*="_closed_"] button::after {
        font-family: "lucide" !important;
        content: "\e06d" !important; /* chevron-down */
        margin-left: 8px;
        font-size: 16px !important;
    }

    /* Cadastros */
    .st-key-menutalentos button::before { content: "\e1a4" !important; } /* users */
    .st-key-menuvagas button::before { content: "\e062" !important; } /* briefcase */
    .st-key-menuhierarquiadeptos button::before { content: "\e125" !important; } /* network */
    .st-key-menuequipes button::before { content: "\e342" !important; } /* user-cog */
    .st-key-menuempresas button::before { content: "\e1cc" !important; } /* building */
    .st-key-menusaas button::before { content: "\e0e8" !important; } /* globe */

    /* Análises */
    .st-key-menudiagnosticos button::before { content: "\e0cc" !important; } /* file-text */
    .st-key-menumapas button::before { content: "\e09b" !important; } /* compass */
    .st-key-menuanalytics button::before { content: "\e06b" !important; } /* pie-chart */
    .st-key-menuprocessoseletivo button::before { content: "\e1a0" !important; } /* user-check */

    /* Configurações */
    .st-key-menuempresa button::before { content: "\e162" !important; } /* sliders */
    .st-key-menuusuarios button::before { content: "\e1ff" !important; } /* shield-check */

    /* Admin */
    .st-key-menupaineldecontrole button::before { content: "\e1ff" !important; } /* shield-check */

    /* Botão Ativo Selecionado */
    .stApp section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-primary"] {
        background-color: rgba(139, 92, 246, 0.16) !important; /* Lilás translúcido */
        color: #FFFFFF !important; /* Branco pleno */
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-left: 4px solid rgba(139, 92, 246, 0.8) !important;
        border-radius: 0 8px 8px 0 !important;
        font-weight: 700 !important;
        box-shadow: none !important;
    }

    .stApp section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-primary"]::before {
        color: #FFFFFF !important; /* Branco pleno no estado ativo */
    }

    /* Submenus Aninhados (Compactação Visual) */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button {
        border-left: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 0 !important;
        padding: 6px 10px 6px 20px !important;
        margin-left: 14px !important;
        font-size: 0.85em !important;
        color: rgba(255,255,255,0.55) !important;
        width: calc(100% - 14px) !important;
    }
    
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button::before {
        font-size: 20px !important; /* Submenu com 20px para hierarquia visual */
        margin-right: 10px;
    }
    
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        border-left: 1px solid rgba(139, 92, 246, 0.6) !important;
        background: rgba(255, 255, 255, 0.02) !important;
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div.stButton > button[data-testid="baseButton-primary"] {
        border: none !important;
        border-left: 2px solid rgba(139, 92, 246, 0.8) !important;
        background: transparent !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 0 !important;
    }

    /* Ações Rápidas no Rodapé (Sair / Reset) */
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div.stButton > button {
        font-size: 0.8em !important;
        padding: 6px 8px !important;
        border-radius: 8px !important;
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        color: rgba(255, 255, 255, 0.7) !important;
        justify-content: center !important;
    }
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div.stButton > button::before {
        font-size: 20px !important; /* 20px para ações secundárias do rodapé */
        color: rgba(255, 255, 255, 0.7) !important;
        margin-right: 8px !important;
    }
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: #FFFFFF !important;
        transform: translateY(-1px) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] div.stButton > button:hover::before {
        color: #FFFFFF !important;
    }
    
    /* Ações Rápidas ícones */
    .st-key-btn_logout_side button::before { content: "\e10e" !important; } /* log-out */
    .st-key-btn_reset_side button::before { content: "\e145" !important; } /* refresh-cw */


    /* --- ESTILO E MAPEAMENTO DOS BOTÕES DO CONTEÚDO PRINCIPAL (LUCIDE ICONS) --- */

    .stApp [data-testid="stMain"] div.stButton > button::before {
        font-family: "lucide" !important;
        display: inline-block;
        margin-right: 8px;
        font-size: 20px !important; /* Padrão de 20px para ações e campos principais */
        font-style: normal !important;
        font-weight: normal !important;
        color: inherit;
        transition: transform 0.2s ease;
        line-height: 1 !important;
    }

    .stApp [data-testid="stMain"] div.stButton > button:hover::before {
        transform: scale(1.08) !important;
    }

    /* Mapeamento de chaves (keys) de botões no Main */
    
    /* Busca e Filtro */
    div[class*="st-key-btn_busca_aud"] button::before { content: "\e151" !important; } /* search */
    div[class*="st-key-btn_eq_add_filter_all"] button::before { content: "\e0dc" !important; } /* filter */

    /* IA sparkles */
    div[class*="st-key-btn_ia_"] button::before { content: "\e412" !important; } /* sparkles */

    /* Downloads */
    div[class*="st-key-dl_p_csv_"] button::before,
    div[class*="st-key-dl_mapa_csv_"] button::before { content: "\e326" !important; } /* file-spreadsheet */
    
    div[class*="st-key-dl_p_pdf_"] button::before,
    div[class*="st-key-dl_mapa_pdf_"] button::before { content: "\e0cc" !important; } /* file-text */

    /* Salvar */
    div[class*="st-key-save_bottom_"] button::before,
    div[class*="st-key-btn_save_"] button::before { content: "\e14d" !important; } /* save */

    /* Adicionar */
    div[class*="st-key-btn_add_"] button::before,
    div[class*="st-key-btn_start_add"] button::before { content: "\e13d" !important; } /* plus */

    /* Cancelar / Limpar */
    div[class*="st-key-btn_eq_clear_temp"] button::before,
    div[class*="st-key-btn_canc_"] button::before { content: "\e1b2" !important; } /* x */

    /* Excluir / Remover */
    div[class*="st-key-btn_d_eq_"] button::before,
    div[class*="st-key-btn_rem_"] button::before,
    div[class*="st-key-btn_delete_"] button::before { content: "\e18e" !important; } /* trash-2 */

    div[class*="st-key-btn_excluir_ed_"] button::before,
    div[class*="st-key-btn_excluir_"] button::before { content: "\e1a3" !important; } /* user-x */

    /* Editar */
    div[class*="st-key-btn_edit_"] button::before { content: "\e172" !important; } /* edit / square-pen */

    /* Quick Access (Home) */
    div[class*="st-key-btn_qa_diag"] button::before { content: "\e09b" !important; } /* compass */
    div[class*="st-key-btn_qa_tal"] button::before { content: "\e1a4" !important; } /* users */

    /* Chevron Home (16px microações) */
    div[class*="st-key-prev_home"] button::before { content: "\e06e" !important; font-size: 16px !important; margin-right: 0 !important; } /* chevron-left */
    div[class*="st-key-next_home"] button::before { content: "\e06f" !important; font-size: 16px !important; margin-right: 0 !important; } /* chevron-right */

    /* SaaS Logout */
    div[class*="st-key-btn_saas_logout"] button::before { content: "\e10e" !important; } /* log-out */

    /* Voltar / Back */
    div[class*="st-key-btn_back_"] button::before { content: "\e011" !important; } /* arrow-left */

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
