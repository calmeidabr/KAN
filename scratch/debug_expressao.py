
import json
import pandas as pd
from collections import Counter

# Mocking parts of the app for debugging
letter_values = {
    'A':1, 'B':2, 'C':3, 'D':4, 'E':5, 'F':8, 'G':3, 'H':5, 'I':1, 'J':1, 'K':2,
    'L':3, 'M':4, 'N':5, 'O':7, 'P':8, 'Q':1, 'R':2, 'S':3, 'T':4, 'U':6, 'V':6,
    'W':6, 'X':6, 'Y':1, 'Z':7, 'Ç':6, 'Ê':3, 'É':7, 'Í':3, 'Ó':9, 'Á':3, 'Ú':8,
    'Ã':4, 'Å':8, 'Ñ':8, 'Ù':3, 'Û':4, 'À':2, 'Ö':5, 'Ô':5, 'È':1, 'Â':8, 'Ì':2, 'Ï':2
}

def reduce_number(n):
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(i) for i in str(n))
    return n

def calcular_numeros_nome(nome_completo):
    nome = nome_completo.upper().replace(' ', '')
    expressao_total = sum(letter_values.get(ch, 0) for ch in nome)
    return reduce_number(expressao_total), expressao_total

# Debug Expressão for Ayrton Senna da Silva
nome = "Ayrton Senna da Silva"
exp, exp_total = calcular_numeros_nome(nome)

print(f"Nome: {nome}")
print(f"Expressão Total: {exp_total}")
print(f"Expressão Reduzida: {exp}")

# Simulate Score Lookup
# Assuming we have the data from previous turns or I'll check it in the actual app file/DB.
