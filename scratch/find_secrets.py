import streamlit as st
import json

try:
    sec = dict(st.secrets)
    # Convert nested dicts
    for k, v in sec.items():
        try:
            sec[k] = dict(v)
        except:
            pass
    res = {"status": "success", "secrets_keys": list(sec.keys()), "secrets": sec}
except Exception as e:
    res = {"status": "error", "message": str(e)}

with open("scratch/secrets_output.json", "w", encoding="utf-8") as f:
    json.dump(res, f, indent=4, ensure_ascii=False)

st.write("Secrets analyzed!")
