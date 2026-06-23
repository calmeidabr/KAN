import streamlit as st
import datetime
from services.db_client import get_supabase_admin

@st.cache_data(ttl=300)
def get_all_plans_cached() -> list:
    """Busca todos os planos e seus limites do banco de dados (cached por 5 min)."""
    admin_client = get_supabase_admin()
    try:
        res = admin_client.table("planos").select("*").execute()
        return res.data if res.data else []
    except Exception as e:
        # Fallback local para robustez em caso de erro de conexão/migração inicial
        return [
            {"id": "free", "nome": "Free", "max_usuarios": 1, "max_talentos": 5, "max_processos_ano": 1, "max_equipes": 0, "custo_mensal": 0.00},
            {"id": "start", "nome": "Start", "max_usuarios": 1, "max_talentos": 10, "max_processos_ano": 3, "max_equipes": 3, "custo_mensal": 179.00},
            {"id": "intermediario", "nome": "Intermediário", "max_usuarios": 3, "max_talentos": 50, "max_processos_ano": 10, "max_equipes": 10, "custo_mensal": 359.00},
            {"id": "business", "nome": "Business", "max_usuarios": 10, "max_talentos": 100, "max_processos_ano": 30, "max_equipes": 30, "custo_mensal": 719.00},
            {"id": "pro", "nome": "Pro", "max_usuarios": 15, "max_talentos": 300, "max_processos_ano": 50, "max_equipes": 70, "custo_mensal": 1979.00},
            {"id": "alta_performance", "nome": "Alta Performance", "max_usuarios": 15, "max_talentos": 700, "max_processos_ano": 75, "max_equipes": 100, "custo_mensal": 2429.00}
        ]

def get_plan_by_id(plan_id: str) -> dict:
    """Retorna os limites de um plano específico."""
    # Compatibilidade com legados
    if plan_id == "basic":
        plan_id = "free"
    elif plan_id == "premium":
        plan_id = "alta_performance"
        
    plans = get_all_plans_cached()
    for p in plans:
        if p["id"] == plan_id:
            return p
            
    # Fallback default (free)
    for p in plans:
        if p["id"] == "free":
            return p
    return {"id": "free", "nome": "Free", "max_usuarios": 1, "max_talentos": 5, "max_processos_ano": 1, "max_equipes": 0, "custo_mensal": 0.00}

def get_tenant_tier(tenant_id: str) -> str:
    """Retorna o tier/plano ativo do tenant."""
    if tenant_id == "00000000-0000-0000-0000-000000000000":
        return "alta_performance"
        
    admin_client = get_supabase_admin()
    try:
        res = admin_client.table("tenants").select("tier").eq("id", tenant_id).execute()
        if res.data:
            return res.data[0].get("tier", "free")
    except Exception:
        pass
    return "free"

def get_tenant_id_by_company(company_name: str) -> str:
    """Busca o tenant_id associado ao nome da empresa."""
    if not company_name:
        return None
    admin_client = get_supabase_admin()
    try:
        res = admin_client.table("empresas").select("tenant_id").eq("nome_empresa", company_name).execute()
        if res.data:
            return res.data[0].get("tenant_id")
    except Exception:
        pass
    return None

def check_limit(tenant_id: str, resource_type: str) -> tuple:
    """
    Verifica se o tenant atingiu o limite para o recurso especificado.
    Retorna: (allowed: bool, current: int, max_val: int, message: str)
    """
    # Bypass para o admin master
    if st.session_state.get("user_rights") == "admin master":
        return True, 0, 999999, ""

    if not tenant_id:
        return True, 0, 999999, ""

    tier = get_tenant_tier(tenant_id)
    limits = get_plan_by_id(tier)
    admin_client = get_supabase_admin()

    if resource_type == "users":
        max_val = limits.get("max_usuarios", 1)
        try:
            res = admin_client.table("usuarios").select("id", count="exact").eq("tenant_id", tenant_id).execute()
            current = res.count if res.count is not None else len(res.data or [])
        except Exception:
            current = 0
        allowed = current < max_val
        msg = f"Seu plano {limits['nome']} permite no máximo {max_val} usuário(s). Atualmente você tem {current}."
        return allowed, current, max_val, msg

    elif resource_type == "talents":
        max_val = limits.get("max_talentos", 5)
        try:
            res = admin_client.table("mapas_salvos").select("id", count="exact").eq("tenant_id", tenant_id).execute()
            current = res.count if res.count is not None else len(res.data or [])
        except Exception:
            current = 0
        allowed = current < max_val
        msg = f"Seu plano {limits['nome']} permite no máximo {max_val} talento(s)/candidato(s). Atualmente você tem {current}."
        return allowed, current, max_val, msg

    elif resource_type == "processes":
        max_val = limits.get("max_processos_ano", 1)
        ano_corrente = datetime.date.today().year
        start_of_year = f"{ano_corrente}-01-01T00:00:00Z"
        end_of_year = f"{ano_corrente}-12-31T23:59:59Z"
        try:
            res = admin_client.table("vagas").select("id", count="exact")\
                .eq("tenant_id", tenant_id)\
                .gte("created_at", start_of_year)\
                .lte("created_at", end_of_year)\
                .execute()
            current = res.count if res.count is not None else len(res.data or [])
        except Exception:
            current = 0
        allowed = current < max_val
        msg = f"Seu plano {limits['nome']} permite no máximo {max_val} processo(s) seletivo(s) por ano. Atualmente você tem {current} no ano de {ano_corrente}."
        return allowed, current, max_val, msg

    elif resource_type == "teams":
        max_val = limits.get("max_equipes", 0)
        try:
            res = admin_client.table("equipes").select("id", count="exact").eq("tenant_id", tenant_id).execute()
            current = res.count if res.count is not None else len(res.data or [])
        except Exception:
            current = 0
        allowed = current < max_val
        msg = f"Seu plano {limits['nome']} permite no máximo {max_val} equipe(s). Atualmente você tem {current}."
        return allowed, current, max_val, msg

    return True, 0, 999999, ""
