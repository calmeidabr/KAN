import streamlit as st
import os

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
    st.session_state["scroll_to_top"] = True

def toggle_exp_group(grupo):
    st.session_state[f"exp_{grupo}"] = not st.session_state.get(f"exp_{grupo}", False)

def handle_logout():
    st.session_state["password_correct"] = False
    if "logged_user" in st.session_state:
        del st.session_state["logged_user"]
    st.session_state["clear_auth_cookie"] = True

def toggle_theme():
    st.session_state["theme"] = "light" if st.session_state.get("theme", "dark") == "dark" else "dark"


class App:
    def __init__(self):
        self.routes = {
            "Home": lambda: HomeMenu(self).render(),
            "Talentos": lambda: TalentosMenu(self).render(),
            "Vagas": lambda: ProcessosMenu(self).render(),
            "Hierarquia / Deptos": lambda: HierarquiaMenu(self).render(),
            "Empresa e Organograma": lambda: HierarquiaMenu(self).render(),
            "Equipes": lambda: EquipesMenu(self).render(),
            "Empresas": lambda: EmpresasMenu(self).render(),
            "SaaS Multi-Tenant": lambda: TenantCrudMenu(self).render(),
            "Empresa": lambda: PlaceholderMenu(self).render(title="Configurações da Empresa", message="Módulo de configurações gerais da empresa em desenvolvimento."),
            "Usuários": lambda: PlaceholderMenu(self).render(title="Gestão de Usuários do Sistema", message="Módulo de gestão de permissões de usuários em desenvolvimento."),
            "Analytics": lambda: AnalyticsMenu(self).render(),
            "Processo seletivo": lambda: ProcessoSeletivoAnaliseMenu(self).render(),
            "Painel de Controle": lambda: AdminMenu(self).render(),
            "Diagnósticos": lambda: DiagnosticosMenu(self).render(mode="diagnostico")
        }

    def navigate(self, route):
        st.session_state["sidebar_menu"] = route
        st.session_state["scroll_to_top"] = True
        st.rerun()

    def render_sidebar(self):
        with st.sidebar:
            import os
            from utils.helpers import get_base64_logo
            logo_html = ""
            try:
                logo_path = os.path.join("images", "kan_logo_header.png")
                logo_b64 = get_base64_logo(logo_path)
                if logo_b64:
                    logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-height: 40px; width: auto; display: block; margin-bottom: 4px;">'
                else:
                    logo_html = '<span style="font-size: 1.15em; color: var(--text-main); margin-right: 8px; font-weight: 700;">◇ KAN</span>'
            except Exception:
                logo_html = '<span style="font-size: 1.15em; color: var(--text-main); margin-right: 8px; font-weight: 700;">◇ KAN</span>'

            st.markdown(f"""
            <div class="sb-brand">
                <div class="sb-brand-title">{logo_html}</div>
                <div class="sb-brand-sub">Análises de Soft Skills</div>
            </div>
            """, unsafe_allow_html=True)
            
            cadastros_itens = ["Talentos", "Vagas", "Empresa e Organograma"]
            tier = st.session_state.get("tenant_tier")
            from services.plan_limits import get_plan_by_id
            plan = get_plan_by_id(tier)
            if plan.get("max_equipes", 0) > 0 or st.session_state.get("user_rights") == "admin master":
                cadastros_itens.append("Equipes")
            if st.session_state.get("user_rights") == "admin master":
                cadastros_itens.append("SaaS Multi-Tenant")

            menu_groups = {
                "CADASTROS": cadastros_itens,
                "ANÁLISES": ["Diagnósticos", "Analytics", "Processo seletivo"],
                "CONFIGURAÇÕES": ["Empresa", "Usuários"]
            }
            if st.session_state.get("user_rights") == "admin master":
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
                    
                    grp_label = grupo
                    grupo_clean = grupo.lower().replace("á", "a").replace("ç", "c").replace("õ", "o")
                    key_grp = f"grp{grupo_clean}_open" if is_exp else f"grp{grupo_clean}_closed"
                    st.button(grp_label, key=key_grp, use_container_width=True, on_click=toggle_exp_group, args=(grupo,))
                        
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
                st.button("Sair", use_container_width=True, key="btn_logout_side", on_click=handle_logout)
                
                current_theme = st.session_state.get("theme", "dark")
                theme_btn_label = "Modo Claro" if current_theme == "dark" else "Modo Escuro"
                st.button(theme_btn_label, use_container_width=True, key="btn_theme_toggle", on_click=toggle_theme)

            user_logged = st.session_state.get("logged_user", "Usuário")
            rights = st.session_state.get("user_rights", "Comum")
            role_str = "Admin Master" if rights == "admin master" else "Gestor" if rights == "Editor" else "Analista" if rights == "Analista" else "Membro"
            st.markdown(f"""
            <div class='user-profile-card'>
                <div style='display: flex; align-items: center; justify-content: space-between;'>
                    <div style='display: flex; align-items: center;'>
                        <div class='user-profile-avatar'>
                            {user_logged[0].upper()}
                        </div>
                        <div style='overflow: hidden; text-align: left;'>
                            <p class='user-profile-name'>{user_logged}</p>
                            <p class='user-profile-role'>{role_str} • Online</p>
                        </div>
                    </div>
                    <div style='color: #22C55E; font-size: 0.8em;'>
                        ●
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    def ver_cadastro_talento(self, nome):
        from models.database import carregar_todos_clientes
        st.session_state["busca_talentos_input"] = nome
        clientes = carregar_todos_clientes()
        if nome in clientes:
            info = clientes[nome]
            st.session_state["cad_nome"] = nome
            st.session_state["cad_data"] = info.get("data_nascimento", "")
            st.session_state["cad_profissao"] = info.get("profissao") or info.get("cargo") or ""
            st.session_state["cad_grupo"] = info.get("grupo", "")
            st.session_state["cad_link"] = info.get("linkedin_url", "")
            st.session_state["cad_exp"] = info.get("experiencias", "")
            emp_nome = info.get("empresa", "Nenhuma / Não associada")
            st.session_state["cad_empresa_sel"] = emp_nome if emp_nome else "Nenhuma / Não associada"
            
            # Adicionar à lista de últimos consultados
            if "ultimos_consultados" not in st.session_state:
                st.session_state["ultimos_consultados"] = []
            if nome and nome.strip() not in st.session_state["ultimos_consultados"]:
                st.session_state["ultimos_consultados"].insert(0, nome.strip())
                st.session_state["ultimos_consultados"] = st.session_state["ultimos_consultados"][:6]
        st.session_state["sidebar_menu"] = "Talentos"
        st.session_state["scroll_to_top"] = True

    def ver_equipe(self, nome_equipe):
        from models.database import carregar_equipes
        equipes = carregar_equipes()
        for idx, eq in enumerate(equipes):
            if eq["nome"] == nome_equipe:
                st.session_state[f"eq_open_{idx}"] = True
                st.session_state["add_equipe_mode"] = False
            else:
                st.session_state[f"eq_open_{idx}"] = False
        st.session_state["sidebar_menu"] = "Equipes"
        st.session_state["scroll_to_top"] = True

    def run(self):
        if not check_password():
            return

        if "theme" not in st.session_state:
            st.session_state["theme"] = "dark"

        if "sidebar_menu" not in st.session_state:
            st.session_state["sidebar_menu"] = "Home"

        if "ver_talento" in st.query_params:
            nome_ver = st.query_params["ver_talento"]
            del st.query_params["ver_talento"]
            self.ver_cadastro_talento(nome_ver)

        if "nav" in st.query_params:
            nav_val = st.query_params.get("nav")
            if nav_val in self.routes:
                st.session_state["sidebar_menu"] = nav_val
            del st.query_params["nav"]

        # Se houver parâmetros de ação de processos seletivos, força a rota correspondente
        if any(x in st.query_params for x in ["assoc_cand", "deassoc_cand", "excluir_cand"]):
            st.session_state["sidebar_menu"] = "Processo seletivo"

        # Detect page changes to set scroll to top
        curr_page = st.session_state.get("sidebar_menu", "Home")
        prev_page = st.session_state.get("prev_sidebar_menu", None)
        if curr_page != prev_page:
            st.session_state["scroll_to_top"] = True
            st.session_state["prev_sidebar_menu"] = curr_page

        # Render scroll-to-top javascript if flagged
        if st.session_state.get("scroll_to_top"):
            st.markdown("""
            <div style="display:none;">
            <script>
                (function() {
                    function scrollToTop(win) {
                        try {
                            win.scrollTo(0, 0);
                        } catch(e) {}
                        try {
                            const doc = win.document;
                            const selectors = ['.main', '[data-testid="stAppViewContainer"]', '[data-testid="stMain"]', '.stApp'];
                            selectors.forEach(sel => {
                                try {
                                    const el = doc.querySelector(sel);
                                    if (el) {
                                        el.scrollTo(0, 0);
                                        el.scrollTop = 0;
                                    }
                                } catch(e) {}
                            });
                        } catch(e) {}
                    }
                    scrollToTop(window);
                    try {
                        if (window.parent && window.parent !== window) {
                            scrollToTop(window.parent);
                        }
                    } catch(e) {}
                })();
            </script>
            </div>
            """, unsafe_allow_html=True)
            st.session_state["scroll_to_top"] = False

        self.render_sidebar()

        escolha = st.session_state.get("sidebar_menu", "Home")
        header_img = get_header_image()

        if escolha != "Home":
            col_logo, col_empty = st.columns([1, 4])
            with col_logo:
                logo_header_path = os.path.join("images", "kan_logo_header.png")
                if os.path.exists(logo_header_path):
                    st.image(logo_header_path, width=140)
                elif header_img not in ["◇", "🔮"] and os.path.exists(header_img):
                    st.image(header_img, width=140)
                else:
                    st.markdown("<h3 style='margin:0; color: #F08A00;'><i class='icon-activity' style='font-size:24px; vertical-align:middle; margin-right:8px;'></i>KAN</h3>", unsafe_allow_html=True)

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
                st.markdown("<p style='color: var(--text-soft); font-size: 12px; margin: 0; padding-top: 15px;'>Todos os direitos reservados para mundokan. Metodologia exclusiva registrada.</p>", unsafe_allow_html=True)
