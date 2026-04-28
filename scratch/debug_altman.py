import urllib.request
import json

url = "https://wfenlrmsiyndtpxwfgxs.supabase.co/rest/v1/matriz?select=*"
headers = {
    "apikey": "sb_publishable_c1cNaU04TtPkJ12cZBS0Rw_LvqPs1DQ",
    "Authorization": "Bearer sb_publishable_c1cNaU04TtPkJ12cZBS0Rw_LvqPs1DQ"
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        matriz_data = {str(row['numero']): row for row in data if row.get('numero')}
        print(f"Total rows in matriz: {len(matriz_data)}")
        row_7 = matriz_data.get("7")
        print(f"Row for number 7: {row_7}")
except Exception as e:
    print(f"Error: {e}")
