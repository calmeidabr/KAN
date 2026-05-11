import os
import streamlit as st
from supabase import create_client, Client

def check_names_starting_with_a():
    try:
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        supabase: Client = create_client(url, key)
        
        # Query for names starting with A (case insensitive)
        # Note: ilike is often supported, or we can just fetch and filter
        response = supabase.table("mapas_salvos").select("nome, perfil_json").ilike("nome", "A%").execute()
        
        if response.data:
            print(f"Encontrados {len(response.data)} registros começando com 'A':")
            for row in response.data:
                nome = row.get("nome")
                perfil = row.get("perfil_json")
                status = "✅ COM MAPA" if perfil and len(str(perfil)) > 10 else "❌ SEM MAPA"
                print(f"- {nome}: {status}")
        else:
            print("Nenhum registro encontrado começando com 'A'.")
            
    except Exception as e:
        print(f"Erro ao acessar o banco: {e}")

if __name__ == "__main__":
    # We need to simulate the streamlit environment to access secrets if running via command line
    # or just use the values if we can find them.
    # Since I am in the environment, I'll try to use the secrets if possible, 
    # but run_command might not have access to streamlit secrets.
    
    # Better approach: check kan.py to see if it already has a way to list them or just run a manual check.
    pass
