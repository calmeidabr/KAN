import urllib.request
import json

SUPABASE_URL = "https://wfenlrmsiyndtpxwfgxs.supabase.co"
SUPABASE_KEY = "sb_publishable_c1cNaU04TtPkJ12cZBS0Rw_LvqPs1DQ"

queries = [
    {"categoria": "Desafio", "valor": "4", "label": "1º Desafio 4"},
    {"categoria": "Desafio", "valor": "3", "label": "2º Desafio 3"},
    {"categoria": "Desafio", "valor": "1", "label": "Desafio Principal 1"},
    {"categoria": "1º Ciclo de Vida", "valor": "7", "label": "1º Ciclo de Vida 7"},
    {"categoria": "2º Ciclo de Vida", "valor": "2", "label": "2º Ciclo de Vida 2"},
    {"categoria": "3º Ciclo de Vida", "valor": "8", "label": "3º Ciclo de Vida 8"},
    {"categoria": "Momento Decisivo", "valor": "9", "label": "1º Momento Decisivo 9"},
    {"categoria": "Momento Decisivo", "valor": "1", "label": "2º Momento Decisivo 1"},
    {"categoria": "Momento Decisivo", "valor": "1", "label": "3º Momento Decisivo 1"},
    {"categoria": "Momento Decisivo", "valor": "6", "label": "4º Momento Decisivo 6"},
]

print("=== VERIFICANDO DESCRIÇÕES VIA REST API ===")

for q in queries:
    url = f"{SUPABASE_URL}/rest/v1/descricoes_mapa?categoria=eq.{urllib.parse.quote(q['categoria'])}&valor=eq.{q['valor']}"
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data:
                print(f"\n[OK] {q['label']}:")
                print(f"  {data[0]['descricao']}")
            else:
                print(f"\n[FALHA] {q['label']} não encontrada!")
    except Exception as e:
        print(f"\n[ERRO] {q['label']}: {e}")
