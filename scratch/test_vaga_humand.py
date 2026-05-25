import streamlit as st
from models.database import init_supabase_admin_client
import json

supabase = init_supabase_admin_client()
result = {}
if supabase:
    try:
        res = supabase.table("vagas").select("*").execute()
        result["status"] = "success"
        result["data"] = res.data
    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)
else:
    result["status"] = "error"
    result["message"] = "Could not initialize client"

with open("scratch/vagas_output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=4, ensure_ascii=False)

st.write("Done!")
