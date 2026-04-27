import pandas as pd

try:
    df_atr = pd.read_csv('Atributos.csv', sep=';')
    categorias_atr = set(df_atr['CATEGORIA'].dropna().unique())
    
    df_desc = pd.read_csv('categoria_descricao.csv', sep=';')
    categorias_desc = set(df_desc['categoria'].dropna().unique())
    
    print("Categorias no Atributos.csv:", sorted(list(categorias_atr)))
    print("Categorias no categoria_descricao.csv:", sorted(list(categorias_desc)))
    
    faltando = categorias_atr - categorias_desc
    if faltando:
        print("\nCUIDADO! Categorias sem descrição:")
        for f in sorted(list(faltando)):
            print(f"- {f}")
    else:
        print("\nSucesso! Todas as categorias possuem descrição.")
        
except Exception as e:
    print(f"Erro: {e}")
