import streamlit as st
import pandas as pd
import datetime
from collections import Counter
from utils.helpers import remover_acentos, normalize_key, get_from_row
from models.database import (
    MATRIZ_DB, ATRIBUTOS_DB, REPETICAO_DB, PESO_DB, PERFIS_DB, PERFIL_DESCRICAO_DB,
    QUALIDADES_DB, LISTA_CATEGORIA_DB, CATEGORIA_DESCRICAO_DB, PESO_CATEGORIA_DB,
    CAMPO_DEFINICAO_DB, DIFERENCIAIS_DESC_DB, KAN_DB, FORTALEZAS_DB, DESAFIOS_DB,
    get_desc_mapa, carregar_todos_clientes
)
from services.numerologia import (
    reduce_number, calcular_numerologia
)

def calcular_perfil_comportamental(expressao, motivacao, impressao, dia, destino, missao, ciclo2_num, momento3_num, triangulo_base):
    def reduce_kan(n):
        while n > 9 and n not in [11, 22]:
            n = sum(int(d) for d in str(n))
        return n
        
    estrutural = reduce_kan(motivacao + impressao + expressao + reduce_number(dia))
    direcionamento = reduce_kan(destino + missao + ciclo2_num + momento3_num)
    kan = reduce_kan(estrutural + direcionamento)

    num_dia_puro = dia
    num_dia_reduzido = reduce_number(dia)
    nums = [motivacao, impressao, expressao, destino, missao, num_dia_puro, triangulo_base, num_dia_reduzido]
    counts = Counter(nums)
    reps = sorted([(num, count) for num, count in counts.items() if count >= 2], key=lambda x: (-x[1], x[0]))
    
    def get_rep_info(idx):
        if idx < len(reps):
            n = reps[idx][0]
            r_data = REPETICAO_DB.get(str(n), {"perfil": ""})
            perfil = r_data.get('perfil', '')
            return f"{n} - {perfil}" if perfil else str(n)
        return ""

    rep1 = get_rep_info(0)
    rep2 = get_rep_info(1)
    return estrutural, direcionamento, kan, rep1, rep2

def realizar_calculos_completos(nome, nascimento, data_atual, cargo, empresa):
    try:
        resultados = calcular_numerologia(nome, nascimento, data_atual)
        (expressao, motivacao, impressao, destino, dia_pessoal, mes_pess,
         ano_pess, missao, dividas_carmicas, licoes_carmicas,
         tendencias_ocultas, soma_tendencias, resposta_subconsciente,
         desafio1, desafio2, desafio_principal, ciclos_vida, momentos_decisivos,
         triangulo_base, triangulo_reps, arcano_atual_res, arcano_atual_periodo) = resultados

        estrutural, direcionamento, kan, rep1, rep2 = calcular_perfil_comportamental(
            expressao, motivacao, impressao, nascimento[0],
            destino, missao, ciclos_vida['ciclo2']['numero'], momentos_decisivos['momento3']['numero'],
            triangulo_base
        )
        
        todos_numeros_mapa = []
        for v in [expressao, motivacao, impressao, destino, missao, nascimento[0]]:
            if isinstance(v, int): todos_numeros_mapa.append(v)
            elif isinstance(v, str) and str(v).isdigit(): todos_numeros_mapa.append(int(v))
            
        for v in [desafio1, desafio2, desafio_principal]:
            if isinstance(v, int): todos_numeros_mapa.append(v)
            elif isinstance(v, str) and str(v).isdigit(): todos_numeros_mapa.append(int(v))
            
        for c_key in ciclos_vida:
            num_c = ciclos_vida[c_key].get('numero')
            if isinstance(num_c, int): todos_numeros_mapa.append(num_c)
            
        for m_key in momentos_decisivos:
            num_m = momentos_decisivos[m_key].get('numero')
            if isinstance(num_m, int): todos_numeros_mapa.append(num_m)
            
        num_psiquico = reduce_number(nascimento[0])
        todos_numeros_mapa.append(num_psiquico)
        if isinstance(triangulo_base, int): todos_numeros_mapa.append(triangulo_base)
        
        c_total = Counter(todos_numeros_mapa)
        r_totais = sorted([(n, c) for n, c in c_total.items()], key=lambda x: (-x[1], x[0]))
        
        num_repeticao_mapa = r_totais[0][0] if r_totais else 0
        perfil_rep_mapa = REPETICAO_DB.get(str(num_repeticao_mapa), {"perfil": ""}).get("perfil", "")
        repeticao_mapa = f"{num_repeticao_mapa} - {perfil_rep_mapa}" if perfil_rep_mapa else str(num_repeticao_mapa)
        
        num_repeticao_2_mapa = r_totais[1][0] if len(r_totais) > 1 else 0
        perfil_rep_2_mapa = REPETICAO_DB.get(str(num_repeticao_2_mapa), {"perfil": ""}).get("perfil", "")
        repeticao_2_mapa = f"{num_repeticao_2_mapa} - {perfil_rep_2_mapa}" if perfil_rep_2_mapa else str(num_repeticao_2_mapa)
        
        num_repeticao_3_mapa = r_totais[2][0] if len(r_totais) > 2 else 0
        perfil_rep_3_mapa = REPETICAO_DB.get(str(num_repeticao_3_mapa), {"perfil": ""}).get("perfil", "")
        repeticao_3_mapa = f"{num_repeticao_3_mapa} - {perfil_rep_3_mapa}" if perfil_rep_3_mapa else str(num_repeticao_3_mapa)
        
        def extract_num(s):
            if not s: return None
            try: return str(s).split(' - ')[0]
            except: return str(s)
            
        colunas_score = ["Motivação", "Impressão", "Expressão", "Destino", "Missão", "Dia Natalício", "Triângulo", "No Psiquico", "Estrutural", "Direcionamento", "REPETIÇÃO 1", "REPETIÇÃO 2"]
        mapa_col_matriz = {"Motivação": "motivacao", "Impressão": "impressao", "Expressão": "expressao", "Destino": "destino", "Missão": "missao", "Dia Natalício": "dia_natalicio", "Triângulo": "triangulo", "No Psiquico": "no_psiquico"}
        
        valores_originais_score = {
            "Motivação": extract_num(motivacao), "Impressão": extract_num(impressao), "Expressão": extract_num(expressao), "Destino": extract_num(destino), "Missão": extract_num(missao),
            "Dia Natalício": nascimento[0], "Triângulo": triangulo_base, "No Psiquico": num_psiquico,
            "Estrutural": estrutural, "Direcionamento": direcionamento, "REPETIÇÃO 1": extract_num(rep1), "REPETIÇÃO 2": num_repeticao_mapa
        }
        
        perfis_list = PERFIS_DB if PERFIS_DB else ["Lider", "Criativo", "Executor", "Resultado", "Vendedor", "Influenciador", "Comunicador"]
        score_df_calc = pd.DataFrame(0, index=perfis_list, columns=colunas_score)
        
        def get_expl(campo_nome):
            base_name = str(campo_nome).split(" - ")[0]
            search = normalize_key(base_name)
            if "psiquico" in search: search = "nopsiquico"
            if "triangulodavida" in search and "repeticao" not in search: search = "triangulodavida"
            if "repeticao" in search: search = "triangulodavidarepeticoes"
            for k, v in CAMPO_DEFINICAO_DB.items():
                if normalize_key(k) == search: return v
            for k, v in CAMPO_DEFINICAO_DB.items():
                if normalize_key(k) in search or search in normalize_key(k):
                    if len(normalize_key(k)) > 3: return v
            return ""

        dados = []
        def add_row(campo_titulo, valor_badge, resultado_texto, explicacao=""):
            if not explicacao or str(explicacao).strip() == "":
                explicacao = get_expl(campo_titulo)
            
            campo_full = f"{campo_titulo} - {valor_badge}" if (valor_badge is not None and str(valor_badge).strip() != "") else campo_titulo
            dados.append({
                "Campo": campo_full,
                "Valor": str(valor_badge) if valor_badge is not None else "",
                "Resultado": str(resultado_texto) if resultado_texto is not None else "",
                "Explicacao": explicacao
            })

        def add_row_mapa(campo_titulo, valor_num, cat_mapa):
            num_clean = extract_num(valor_num)
            desc = get_desc_mapa(cat_mapa, str(num_clean)) if num_clean is not None else ""
            add_row(campo_titulo, valor_num, desc if desc else valor_num)

        add_row_mapa("Motivação", motivacao, "Motivacao")
        add_row_mapa("Impressão", impressao, "Impressao")
        add_row_mapa("Expressão", expressao, "Expressao")
        add_row_mapa("Dia Natalício", str(nascimento[0]), "Dia Natalicio")
        add_row_mapa("Número Psíquico", str(num_psiquico), "Numero Psiquico")
        add_row_mapa("Destino", destino, "Destino")
        add_row_mapa("Missão", missao, "Missao")

        if dividas_carmicas:
            dividas_str = ', '.join(str(d) for d in dividas_carmicas)
            dividas_parts = [f"<b>{d}</b>: {get_desc_mapa('Divida Carmica', str(d)) or d}" for d in dividas_carmicas]
            add_row("Dívidas Cármicas", dividas_str, ' | '.join(dividas_parts))
        else: add_row("Dívidas Cármicas", None, "Não há")

        if licoes_carmicas:
            licoes_str = ', '.join(str(l) for l in licoes_carmicas)
            licoes_parts = [f"<b>{l}</b>: {get_desc_mapa('Licao Carmica', str(l)) or l}" for l in licoes_carmicas]
            add_row("Lições Cármicas", licoes_str, ' | '.join(licoes_parts))
        else: add_row("Lições Cármicas", None, "Não há")

        if tendencias_ocultas:
            tend_str = ', '.join(str(t) for t in tendencias_ocultas)
            tend_parts = [f"<b>{t}</b>: {get_desc_mapa('Tendencia Oculta', str(t)) or t}" for t in tendencias_ocultas]
            add_row("Tendências Ocultas", tend_str, ' | '.join(tend_parts))
        else: add_row("Tendências Ocultas", None, "Não há")

        desc_resp = get_desc_mapa("Resposta Subconsciente", str(extract_num(resposta_subconsciente))) if resposta_subconsciente else ""
        add_row("Resposta Subconsciente", resposta_subconsciente, desc_resp if desc_resp else resposta_subconsciente)

        desc_des1 = get_desc_mapa("Desafio", str(desafio1))
        add_row("1º Desafio", str(desafio1), desc_des1 if desc_des1 else str(desafio1))
        desc_des2 = get_desc_mapa("Desafio", str(desafio2))
        add_row("2º Desafio", str(desafio2), desc_des2 if desc_des2 else str(desafio2))
        desc_des_princ = get_desc_mapa("Desafio", str(desafio_principal))
        add_row("Desafio Principal", str(desafio_principal), desc_des_princ if desc_des_princ else str(desafio_principal))

        c1_num = str(ciclos_vida['ciclo1']['numero'])
        c1_periodo = f"({ciclos_vida['ciclo1']['inicio']} a {ciclos_vida['ciclo1']['fim']})"
        desc_c1 = get_desc_mapa("1º Ciclo de Vida", c1_num)
        add_row("1º Ciclo de Vida", c1_num, f"<b>Período: {c1_periodo}</b><br>{desc_c1}" if desc_c1 else f"{c1_periodo} {c1_num}")

        c2_num = str(ciclos_vida['ciclo2']['numero'])
        c2_periodo = f"({ciclos_vida['ciclo2']['inicio']} a {ciclos_vida['ciclo2']['fim']})"
        desc_c2 = get_desc_mapa("2º Ciclo de Vida", c2_num)
        add_row("2º Ciclo de Vida", c2_num, f"<b>Período: {c2_periodo}</b><br>{desc_c2}" if desc_c2 else f"{c2_periodo} {c2_num}")

        c3_num = str(ciclos_vida['ciclo3']['numero'])
        c3_periodo = f"(A partir de {ciclos_vida['ciclo3']['inicio']})"
        desc_c3 = get_desc_mapa("3º Ciclo de Vida", c3_num)
        add_row("3º Ciclo de Vida", c3_num, f"<b>Período: {c3_periodo}</b><br>{desc_c3}" if desc_c3 else f"{c3_periodo} {c3_num}")

        m1_num = str(momentos_decisivos['momento1']['numero'])
        m1_periodo = f"({momentos_decisivos['momento1']['inicio']} a {momentos_decisivos['momento1']['fim']})"
        desc_m1 = get_desc_mapa("Momento Decisivo", m1_num)
        add_row("1º Momento Decisivo", m1_num, f"<b>Período: {m1_periodo}</b><br>{desc_m1}" if desc_m1 else f"{m1_periodo} {m1_num}")

        m2_num = str(momentos_decisivos['momento2']['numero'])
        m2_periodo = f"({momentos_decisivos['momento2']['inicio']} a {momentos_decisivos['momento2']['fim']})"
        desc_m2 = get_desc_mapa("Momento Decisivo", m2_num)
        add_row("2º Momento Decisivo", m2_num, f"<b>Período: {m2_periodo}</b><br>{desc_m2}" if desc_m2 else f"{m2_periodo} {m2_num}")

        m3_num = str(momentos_decisivos['momento3']['numero'])
        m3_periodo = f"({momentos_decisivos['momento3']['inicio']} a {momentos_decisivos['momento3']['fim']})"
        desc_m3 = get_desc_mapa("Momento Decisivo", m3_num)
        add_row("3º Momento Decisivo", m3_num, f"<b>Período: {m3_periodo}</b><br>{desc_m3}" if desc_m3 else f"{m3_periodo} {m3_num}")

        m4_num = str(momentos_decisivos['momento4']['numero'])
        m4_periodo = f"(A partir de {momentos_decisivos['momento4']['inicio']})"
        desc_m4 = get_desc_mapa("Momento Decisivo", m4_num)
        add_row("4º Momento Decisivo", m4_num, f"<b>Período: {m4_periodo}</b><br>{desc_m4}" if desc_m4 else f"{m4_periodo} {m4_num}")

        add_row("Ano Pessoal", str(ano_pess), get_desc_mapa("Ano Pessoal", str(ano_pess)) or str(ano_pess))
        add_row("Mês Pessoal", str(mes_pess), str(mes_pess))
        add_row("Dia Pessoal", str(dia_pessoal), str(dia_pessoal))
        add_row("Triângulo Harmônico", str(triangulo_base), str(triangulo_base))
        add_row("Arcano Atual", None, arcano_atual_res)
        add_row("Arcano Atual (Período)", None, arcano_atual_periodo)
        add_row("Repetição Mapa", None, repeticao_mapa)
        add_row("Repetição 2 Mapa", None, repeticao_2_mapa)
        add_row("Repetição 3 Mapa", None, repeticao_3_mapa)
        
        for campo_s in colunas_score:
            val_s = valores_originais_score.get(campo_s)
            if val_s is None: continue
            perfil_enc = None
            if campo_s in mapa_col_matriz:
                row_m = MATRIZ_DB.get(str(val_s))
                if row_m:
                    attr_t = str(get_from_row(row_m, campo_s) or "").upper()
                    if (not attr_t or attr_t == "NAN") and str(val_s).isdigit() and int(val_s) in (11, 22, 33):
                        num_reduz = sum(int(d) for d in str(val_s))
                        row_m_reduz = MATRIZ_DB.get(str(num_reduz))
                        if row_m_reduz: attr_t = str(get_from_row(row_m_reduz, campo_s) or "").upper()
                    if attr_t and attr_t != "NAN":
                        ai = ATRIBUTOS_DB.get(attr_t)
                        if ai: perfil_enc = get_from_row(ai, 'perfil')
            else:
                ri = REPETICAO_DB.get(str(val_s))
                if ri: perfil_enc = get_from_row(ri, 'perfil')
            
            if perfil_enc:
                pn = str(perfil_enc).strip().capitalize()
                if pn in score_df_calc.index:
                    pv = PESO_DB.get(campo_s, 0)
                    score_df_calc.at[pn, campo_s] = int(pv)

        score_df_calc['TOTAL'] = score_df_calc.sum(axis=1)

        lista_cat = LISTA_CATEGORIA_DB if LISTA_CATEGORIA_DB else ["Justo"]
        score_cat_df = pd.DataFrame(0, index=lista_cat, columns=colunas_score)
        
        cat_dia_natalicio = ""
        for campo_c in colunas_score:
            val_c = valores_originais_score.get(campo_c)
            if val_c is None: continue
            
            cat_encontrada = None
            if campo_c in mapa_col_matriz:
                row_m_cat = MATRIZ_DB.get(str(val_c))
                if row_m_cat:
                    attr_t_cat = str(get_from_row(row_m_cat, campo_c)).upper()
                    if attr_t_cat and attr_t_cat != "NAN":
                        ai_cat = ATRIBUTOS_DB.get(attr_t_cat)
                        if ai_cat: cat_encontrada = get_from_row(ai_cat, 'categoria')
            else:
                ri_cat = REPETICAO_DB.get(str(val_c))
                if ri_cat: cat_encontrada = get_from_row(ri_cat, 'categoria')
                
            if cat_encontrada:
                cn = str(cat_encontrada).strip().capitalize()
                if campo_c == "Dia Natalício": cat_dia_natalicio = cn
                if cn in score_cat_df.index:
                    pv_cat = PESO_CATEGORIA_DB.get(campo_c, 0)
                    score_cat_df.at[cn, campo_c] = int(pv_cat)

        score_cat_df['TOTAL'] = score_cat_df.sum(axis=1)
        
        lista_quals = list(QUALIDADES_DB.keys()) if QUALIDADES_DB else ["Relacionamento"]
        score_qual_df = pd.DataFrame(0, index=lista_quals, columns=colunas_score)
        dados_auditoria_qual = []
        for campo_q in colunas_score:
            val_q = valores_originais_score.get(campo_q)
            if val_q is None: continue
            
            qual_en = None; p_v = "N/A"; c_v = "N/A"; attr_t_q = ""
            if campo_q in mapa_col_matriz:
                row_m_q = MATRIZ_DB.get(str(val_q))
                if row_m_q:
                    attr_t_q = str(get_from_row(row_m_q, campo_q) or "").upper()
                    if attr_t_q and attr_t_q != "NAN":
                        ai_q = ATRIBUTOS_DB.get(attr_t_q)
                        if ai_q:
                            p_v = get_from_row(ai_q, 'perfil') or "N/A"; c_v = get_from_row(ai_q, 'categoria') or "N/A"
                            qual_en = (get_from_row(ai_q, 'qualidades') or get_from_row(ai_q, 'qualidade') or get_from_row(ai_q, 'area de suporte') or get_from_row(ai_q, 'categoria') or get_from_row(ai_q, 'perfil'))
            else:
                ri_q = REPETICAO_DB.get(str(val_q))
                if ri_q:
                    p_v = get_from_row(ri_q, 'perfil') or "N/A"; c_v = get_from_row(ri_q, 'categoria') or "N/A"
                    qual_en = (get_from_row(ri_q, 'qualidade') or get_from_row(ri_q, 'area de suporte') or get_from_row(ri_q, 'categoria') or get_from_row(ri_q, 'perfil'))
                    attr_t_q = "Tabela Repetição"
            if qual_en:
                qn = remover_acentos(str(qual_en).strip()).upper()
                for idx_name in score_qual_df.index:
                    if remover_acentos(idx_name).upper() == qn: score_qual_df.at[idx_name, campo_q] += int(PESO_DB.get(campo_q, 0)); break
            dados_auditoria_qual.append({"Campo": campo_q, "Valor": val_q, "Matriz": attr_t_q if attr_t_q else "N/A", "Perfil": p_v, "Categoria": c_v, "Qualidade": qual_en if qual_en else "N/A"})
        score_qual_df['TOTAL'] = score_qual_df.sum(axis=1)

        dados_perfil = []
        def add_row_perfil_split(campo, valor, descricao):
            desc_limpa = descricao.replace("<b>", "").replace("</b>", "").replace("<br>", " | ")
            dados_perfil.append({"Campo": campo, "Valor": valor, "Descricao": descricao, "Resultado": f"{valor} - {desc_limpa}" if desc_limpa else valor})
        
        k_data = KAN_DB.get(str(kan), {"kan": str(kan), "descricao": ""})
        add_row_perfil_split("KAN", k_data['kan'], k_data['descricao'])
        
        totais_s = score_df_calc['TOTAL'].sort_values(ascending=False); perfis_escolhidos = []
        if not totais_s[totais_s > 0].empty:
            max_s = totais_s.iloc[0]
            for p, s in totais_s[totais_s > 0].items():
                if max_s / s <= st.session_state.get('score_perfil_corte_slider', 1.8): perfis_escolhidos.append(p)
                else: break
        perfil_val = ", ".join(perfis_escolhidos); p_desc_list = []
        for p in perfis_escolhidos:
            d = ""; pn = remover_acentos(p).upper()
            for k_desc, v_desc in PERFIL_DESCRICAO_DB.items():
                if remover_acentos(k_desc).upper() == pn: d = v_desc; break
            if d: p_desc_list.append(d)
        add_row_perfil_split("Perfil", perfil_val, "<br><br>".join(p_desc_list) if p_desc_list else "")
        
        modo_corte_cat = st.session_state.get('corte_categoria_modo', 'Calculo')
        cat_sel = cat_dia_natalicio if modo_corte_cat == 'Dia Natalicio' else (score_cat_df['TOTAL'].sort_values(ascending=False).index[0] if not score_cat_df['TOTAL'].empty else "")
        cat_d = ""; cn = remover_acentos(cat_sel).upper()
        for k_desc, v_desc in CATEGORIA_DESCRICAO_DB.items():
            if remover_acentos(k_desc).upper() == cn: cat_d = v_desc; break
        add_row_perfil_split("Categoria", cat_sel, cat_d)
        
        campos_para_dif = [extract_num(motivacao), extract_num(impressao), extract_num(expressao), extract_num(destino), extract_num(missao), str(nascimento[0]), str(triangulo_base), str(num_psiquico)]
        dif_ativos = []; dif_d_list = []
        for v_dif in ["11", "22"]:
            if v_dif in campos_para_dif:
                d_dif = DIFERENCIAIS_DESC_DB.get(v_dif)
                if d_dif: dif_ativos.append(d_dif['diferencial']); dif_d_list.append(f"<b>{d_dif['diferencial']}</b>: {d_dif['descricao']}")
        if dif_ativos: add_row_perfil_split("Diferenciais", ", ".join(dif_ativos), "<br><br>".join(dif_d_list))
        
        totais_q = score_qual_df['TOTAL'].sort_values(ascending=False); q_escolhidas = list(totais_q[totais_q > 0].index)[:2]; q_d_list = []
        for q in q_escolhidas:
            d = ""; qn = remover_acentos(q).upper()
            for k_desc, v_desc in QUALIDADES_DB.items():
                if remover_acentos(k_desc).upper() == qn: d = v_desc; break
            if d: q_d_list.append(f"<b>{q}</b>: {d}")
        add_row_perfil_split("Qualidades", ", ".join(q_escolhidas), "<br>".join(q_d_list) if q_d_list else "")
        
        user_name_key = f"diag_{nome}"
        cl_map = carregar_todos_clientes()
        desc_diag = st.session_state.get("ai_diagnosis", {}).get(user_name_key) or (cl_map.get(nome, {}).get('ai_diagnosis')) or "Clique no botão ao final da página para gerar o Diagnóstico com Inteligência Artificial."
        add_row_perfil_split("Diagnóstico", "Análise de Performance", desc_diag)
        f_data = FORTALEZAS_DB.get(str(triangulo_base), {"fortaleza": "N/E", "descricao": ""}); add_row_perfil_split("Fortaleza", f_data['fortaleza'], f_data['descricao'])
        d_data = DESAFIOS_DB.get(str(nascimento[0]), {"desafio": "N/E", "descricao": ""}); add_row_perfil_split("Desafio", d_data['desafio'], d_data['descricao'])
        
        return dados, dados_perfil, kan, estrutural, direcionamento, rep1, repeticao_mapa, repeticao_2_mapa, repeticao_3_mapa, score_df_calc, score_cat_df, score_qual_df, pd.DataFrame(dados_auditoria_qual)
    except Exception as e:
        st.error(f"Erro nos cálculos: {e}"); return [], [], None, None, None, None, None, None, None, None, None, None, None

@st.cache_data(ttl=3600)
def calcular_perfil_faltante(nome, data_str, _matriz, _atributos, _repeticao, _peso, _perfis, _lista_cat, _qualidades):
    try:
        partes_data = str(data_str).split('/')
        if len(partes_data) != 3: return "", "", "", ""
        dia, mes, ano = int(partes_data[0]), int(partes_data[1]), int(partes_data[2])
        nascimento = (dia, mes, ano)
        data_atual = (datetime.date.today().day, datetime.date.today().month, datetime.date.today().year)
        
        resultados = calcular_numerologia(nome, nascimento, data_atual)
        expressao, motivacao, impressao, destino = resultados[0], resultados[1], resultados[2], resultados[3]
        missao, desafio1, desafio2, desafio_principal = resultados[7], resultados[13], resultados[14], resultados[15]
        ciclos_vida, momentos_decisivos, triangulo_base = resultados[16], resultados[17], resultados[18]
        
        estrutural, direcionamento, kan, rep1, rep2 = calcular_perfil_comportamental(
            expressao, motivacao, impressao, dia,
            destino, missao, ciclos_vida['ciclo2']['numero'], momentos_decisivos['momento3']['numero'],
            triangulo_base
        )
        
        def extract_num(s):
            if not s: return None
            try: return str(s).split(' - ')[0]
            except: return str(s)
        
        todos_numeros_mapa = []
        for v in [expressao, motivacao, impressao, destino, missao, dia]:
            if isinstance(v, int): todos_numeros_mapa.append(v)
            elif isinstance(v, str) and str(v).isdigit(): todos_numeros_mapa.append(int(v))
        for v in [desafio1, desafio2, desafio_principal]:
            if isinstance(v, int): todos_numeros_mapa.append(v)
            elif isinstance(v, str) and str(v).isdigit(): todos_numeros_mapa.append(int(v))
        for c_key in ciclos_vida:
            num_c = ciclos_vida[c_key].get('numero')
            if isinstance(num_c, int): todos_numeros_mapa.append(num_c)
        for m_key in momentos_decisivos:
            num_m = momentos_decisivos[m_key].get('numero')
            if isinstance(num_m, int): todos_numeros_mapa.append(num_m)
        num_psiquico = reduce_number(dia)
        todos_numeros_mapa.append(num_psiquico)
        if isinstance(triangulo_base, int): todos_numeros_mapa.append(triangulo_base)
        
        c_total = Counter(todos_numeros_mapa)
        r_totais = sorted([(num, ct) for num, ct in c_total.items()], key=lambda x: (-x[1], x[0]))
        num_repeticao_mapa = r_totais[0][0] if r_totais else 0
        rep2_val = str(num_repeticao_mapa)
        
        perfis_list = _perfis if _perfis else ["Lider", "Criativo", "Executor", "Resultado", "Vendedor", "Influenciador", "Comunicador"]
        colunas_score = ["Motivação", "Impressão", "Expressão", "Destino", "Missão", "Dia Natalício", "Triângulo", "No Psiquico", "Estrutural", "Direcionamento", "REPETIÇÃO 1", "REPETIÇÃO 2"]
        mapa_col_matriz = {"Motivação": "motivacao", "Impressão": "impressao", "Expressão": "expressao", "Destino": "destino", "Missão": "missao", "Dia Natalício": "dia_natalicio", "Triângulo": "triangulo", "No Psiquico": "no_psiquico"}
        
        valores_originais_score = {
            "Motivação": extract_num(motivacao), "Impressão": extract_num(impressao), "Expressão": extract_num(expressao), "Destino": extract_num(destino), "Missão": extract_num(missao),
            "Dia Natalício": dia, "Triângulo": triangulo_base, "No Psiquico": num_psiquico,
            "Estrutural": estrutural, "Direcionamento": direcionamento, "REPETIÇÃO 1": extract_num(rep1), "REPETIÇÃO 2": int(rep2_val) if str(rep2_val).isdigit() else 0
        }
        
        score_df_calc = pd.DataFrame(0, index=perfis_list, columns=colunas_score)
        for campo_s in colunas_score:
            val_s = valores_originais_score.get(campo_s)
            if val_s is None: continue
            perfil_enc = None
            if campo_s in mapa_col_matriz:
                row_m = _matriz.get(str(val_s))
                if row_m:
                    attr_t = str(get_from_row(row_m, campo_s) or "").upper()
                    if (not attr_t or attr_t == "NAN") and str(val_s).isdigit() and int(val_s) in (11, 22, 33):
                        num_reduz = sum(int(d) for d in str(val_s))
                        row_m_reduz = _matriz.get(str(num_reduz))
                        if row_m_reduz: attr_t = str(get_from_row(row_m_reduz, campo_s) or "").upper()
                    if attr_t and attr_t != "NAN":
                        ai = _atributos.get(attr_t)
                        if ai: perfil_enc = get_from_row(ai, 'perfil')
            else:
                ri = _repeticao.get(str(val_s))
                if ri: perfil_enc = get_from_row(ri, 'perfil')
            
            if perfil_enc:
                pn = str(perfil_enc).strip().capitalize()
                if pn in score_df_calc.index:
                    pv = _peso.get(campo_s, 0)
                    score_df_calc.at[pn, campo_s] = int(pv)

        score_df_calc['TOTAL'] = score_df_calc.sum(axis=1)
        totais_s = score_df_calc['TOTAL'].sort_values(ascending=False)
        totais_s = totais_s[totais_s > 0]
        perfis_escolhidos = []
        if not totais_s.empty:
            max_score = totais_s.iloc[0]
            for p, s in totais_s.items():
                if max_score / s <= 1.8: perfis_escolhidos.append(p)
                else: break
        perfil_val = ", ".join(perfis_escolhidos)
        
        lista_cat = _lista_cat if _lista_cat else ["Justo"]
        score_cat_df = pd.DataFrame(0, index=lista_cat, columns=colunas_score)
        
        for campo_c in colunas_score:
            val_c = valores_originais_score.get(campo_c)
            if val_c is None: continue
            
            cat_encontrada = None
            if campo_c in mapa_col_matriz:
                row_m_cat = _matriz.get(str(val_c))
                if row_m_cat:
                    attr_t_cat = str(get_from_row(row_m_cat, campo_c)).upper()
                    if attr_t_cat and attr_t_cat != "NAN":
                        ai_cat = _atributos.get(attr_t_cat)
                        if ai_cat: cat_encontrada = get_from_row(ai_cat, 'categoria')
            else:
                ri_cat = _repeticao.get(str(val_c))
                if ri_cat: cat_encontrada = get_from_row(ri_cat, 'categoria')
                
            if cat_encontrada:
                cn = str(cat_encontrada).strip().capitalize()
                if cn in score_cat_df.index:
                    pv_cat = _peso.get(campo_c, 0)
                    score_cat_df.at[cn, campo_c] = int(pv_cat)

        score_cat_df['TOTAL'] = score_cat_df.sum(axis=1)
        totais_cat = score_cat_df['TOTAL'].sort_values(ascending=False)
        totais_cat = totais_cat[totais_cat > 0]
        categoria_selecionada = totais_cat.index[0] if not totais_cat.empty else ""
        
        lista_quals = list(_qualidades.keys()) if _qualidades else ["Relacionamento"]
        score_qual_df = pd.DataFrame(0, index=lista_quals, columns=colunas_score)
        for campo_q in colunas_score:
            val_q = valores_originais_score.get(campo_q)
            if val_q is None: continue
            
            qual_encontrada = None
            if campo_q in mapa_col_matriz:
                row_m_q = _matriz.get(str(val_q))
                if row_m_q:
                    attr_t_q = str(get_from_row(row_m_q, campo_q) or "").upper()
                    if attr_t_q and attr_t_q != "NAN":
                        ai_q = _atributos.get(attr_t_q)
                        if ai_q: qual_encontrada = get_from_row(ai_q, 'qualidades')
            else:
                ri_q = _repeticao.get(str(val_q))
                if ri_q: qual_encontrada = get_from_row(ri_q, 'qualidade')

            if qual_encontrada:
                quals = [x.strip().capitalize() for x in str(qual_encontrada).split(',')]
                for q_name in quals:
                    if q_name in score_qual_df.index: score_qual_df.at[q_name, campo_q] = 1

        score_qual_df['TOTAL'] = score_qual_df.sum(axis=1)
        totais_q = score_qual_df['TOTAL'].sort_values(ascending=False)
        totais_q = totais_q[totais_q > 0]
        qual_val = ", ".join(list(totais_q.index)[:2])
        
        return perfil_val, categoria_selecionada, qual_val, str(kan)
    except Exception as e:
        import traceback
        return f"ERRO: {e} | {traceback.format_exc()}", "ERRO", "ERRO", "ERRO"
