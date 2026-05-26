import streamlit as st
import time
from menus.base_menu import BaseMenu
from services.tenant_service import (
    login_user, register_user, logout_user, get_current_user, get_current_tenant,
    list_records, create_record, update_record, delete_record
)

class TenantCrudMenu(BaseMenu):
    def render(self):
        st.title("Demonstração SaaS Multi-Tenant")
        st.info("Esta tela demonstra o isolamento real de dados por Row Level Security (RLS) no Supabase baseado no usuário ativo.")

        user = get_current_user()
        
        # 1. FLUXO DE LOGIN E ONBOARDING
        if not user:
            st.warning("Para testar o isolamento, você precisa se autenticar ou criar uma conta no Supabase Auth.")
            
            tab_login, tab_register = st.tabs(["Entrar", "Cadastrar Novo Usuário"])
            
            with tab_login:
                st.subheader("Acesse sua conta SaaS")
                email = st.text_input("E-mail", key="saas_login_email")
                password = st.text_input("Senha", type="password", key="saas_login_pwd")
                if st.button("Entrar no Workspace", type="primary", key="btn_saas_login"):
                    if not email or not password:
                        st.error("Preencha todos os campos.")
                    else:
                        success, message = login_user(email, password)
                        if success:
                            st.success(message)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Erro no login: {message}")
                            
            with tab_register:
                st.subheader("Crie sua conta (Onboarding Automático)")
                st.write("Ao se cadastrar, o banco de dados criará automaticamente um Tenant/Workspace exclusivo para você via Trigger.")
                new_name = st.text_input("Nome Completo", key="saas_reg_name")
                new_email = st.text_input("E-mail", key="saas_reg_email")
                new_password = st.text_input("Senha (min. 6 caracteres)", type="password", key="saas_reg_pwd")
                
                if st.button("Cadastrar e Iniciar", type="primary", key="btn_saas_register"):
                    if not new_name or not new_email or not new_password:
                        st.error("Preencha todos os campos.")
                    elif len(new_password) < 6:
                        st.error("A senha deve ter no mínimo 6 caracteres.")
                    else:
                        success, message = register_user(new_email, new_password, new_name)
                        if success:
                            st.success(message)
                            st.info("Protip: Vá na aba 'Entrar' para acessar seu workspace.")
                        else:
                            st.error(f"Erro no cadastro: {message}")
            return

        # 2. SEÇÃO DO USUÁRIO LOGADO E TENANT ATIVO
        tenant_id = get_current_tenant()
        
        with st.container(border=True):
            col_u1, col_u2 = st.columns([4, 1])
            with col_u1:
                st.markdown(f"**Logado como:** `{user.email}`")
                st.markdown(f"**Workspace Ativo (tenant_id):** `{tenant_id}`")
            with col_u2:
                if st.button("Sair do Workspace", use_container_width=True, key="btn_saas_logout"):
                    logout_user()

        # Inicia variáveis de controle do CRUD
        if "edit_id" not in st.session_state:
            st.session_state["edit_id"] = None
        if "add_mode" not in st.session_state:
            st.session_state["add_mode"] = False

        st.write("---")

        # 3. FLUXO DE INSERÇÃO E EDICAO DE REGISTRO
        if st.session_state["add_mode"]:
            st.subheader("Criar Novo Registro no Tenant")
            nome = st.text_input("Nome do Registro*", key="rec_name")
            desc = st.text_area("Descrição", key="rec_desc")
            
            col_b1, col_b2 = st.columns([1, 5])
            with col_b1:
                if st.button("Salvar", type="primary", key="btn_save_changes_rec"):
                    if not nome.strip():
                        st.error("O nome é obrigatório.")
                    else:
                        if create_record(nome.strip(), desc.strip()):
                            st.success("Registro adicionado com sucesso no seu tenant!")
                            st.session_state["add_mode"] = False
                            time.sleep(1)
                            st.rerun()
            with col_b2:
                if st.button("Cancelar", key="btn_canc_add"):
                    st.session_state["add_mode"] = False
                    st.rerun()

        elif st.session_state["edit_id"] is not None:
            rec_id = st.session_state["edit_id"]
            records = list_records()
            record_to_edit = next((r for r in records if r["id"] == rec_id), None)
            
            if not record_to_edit:
                st.error("Registro não encontrado ou você não tem acesso.")
                st.session_state["edit_id"] = None
                st.rerun()
                
            st.subheader(f"Editar Registro #{rec_id}")
            ed_nome = st.text_input("Nome do Registro*", value=record_to_edit["nome"], key="ed_rec_name")
            ed_desc = st.text_area("Descrição", value=record_to_edit["descricao"] or "", key="ed_rec_desc")
            
            col_eb1, col_eb2 = st.columns([1, 5])
            with col_eb1:
                if st.button("Salvar Alterações", type="primary", key="btn_save_changes_edit"):
                    if not ed_nome.strip():
                        st.error("O nome é obrigatório.")
                    else:
                        if update_record(rec_id, ed_nome.strip(), ed_desc.strip()):
                            st.success("Registro atualizado com sucesso!")
                            st.session_state["edit_id"] = None
                            time.sleep(1)
                            st.rerun()
            with col_eb2:
                if st.button("Cancelar", key="btn_canc_edit"):
                    st.session_state["edit_id"] = None
                    st.rerun()

        # 4. EXIBIÇÃO DA LISTAGEM DO TENANT
        else:
            col_h1, col_h2 = st.columns([4, 1])
            with col_h1:
                st.subheader("Registros cadastrados neste Workspace")
            with col_h2:
                if st.button("Adicionar Registro", use_container_width=True, type="primary", key="btn_start_add"):
                    st.session_state["add_mode"] = True
                    st.rerun()
            
            # Listagem de registros (filtrado nativamente pelas políticas de RLS)
            records = list_records()
            
            if not records:
                st.info("Não há nenhum registro cadastrado no seu workspace ainda. Crie um novo registro acima.")
            else:
                for rec in records:
                    with st.container(border=True):
                        col_r1, col_r2 = st.columns([4, 1])
                        with col_r1:
                            st.markdown(f"##### <i class='icon-folder' style='color:#F18617; font-size:18px; vertical-align:middle; margin-right:6px;'></i><span style='vertical-align:middle;'>{rec['nome']}</span>", unsafe_allow_html=True)
                            st.write(rec['descricao'] or "*Sem descrição*")
                            st.caption(f"ID do Registro: {rec['id']} | Criado em: {rec['created_at']}")
                        with col_r2:
                            # Botões de ação para Edição e Exclusão
                            if st.button("Editar", key=f"btn_edit_{rec['id']}", use_container_width=True):
                                st.session_state["edit_id"] = rec["id"]
                                st.rerun()
                            if st.button("Excluir", key=f"btn_delete_{rec['id']}", use_container_width=True):
                                if delete_record(rec["id"]):
                                    st.success("Registro excluído!")
                                    time.sleep(0.5)
                                    st.rerun()
