from supabase import create_client
import json

URL = "https://wfenlrmsiyndtpxwfgxs.supabase.co"
KEY = "sb_publishable_c1cNaU04TtPkJ12cZBS0Rw_LvqPs1DQ"

supabase = create_client(URL, KEY)

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

print("=== VERIFICANDO DESCRIÇÕES ===")
for q in queries:
    res = supabase.table("descricoes_mapa").select("*").eq("categoria", q["categoria"]).eq("valor", q["valor"]).execute()
    if res.data:
        print(f"\n[OK] {q['label']}:")
        print(res.data[0]['descricao'])
    else:
        print(f"\n[FALHA] {q['label']} não encontrada!")
