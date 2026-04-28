import pandas as pd

excel_path = "descricao_mapa_numerologico.xlsx"
xl = pd.ExcelFile(excel_path)
print("Sheet Names:", xl.sheet_names)
