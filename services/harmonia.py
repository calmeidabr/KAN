import datetime
from collections import Counter
from services.numerologia import calcular_numerologia, reduce_number
from services.perfil import calcular_perfil_comportamental

# Coordenadas oficiais dos planos no Plano de Tesla
COORDS_MAP = {
    1: (794, 176), 2: (1037, 243), 3: (960, 380),
    4: (794, 585), 5: (486, 585), 6: (320, 380),
    7: (243, 243), 8: (486, 176), 9: (640, 120),
    11: (1037, 243), 22: (794, 585)
}

def clean_value(v):
    if v is None:
        return None
    s = str(v).split(" - ")[0]
    return int(s) if s.isdigit() and int(s) > 0 else None

def obter_vertices_triangulo(nome_comp, data_nasc_str):
    """
    Calcula e retorna os 3 vértices do triângulo harmônico (números de 1 a 9)
    e o KAN principal correspondente a um talento com base em numerologia.
    """
    try:
        if isinstance(data_nasc_str, (datetime.datetime, datetime.date)):
            nasc_dt = data_nasc_str
        else:
            try:
                nasc_dt = datetime.datetime.strptime(data_nasc_str, "%d/%m/%Y")
            except ValueError:
                nasc_dt = datetime.datetime.strptime(data_nasc_str, "%Y-%m-%d")
        
        nasc_tuple = (nasc_dt.day, nasc_dt.month, nasc_dt.year)
        now_dt = datetime.datetime.now()
        data_at = (now_dt.day, now_dt.month, now_dt.year)

        res = calcular_numerologia(nome_comp, nasc_tuple, data_at)
        (expressao, motivacao, impressao, destino, _, _, _, missao, _, _,
         _, _, _, _, _, _, ciclos_vida, momentos_decisivos, triangulo_base, _, _, _) = res

        estrutural, direcionamento, kan, rep1, rep2 = calcular_perfil_comportamental(
            expressao, motivacao, impressao, nasc_tuple[0],
            destino, missao,
            ciclos_vida['ciclo2']['numero'],
            momentos_decisivos['momento3']['numero'],
            triangulo_base
        )

        todos_num = []
        for v_it in [expressao, motivacao, impressao, destino, missao, nasc_tuple[0]]:
            if isinstance(v_it, int):
                todos_num.append(v_it)
            elif isinstance(v_it, str) and str(v_it).isdigit():
                todos_num.append(int(v_it))
        
        for c_key in ciclos_vida:
            num_c = ciclos_vida[c_key].get('numero')
            if isinstance(num_c, int):
                todos_num.append(num_c)
        for m_key in momentos_decisivos:
            num_m = momentos_decisivos[m_key].get('numero')
            if isinstance(num_m, int):
                todos_num.append(num_m)
        
        num_ps = reduce_number(nasc_tuple[0])
        todos_num.append(num_ps)
        if isinstance(triangulo_base, int):
            todos_num.append(triangulo_base)

        c_tot = Counter(todos_num)
        r_tot = sorted([(n, c) for n, c in c_tot.items()], key=lambda x: (-x[1], x[0]))
        r2_v = r_tot[0][0] if r_tot else 0
        r3_v = r_tot[1][0] if len(r_tot) > 1 else 0
        r4_v = r_tot[2][0] if len(r_tot) > 2 else 0

        todos_comp = [
            {"campo": "KAN",            "valor": clean_value(kan)},
            {"campo": "ESTRUTURAL",     "valor": clean_value(estrutural)},
            {"campo": "DIRECIONAMENTO", "valor": clean_value(direcionamento)},
            {"campo": "REPETIÇÃO 1",    "valor": clean_value(rep1)},
            {"campo": "REP. MAPA",      "valor": r2_v if r2_v else None},
            {"campo": "REP. MAPA 2",    "valor": r3_v if r3_v else None},
            {"campo": "REP. MAPA 3",    "valor": r4_v if r4_v else None},
        ]

        verts = []
        vals_seen = set()
        for it in todos_comp:
            v_it = it["valor"]
            if v_it is not None and v_it not in [11, 22] and v_it not in vals_seen:
                verts.append(v_it)
                vals_seen.add(v_it)
            if len(verts) == 3:
                break
        
        # Fallback para completar 3 vértices distintos se necessário
        if len(verts) < 3:
            for fallback_val in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                if fallback_val not in vals_seen:
                    verts.append(fallback_val)
                    vals_seen.add(fallback_val)
                if len(verts) == 3:
                    break

        kan_str = str(kan) if kan else "Nenhum"
        return verts, kan_str
    except Exception:
        return [1, 2, 3], "Nenhum"

# --- HELPERS GEOMÉTRICOS ---

def ccw(A, B, C):
    """
    Verifica se a orientação dos pontos A, B e C é anti-horária (True) ou horária/colinear (False).
    """
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

def se_cruzam(A, B, C, D):
    """
    Verifica se o segmento de reta AB cruza com o segmento CD.
    """
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

def obter_coordenada(plano):
    """
    Retorna a coordenada (x, y) de um plano de 1 a 9.
    Reduz 11 a 2 e 22 a 4.
    """
    p = int(plano)
    if p == 11:
        p = 2
    elif p == 22:
        p = 4
    return COORDS_MAP.get(p, (640, 360))

def classificar_relacao_geometrica(T_A, T_B):
    """
    Classifica a relação geométrica entre dois triângulos T_A e T_B no Plano de Tesla.
    T_A e T_B são listas com 3 vértices de 1 a 9.
    
    Categorias retornadas:
    - "Sobreposição Idêntica"
    - "Lateral em Comum"
    - "Vértice em Comum"
    - "Atravessamento"
    - "Afastamento"
    """
    set_A = set(T_A)
    set_B = set(T_B)
    
    # 1. Sobreposição Idêntica
    if set_A == set_B:
        return "Sobreposição Idêntica"
    
    # 2. Lateral em Comum
    intersec = set_A.intersection(set_B)
    if len(intersec) == 2:
        return "Lateral em Comum"
    
    # 3. Vértice em Comum
    if len(intersec) == 1:
        return "Vértice em Comum"
    
    # 4. Atravessamento (nenhum vértice compartilhado, mas as arestas se cruzam)
    # Arestas de A e B
    arestas_A = [(T_A[0], T_A[1]), (T_A[1], T_A[2]), (T_A[2], T_A[0])]
    arestas_B = [(T_B[0], T_B[1]), (T_B[1], T_B[2]), (T_B[2], T_B[0])]
    
    for a_A in arestas_A:
        pA1 = obter_coordenada(a_A[0])
        pA2 = obter_coordenada(a_A[1])
        for a_B in arestas_B:
            pB1 = obter_coordenada(a_B[0])
            pB2 = obter_coordenada(a_B[1])
            if se_cruzam(pA1, pA2, pB1, pB2):
                return "Atravessamento"
                
    # 5. Afastamento
    return "Afastamento"

# --- FUNÇÃO PRINCIPAL DE HARMÔNIA ---

def calcular_harmonia_trio(membro1, membro2, candidato, pesos=None):
    """
    Calcula o encaixe (harmonia) de um candidato em um trio com dois membros de equipe.
    Cada entrada é um dicionário contendo {"nome": str, "vertices": list, "kan": str}.
    
    Retorna um dicionário:
    {
        "nota_final": float (0 a 100),
        "faixa": str (Encaixe Muito Alto, Bom Encaixe, etc.),
        "blocos": dict (pontuações parciais 0 a 5),
        "justificativa": str (texto em português de negócios)
    }
    """
    if pesos is None:
        pesos = {
            "complementaridade": 25,
            "integracao": 25,
            "balanceamento": 20,
            "entrega": 15,
            "conflito": 15
        }
        
    n1, n2, nc = membro1["nome"], membro2["nome"], candidato["nome"]
    v1, v2, vc = membro1["vertices"], membro2["vertices"], candidato["vertices"]
    
    def normalizar_nome_kan(k_val):
        if k_val is None:
            return "Nenhum"
        k_str = str(k_val).strip()
        # Mapeamento de números/floats para nomes de KAN
        if k_str in ("3", "3.0"):
            return "Criação"
        if k_str in ("6", "6.0"):
            return "Movimento"
        if k_str in ("9", "9.0"):
            return "Finalidade"
        # Trata capitalizações e grafias comuns
        k_cap = k_str.capitalize()
        if k_cap in ("Criação", "Criacao"):
            return "Criação"
        if k_cap in ("Movimento"):
            return "Movimento"
        if k_cap in ("Finalidade"):
            return "Finalidade"
        return k_cap

    k1 = normalizar_nome_kan(membro1["kan"])
    k2 = normalizar_nome_kan(membro2["kan"])
    kc = normalizar_nome_kan(candidato["kan"])
    
    # --- BLOCO 1: Complementaridade de KANs (peso 25%) ---
    # Trio ideal possui Criação, Movimento e Finalidade representados
    kans_ativos = {k1.strip().capitalize(), k2.strip().capitalize(), kc.strip().capitalize()}
    # Remove eventuais "Nenhum" ou inválidos
    kans_validos = {k for k in kans_ativos if k in ("Criação", "Movimento", "Finalidade")}
    
    if len(kans_validos) == 3:
        bloco_kan = 5.0
    elif len(kans_validos) == 2:
        bloco_kan = 3.5
    else:
        bloco_kan = 1.5
        
    # --- BLOCO 2: Integração Geométrica (peso 25%) ---
    # Relações entre os pares: (membro1, membro2), (membro1, candidato), (membro2, candidato)
    r12 = classificar_relacao_geometrica(v1, v2)
    r1c = classificar_relacao_geometrica(v1, vc)
    r2c = classificar_relacao_geometrica(v2, vc)
    
    pontos_relacao = {
        "Lateral em Comum": 5.0,
        "Vértice em Comum": 4.0,
        "Atravessamento": 3.0,
        "Sobreposição Idêntica": 2.5,
        "Afastamento": 1.0
    }
    
    nota_r12 = pontos_relacao[r12]
    nota_r1c = pontos_relacao[r1c]
    nota_r2c = pontos_relacao[r2c]
    
    # Integração geométrica é a média
    bloco_geo = (nota_r12 + nota_r1c + nota_r2c) / 3.0
    
    # --- BLOCO 3: Balanceamento do Trio (peso 20%) ---
    # Cobertura de planos de 1 a 9
    planos_cobertos = set(v1).union(set(v2)).union(set(vc))
    num_planos = len(planos_cobertos)
    
    if num_planos >= 6:
        bloco_bal = 5.0
    elif num_planos == 5:
        bloco_bal = 4.0
    elif num_planos == 4:
        bloco_bal = 3.0
    elif num_planos == 3:
        bloco_bal = 2.0
    elif num_planos == 2:
        bloco_bal = 1.0
    else:
        bloco_bal = 0.5
        
    # --- BLOCO 4: Potencial de Entrega (peso 15%) ---
    # Foco nos planos práticos 4 (Construção), 8 (Materialidade) e 9 (Finalidade)
    planos_praticos = {4, 8, 9}
    conexoes_praticas = 0
    
    # Vértices compartilhados no trio
    vertices_compartilhados = set()
    for v in set(v1).intersection(set(vc)):
        vertices_compartilhados.add(v)
    for v in set(v2).intersection(set(vc)):
        vertices_compartilhados.add(v)
    for v in set(v1).intersection(set(v2)):
        vertices_compartilhados.add(v)
        
    conexoes_praticas_compartilhadas = vertices_compartilhados.intersection(planos_praticos)
    
    # Nota de conexões
    nota_conexoes = 0.0
    if len(conexoes_praticas_compartilhadas) >= 2:
        nota_conexoes = 4.0
    elif len(conexoes_praticas_compartilhadas) == 1:
        nota_conexoes = 2.5
        
    # Presença de KAN Finalidade (liderança/finalização)
    ponto_finalidade = 0.0
    tem_finalidade_geral = any(k.strip().capitalize() == "Finalidade" for k in (k1, k2, kc))
    if tem_finalidade_geral:
        ponto_finalidade += 0.5
    if kc.strip().capitalize() == "Finalidade":
        ponto_finalidade += 0.5
        
    bloco_entrega = min(5.0, 1.0 + nota_conexoes + ponto_finalidade)
    
    # --- BLOCO 5: Risco de Conflito (peso 15%) ---
    # 5.0 representa risco mínimo (excelente harmonia), 0.0 risco crítico
    bloco_conflito = 5.0
    
    # Penalidade por sobreposições idênticas
    if r1c == "Sobreposição Idêntica":
        bloco_conflito -= 1.8
    if r2c == "Sobreposição Idêntica":
        bloco_conflito -= 1.8
    if r12 == "Sobreposição Idêntica":
        bloco_conflito -= 1.0 # Menor peso por ser o time atual
        
    # Penalidade por mesmo KAN (falta de variedade / disputa de espaço)
    if k1.strip().capitalize() == k2.strip().capitalize() == kc.strip().capitalize() and k1.strip().capitalize() != "Nenhum":
        bloco_conflito -= 1.5
    else:
        if k1.strip().capitalize() == kc.strip().capitalize() and k1.strip().capitalize() != "Nenhum":
            bloco_conflito -= 0.8
        if k2.strip().capitalize() == kc.strip().capitalize() and k2.strip().capitalize() != "Nenhum":
            bloco_conflito -= 0.8
        if k1.strip().capitalize() == k2.strip().capitalize() and k1.strip().capitalize() != "Nenhum":
            bloco_conflito -= 0.5
        
    # Penalidade por afastamentos
    if r1c == "Afastamento":
        bloco_conflito -= 0.6
    if r2c == "Afastamento":
        bloco_conflito -= 0.6
        
    # Concentração excessiva de planos
    if num_planos <= 3:
        bloco_conflito -= 1.0
        
    bloco_conflito = max(0.0, min(5.0, bloco_conflito))
    
    # --- CÁLCULO DA NOTA FINAL ---
    nota_final_5 = (
        bloco_kan * pesos["complementaridade"] +
        bloco_geo * pesos["integracao"] +
        bloco_bal * pesos["balanceamento"] +
        bloco_entrega * pesos["entrega"] +
        bloco_conflito * pesos["conflito"]
    ) / 100.0
    
    nota_final = (nota_final_5 / 5.0) * 100.0
    nota_final = round(nota_final, 1)
    
    # --- CLASSIFICAÇÃO DA FAIXA ---
    if nota_final >= 85.0:
        faixa = "Encaixe Muito Alto"
    elif nota_final >= 70.0:
        faixa = "Bom Encaixe"
    elif nota_final >= 55.0:
        faixa = "Encaixe Moderado"
    elif nota_final >= 40.0:
        faixa = "Encaixe Frágil"
    else:
        faixa = "Encaixe Baixo"
        
    # --- GERAÇÃO DE JUSTIFICATIVA TEXTUAL QUALITATIVA ---
    just_parts = []
    
    # Introdução baseada no KAN e faixa
    just_parts.append(
        f"A integração de **{nc}** com a equipe formada por **{n1}** e **{n2}** apresenta um **{faixa.upper()}** (Nota: **{nota_final}**/100)."
    )
    
    # Análise de KANs e complementaridade
    if bloco_kan == 5.0:
        just_parts.append(
            f"O trio alcança equilíbrio absoluto de forças KAN: os três KANs essenciais (Criação, Movimento e Finalidade) estão representados. Isso assegura que o time terá estímulo para gerar ideias, articular contatos e finalizar tarefas."
        )
    elif bloco_kan >= 3.5:
        representados = [k for k in kans_validos]
        just_parts.append(
            f"Há uma boa complementaridade com a representação de {len(representados)} das forças KAN ({', '.join(representados)}). O time é funcional, porém pode apresentar uma leve lacuna no KAN restante."
        )
    else:
        just_parts.append(
            f"O time apresenta alta concentração na força KAN '{k1}' ({len(kans_validos)} KAN distinto no trio). Há risco de redundância comportamental, onde todos buscam focar nas mesmas ações (ex: excesso de idealização ou falta de acabativa)."
        )
        
    # Análise Geométrica e Sinergia
    convergencias = []
    if r1c == "Lateral em Comum":
        convergencias.append(f"**{nc}** e **{n1}** compartilham uma lateral inteira de seus triângulos, demonstrando complementaridade direta no trabalho.")
    elif r1c == "Vértice em Comum":
        convergencias.append(f"**{nc}** conecta-se a **{n1}** por um vértice em comum, indicando sintonia e boa integração funcional.")
    elif r1c == "Sobreposição Idêntica":
        convergencias.append(f"**{nc}** tem triângulo sobreposto a **{n1}**, gerando alta sinergia e espelhamento mútuo no trabalho.")
        
    if r2c == "Lateral em Comum":
        convergencias.append(f"**{nc}** e **{n2}** compartilham uma lateral em comum, reforçando a estabilidade e o apoio mútuo.")
    elif r2c == "Vértice em Comum":
        convergencias.append(f"**{nc}** toca o triângulo de **{n2}** em um vértice comum, facilitando a troca e cooperação direta.")
    elif r2c == "Sobreposição Idêntica":
        convergencias.append(f"**{nc}** e **{n2}** possuem triângulos idênticos, favorecendo o alinhamento rápido e a comunicação imediata.")
        
    if convergencias:
        just_parts.append(" ".join(convergencias))
    else:
        just_parts.append(
            f"Do ponto de vista geométrico, **{nc}** possui triângulo afastado dos demais membros do time, indicando possíveis distanciamentos nas tomadas de decisão e maior esforço necessário para comunicação."
        )
        
    # Potencial de Entrega
    if bloco_entrega >= 4.0:
        just_parts.append(
            f"O potencial de entrega conjunta é excelente. O trio compartilha conexões nos planos práticos de Materialidade/Construção/Finalidade no Plano de Tesla. A presença de perfil com KAN Finalidade traz um forte senso de acabativa para as entregas."
        )
    elif bloco_entrega >= 2.5:
        just_parts.append(
            f"O potencial de entrega é moderado. Há presença de força de acabativa ou conexões em planos de realização, permitindo fluidez na execução das demandas de negócio."
        )
    else:
        just_parts.append(
            f"O potencial de entrega é reduzido, pois não foram identificadas conexões fortes nos planos de Materialidade e Construção (planos 8 e 4) ou liderança KAN Finalidade, exigindo supervisão externa para finalização de projetos."
        )
        
    # Riscos de Conflito
    riscos = []
    if r1c == "Sobreposição Idêntica" or r2c == "Sobreposição Idêntica":
        riscos.append("A sobreposição idêntica de triângulos indica alta similaridade, o que pode gerar disputa de espaço ou conflito de egos caso não haja clara divisão de papéis.")
    if r1c == "Afastamento" and r2c == "Afastamento":
        riscos.append("O duplo afastamento geométrico do candidato em relação aos membros do time pode isolá-lo, dificultando a coesão interna.")
    if bloco_conflito <= 2.0:
        riscos.append("Recomenda-se acompanhamento e alinhamento próximo nos primeiros meses, dado o alto risco de desalinhamento ou redundâncias de perfil identificadas.")
        
    if riscos:
        just_parts.append(" ".join(riscos))
    else:
        just_parts.append(
            "Não há riscos de conflito severos projetados; a combinação geométrica e comportamental indica excelente estabilidade relacional."
        )
        
    justificativa = " ".join(just_parts)
    
    return {
        "nota_final": nota_final,
        "faixa": faixa,
        "blocos": {
            "complementaridade": bloco_kan,
            "integracao": bloco_geo,
            "balanceamento": bloco_bal,
            "entrega": bloco_entrega,
            "conflito": bloco_conflito
        },
        "justificativa": justificativa
    }
