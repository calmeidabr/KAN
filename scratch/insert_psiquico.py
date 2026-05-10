import os
import streamlit as st
from supabase import create_client

# Carrega segredos do Streamlit se estiver rodando em ambiente compatível
# Caso contrário, tenta ler do arquivo diretamente
try:
    url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
    key = st.secrets["connections"]["supabase"]["SUPABASE_SERVICE_KEY"]
except:
    # Fallback para leitura manual se necessário
    import toml
    secrets = toml.load(".streamlit/secrets.toml")
    url = secrets["connections"]["supabase"]["SUPABASE_URL"]
    key = secrets["connections"]["supabase"]["SUPABASE_SERVICE_KEY"]

supabase = create_client(url, key)

data = [
    {'categoria': 'Numero Psiquico', 'valor': '1', 'descricao': 'Independência, pioneirismo, liderança e coragem.'},
    {'categoria': 'Numero Psiquico', 'valor': '2', 'descricao': 'Diplomacia, cooperação, união, intuição e sensibilidade.'},
    {'categoria': 'Numero Psiquico', 'valor': '3', 'descricao': 'Comunicação, expressão, criatividade e natureza artística.'},
    {'categoria': 'Numero Psiquico', 'valor': '4', 'descricao': 'Determinação, persistência, organização, resistência e trabalho.'},
    {'categoria': 'Numero Psiquico', 'valor': '5', 'descricao': 'Adaptação, liberdade, movimento, curiosidade e progresso.'},
    {'categoria': 'Numero Psiquico', 'valor': '6', 'descricao': 'Sensibilidade, harmonia, cuidado, responsabilidade e vínculos.'},
    {'categoria': 'Numero Psiquico', 'valor': '7', 'descricao': 'Perfeccionismo, introspecção, inspiração, intuição e conhecimento.'},
    {'categoria': 'Numero Psiquico', 'valor': '8', 'descricao': 'Liderança, gestão, força prática, autoridade e foco em resultados.'},
    {'categoria': 'Numero Psiquico', 'valor': '9', 'descricao': 'Altruísmo, compaixão, generosidade, intuição e carisma.'},
    {'categoria': 'Numero Psiquico', 'valor': '11', 'descricao': 'Intuição elevada, visão, inspiração e sensibilidade espiritual.'},
    {'categoria': 'Numero Psiquico', 'valor': '22', 'descricao': 'Construção em grande escala, realização, liderança prática e potencial de impacto coletivo.'}
]

print(f"Inserindo {len(data)} registros na tabela descricoes_mapa...")
for item in data:
    try:
        # Tenta inserir. Se já existir (dependendo da PK), pode dar erro, mas aqui inserimos como novos.
        res = supabase.table("descricoes_mapa").insert(item).execute()
        print(f"Inserido: {item['valor']}")
    except Exception as e:
        print(f"Erro ao inserir {item['valor']}: {e}")

print("Concluído.")
