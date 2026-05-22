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

        # Inicializar dicionário de candidatos e customizações por vaga no session_state
        if "candidatos_vagas" not in st.session_state:
            st.session_state["candidatos_vagas"] = {}
            st.session_state["custom_perfis_vagas"] = {}
            st.session_state["custom_categorias_vagas"] = {}
            st.session_state["custom_qualidades_vagas"] = {}
            st.session_state["custom_kan_vagas"] = {}
            # Carregar as associações e customizações existentes de processos_seletivos do Supabase
            try:
                res_proc = supabase_client.table("processos_seletivos").select("vaga_id, candidatos, perfis_ideais, categorias_ideais, qualidades_ideais, kan_ideal").execute()
                if res_proc and res_proc.data:
                    for r in res_proc.data:
                        v_id = r.get("vaga_id")
                        cands = r.get("candidatos")
                        custom_p = r.get("perfis_ideais")
                        custom_c = r.get("categorias_ideais")
                        custom_q = r.get("qualidades_ideais")
                        custom_k = r.get("kan_ideal")
                        if v_id is not None:
                            try:
                                v_id_int = int(v_id)
                            except:
                                v_id_int = v_id
                            
                            # Candidatos
                            if isinstance(cands, list):
                                st.session_state["candidatos_vagas"][v_id_int] = cands
                            elif isinstance(cands, str):
                                try:
                                    st.session_state["candidatos_vagas"][v_id_int] = json.loads(cands)
                                except:
                                    st.session_state["candidatos_vagas"][v_id_int] = []
                                    
                            # Perfis customizados
                            if custom_p is not None:
                                if isinstance(custom_p, list):
                                    st.session_state["custom_perfis_vagas"][v_id_int] = custom_p
                                elif isinstance(custom_p, str):
                                    try:
                                        st.session_state["custom_perfis_vagas"][v_id_int] = json.loads(custom_p)
                                    except:
                                        st.session_state["custom_perfis_vagas"][v_id_int] = None
                                        
                            # Categorias customizadas
                            if custom_c is not None:
                                if isinstance(custom_c, list):
                                    st.session_state["custom_categorias_vagas"][v_id_int] = custom_c
                                elif isinstance(custom_c, str):
                                    try:
                                        st.session_state["custom_categorias_vagas"][v_id_int] = json.loads(custom_c)
                                    except:
                                        st.session_state["custom_categorias_vagas"][v_id_int] = None
                                        
                            # Qualidades customizadas
                            if custom_q is not None:
                                if isinstance(custom_q, list):
                                    st.session_state["custom_qualidades_vagas"][v_id_int] = custom_q
                                elif isinstance(custom_q, str):
                                    try:
                                        st.session_state["custom_qualidades_vagas"][v_id_int] = json.loads(custom_q)
                                    except:
                                        st.session_state["custom_qualidades_vagas"][v_id_int] = None
                                        
                            # KAN customizado
                            if custom_k is not None:
                                st.session_state["custom_kan_vagas"][v_id_int] = str(custom_k).strip()
            except Exception:
                pass

        if "custom_perfis_vagas" not in st.session_state:
            st.session_state["custom_perfis_vagas"] = {}
        if "custom_categorias_vagas" not in st.session_state:
            st.session_state["custom_categorias_vagas"] = {}
        if "custom_qualidades_vagas" not in st.session_state:
            st.session_state["custom_qualidades_vagas"] = {}
        if "custom_kan_vagas" not in st.session_state:
            st.session_state["custom_kan_vagas"] = {}

        # Verificar se há pedido de exclusão via URL (query params)
        if "excluir_cand" in st.query_params:
            cand_nome = st.query_params["excluir_cand"]
            vaga_id = st.query_params.get("vaga_id")
            if vaga_id:
                try:
                    vaga_id_int = int(vaga_id)
                except:
                    vaga_id_int = vaga_id
                
                if vaga_id_int in st.session_state["candidatos_vagas"]:
                    if cand_nome in st.session_state["candidatos_vagas"][vaga_id_int]:
                        st.session_state["candidatos_vagas"][vaga_id_int].remove(cand_nome)
                        
                        # Atualizar no Supabase
                        new_cands = st.session_state["candidatos_vagas"][vaga_id_int]
                        try:
                            check_ex = supabase_client.table("processos_seletivos").select("id").eq("vaga_id", vaga_id_int).execute()
                            if check_ex and check_ex.data:
                                row_id = check_ex.data[0]["id"]
                                supabase_client.table("processos_seletivos").update({
                                    "candidatos": new_cands,
                                    "updated_at": "now()"
                                }).eq("id", row_id).execute()
                        except Exception:
                            pass
            # Limpar parâmetros específicos de exclusão e recarregar a tela limpa
            del st.query_params["excluir_cand"]
            if "vaga_id" in st.query_params:
                del st.query_params["vaga_id"]
            st.rerun()

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

        # Importar as listas de opções do banco de dados
        from models.database import PERFIS_DB, LISTA_CATEGORIA_DB, QUALIDADES_DB

        # Preparar listas de opções de forma segura
        perfis_opcoes = sorted(list(set([str(x).strip() for x in PERFIS_DB if x])))
        if not perfis_opcoes:
            perfis_opcoes = ["LIDER", "CRIATIVO", "EXECUTOR", "RESULTADO", "VENDEDOR", "INFLUENCIADOR", "COMUNICADOR"]

        categorias_opcoes = sorted(list(set([str(x).strip() for x in LISTA_CATEGORIA_DB if x])))
        if not categorias_opcoes:
            categorias_opcoes = ["VERSÁTIL", "ESPECIALISTA", "GENERALISTA"]

        qualidades_opcoes = sorted(list(set([str(x).strip() for x in QUALIDADES_DB.keys() if x])))
        if not qualidades_opcoes:
            qualidades_opcoes = ["COMUNICAÇÃO", "VERSATILIDADE", "LIDERANÇA", "FOCO", "EMPATIA", "ORGANIZAÇÃO"]

        try:
            vaga_id_int = int(vaga["id"])
        except Exception:
            vaga_id_int = vaga["id"]

        # 1. Determinar Requisitos Ativos (Widget > session_state customizado > original da vaga)
        if f"custom_kan_sel_{vaga_id_int}" in st.session_state:
            raw_kan = st.session_state[f"custom_kan_sel_{vaga_id_int}"]
        elif vaga_id_int in st.session_state.get("custom_kan_vagas", {}) and st.session_state["custom_kan_vagas"][vaga_id_int] is not None:
            raw_kan = st.session_state["custom_kan_vagas"][vaga_id_int]
        else:
            raw_kan = vaga.get('kan_ideal', 'Nenhum')

        kan_opcoes = ["Nenhum / Não Exigido", "Criação", "Movimento", "Finalidade"]
        
        # Mapeamento do KAN para default do selectbox
        raw_kan_clean = str(raw_kan).strip().upper()
        default_kan = "Nenhum / Não Exigido"
        if raw_kan_clean in ("NENHUM", "NENHUM / NÃO EXIGIDO", ""):
            default_kan = "Nenhum / Não Exigido"
        else:
            for opt in kan_opcoes:
                if opt.strip().upper() == raw_kan_clean:
                    default_kan = opt
                    break

        if default_kan == "Nenhum / Não Exigido":
            vaga_kan = "Nenhum"
        else:
            vaga_kan = default_kan

        if f"custom_perfis_sel_{vaga_id_int}" in st.session_state:
            raw_perfis = st.session_state[f"custom_perfis_sel_{vaga_id_int}"]
        elif vaga_id_int in st.session_state.get("custom_perfis_vagas", {}) and st.session_state["custom_perfis_vagas"][vaga_id_int] is not None:
            raw_perfis = st.session_state["custom_perfis_vagas"][vaga_id_int]
        else:
            raw_perfis = parse_json_list(vaga.get('perfis_ideais'))

        if f"custom_categorias_sel_{vaga_id_int}" in st.session_state:
            raw_cats = st.session_state[f"custom_categorias_sel_{vaga_id_int}"]
        elif vaga_id_int in st.session_state.get("custom_categorias_vagas", {}) and st.session_state["custom_categorias_vagas"][vaga_id_int] is not None:
            raw_cats = st.session_state["custom_categorias_vagas"][vaga_id_int]
        else:
            raw_cats = parse_json_list(vaga.get('categorias_ideais'))

        if f"custom_qualidades_sel_{vaga_id_int}" in st.session_state:
            raw_quals = st.session_state[f"custom_qualidades_sel_{vaga_id_int}"]
        elif vaga_id_int in st.session_state.get("custom_qualidades_vagas", {}) and st.session_state["custom_qualidades_vagas"][vaga_id_int] is not None:
            raw_quals = st.session_state["custom_qualidades_vagas"][vaga_id_int]
        else:
            raw_quals = parse_json_list(vaga.get('qualidades_ideais'))

        def map_to_options(requirements, options):
            mapped = []
            opt_map = {opt.strip().upper(): opt for opt in options}
            for req in requirements:
                if not req: continue
                req_upper = str(req).strip().upper()
                if req_upper in opt_map:
                    mapped.append(opt_map[req_upper])
                else:
                    options.append(str(req).strip())
                    opt_map[req_upper] = str(req).strip()
                    mapped.append(str(req).strip())
            return mapped

        # Mapear para obter a capitalização correta dos defaults
        mapped_perfis = map_to_options(raw_perfis, perfis_opcoes)
        mapped_cats = map_to_options(raw_cats, categorias_opcoes)
        mapped_quals = map_to_options(raw_quals, qualidades_opcoes)

        vaga_perfis = [p.upper() for p in mapped_perfis]
        vaga_cats = [c.upper() for c in mapped_cats]
        vaga_quals = [q.upper() for q in mapped_quals]

        # Container visual dos requisitos da Vaga
        with st.container(border=True):
            st.markdown(f"### Requisitos Comportamentais da Vaga: **{vaga['nome_vaga']}**")
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
                with st.expander("Descrição da Vaga", expanded=False):
                    st.write(vaga['descricao_vaga'])
            
            # Painel expansivo de customização de requisitos para este processo
            with st.expander("Personalizar Requisitos Comportamentais para este Processo", expanded=False):
                st.markdown("<p style='font-family: Outfit; font-size: 0.95em;'>Modifique os requisitos específicos para este processo seletivo. Essas alterações afetarão o cálculo de aderência em tempo real e podem ser salvas no banco de dados.</p>", unsafe_allow_html=True)
                
                col_sel1, col_sel2, col_sel3, col_sel4 = st.columns(4)
                with col_sel1:
                    novo_kan = st.selectbox(
                        "KAN Ideal:",
                        options=kan_opcoes,
                        index=kan_opcoes.index(default_kan),
                        key=f"custom_kan_sel_{vaga_id_int}"
                    )
                with col_sel2:
                    novos_perfis = st.multiselect(
                        "Perfis Ideais:",
                        options=perfis_opcoes,
                        default=mapped_perfis,
                        key=f"custom_perfis_sel_{vaga_id_int}"
                    )
                with col_sel3:
                    novas_categorias = st.multiselect(
                        "Categorias:",
                        options=categorias_opcoes,
                        default=mapped_cats,
                        key=f"custom_categorias_sel_{vaga_id_int}"
                    )
                with col_sel4:
                    novas_qualidades = st.multiselect(
                        "Qualidades:",
                        options=qualidades_opcoes,
                        default=mapped_quals,
                        key=f"custom_qualidades_sel_{vaga_id_int}"
                    )

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("Salvar Requisitos do Processo", type="primary", use_container_width=True, key=f"btn_salvar_req_{vaga_id_int}"):
                        st.session_state["custom_perfis_vagas"][vaga_id_int] = novos_perfis
                        st.session_state["custom_categorias_vagas"][vaga_id_int] = novas_categorias
                        st.session_state["custom_qualidades_vagas"][vaga_id_int] = novas_qualidades
                        
                        db_kan_val = "Nenhum" if novo_kan == "Nenhum / Não Exigido" else novo_kan
                        st.session_state["custom_kan_vagas"][vaga_id_int] = db_kan_val
                        
                        try:
                            check_ex = supabase_client.table("processos_seletivos").select("id").eq("vaga_id", vaga_id_int).execute()
                            if check_ex and check_ex.data:
                                row_id = check_ex.data[0]["id"]
                                supabase_client.table("processos_seletivos").update({
                                    "perfis_ideais": novos_perfis,
                                    "categorias_ideais": novas_categorias,
                                    "qualidades_ideais": novas_qualidades,
                                    "kan_ideal": db_kan_val,
                                    "updated_at": "now()"
                                }).eq("id", row_id).execute()
                            else:
                                supabase_client.table("processos_seletivos").insert({
                                    "vaga_id": vaga_id_int,
                                    "empresa": empresa_selecionada,
                                    "candidatos": [],
                                    "perfis_ideais": novos_perfis,
                                    "categorias_ideais": novas_categorias,
                                    "qualidades_ideais": novas_qualidades,
                                    "kan_ideal": db_kan_val
                                }).execute()
                            st.success("Requisitos personalizados salvos com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar requisitos personalizados no Supabase: {e}")
                with col_btn2:
                    if st.button("Restaurar Originais da Vaga", use_container_width=True, key=f"btn_restaurar_req_{vaga_id_int}"):
                        st.session_state["custom_perfis_vagas"][vaga_id_int] = None
                        st.session_state["custom_categorias_vagas"][vaga_id_int] = None
                        st.session_state["custom_qualidades_vagas"][vaga_id_int] = None
                        st.session_state["custom_kan_vagas"][vaga_id_int] = None
                        
                        if f"custom_perfis_sel_{vaga_id_int}" in st.session_state:
                            del st.session_state[f"custom_perfis_sel_{vaga_id_int}"]
                        if f"custom_categorias_sel_{vaga_id_int}" in st.session_state:
                            del st.session_state[f"custom_categorias_sel_{vaga_id_int}"]
                        if f"custom_qualidades_sel_{vaga_id_int}" in st.session_state:
                            del st.session_state[f"custom_qualidades_sel_{vaga_id_int}"]
                        if f"custom_kan_sel_{vaga_id_int}" in st.session_state:
                            del st.session_state[f"custom_kan_sel_{vaga_id_int}"]
                            
                        try:
                            check_ex = supabase_client.table("processos_seletivos").select("id").eq("vaga_id", vaga_id_int).execute()
                            if check_ex and check_ex.data:
                                row_id = check_ex.data[0]["id"]
                                supabase_client.table("processos_seletivos").update({
                                    "perfis_ideais": None,
                                    "categorias_ideais": None,
                                    "qualidades_ideais": None,
                                    "kan_ideal": None,
                                    "updated_at": "now()"
                                }).eq("id", row_id).execute()
                            st.success("Requisitos restaurados para os originais da vaga!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao restaurar requisitos no Supabase: {e}")

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
                "Empresa": info["empresa"],
                "Aderência (%)": round(total_score, 1),
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
            st.info("Nenhum talento cadastrado no sistema para realizar o matching.")
            return

        # -------------------------------------------------------------------------
        # SEÇÃO: CANDIDATOS ASSOCIADOS AO PROCESSO
        # -------------------------------------------------------------------------
        if "mostrar_selector_talentos" not in st.session_state:
            st.session_state["mostrar_selector_talentos"] = False

        st.write("---")
        col_sec_title, col_sec_btn = st.columns([3, 1])
        with col_sec_title:
            st.subheader("Candidatos Associados ao Processo")
        with col_sec_btn:
            if st.button("Associar Talentos", key="btn_toggle_assoc", use_container_width=True):
                st.session_state["mostrar_selector_talentos"] = True

        # Renderizar seletor de associação
        if st.session_state["mostrar_selector_talentos"]:
            with st.container(border=True):
                st.markdown("#### Selecionar Talentos para o Processo")
                # Mostrar todos os talentos cadastrados no sistema
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
                        
                        # Salvar/Atualizar no Supabase na tabela processos_seletivos
                        try:
                            check_ex = supabase_client.table("processos_seletivos").select("id").eq("vaga_id", vaga["id"]).execute()
                            if check_ex and check_ex.data:
                                row_id = check_ex.data[0]["id"]
                                supabase_client.table("processos_seletivos").update({
                                    "candidatos": candidatos_selecionados,
                                    "empresa": empresa_selecionada,
                                    "updated_at": "now()"
                                }).eq("id", row_id).execute()
                            else:
                                supabase_client.table("processos_seletivos").insert({
                                    "vaga_id": vaga["id"],
                                    "empresa": empresa_selecionada,
                                    "candidatos": candidatos_selecionados
                                }).execute()
                        except Exception as e:
                            # Caso a tabela ainda não exista no Supabase do usuário, mostramos um aviso útil
                            st.warning(f"Não foi possível salvar no Supabase (certifique-se de executar o arquivo 'processos_seletivos_schema.sql' no seu painel Supabase): {e}")
                        
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
                        # Gerar HTML do avatar/foto crop (sem indentação inicial nas linhas para evitar que o markdown interprete como bloco de código)
                        if cand["foto_base64"]:
                            avatar_html = f'<div style="display: flex; justify-content: center; margin-bottom: 12px;"><img src="data:image/png;base64,{cand["foto_base64"]}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 2px solid #F18617; box-shadow: 0 4px 10px rgba(0,0,0,0.3);"></div>'
                        else:
                            avatar_html = f'<div style="display: flex; justify-content: center; margin-bottom: 12px;"><div style="width: 100px; height: 100px; border-radius: 50%; background: linear-gradient(135deg, #F18617, #9333EA); display: flex; align-items: center; justify-content: center; font-size: 2.2em; font-weight: bold; color: white; border: 2px solid rgba(255,255,255,0.1); box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-family: Outfit;">{cand["Nome"][0].upper()}</div></div>'
                            
                        card_html = f"""<div class="candidato-card" style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 20px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.25); backdrop-filter: blur(10px); margin-bottom: 20px; font-family: Outfit, sans-serif; position: relative;">
<a href="?excluir_cand={cand['Nome']}&vaga_id={vaga['id']}" target="_self" style="position: absolute; top: 15px; right: 15px; background-color: #F18617; color: #7C3AED; border: none; border-radius: 50%; width: 22px; height: 22px; text-decoration: none; font-size: 13px; font-weight: 800; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 5px rgba(0,0,0,0.3); z-index: 1000; line-height: 1;">x</a>
{avatar_html}
<h4 style="margin: 10px 0 2px 0; color: #FFFFFF; font-size: 1.15em; font-weight: 700; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">{cand['Nome']}</h4>
<p style="margin: 0 0 15px 0; color: rgba(255, 255, 255, 0.5); font-size: 0.8em;">📅 {cand['data_nascimento']}</p>
<div style="text-align: left; font-size: 0.85em; line-height: 1.5; color: rgba(255, 255, 255, 0.8); border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 12px; margin-bottom: 15px;">
<div style="margin-bottom: 4px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;"><strong>KAN:</strong> <span style="color: #F18617;">{cand['kan']}</span></div>
<div style="margin-bottom: 4px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;"><strong>Perfil:</strong> {cand['perfil']}</div>
<div style="margin-bottom: 4px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;"><strong>Categoria:</strong> {cand['categoria']}</div>
<div style="text-overflow: ellipsis; overflow: hidden; white-space: nowrap;"><strong>Qualidades:</strong> {cand['qualidades']}</div>
</div>
<div style="background: rgba(241, 134, 23, 0.1); border: 1px solid rgba(241, 134, 23, 0.2); border-radius: 8px; padding: 8px; color: #F18617; font-weight: 700; font-size: 1em;">
🎯 {cand['total_pts']} Pontos
<div style="font-size: 0.65em; font-weight: 400; color: rgba(255,255,255,0.6); margin-top: 2px;">
KAN: {cand['pts_kan']} | Perf: {cand['pts_perfil']} | Qual: {cand['pts_qual']}
</div>
</div>
</div>"""
                        st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.info("Nenhum talento associado a este processo seletivo ainda. Clique em 'Associar Talentos' acima para selecionar participantes.")

        # Ordenar por aderência
        df_matching = pd.DataFrame(matching_results).sort_values(by="Aderência (%)", ascending=False)
        
        # -------------------------------------------------------------------------
        # TABELAS GERAIS E COMPARATIVOS
        # -------------------------------------------------------------------------
        st.write("---")
        st.subheader(f"Ranking Geral de Aderência (Todos os Talentos de {empresa_selecionada})")
        
        # Filtrar o ranking geral pela empresa selecionada
        df_matching_empresa = df_matching[df_matching["Empresa"] == empresa_selecionada]
        
        if not df_matching_empresa.empty:
            df_display = df_matching_empresa.drop(columns=["talento_detalhes", "foto_base64", "data_nascimento", "Empresa"])
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info(f"Nenhum talento cadastrado originalmente na empresa {empresa_selecionada}. No entanto, você ainda pode associar livremente talentos de outras empresas ao processo usando o botão acima!")

        st.write("---")
        st.subheader("Comparativo Detalhado Side-by-Side")
        
        selected_talent_nome = st.selectbox("Selecione um talento para visualizar o comparativo detalhado:", options=df_matching["Nome"].tolist(), key="select_side_by_side_talent")
        
        talent_row = df_matching[df_matching["Nome"] == selected_talent_nome].iloc[0]
        talento_detalhes = talent_row["talento_detalhes"]

        col_comp1, col_comp2 = st.columns(2)
        
        with col_comp1:
            with st.container(border=True):
                st.markdown(f"#### Requisitos da Vaga\n**{vaga_selecionada_nome}**")
                st.write(f"**KAN Exigido:** `{vaga_kan.upper()}`")
                st.write(f"**Perfis Exigidos:** `{', '.join(vaga_perfis) if vaga_perfis else 'Nenhum'}`")
                st.write(f"**Categorias Exigidas:** `{', '.join(vaga_cats) if vaga_cats else 'Nenhuma'}`")
                st.write(f"**Qualidades Exigidas:** `{', '.join(vaga_quals) if vaga_quals else 'Nenhuma'}`")

        with col_comp2:
            with st.container(border=True):
                st.markdown(f"#### Perfil do Talento\n**{selected_talent_nome}**")
                st.write(f"**KAN do Talento:** `{talento_detalhes['kan']}`")
                st.write(f"**Perfis do Talento:** `{', '.join(talento_detalhes['perfis']) if talento_detalhes['perfis'] else 'Nenhum'}`")
                st.write(f"**Categorias do Talento:** `{', '.join(talento_detalhes['categorias']) if talento_detalhes['categorias'] else 'Nenhuma'}`")
                st.write(f"**Qualidades do Talento:** `{', '.join(talento_detalhes['qualidades']) if talento_detalhes['qualidades'] else 'Nenhuma'}`")

        # Barra de progresso de aderência
        aderencia_percent = talent_row["Aderência (%)"]
        st.markdown(f"### Aderência Geral: **{aderencia_percent}%**")
        st.progress(max(0, min(100, int(aderencia_percent))))
