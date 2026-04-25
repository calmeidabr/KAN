
import json

# Simulation of what's in the DB
# I'll use the values provided by the user and my previous knowledge

MATRIZ_DB = {
    "9": {"motivacao": "HUMANITARISMO", "destino": "HUMANITARISMO", "missao": "HUMANITARISMO"},
    "8": {"missao": "JUSTICA"},
    "22": {"destino": "CONSTRUTOR"},
    "4": {"expressao": "EXECUTOR", "impressao": "EXECUTOR"},
    "3": {"no_psiquico": "COMUNICADOR"},
    "21": {"dia_natalicio": "SABEDORIA"}
}

ATRIBUTOS_DB = {
    "HUMANITARISMO": {"perfil": "Lider"}, # ?
    "JUSTICA": {"perfil": ""},
    "CONSTRUTOR": {"perfil": "Executor"},
    "EXECUTOR": {"perfil": "Executor"},
    "COMUNICADOR": {"perfil": "Comunicador"},
    "SABEDORIA": {"perfil": ""}
}

PESO_DB = {
    "Motivação": 150,
    "Impressão": 100,
    "Expressão": 100,
    "Destino": 150,
    "Missão": 150,
    "Dia Natalício": 100,
    "Triângulo": 150,
    "No Psiquico": 100,
    "REPETIÇÃO 1": 100
}

# Let's trace Ayrton
# Motivação: 9 -> HUMANITARISMO -> Lider (150)
# Destino: 22 -> CONSTRUTOR -> Executor (150)
# Missão: 8 -> JUSTICA -> (0)
# Triângulo: ? (User says 150 for Lider)
# No Psiquico: 3 -> COMUNICADOR -> Comunicador (100)
# Wait, user says Lider should get 100 from No Psiquico?
# No, they said "100 do No Psiquico".

print("Checking Ayrton scores...")
