
import streamlit as st
import pandas as pd
from supabase import create_client, Client

def debug_db():
    url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
    key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    
    resp = supabase.table("atributos").select("*").limit(5).execute()
    st.write("Exemplo de dados na tabela ATRIBUTOS:", resp.data)
    
    if resp.data:
        st.write("Colunas disponíveis:", list(resp.data[0].keys()))

if __name__ == "__main__":
    debug_db()
