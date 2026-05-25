import streamlit as st
import datetime
from supabase import create_client, Client

# Inicializa o cliente público básico
def get_public_client() -> Client:
    url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
    key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
    return create_client(url, key)

# Obtém o cliente autenticado do usuário para as consultas com RLS ativo
def get_supabase_user_client() -> Client:
    client = get_public_client()
    # Se o usuário estiver autenticado no Supabase, associa o access_token nas chamadas
    if "supabase_session" in st.session_state:
        session = st.session_state["supabase_session"]
        # Injeta o token de acesso (JWT) do usuário nas chamadas de banco de dados
        client.postgrest.auth(session.access_token)
    return client

# Realiza autenticação com e-mail e senha no Supabase Auth
def login_user(email, password):
    client = get_public_client()
    try:
        res = client.auth.sign_in_with_password({"email": email, "password": password})
        if res.session:
            st.session_state["supabase_session"] = res.session
            st.session_state["logged_user"] = email
            st.session_state["password_correct"] = True
            
            # Carrega o perfil do usuário para descobrir o tenant ativo padrão
            user_client = get_supabase_user_client()
            prof_res = user_client.table("profiles").select("default_tenant_id").eq("id", res.user.id).execute()
            if prof_res.data:
                st.session_state["tenant_id"] = prof_res.data[0]["default_tenant_id"]
            return True, "Login efetuado com sucesso."
    except Exception as e:
        return False, str(e)
    return False, "Falha na autenticação."

# Realiza o cadastro de um novo usuário
def register_user(email, password, full_name):
    client = get_public_client()
    try:
        # Cadastra o usuário no Supabase Auth
        res = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name
                }
            }
        })
        if res.user:
            return True, "Cadastro realizado com sucesso! Você já pode entrar com seu e-mail e senha."
    except Exception as e:
        return False, str(e)
    return False, "Erro inesperado ao realizar cadastro."

# Logout do usuário limpando estados da sessão
def logout_user():
    for key in ["supabase_session", "logged_user", "password_correct", "tenant_id"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Recupera o usuário logado
def get_current_user():
    if "supabase_session" in st.session_state:
        return st.session_state["supabase_session"].user
    return None

# Recupera o ID do tenant ativo do usuário logado
def get_current_tenant():
    return st.session_state.get("tenant_id")

# ==========================================
# OPERAÇÕES DE CRUD NA TABELA DE NEGÓCIO
-- (Baseadas no cliente autenticado RLS)
# ==========================================

# Listagem (filtrada automaticamente pelo RLS)
def list_records():
    client = get_supabase_user_client()
    try:
        res = client.table("cadastros").select("*").order("created_at").execute()
        return res.data if res.data is not None else []
    except Exception as e:
        st.error(f"Erro ao listar registros: {e}")
        return []

# Criação (associa o tenant_id de forma forçada e segura)
def create_record(nome, descricao):
    client = get_supabase_user_client()
    user = get_current_user()
    tenant_id = get_current_tenant()
    
    if not tenant_id:
        st.error("Nenhum workspace ativo selecionado.")
        return False
        
    payload = {
        "tenant_id": tenant_id,
        "nome": nome,
        "descricao": descricao,
        "created_by": user.id if user else None
    }
    
    try:
        client.table("cadastros").insert(payload).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao criar registro: {e}")
        return False

# Edição (segura pelo RLS e tenant_id correto)
def update_record(record_id, nome, descricao):
    client = get_supabase_user_client()
    tenant_id = get_current_tenant()
    
    payload = {
        "nome": nome,
        "descricao": descricao
    }
    
    try:
        # A política RLS garante que o registro só pode ser atualizado se o tenant correspondente for igual
        client.table("cadastros").update(payload).eq("id", record_id).eq("tenant_id", tenant_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar registro: {e}")
        return False

# Exclusão (segura pelo RLS e tenant_id correto)
def delete_record(record_id):
    client = get_supabase_user_client()
    tenant_id = get_current_tenant()
    
    try:
        client.table("cadastros").delete().eq("id", record_id).eq("tenant_id", tenant_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir registro: {e}")
        return False
