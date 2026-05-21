import streamlit as st
import pandas as pd
import json
from menus.base_menu import BaseMenu
from models.database import carregar_empresas, get_supabase_admin
from utils.helpers import remover_acentos

class ProcessoSeletivoAnaliseMenu(BaseMenu):
    def render(self):
        st.title("Processo Seletivo (Análise de Matching)")
        st.markdown("<p style='font-size: 1.15em; color: rgba(255,255,255,0.7); margin-bottom: 20px; font-family: Outfit;'>Compare a aderência comportamental dos talentos cadastrados em relação aos perfis de vagas definidos.</p>", unsafe_allow_html=True)
        st.write("---")

        supabase_client = get_supabase_admin()
        if not supabase_client:
            st.error("Conexão administrativa do Supabase não configurada.")
            return

        # Inicializar dicionário de candidatos por vaga no session_state
        if "candidatos_vagas" not in st.session_state:
            st.session_state["candidatos_vagas"] = {}

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
            res_ms = supabase_client.table("mapas_salvos").select("nome, empresa, cargo, data_nascimento, foto_base64").execute()
            rows_ms = res_ms.data if res_ms and res_ms.data else []
        except Exception as e:
            st.error(f"Erro ao carregar talentos da base de dados: {e}")
            return

        if not rows_val:
            st.warning("Nenhum mapa calculado na base. Calcule os mapas salvos no Painel de Controle antes de realizar a análise.")
            return

        # Dicionário de cargos/empresas/fotos/datas
        ms_dict = {}
        for r in rows_ms:
            ms_dict[r.get("nome")] = {
                "empresa": r.get("empresa") or "Sem Empresa",
                "cargo": r.get("cargo") or "Sem Cargo",
                "data_nascimento": r.get("data_nascimento") or "",
                "foto_base64": r.get("foto_base64") or ""
            }

        # Calcular scores
        matching_results = []
        for row in rows_val:
            nome = row.get("nome", "Desconhecido")
            info = ms_dict.get(nome, {"empresa": "Sem Empresa", "cargo": "Sem Cargo", "data_nascimento": "", "foto_base64": ""})
            
            # Filtro por empresa do talento
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
            elif remover_acentos(talento_kan).upper().strip() == remover_acentos(vaga_kan).upper().strip():
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
                "Aderência (%)": round(total_score * 4, 1),
                "KAN": kan_status,
                "Perfil": perfil_status,
                "Categoria": cat_status,
                "Qualidades": qual_status,
                "data_nascimento": info["data_nascimento"],
                "foto_base64": info["foto_base64"],
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

        # -------------------------------------------------------------------------
        # SEÇÃO: CANDIDATOS ASSOCIADOS AO PROCESSO
        # -------------------------------------------------------------------------
        if "mostrar_selector_talentos" not in st.session_state:
            st.session_state["mostrar_selector_talentos"] = False

        st.write("---")
        col_sec_title, col_sec_btn = st.columns([3, 1])
        with col_sec_title:
            st.subheader("👥 Candidatos Associados ao Processo")
        with col_sec_btn:
            if st.button("➕ Associar Talentos", key="btn_toggle_assoc", use_container_width=True):
                st.session_state["mostrar_selector_talentos"] = True

        # Renderizar seletor de associação
        if st.session_state["mostrar_selector_talentos"]:
            with st.container(border=True):
                st.markdown("#### Selecionar Talentos para o Processo")
                opcoes_talentos = sorted([r["Nome"] for r in matching_results])
                
                candidatos_selecionados = st.multiselect(
                    "Selecione os talentos que participarão deste processo:",
                    options=opcoes_talentos,
                    default=st.session_state["candidatos_vagas"].get(vaga["id"], []),
                    key="selector_talentos_multiselect"
                )
                
                col_actions1, col_actions2 = st.columns(2)
                with col_actions1:
                    if st.button("Salvar Associação", type="primary", use_container_width=True, key="btn_salvar_assoc"):
                        st.session_state["candidatos_vagas"][vaga["id"]] = candidatos_selecionados
                        st.session_state["mostrar_selector_talentos"] = False
                        st.success("Candidatos associados com sucesso!")
                        st.rerun()
                with col_actions2:
                    if st.button("Cancelar", use_container_width=True, key="btn_cancelar_assoc"):
                        st.session_state["mostrar_selector_talentos"] = False
                        st.rerun()

        # Renderizar os Cards dos Candidatos Associados
        associated_names = st.session_state["candidatos_vagas"].get(vaga["id"], [])
        
        if associated_names:
            candidatos_processo = []
            for r in matching_results:
                if r["Nome"] in associated_names:
                    t_kan = r["talento_detalhes"]["kan"]
                    t_perfis = r["talento_detalhes"]["perfis"]
                    t_quals = r["talento_detalhes"]["qualidades"]
                    t_cats = r["talento_detalhes"]["categorias"]
                    
                    # 1. KAN Match (3 pts)
                    pts_kan = 0
                    if vaga_kan and vaga_kan.upper() not in ("NENHUM", "NENHUM / NÃO EXIGIDO", ""):
                        if remover_acentos(t_kan).upper().strip() == remover_acentos(vaga_kan).upper().strip():
                            pts_kan = 3
                            
                    # 2. Perfil Match (2 pts por match)
                    pts_perfil = 0
                    if vaga_perfis:
                        vaga_perfis_norm = [remover_acentos(p).upper().strip() for p in vaga_perfis]
                        talento_perfis_norm = [remover_acentos(p).upper().strip() for p in t_perfis]
                        perfis_intersect = set(vaga_perfis_norm).intersection(set(talento_perfis_norm))
                        pts_perfil = 2 * len(perfis_intersect)
                        
                    # 3. Qualidades Match (1 pt por match)
                    pts_qual = 0
                    if vaga_quals:
                        vaga_quals_norm = [remover_acentos(q).upper().strip() for q in vaga_quals]
                        talento_quals_norm = [remover_acentos(q).upper().strip() for q in t_quals]
                        quals_intersect = set(vaga_quals_norm).intersection(set(talento_quals_norm))
                        pts_qual = 1 * len(quals_intersect)
                        
                    total_pts = pts_kan + pts_perfil + pts_qual
                    
                    candidatos_processo.append({
                        "Nome": r["Nome"],
                        "data_nascimento": r["data_nascimento"],
                        "foto_base64": r["foto_base64"],
                        "kan": t_kan,
                        "perfil": ", ".join(t_perfis),
                        "categoria": ", ".join(t_cats),
                        "qualidades": ", ".join(t_quals),
                        "pts_kan": pts_kan,
                        "pts_perfil": pts_perfil,
                        "pts_qual": pts_qual,
                        "total_pts": total_pts
                    })
                    
            # Ordenar por pontuação descendente
            candidatos_processo = sorted(candidatos_processo, key=lambda x: x["total_pts"], reverse=True)
            
            # Exibir cards lado a lado com tamanho uniforme
            cards_per_row = 3
            for i in range(0, len(candidatos_processo), cards_per_row):
                chunk = candidatos_processo[i:i + cards_per_row]
                cols = st.columns(cards_per_row)
                for idx, cand in enumerate(chunk):
                    with cols[idx]:
                        # Gerar HTML do avatar/foto crop
                        if cand["foto_base64"]:
                            avatar_html = f"""
                            <div style="display: flex; justify-content: center; margin-bottom: 12px;">
                                <img src="data:image/png;base64,{cand['foto_base64']}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 2px solid #F18617; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
                            </div>
                            """
                        else:
                            avatar_html = f"""
                            <div style="display: flex; justify-content: center; margin-bottom: 12px;">
                                <div style="width: 100px; height: 100px; border-radius: 50%; background: linear-gradient(135deg, #F18617, #9333EA); display: flex; align-items: center; justify-content: center; font-size: 2.2em; font-weight: bold; color: white; border: 2px solid rgba(255,255,255,0.1); box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-family: Outfit;">
                                    {cand['Nome'][0].upper()}
                                </div>
                            </div>
                            """
                            
                        card_html = f"""
                        <div style="
                            background: rgba(255, 255, 255, 0.04);
                            border: 1px solid rgba(255, 255, 255, 0.08);
                            border-radius: 16px;
                            padding: 20px;
                            text-align: center;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.25);
                            backdrop-filter: blur(10px);
                            margin-bottom: 20px;
                            font-family: Outfit, sans-serif;
                        ">
                            {avatar_html}
                            <h4 style="margin: 10px 0 2px 0; color: #FFFFFF; font-size: 1.15em; font-weight: 700; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">{cand['Nome']}</h4>
                            <p style="margin: 0 0 15px 0; color: rgba(255, 255, 255, 0.5); font-size: 0.8em;">📅 {cand['data_nascimento']}</p>
                            
                            <div style="text-align: left; font-size: 0.85em; line-height: 1.5; color: rgba(255, 255, 255, 0.8); border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 12px; margin-bottom: 15px;">
                                <div style="margin-bottom: 4px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;"><strong>KAN:</strong> <span style="color: #F18617;">{cand['kan']}</span></div>
                                <div style="margin-bottom: 4px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;"><strong>Perfil:</strong> {cand['perfil']}</div>
                                <div style="margin-bottom: 4px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;"><strong>Categoria:</strong> {cand['categoria']}</div>
                                <div style="text-overflow: ellipsis; overflow: hidden; white-space: nowrap;"><strong>Qualidades:</strong> {cand['qualidades']}</div>
                            </div>
                            
                            <div style="
                                background: rgba(241, 134, 23, 0.1);
                                border: 1px solid rgba(241, 134, 23, 0.2);
                                border-radius: 8px;
                                padding: 8px;
                                color: #F18617;
                                font-weight: 700;
                                font-size: 1em;
                            ">
                                🎯 {cand['total_pts']} Pontos
                                <div style="font-size: 0.65em; font-weight: 400; color: rgba(255,255,255,0.6); margin-top: 2px;">
                                    KAN: {cand['pts_kan']} | Perf: {cand['pts_perfil']} | Qual: {cand['pts_qual']}
                                </div>
                            </div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.info("Nenhum talento associado a este processo seletivo ainda. Clique em '➕ Associar Talentos' acima para selecionar participantes.")

        # Ordenar por aderência
        df_matching = pd.DataFrame(matching_results).sort_values(by="Aderência (%)", ascending=False)
        
        # -------------------------------------------------------------------------
        # TABELAS GERAIS E COMPARATIVOS
        # -------------------------------------------------------------------------
        st.write("---")
        st.subheader("📊 Ranking Geral de Aderência (Todos os Talentos da Empresa)")
        
        df_display = df_matching.drop(columns=["talento_detalhes", "foto_base64", "data_nascimento"])
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.write("---")
        st.subheader("🔍 Comparativo Detalhado Side-by-Side")
        
        selected_talent_nome = st.selectbox("Selecione um talento para visualizar o comparativo detalhado:", options=df_matching["Nome"].tolist(), key="select_side_by_side_talent")
        
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
