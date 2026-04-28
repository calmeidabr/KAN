import urllib.request
import json

SUPABASE_URL = "https://wfenlrmsiyndtpxwfgxs.supabase.co"
SUPABASE_KEY = "sb_publishable_c1cNaU04TtPkJ12cZBS0Rw_LvqPs1DQ"

def get_table(table):
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

print("Tabela desafios:")
print(get_table("desafios")[:3])
