import pandas as pd

df = pd.read_csv("Atributos.csv", sep=";")
if df.shape[1] <= 1:
    df = pd.read_csv("Atributos.csv", sep=",")

for _, row in df.iterrows():
    attr = str(row.get('ATRIBUTOS', '')).upper().strip()
    if "DETERMINA" in attr or "CONHECIMENTO" in attr:
        print(row.to_dict())
