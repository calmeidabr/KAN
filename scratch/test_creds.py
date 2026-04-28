import json
import os

# Lê as credenciais do arquivo .streamlit/secrets.toml
try:
    import tomllib
    secrets_path = "c:/Users/calme/OneDrive/Documentos/KAN/PROG/.streamlit/secrets.toml"
    with open(secrets_path, "rb") as f:
        secrets = tomllib.load(f)
    SUPABASE_URL = secrets["connections"]["supabase"]["SUPABASE_URL"]
    SUPABASE_KEY = secrets["connections"]["supabase"]["SUPABASE_KEY"]
    print(f"URL: {SUPABASE_URL[:40]}...")
    print("Credenciais carregadas com sucesso!")
except Exception as e:
    print(f"Erro ao carregar credenciais: {e}")
    print("Tentando via toml...")
    try:
        import toml
        with open(secrets_path, "r", encoding="utf-8") as f:
            secrets = toml.load(f)
        SUPABASE_URL = secrets["connections"]["supabase"]["SUPABASE_URL"]
        SUPABASE_KEY = secrets["connections"]["supabase"]["SUPABASE_KEY"]
        print(f"URL: {SUPABASE_URL[:40]}...")
    except Exception as e2:
        print(f"Erro com toml: {e2}")
        SUPABASE_URL = None
        SUPABASE_KEY = None
