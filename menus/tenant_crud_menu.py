import streamlit as st
import time
from menus.base_menu import BaseMenu
from services.db_client import get_supabase_admin, get_supabase_client

class TenantCrudMenu(BaseMenu):
    def render(self):
        # Proteção adicional de segurança
        if st.session_state.get("user_rights") != "admin master":
            st.error("Acesso restrito ao administrador master (adminkan).")
            st.stop()

        st.markdown("<h2 style='text-align: left; margin-bottom: 5px;'>🔮 Painel de Gestão Multi-Tenant</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.1em; color: var(--text-soft); margin-bottom: 20px;'>Gerenciamento de organizações (tenants), limites de assinatura e credenciais de usuários principais.</p>", unsafe_allow_html=True)

        admin_client = get_supabase_admin()

        # Abas do Painel
        tab_list, tab_create, tab_users = st.tabs([
            "📂 Listar Clientes (Tenants)", 
            "➕ Adicionar Novo Cliente", 
            "👤 Listar Usuários"
        ])

        # ABA 1: LISTAR TENANTS
        with tab_list:
            st.subheader("Clientes cadastrados no KAN")
            try:
                # Carrega os tenants
                tenants_resp = admin_client.table("tenants").select("*").order("created_at", desc=True).execute()
                tenants = tenants_resp.data if tenants_resp.data else []

                # Carrega todos os usuários para associar e exibir nos boxes
                users_resp = admin_client.table("usuarios").select("id, usuario, email, tenant_id").execute()
                users_by_tenant = {}
                for u in (users_resp.data or []):
                    t_id = u.get("tenant_id")
                    if t_id:
                        if t_id not in users_by_tenant:
                            users_by_tenant[t_id] = []
                        users_by_tenant[t_id].append(u)

                if not tenants:
                    st.info("Nenhum cliente cadastrado ainda.")
                else:
                    for t in tenants:
                        # Ignora o tenant padrão na contagem de edição simples, ou exibe-o de forma distinta
                        is_default = t["id"] == "00000000-0000-0000-0000-000000000000"
                        badge_color = "#22C55E" if t["tier"] == "premium" else "#6B7280"
                        
                        with st.container(border=True):
                            col_t1, col_t2 = st.columns([3.8, 1.4])
                            with col_t1:
                                st.markdown(f"#### {t['name']}")
                                st.markdown(f"**Slug:** `{t['slug']}` | **ID:** `{t['id']}`")
                                st.caption(f"Criado em: {t['created_at']}")
                                
                                # Mostra usuários deste tenant
                                tenant_users = users_by_tenant.get(t["id"], [])
                                if tenant_users:
                                    st.write("")
                                    st.markdown("**Usuários criados:**")
                                    for u in tenant_users:
                                        # Exibe informações do usuário e formulário de reset de senha
                                        col_u_info, col_u_action = st.columns([2.5, 1.5])
                                        with col_u_info:
                                            st.markdown(f"👤 **{u['usuario']}** (`{u['email']}`)")
                                        with col_u_action:
                                            with st.popover("🔑 Alterar Senha", use_container_width=True):
                                                new_pwd = st.text_input("Nova Senha", type="password", key=f"pwd_{u['id']}", placeholder="Mínimo 6 caracteres")
                                                if st.button("Confirmar", key=f"btn_pwd_{u['id']}", use_container_width=True, type="primary"):
                                                    if len(new_pwd.strip()) < 6:
                                                        st.error("A senha deve ter no mínimo 6 caracteres.")
                                                    else:
                                                        try:
                                                            admin_client.auth.admin.update_user_by_id(u["id"], {"password": new_pwd.strip()})
                                                            st.success("Senha alterada!")
                                                            time.sleep(1)
                                                            st.rerun()
                                                        except Exception as ex:
                                                            st.error(f"Erro: {ex}")
                                else:
                                    st.caption("Nenhum usuário cadastrado neste cliente.")
                                    
                            with col_t2:
                                st.markdown(f"<span style='background-color: {badge_color}; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.85em; font-weight: bold;'>Plano {t['tier'].upper()}</span>", unsafe_allow_html=True)
                                st.write("")
                                # Permite alterar o plano do tenant
                                if not is_default:
                                    new_tier = "basic" if t["tier"] == "premium" else "premium"
                                    btn_label = "Mudar para Básico" if t["tier"] == "premium" else "Mudar para Premium"
                                    if st.button(btn_label, key=f"btn_tier_{t['id']}", use_container_width=True):
                                        admin_client.table("tenants").update({"tier": new_tier}).eq("id", t["id"]).execute()
                                        st.toast(f"Plano alterado com sucesso para {new_tier.upper()}!", icon="✅")
                                        time.sleep(0.5)
                                        st.rerun()
            except Exception as e:
                st.error(f"Erro ao carregar clientes: {e}")

        # ABA 2: CRIAR NOVO CLIENTE E USUÁRIO PRINCIPAL
        with tab_create:
            st.subheader("Registrar nova organização e conta administradora")
            st.write("Isso criará uma organização (tenant) e o respectivo usuário principal com a senha inicial fornecida.")
            
            with st.form("create_tenant_form", border=False):
                col_c1, col_c2 = st.columns([1, 1])
                with col_c1:
                    st.markdown("##### Dados do Cliente (Organização)")
                    tenant_name = st.text_input("Nome da Empresa*", placeholder="Ex: Acme Corporation")
                    tenant_tier = st.selectbox("Plano de Assinatura*", ["basic", "premium"], format_func=lambda x: "Básico (Sem Equipes/Harmonia)" if x == "basic" else "Premium (Acesso Total)")
                
                with col_c2:
                    st.markdown("##### Usuário Administrador Principal")
                    user_name = st.text_input("Nome do Usuário*", placeholder="Ex: joaosilva")
                    user_email = st.text_input("E-mail do Usuário*", placeholder="Ex: joao@acme.com")
                    user_pwd = st.text_input("Senha Inicial*", type="password", placeholder="Mínimo de 6 caracteres")

                st.markdown("<br>", unsafe_allow_html=True)
                submit_create = st.form_submit_button("Criar Cliente e Usuário", type="primary", use_container_width=True)

                if submit_create:
                    if not tenant_name.strip() or not user_name.strip() or not user_email.strip() or not user_pwd.strip():
                        st.error("Por favor, preencha todos os campos obrigatórios (*).")
                    elif len(user_pwd) < 6:
                        st.error("A senha deve conter pelo menos 6 caracteres.")
                    elif "@" not in user_email:
                        st.error("Digite um e-mail válido.")
                    else:
                        with st.spinner("Registrando conta no Supabase Auth e criando workspace..."):
                            try:
                                # 1. Cria o usuário no Supabase Auth
                                new_user = admin_client.auth.admin.create_user({
                                    "email": user_email.strip(),
                                    "password": user_pwd.strip(),
                                    "email_confirm": True,
                                    "user_metadata": {
                                        "full_name": user_name.strip().capitalize()
                                    }
                                })
                                
                                if new_user and new_user.user:
                                    # O trigger handle_new_user já foi executado no banco, criando o tenant básico
                                    # 2. Localiza o tenant_id criado automaticamente
                                    time.sleep(1) # Aguarda propagação
                                    u_res = admin_client.table("usuarios").select("tenant_id").eq("id", new_user.user.id).execute()
                                    
                                    if u_res.data:
                                        t_id = u_res.data[0]["tenant_id"]
                                        # 3. Atualiza o tenant com o nome real e plano/tier desejados
                                        slug_val = tenant_name.lower().replace(" ", "-").replace("/", "") + f"-{int(time.time()) % 1000}"
                                        admin_client.table("tenants").update({
                                            "name": tenant_name.strip(),
                                            "slug": slug_val,
                                            "tier": tenant_tier
                                        }).eq("id", t_id).execute()
                                        
                                        # 4. Atualiza o nome_completo e usuário na tabela public.usuarios
                                        admin_client.table("usuarios").update({
                                            "nome_completo": tenant_name.strip() + " Admin",
                                            "usuario": user_name.strip(),
                                            "is_main_user": True,
                                            "direitos": "Editor" # Define como Editor (Gestor)
                                        }).eq("id", new_user.user.id).execute()

                                        st.success(f"✅ Cliente '{tenant_name}' e usuário principal '{user_name}' criados com sucesso!")
                                        time.sleep(1.5)
                                        st.rerun()
                                    else:
                                        st.error("O usuário foi criado, mas houve um problema ao associar o Workspace. Verifique as triggers de banco.")
                            except Exception as e:
                                st.error(f"Erro ao criar cliente: {e}")

        # ABA 3: LISTAR USUÁRIOS
        with tab_users:
            st.subheader("Usuários do sistema")
            try:
                # Busca todos os usuários associados a seus tenants
                users_resp = admin_client.table("usuarios").select("*").order("usuario").execute()
                users = users_resp.data if users_resp.data else []
                
                # Para mostrar o nome da empresa, buscamos os tenants e fazemos o mapeamento
                tenants_resp = admin_client.table("tenants").select("id, name").execute()
                tenant_map = {t["id"]: t["name"] for t in tenants_resp.data} if tenants_resp.data else {}

                if not users:
                    st.info("Nenhum usuário cadastrado.")
                else:
                    for u in users:
                        t_name = tenant_map.get(u.get("tenant_id"), "Desconhecido")
                        badge_color = "#3B82F6" if u["direitos"] == "admin master" else "#10B981" if u["direitos"] == "Editor" else "#F59E0B" if u["direitos"] == "Analista" else "#6B7280"
                        
                        with st.container(border=True):
                            col_u1, col_u2 = st.columns([4, 1.2])
                            with col_u1:
                                st.markdown(f"#### {u['usuario']}")
                                st.markdown(f"**E-mail:** `{u['email']}` | **Empresa (Tenant):** `{t_name}`")
                                st.caption(f"Status: {u['status']} | Criado em: {u['created_at']}")
                            with col_u2:
                                st.markdown(f"<span style='background-color: {badge_color}; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.85em; font-weight: bold;'>{u['direitos'].upper()}</span>", unsafe_allow_html=True)
                                if u["is_main_user"]:
                                    st.markdown("<p style='font-size:0.8em; color:#10B981; margin: 4px 0 0 0;'>🔑 Usuário Principal</p>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erro ao carregar usuários: {e}")
