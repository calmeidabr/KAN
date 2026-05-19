import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter

from menus.base_menu import BaseMenu
from models.database import carregar_todos_clientes, carregar_empresas

class AnalyticsMenu(BaseMenu):
    def render(self):
        st.markdown("<h2 style='text-align: left; margin-bottom: 5px;'>Analytics & BI Comportamental</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.1em; color: rgba(255,255,255,0.7); margin-bottom: 20px;'>Visão analítica consolidada e cruzamento de dados comportamentais das equipes.</p>", unsafe_allow_html=True)
        st.write("---")

        # Carregar dados reais da base
        clientes = carregar_todos_clientes()
        empresas_salvas = carregar_empresas()
        
        if not clientes:
            st.warning("Nenhum perfil cadastrado no sistema para análise. Vá ao menu 'Talentos' para adicionar perfis.")
            return

        # Converter para lista de dicionários com o nome incluído
        data_list = []
        for nome, info in clientes.items():
            item = info.copy()
            item["nome"] = nome
            # Preencher campos vazios
            if not item.get("empresa") or str(item["empresa"]).strip() == "" or str(item["empresa"]) == "nan":
                item["empresa"] = "Sem Empresa"
            if not item.get("cargo") or str(item["cargo"]).strip() == "" or str(item["cargo"]) == "nan":
                item["cargo"] = "Sem Cargo"
            if not item.get("perfil") or str(item["perfil"]).strip() == "":
                item["perfil"] = "Não Calculado"
            if not item.get("categoria") or str(item["categoria"]).strip() == "":
                item["categoria"] = "Não Calculada"
            if not item.get("qualidades") or str(item["qualidades"]).strip() == "":
                item["qualidades"] = "Não Calculada"
            data_list.append(item)

        df = pd.DataFrame(data_list)

        # Filtros no topo (Sidebar e topo combinados para visual limpo)
        with st.container(border=True):
            st.markdown("<h5 style='margin-top:0;'>Filtros Globais</h5>", unsafe_allow_html=True)
            col_f1, col_f2 = st.columns(2)
            
            # Opções de Empresa
            list_empresas = sorted(list(df["empresa"].unique()))
            if "Sem Empresa" in list_empresas:
                list_empresas.remove("Sem Empresa")
                list_empresas.append("Sem Empresa")
            empresa_selecionada = col_f1.selectbox("Filtrar por Empresa:", ["Todas"] + list_empresas)
            
            # Opções de Cargo
            list_cargos = sorted(list(df["cargo"].unique()))
            if "Sem Cargo" in list_cargos:
                list_cargos.remove("Sem Cargo")
                list_cargos.append("Sem Cargo")
            cargo_selecionado = col_f2.selectbox("Filtrar por Cargo:", ["Todos"] + list_cargos)

        # Aplicar filtros
        df_filtered = df.copy()
        if empresa_selecionada != "Todas":
            df_filtered = df_filtered[df_filtered["empresa"] == empresa_selecionada]
        if cargo_selecionado != "Todos":
            df_filtered = df_filtered[df_filtered["cargo"] == cargo_selecionado]

        if df_filtered.empty:
            st.warning("Nenhum talento corresponde aos filtros selecionados.")
            return

        # KPIs Principais
        total_talentos = len(df_filtered)
        
        # Perfis válidos (excluindo Não Calculado)
        df_valid_perfil = df_filtered[df_filtered["perfil"] != "Não Calculado"]
        perfil_dominante = df_valid_perfil["perfil"].mode().iloc[0] if not df_valid_perfil.empty else "N/A"
        
        # Cobertura IA
        total_ia = df_filtered["ai_diagnosis"].apply(lambda x: bool(x) and str(x).strip() != "").sum()
        pct_ia = (total_ia / total_talentos) * 100 if total_talentos > 0 else 0

        # Empresas Ativas filtradas
        total_empresas = df_filtered["empresa"].nunique()

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
                <div class="kpi-lbl">Empresas Cadastradas</div>
                <div class="kpi-num">""" + str(total_empresas) + """</div>
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
                perfis_counts = df_filtered["perfil"].value_counts().reset_index()
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
                qual_counts = df_filtered["qualidades"].value_counts().reset_index()
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
                # Gráfico 4: Distribuição por Número KAN
                # Limpar KAN para inteiros válidos
                df_kan = df_filtered.copy()
                df_kan["kan_num"] = df_kan["kan"].apply(lambda x: int(x) if str(x).isdigit() else None)
                df_kan = df_kan.dropna(subset=["kan_num"])
                
                if not df_kan.empty:
                    kan_counts = df_kan["kan_num"].value_counts().reset_index()
                    kan_counts.columns = ["KAN", "Quantidade"]
                    kan_counts = kan_counts.sort_values("KAN")
                    
                    fig_kan = px.bar(
                        kan_counts,
                        x="KAN",
                        y="Quantidade",
                        color_discrete_sequence=[color_palette[2]]
                    )
                    fig_kan.update_layout(xaxis=dict(tickmode="linear", dtick=1))
                    apply_dark_layout(fig_kan, "Distribuição por Número KAN")
                    st.plotly_chart(fig_kan, use_container_width=True, config={"displayModeBar": False})
                else:
                    st.info("Dados de KAN insuficientes para gerar a distribuição.")

        st.write("---")
        
        # Tabela Analítica de Detalhes
        st.subheader("📋 Tabela Analítica de Talentos")
        
        # Selecionar e ordenar colunas principais para visualização
        table_df = df_filtered[["nome", "empresa", "cargo", "kan", "perfil", "categoria", "qualidades", "ai_diagnosis"]].copy()
        
        # Formatar a coluna de Diagnóstico de IA para sim/não visual
        table_df["Diagnóstico IA"] = table_df["ai_diagnosis"].apply(lambda x: "✅ Ativo" if bool(x) and str(x).strip() != "" else "❌ Ausente")
        table_df = table_df.drop(columns=["ai_diagnosis"])
        
        # Renomear cabeçalhos
        table_df.columns = ["Nome", "Empresa", "Cargo", "Número KAN", "Perfil Dominante", "Categoria", "Qualidades", "Status Diagnóstico IA"]
        
        # Exibir tabela interativa
        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True
        )
