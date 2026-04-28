import pandas as pd

excel_path = "descricao_mapa_numerologico.xlsx"
xls = pd.ExcelFile(excel_path)

print(f"Sheets in {excel_path}:")
print(xls.sheet_names)

for sheet in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet)
    print(f"\n--- Sheet: {sheet} ---")
    print(df.head(2))
    print(df.columns.tolist())
