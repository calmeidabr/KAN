import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter

import json
from menus.base_menu import BaseMenu
from models.database import get_supabase_admin, carregar_empresas
from utils.helpers import normalize_key

class AnalyticsMenu(BaseMenu):
    def render(self):
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
        
        .analytics-wrapper * {
            font-family: 'Outfit', sans-serif !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='analytics-wrapper'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: left; margin-bottom: 5px; font-family: Outfit;'>Analytics & BI Comportamental</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.1em; color: rgba(255,255,255,0.7); margin-bottom: 20px; font-family: Outfit;'>Visão analítica consolidada (direto da tabela mapas_salvos).</p>", unsafe_allow_html=True)
        st.write("---")

        client = get_supabase_admin()
        if not client:
            st.error("Conexão com banco de dados indisponível.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        try:
            res_val = client.table("mapas_salvos_valores").select("*").execute()
            rows_val = res_val.data
            
            res_ms = client.table("mapas_salvos").select("*").execute()
            rows_ms = res_ms.data
            
            # Buscar dicionário de soft skills
            res_soft = client.table("soft_skills").select("*").execute()
            soft_skills_list = res_soft.data if res_soft and res_soft.data else []
            
        except Exception as e:
            st.error(f"Erro ao acessar base de dados: {e}")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        if not rows_val:
            st.warning("A tabela 'mapas_salvos_valores' está vazia. Vá ao Painel de Controle > Auditoria e clique em 'CALCULAR MAPAS SALVOS' para popular a base analítica.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        ms_dict = {}
        for r in rows_ms:
            is_migrated_profissao = 'profissao' in r
            profissao_val = r.get('profissao') if is_migrated_profissao else r.get('cargo')
            cargo_val = r.get('cargo') if is_migrated_profissao else ''
            
            ms_dict[r.get("nome")] = {
                "grupo": r.get("grupo", r.get("empresa", "")) if (r.get("grupo") or r.get("empresa")) and str(r.get("grupo") or r.get("empresa")).strip() and str(r.get("grupo") or r.get("empresa")) != "nan" else "Sem Grupo",
                "profissao": profissao_val if profissao_val and str(profissao_val).strip() and str(profissao_val) != "nan" else "Sem Profissão",
                "cargo": cargo_val if cargo_val and str(cargo_val).strip() and str(cargo_val) != "nan" else "",
                "ai_diagnosis": r.get("ai_diagnosis", "")
            }

        def get_geracao(dt_str):
            if not dt_str: return "Desconhecida"
            import re
            match = re.search(r'\b(19\d{2}|20\d{2})\b', str(dt_str))
            if not match: return "Desconhecida"
            ano = int(match.group(1))
            if ano < 1923: return "Anteriores"
            elif 1923 <= ano <= 1946: return "Geração Silenciosa"
            elif 1947 <= ano <= 1964: return "Baby Boomers"
            elif 1965 <= ano <= 1980: return "Geração X"
            elif 1981 <= ano <= 1996: return "Geração Y / Millennials"
            elif 1997 <= ano <= 2009: return "Geração Z"
            else: return "Geração Alpha"

        data_list = []
        for row in rows_val:
            nome = row.get("nome", "Desconhecido")
            ms_info = ms_dict.get(nome, {"grupo": "Sem Grupo", "profissao": "Sem Profissão", "cargo": "", "ai_diagnosis": ""})
            
            data_list.append({
                "nome": nome,
                "grupo": ms_info["grupo"],
                "profissao": ms_info["profissao"],
                "cargo": ms_info["cargo"],
                "perfil": row.get("perfil") if row.get("perfil") and str(row.get("perfil")).strip() else "Não Calculado",
                "categoria": row.get("categoria") if row.get("categoria") and str(row.get("categoria")).strip() else "Não Calculada",
                "qualidades": row.get("qualidades") if row.get("qualidades") and str(row.get("qualidades")).strip() else "Não Calculada",
                "kan": row.get("kan"),
                "ai_diagnosis": ms_info["ai_diagnosis"],
                "geracao": get_geracao(row.get("data_nascimento"))
            })

        df = pd.DataFrame(data_list)

        # Filtros no topo (Sidebar e topo combinados para visual limpo)
        with st.container(border=True):
            st.markdown("<h5 style='margin-top:0;'>Filtros Globais</h5>", unsafe_allow_html=True)
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            
            # Opções de Grupo
            list_grupos = sorted([str(g) for g in df["grupo"].unique() if g is not None and str(g) != "nan" and str(g).strip()])
            if "Sem Grupo" in list_grupos:
                list_grupos.remove("Sem Grupo")
                list_grupos.append("Sem Grupo")
            grupo_selecionado = col_f1.selectbox("Filtrar por Grupo:", ["Todos"] + list_grupos)
            
            # Opções de Profissão
            list_profissoes = sorted([str(p) for p in df["profissao"].unique() if p is not None and str(p) != "nan" and str(p).strip()])
            if "Sem Profissão" in list_profissoes:
                list_profissoes.remove("Sem Profissão")
                list_profissoes.append("Sem Profissão")
            profissao_selecionada = col_f2.multiselect("Filtrar por Profissão:", options=list_profissoes, default=[])
            
            # Opções de Cargo
            list_cargos = sorted([str(c) for c in df["cargo"].unique() if c is not None and str(c) != "nan" and str(c).strip()])
            cargo_selecionado = col_f3.multiselect("Filtrar por Cargo:", options=list_cargos, default=[])

            # Opções de Geração
            ordem_geracoes_todas = ["Anteriores", "Geração Silenciosa", "Baby Boomers", "Geração X", "Geração Y / Millennials", "Geração Z", "Geração Alpha", "Desconhecida"]
            list_geracoes = [g for g in ordem_geracoes_todas if g in df["geracao"].unique()]
            geracao_selecionada = col_f4.multiselect("Filtrar por Geração:", options=list_geracoes, default=[])
            
            # Filtro por Soft Skills
            st.markdown("---")
            st.markdown("<h6 style='margin-top:0;'>Filtro Comportamental Inteligente</h6>", unsafe_allow_html=True)
            soft_skills_names = sorted([s["nome"] for s in soft_skills_list])
            soft_skills_selecionadas = st.multiselect("Filtrar perfis que possuem traços ideais para estas Soft Skills:", options=soft_skills_names, default=[])

        # Aplicar filtros
        df_filtered = df.copy()
        if grupo_selecionado != "Todos":
            df_filtered = df_filtered[df_filtered["grupo"] == grupo_selecionado]
        if profissao_selecionada:
            df_filtered = df_filtered[df_filtered["profissao"].isin(profissao_selecionada)]
        if cargo_selecionado:
            df_filtered = df_filtered[df_filtered["cargo"].isin(cargo_selecionado)]
        if geracao_selecionada:
            df_filtered = df_filtered[df_filtered["geracao"].isin(geracao_selecionada)]
            
        if soft_skills_selecionadas:
            # Filtra perfis que atendem a pelo menos um traço (KAN, Perfil, Categoria ou Qualidade) de TODAS as soft skills selecionadas (interseção para afunilar)
            for sk_name in soft_skills_selecionadas:
                sk_data = next((x for x in soft_skills_list if x["nome"] == sk_name), None)
                if sk_data:
                    ideal_kan = [x.strip().upper() for x in str(sk_data.get("kan_relacionado", "")).split(",") if x.strip()]
                    ideal_perfis = [x.strip().upper() for x in str(sk_data.get("perfis_relacionados", "")).split(",") if x.strip()]
                    ideal_cats = [x.strip().upper() for x in str(sk_data.get("categorias_relacionadas", "")).split(",") if x.strip()]
                    ideal_quals = [x.strip().upper() for x in str(sk_data.get("qualidades_relacionadas", "")).split(",") if x.strip()]
                    
                    def matches_skill(row):
                        u_kan = [x.strip().upper() for x in str(row.get("kan", "")).split(",") if x.strip() and x.strip() != "NAN"]
                        u_perfil = [x.strip().upper() for x in str(row.get("perfil", "")).split(",") if x.strip() and x.strip() != "NAN"]
                        u_cat = [x.strip().upper() for x in str(row.get("categoria", "")).split(",") if x.strip() and x.strip() != "NAN"]
                        u_qual = [x.strip().upper() for x in str(row.get("qualidades", "")).split(",") if x.strip() and x.strip() != "NAN"]
                        
                        match_kan = bool(set(u_kan) & set(ideal_kan))
                        match_perfil = bool(set(u_perfil) & set(ideal_perfis))
                        match_cat = bool(set(u_cat) & set(ideal_cats))
                        match_qual = bool(set(u_qual) & set(ideal_quals))
                        
                        # Atende à soft skill se possuir ao menos 1 traço relacionado na metodologia KAN
                        return match_kan or match_perfil or match_cat or match_qual
                        
                    df_filtered = df_filtered[df_filtered.apply(matches_skill, axis=1)]

        if df_filtered.empty:
            st.warning("Nenhum talento corresponde aos filtros selecionados.")
            return

        # KPIs Principais
        total_talentos = len(df_filtered)
        
        # Perfis válidos (excluindo Não Calculado)
        df_valid_perfil_series = df_filtered["perfil"].dropna().astype(str).str.split(r",\s*").explode().str.strip()
        df_valid_perfil_series = df_valid_perfil_series[(df_valid_perfil_series != "") & (df_valid_perfil_series != "Não Calculado") & (df_valid_perfil_series != "None")]
        perfil_dominante = df_valid_perfil_series.mode().iloc[0] if not df_valid_perfil_series.empty else "N/A"
        
        # Cobertura IA
        total_ia = df_filtered["ai_diagnosis"].apply(lambda x: bool(x) and str(x).strip() != "").sum()
        pct_ia = (total_ia / total_talentos) * 100 if total_talentos > 0 else 0

        # Grupos Ativos filtrados
        total_grupos = df_filtered["grupo"].nunique()

        # Renderizar KPIs com estilo Premium
        st.write("")
        st.markdown("""
        <style>
        .kpi-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }
        .kpi-box {
            background: rgba(255,255,255,0.03);
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.06);
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            backdrop-filter: blur(10px);
        }
        .kpi-num {
            font-size: 2.2em;
            font-weight: 800;
            color: #F18617;
            margin: 5px 0;
        }
        .kpi-lbl {
            font-size: 0.85em;
            color: rgba(255,255,255,0.6);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        </style>
        <div class="kpi-row">
            <div class="kpi-box">
                <div class="kpi-lbl">Total de Talentos</div>
                <div class="kpi-num">""" + str(total_talentos) + """</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-lbl">Perfil Dominante</div>
                <div class="kpi-num" style="font-size: 1.5em; padding-top: 10px; padding-bottom: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">""" + str(perfil_dominante) + """</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-lbl">Cobertura de IA</div>
                <div class="kpi-num">""" + f"{pct_ia:.1f}%" + """</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-lbl">Grupos Cadastrados</div>
                <div class="kpi-num">""" + str(total_grupos) + """</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("---")

        # Configuração de Cores para Gráficos
        accent_color = "#F18617"
        color_palette = ["#F18617", "#9333EA", "#06B6D4", "#10B981", "#EF4444", "#F59E0B", "#3B82F6"]

        def apply_dark_layout(fig, title_text):
            fig.update_layout(
                title=dict(text=title_text, font=dict(size=16, color="#f8fafc"), x=0.05),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f8fafc'),
                margin=dict(l=30, r=20, t=50, b=30),
                legend=dict(font=dict(color='#f8fafc', size=10)),
                xaxis=dict(
                    gridcolor='rgba(255,255,255,0.05)',
                    zerolinecolor='rgba(255,255,255,0.05)',
                    tickfont=dict(color='rgba(255,255,255,0.7)')
                ),
                yaxis=dict(
                    gridcolor='rgba(255,255,255,0.05)',
                    zerolinecolor='rgba(255,255,255,0.05)',
                    tickfont=dict(color='rgba(255,255,255,0.7)')
                )
            )

        # Seção de Gráficos em Linhas/Colunas
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            with st.container(border=True):
                # Gráfico 1: Distribuição de Perfis Comportamentais
                perfis_series = df_filtered["perfil"].dropna().astype(str).str.split(r",\s*").explode().str.strip()
                perfis_series = perfis_series[(perfis_series != "") & (perfis_series != "Não Calculado") & (perfis_series != "None")]
                perfis_counts = perfis_series.value_counts().reset_index()
                perfis_counts.columns = ["Perfil", "Quantidade"]
                
                fig_perf = px.bar(
                    perfis_counts,
                    y="Perfil",
                    x="Quantidade",
                    orientation="h",
                    color_discrete_sequence=[accent_color]
                )
                apply_dark_layout(fig_perf, "Distribuição de Perfis Comportamentais")
                fig_perf.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_perf, use_container_width=True, config={"displayModeBar": False})

        with col_g2:
            with st.container(border=True):
                # Gráfico 2: Distribuição de Categorias
                cat_counts = df_filtered["categoria"].value_counts().reset_index()
                cat_counts.columns = ["Categoria", "Quantidade"]
                
                fig_cat = px.pie(
                    cat_counts,
                    values="Quantidade",
                    names="Categoria",
                    hole=0.4,
                    color_discrete_sequence=color_palette
                )
                apply_dark_layout(fig_cat, "Distribuição de Categorias Comportamentais")
                st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})

        col_g3, col_g4 = st.columns(2)

        with col_g3:
            with st.container(border=True):
                # Gráfico 3: Distribuição de Qualidades
                qual_series = df_filtered["qualidades"].dropna().astype(str).str.split(r",\s*").explode().str.strip()
                qual_series = qual_series[(qual_series != "") & (qual_series != "Não Calculada") & (qual_series != "None")]
                qual_counts = qual_series.value_counts().reset_index()
                qual_counts.columns = ["Qualidade", "Quantidade"]
                
                fig_qual = px.bar(
                    qual_counts,
                    x="Qualidade",
                    y="Quantidade",
                    color_discrete_sequence=[color_palette[1]]
                )
                apply_dark_layout(fig_qual, "Distribuição de Qualidades de Suporte")
                st.plotly_chart(fig_qual, use_container_width=True, config={"displayModeBar": False})

        with col_g4:
            with st.container(border=True):
                # Gráfico 4: Distribuição por KAN (Criação, Movimento, Finalidade)
                kan_series = df_filtered["kan"].dropna().astype(str).str.strip().str.upper()
                valid_kans = ["CRIAÇÃO", "MOVIMENTO", "FINALIDADE", "CRIACAO"]
                df_kan_filtered = kan_series[kan_series.isin(valid_kans)]
                
                if not df_kan_filtered.empty:
                    kan_counts = df_kan_filtered.value_counts().reset_index()
                    kan_counts.columns = ["KAN", "Quantidade"]
                    
                    fig_kan = px.pie(
                        kan_counts,
                        values="Quantidade",
                        names="KAN",
                        hole=0.4,
                        color_discrete_sequence=[color_palette[2], color_palette[3], color_palette[0]]
                    )
                    apply_dark_layout(fig_kan, "Distribuição KAN")
                    st.plotly_chart(fig_kan, use_container_width=True, config={"displayModeBar": False})
                else:
                    st.info("Nenhum dado de KAN classificado como Criação, Movimento ou Finalidade.")

        col_g5, col_g6 = st.columns(2)
        with col_g5:
            with st.container(border=True):
                # Gráfico 5: Distribuição por Gerações
                ger_series = df_filtered["geracao"].dropna()
                ger_series = ger_series[ger_series != "Desconhecida"]
                
                # Definir ordem cronológica
                ordem_geracoes = ["Anteriores", "Geração Silenciosa", "Baby Boomers", "Geração X", "Geração Y / Millennials", "Geração Z", "Geração Alpha"]
                
                ger_counts = ger_series.value_counts().reset_index()
                ger_counts.columns = ["Geração", "Quantidade"]
                # Forçar ordenação cronológica no Plotly
                ger_counts['Geração'] = pd.Categorical(ger_counts['Geração'], categories=ordem_geracoes, ordered=True)
                ger_counts = ger_counts.sort_values('Geração').dropna()
                
                fig_ger = px.bar(
                    ger_counts,
                    x="Quantidade",
                    y="Geração",
                    orientation="h",
                    color_discrete_sequence=[color_palette[2]]
                )
                apply_dark_layout(fig_ger, "Distribuição por Gerações Etárias")
                fig_ger.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_ger, use_container_width=True, config={"displayModeBar": False})
                
        with col_g6:
            st.empty() # Placeholder for future charts

        st.write("---")
        
        # Tabela Analítica de Detalhes
        st.subheader("📋 Tabela Analítica de Talentos")
        
        # Selecionar e ordenar colunas principais para visualização
        table_df = df_filtered[["nome", "grupo", "profissao", "cargo", "kan", "perfil", "categoria", "qualidades", "ai_diagnosis"]].copy()
        
        # Formatar a coluna de Diagnóstico de IA para sim/não visual
        table_df["Diagnóstico IA"] = table_df["ai_diagnosis"].apply(lambda x: "✅ Ativo" if bool(x) and str(x).strip() != "" else "❌ Ausente")
        table_df = table_df.drop(columns=["ai_diagnosis"])
        
        # Renomear cabeçalhos
        table_df.columns = ["Nome", "Grupo", "Profissão", "Cargo", "Número KAN", "Perfil Dominante", "Categoria", "Qualidades", "Status Diagnóstico IA"]
        
        # Exibir tabela interativa
        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True
        )
