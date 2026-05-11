import sys
import os
import json
import pandas as pd
import datetime
sys.path.append(r'c:\Users\calme\OneDrive\Documentos\KAN\PROG')
from kan import calcular_perfil_faltante, fetch_matriz, fetch_atributos, fetch_repeticao, fetch_peso, fetch_perfis, fetch_lista_categoria, fetch_qualidades

def test():
    MATRIZ = fetch_matriz()
    ATRIBUTOS = fetch_atributos()
    REPETICAO = fetch_repeticao()
    PESO = fetch_peso()
    PERFIS = fetch_perfis()
    LISTA_CAT = fetch_lista_categoria()
    QUALIDADES = fetch_qualidades()

    res = calcular_perfil_faltante("Teste", "01/01/2000", MATRIZ, ATRIBUTOS, REPETICAO, PESO, PERFIS, LISTA_CAT, QUALIDADES)
    print("RESULTADO:", res)

if __name__ == '__main__':
    test()
