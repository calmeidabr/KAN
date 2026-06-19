import streamlit as st
from supabase import create_client, Client

def get_public_client() -> Client:
    """
    Retorna o cliente Supabase básico com a chave pública (anon key).
    Útil para operações públicas ou inicialização antes do login.
    """
    try:
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Erro ao inicializar cliente Supabase público: {e}")
        raise e

def get_supabase_client() -> Client:
    """
    Retorna o cliente Supabase associado ao JWT do usuário logado.
    Qualquer operação feita com este cliente respeitará estritamente as políticas de RLS
    no banco de dados, pois o JWT do usuário é injetado no header da requisição.
    """
    client = get_public_client()
    if "supabase_session" in st.session_state:
        session = st.session_state["supabase_session"]
        # Injeta o token JWT ativo do usuário
        client.postgrest.auth(session.access_token)
    return client

def get_supabase_admin() -> Client:
    """
    Retorna o cliente Supabase com privilégios de service_role.
    ATENÇÃO: Este cliente ignora todas as políticas de RLS.
    Deve ser usado apenas em tarefas automáticas do sistema e ações de administrador master (adminkan).
    """
    try:
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_SERVICE_ROLE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Erro ao inicializar cliente Supabase administrativo: {e}")
        raise e
