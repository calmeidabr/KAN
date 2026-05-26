import streamlit as st
import os
from PIL import Image

from services.auth import check_password, get_header_image
from menus.home_menu import HomeMenu
from menus.talentos_menu import TalentosMenu
from menus.processos_menu import ProcessosMenu
from menus.hierarquia_menu import HierarquiaMenu
from menus.empresas_menu import EmpresasMenu
from menus.admin_menu import AdminMenu
from menus.equipes_menu import EquipesMenu
from menus.diagnosticos_menu import DiagnosticosMenu
from menus.analytics_menu import AnalyticsMenu
from menus.processo_seletivo_analise_menu import ProcessoSeletivoAnaliseMenu
from menus.placeholder_menu import PlaceholderMenu
from menus.tenant_crud_menu import TenantCrudMenu

def set_nav_route(route):
    st.session_state["sidebar_menu"] = route

def toggle_exp_group(grupo):
    st.session_state[f"exp_{grupo}"] = not st.session_state.get(f"exp_{grupo}", False)

def handle_logout():
    st.session_state["password_correct"] = False

def handle_reset():
    st.cache_data.clear()

class App:
    def __init__(self):
        self.routes = {
            "Home": lambda: HomeMenu(self).render(),
            "Talentos": lambda: TalentosMenu(self).render(),
            "Vagas": lambda: ProcessosMenu(self).render(),
            "Hierarquia / Deptos": lambda: HierarquiaMenu(self).render(),
            "Equipes": lambda: EquipesMenu(self).render(),
            "Empresas": lambda: EmpresasMenu(self).render(),
            "SaaS Multi-Tenant": lambda: TenantCrudMenu(self).render(),
            "Empresa": lambda: PlaceholderMenu(self).render(title="Configurações da Empresa", message="Módulo de configurações gerais da empresa em desenvolvimento."),
            "Usuários": lambda: PlaceholderMenu(self).render(title="Gestão de Usuários do Sistema", message="Módulo de gestão de permissões de usuários em desenvolvimento."),
            "Analytics": lambda: AnalyticsMenu(self).render(),
            "Processo seletivo": lambda: ProcessoSeletivoAnaliseMenu(self).render(),
            "Painel de Controle": lambda: AdminMenu(self).render(),
            "Diagnósticos": lambda: DiagnosticosMenu(self).render(mode="diagnostico"),
            "Mapas": lambda: DiagnosticosMenu(self).render(mode="mapa")
        }

    def navigate(self, route):
        st.session_state["sidebar_menu"] = route
        st.rerun()

    def render_sidebar(self):
        with st.sidebar:
            import base64
            import os
            logo_html = ""
            try:
                logo_path = os.path.join("images", "ico_k.png")
                if os.path.exists(logo_path):
                    with open(logo_path, "rb") as f:
                        logo_b64 = base64.b64encode(f.read()).decode()
                    logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;">'
                else:
                    logo_html = '<span style="font-size: 1.15em; color: #FFFFFF; margin-right: 8px; font-weight: 700;">◇</span>'
            except Exception:
                logo_html = '<span style="font-size: 1.15em; color: #FFFFFF; margin-right: 8px; font-weight: 700;">◇</span>'

            st.markdown(f"""
            <div class="sb-brand">
                <div class="sb-brand-title">{logo_html} KAN</div>
                <div class="sb-brand-sub">Análises de Soft Skills</div>
            </div>
            """, unsafe_allow_html=True)
            
            icones = {
                "Home": "◇",
                "Talentos": "●",
                "Vagas": "●",
                "Diagnósticos": "●",
                "Mapas": "●",
                "Analytics": "●",
                "Processo seletivo": "●",
                "Hierarquia / Deptos": "●",
                "Equipes": "●",
                "Empresas": "●",
                "SaaS Multi-Tenant": "❖",
                "Empresa": "●",
                "Usuários": "●",
                "Painel de Controle": "●"
            }

            group_icons = {
                "CADASTROS": "⊞",
                "ANÁLISES": "⎔",
                "CONFIGURAÇÕES": "⚙",
                "ADMIN": "⛭"
            }
            menu_groups = {
                "CADASTROS": ["Talentos", "Vagas", "Hierarquia / Deptos", "Equipes", "Empresas", "SaaS Multi-Tenant"],
                "ANÁLISES": ["Diagnósticos", "Mapas", "Analytics", "Processo seletivo"],
                "CONFIGURAÇÕES": ["Empresa", "Usuários"]
            }
            if st.session_state.get("logged_user") == "adminkan":
                menu_groups["ADMIN"] = ["Painel de Controle"]

            for grupo in menu_groups.keys():
                if f"exp_{grupo}" not in st.session_state:
                    st.session_state[f"exp_{grupo}"] = (grupo == "ANÁLISES")

            # Seção de Navegação
            with st.container(border=True):
                is_home = (st.session_state.get("sidebar_menu", "Home") == "Home")
                st.button("Home", key="sidehome", use_container_width=True, type="primary" if is_home else "secondary", on_click=set_nav_route, args=("Home",))

                for grupo, itens in menu_groups.items():
                    is_exp = st.session_state[f"exp_{grupo}"]
                    chevron = "▴" if is_exp else "▾"
                    
                    grp_label = f"{grupo} \u00A0 {chevron}"
                    grupo_clean = grupo.lower().replace("á", "a").replace("ç", "c").replace("õ", "o")
                    st.button(grp_label, key=f"grp{grupo_clean}", use_container_width=True, on_click=toggle_exp_group, args=(grupo,))
                        
                    if is_exp:
                        with st.container():
                            for opcao in itens:
                                is_sel = (st.session_state.get("sidebar_menu", "Home") == opcao)
                                sub_label = opcao
                                key_opcao = "menusaas" if opcao == "SaaS Multi-Tenant" else f"menu{opcao.lower().replace(' ', '').replace('/', '')}"
                                st.button(sub_label, key=key_opcao, use_container_width=True, type="primary" if is_sel else "secondary", on_click=set_nav_route, args=(opcao,))

            # Seção de Ações Rápidas
            with st.container(border=True):
                st.markdown('<div class="sb-label">Ações</div>', unsafe_allow_html=True)
                col_out1, col_out2 = st.columns(2)
                with col_out1:
                    st.button("Sair", use_container_width=True, key="btn_logout_side", on_click=handle_logout)
                with col_out2:
                    st.button("Reset", use_container_width=True, key="btn_reset_side", on_click=handle_reset)

            user_logged = st.session_state.get("logged_user", "Usuário")
            role_str = "Admin Master" if user_logged == "adminkan" else "Gestor" if user_logged in ["admin", "cristiano"] else "Membro"
            st.markdown(f"""
            <div class='user-profile-card'>
                <div style='display: flex; align-items: center; justify-content: space-between;'>
                    <div style='display: flex; align-items: center;'>
                        <div style='background: rgba(255, 255, 255, 0.08); width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #FFFFFF; margin-right: 12px; font-size: 1.1em; border: 1px solid rgba(255, 255, 255, 0.1);'>
                            {user_logged[0].upper()}
                        </div>
                        <div style='overflow: hidden; text-align: left;'>
                            <p style='margin: 0; font-size: 0.9em; font-weight: 700; color: white; white-space: nowrap; text-overflow: ellipsis;'>{user_logged}</p>
                            <p style='margin: 0; font-size: 0.7em; color: rgba(255,255,255,0.5);'>{role_str} • Online</p>
                        </div>
                    </div>
                    <div style='color: #39ff14; font-size: 0.8em; text-shadow: 0 0 8px #39ff14;'>
                        ●
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    def run(self):
        if not check_password():
            return

        if "sidebar_menu" not in st.session_state:
            st.session_state["sidebar_menu"] = "Home"

        if "nav" in st.query_params:
            nav_val = st.query_params.get("nav")
            if nav_val in self.routes:
                st.session_state["sidebar_menu"] = nav_val
            del st.query_params["nav"]

        self.render_sidebar()

        escolha = st.session_state.get("sidebar_menu", "Home")
        header_img = get_header_image()

        if escolha != "Home":
            col_logo, col_empty = st.columns([1, 4])
            with col_logo:
                if header_img != "🔮":
                    st.image(header_img, width=150)
                else:
                    st.markdown("<h3 style='margin:0; color: #F18617;'>🔮 KAN</h3>", unsafe_allow_html=True)

        handler = self.routes.get(escolha, self.routes["Home"])
        handler()

        if escolha != "Home":
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            st.markdown("---")
            col_footer1, col_footer2 = st.columns([1, 8])
            try:
                footer_img_path = os.path.join("images", "logo_mundo_kan_peq_neg2.png")
                if os.path.exists(footer_img_path):
                    with col_footer1:
                        st.image(footer_img_path)
            except Exception: pass
            with col_footer2:
                st.markdown("<p style='color: white; font-size: 12px; margin: 0; padding-top: 15px;'>Todos os direitos reservados para mundokan. Metodologia exclusiva registrada.</p>", unsafe_allow_html=True)
