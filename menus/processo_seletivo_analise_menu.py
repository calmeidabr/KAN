import streamlit as st
import pandas as pd
import json
from menus.base_menu import BaseMenu
from models.database import carregar_empresas, get_supabase_admin

class ProcessoSeletivoAnaliseMenu(BaseMenu):
    def render(self):
        st.title("Processo Seletivo (Análise de Matching)")
        st.markdown("<p style='font-size: 1.15em; color: rgba(255,255,255,0.7); margin-bottom: 20px; font-family: Outfit;'>Compare a aderência comportamental dos talentos cadastrados em relação aos perfis de vagas definidos.</p>", unsafe_allow_html=True)
        st.write("---")

        supabase_client = get_supabase_admin()
        if not supabase_client:
            st.error("Conexão administrativa do Supabase não configurada.")
            return

        # Carregar empresas cadastradas
        lista_empresas_salvas = carregar_empresas()
        nomes_empresas = [e["nome_empresa"] for e in lista_empresas_salvas if e.get("nome_empresa")]
        if not nomes_empresas:
            nomes_empresas = ["Mundo KAN"]

        col_filtro1, col_filtro2 = st.columns([1, 1])
        with col_filtro1:
            empresa_selecionada = st.selectbox("Selecione a Empresa:", options=nomes_empresas, key="analise_proc_emp_sel")

        # Buscar vagas cadastradas da empresa
        try:
            res_vagas = supabase_client.table("vagas").select("*").eq("empresa", empresa_selecionada).order("created_at", desc=True).execute()
            vagas_list = res_vagas.data if res_vagas and res_vagas.data else []
        except Exception as e:
            st.error(f"Erro ao carregar vagas: {e}")
            return

        if not vagas_list:
            st.info(f"Nenhuma vaga cadastrada para a empresa {empresa_selecionada}. Cadastre vagas no menu Vagas antes de realizar a análise.")
            return

        # Dicionário de vagas
        vagas_dict = {f"{v['nome_vaga']} ({v['senioridade']})": v for v in vagas_list}
        with col_filtro2:
            vaga_selecionada_nome = st.selectbox("Selecione a Vaga para Análise:", options=list(vagas_dict.keys()), key="analise_proc_vaga_sel")

        vaga = vagas_dict[vaga_selecionada_nome]

        # Parsing de requisitos da vaga
        def parse_json_list(val):
            if not val: return []
            if isinstance(val, list): return val
            try: return json.loads(val)
            except Exception: return []

        vaga_kan = str(vaga.get('kan_ideal', 'Nenhum')).strip()
        vaga_perfis = [str(x).strip().upper() for x in parse_json_list(vaga.get('perfis_ideais'))]
        vaga_cats = [str(x).strip().upper() for x in parse_json_list(vaga.get('categorias_ideais'))]
        vaga_quals = [str(x).strip().upper() for x in parse_json_list(vaga.get('qualidades_ideais'))]

        # Container visual dos requisitos da Vaga
        with st.container(border=True):
            st.markdown(f"### 📋 Requisitos Comportamentais da Vaga: **{vaga['nome_vaga']}**")
            col_r1, col_r2, col_r3, col_r4 = st.columns(4)
            with col_r1:
                st.markdown(f"**KAN Ideal**\n\n`{vaga_kan.upper()}`")
            with col_r2:
                perfis_str = ", ".join(vaga_perfis) if vaga_perfis else "Nenhum exigido"
                st.markdown(f"**Perfis Ideais**\n\n`{perfis_str}`")
            with col_r3:
                cats_str = ", ".join(vaga_cats) if vaga_cats else "Nenhuma exigida"
                st.markdown(f"**Categorias**\n\n`{cats_str}`")
            with col_r4:
                quals_str = ", ".join(vaga_quals) if vaga_quals else "Nenhuma exigida"
                st.markdown(f"**Qualidades**\n\n`{quals_str}`")
            if vaga.get('descricao_vaga'):
                st.markdown(f"**Descrição:** {vaga['descricao_vaga']}")

        # Buscar talentos (candidatos) para fazer o matching
        try:
            res_val = supabase_client.table("mapas_salvos_valores").select("*").execute()
            rows_val = res_val.data if res_val and res_val.data else []
            res_ms = supabase_client.table("mapas_salvos").select("nome, empresa, cargo").execute()
            rows_ms = res_ms.data if res_ms and res_ms.data else []
        except Exception as e:
            st.error(f"Erro ao carregar talentos da base de dados: {e}")
            return

        if not rows_val:
            st.warning("Nenhum mapa calculado na base. Calcule os mapas salvos no Painel de Controle antes de realizar a análise.")
            return

        # Dicionário de cargos/empresas
        ms_dict = {}
        for r in rows_ms:
            ms_dict[r.get("nome")] = {
                "empresa": r.get("empresa") or "Sem Empresa",
                "cargo": r.get("cargo") or "Sem Cargo"
            }

        # Calcular scores
        matching_results = []
        for row in rows_val:
            nome = row.get("nome", "Desconhecido")
            info = ms_dict.get(nome, {"empresa": "Sem Empresa", "cargo": "Sem Cargo"})
            
            # Filtro por empresa do talento (opcional: ou mostrar todos os talentos da empresa selecionada)
            if info["empresa"] != empresa_selecionada:
                continue

            # Traços do talento
            talento_kan = str(row.get("kan", "")).strip().upper()
            talento_perfis = [str(x).strip().upper() for x in str(row.get("perfil", "")).split(",") if x.strip()]
            talento_cats = [str(x).strip().upper() for x in str(row.get("categoria", "")).split(",") if x.strip()]
            talento_quals = [str(x).strip().upper() for x in str(row.get("qualidades", "")).split(",") if x.strip()]

            # 1. KAN Match (25%)
            if vaga_kan in ("Nenhum", "Nenhum / Não Exigido", ""):
                kan_score = 25.0
                kan_status = "✓ N/A"
            elif talento_kan == vaga_kan.upper():
                kan_score = 25.0
                kan_status = "✓ Compatível"
            else:
                kan_score = 0.0
                kan_status = "✗ Incompatível"

            # 2. Perfis Match (25%)
            if not vaga_perfis:
                perfil_score = 25.0
                perfil_status = "✓ N/A"
            else:
                perfis_intersec = set(vaga_perfis).intersection(set(talento_perfis))
                prop = len(perfis_intersec) / len(vaga_perfis)
                perfil_score = 25.0 * prop
                perfil_status = f"{len(perfis_intersec)}/{len(vaga_perfis)} compatíveis" if perfis_intersec else "✗ Incompatível"

            # 3. Categorias Match (25%)
            if not vaga_cats:
                cat_score = 25.0
                cat_status = "✓ N/A"
            else:
                cats_intersec = set(vaga_cats).intersection(set(talento_cats))
                prop = len(cats_intersec) / len(vaga_cats)
                cat_score = 25.0 * prop
                cat_status = f"{len(cats_intersec)}/{len(vaga_cats)} compatíveis" if cats_intersec else "✗ Incompatível"

            # 4. Qualidades Match (25%)
            if not vaga_quals:
                qual_score = 25.0
                qual_status = "✓ N/A"
            else:
                quals_intersec = set(vaga_quals).intersection(set(talento_quals))
                prop = len(quals_intersec) / len(vaga_quals)
                qual_score = 25.0 * prop
                qual_status = f"{len(quals_intersec)}/{len(vaga_quals)} compatíveis" if quals_intersec else "✗ Incompatível"

            total_score = kan_score + perfil_score + cat_score + qual_score

            matching_results.append({
                "Nome": nome,
                "Cargo Atual": info["cargo"],
                "Aderência (%)": round(total_score * 4, 1), # Multiplicado por 4 para ir de 0 a 100% (25% * 4 = 100%)
                "KAN": kan_status,
                "Perfil": perfil_status,
                "Categoria": cat_status,
                "Qualidades": qual_status,
                "talento_detalhes": {
                    "kan": talento_kan,
                    "perfis": talento_perfis,
                    "categorias": talento_cats,
                    "qualidades": talento_quals
                }
            })

        if not matching_results:
            st.info(f"Nenhum talento cadastrado na empresa {empresa_selecionada} para realizar o matching.")
            return

        # Ordenar por aderência
        df_matching = pd.DataFrame(matching_results).sort_values(by="Aderência (%)", ascending=False)
        
        # Exibir a Tabela de Matching
        st.subheader("📊 Ranking de Aderência dos Talentos")
        
        # Formatando a exibição do DataFrame
        df_display = df_matching.drop(columns=["talento_detalhes"])
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.write("---")
        st.subheader("🔍 Comparativo Detalhado Side-by-Side")
        
        selected_talent_nome = st.selectbox("Selecione um talento para visualizar o comparativo detalhado:", options=df_matching["Nome"].tolist())
        
        talent_row = df_matching[df_matching["Nome"] == selected_talent_nome].iloc[0]
        talento_detalhes = talent_row["talento_detalhes"]

        col_comp1, col_comp2 = st.columns(2)
        
        with col_comp1:
            with st.container(border=True):
                st.markdown(f"#### 💼 Requisitos da Vaga\n**{vaga_selecionada_nome}**")
                st.write(f"**KAN Exigido:** `{vaga_kan.upper()}`")
                st.write(f"**Perfis Exigidos:** `{', '.join(vaga_perfis) if vaga_perfis else 'Nenhum'}`")
                st.write(f"**Categorias Exigidas:** `{', '.join(vaga_cats) if vaga_cats else 'Nenhuma'}`")
                st.write(f"**Qualidades Exigidas:** `{', '.join(vaga_quals) if vaga_quals else 'Nenhuma'}`")

        with col_comp2:
            with st.container(border=True):
                st.markdown(f"#### 👤 Perfil do Talento\n**{selected_talent_nome}**")
                st.write(f"**KAN do Talento:** `{talento_detalhes['kan']}`")
                st.write(f"**Perfis do Talento:** `{', '.join(talento_detalhes['perfis']) if talento_detalhes['perfis'] else 'Nenhum'}`")
                st.write(f"**Categorias do Talento:** `{', '.join(talento_detalhes['categorias']) if talento_detalhes['categorias'] else 'Nenhuma'}`")
                st.write(f"**Qualidades do Talento:** `{', '.join(talento_detalhes['qualidades']) if talento_detalhes['qualidades'] else 'Nenhuma'}`")

        # Barra de progresso de aderência
        aderencia_percent = talent_row["Aderência (%)"]
        st.markdown(f"### Aderência Geral: **{aderencia_percent}%**")
        st.progress(int(aderencia_percent))
