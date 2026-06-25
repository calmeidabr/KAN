import streamlit as st
import pandas as pd
import json
import google.generativeai as genai
from menus.base_menu import BaseMenu
from models.database import carregar_empresas, get_supabase_admin, carregar_equipes
from utils.helpers import remover_acentos, format_vaga_title, converter_markdown_para_html
from services.harmonia import calcular_harmonia_trio, obter_vertices_triangulo
from utils.graphics import gerar_svg_triangulos_harmonicos

class ProcessoSeletivoAnaliseMenu(BaseMenu):
    def render(self):
        supabase_client = get_supabase_admin()
        if not supabase_client:
            st.error("Conexão administrativa do banco de dados não configurada.")
            return

        st.markdown("<h2 style='text-align: left; margin-bottom: 5px;'>Processo Seletivo</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.1em; color: rgba(255,255,255,0.7); margin-bottom: 20px;'>Análise comportamental inteligente e matching de talentos.</p>", unsafe_allow_html=True)

        # Verificar se há empresas cadastradas
        lista_empresas_salvas = carregar_empresas()
        nomes_empresas = [e["nome_empresa"] for e in lista_empresas_salvas if e.get("nome_empresa")]
        if not nomes_empresas:
            st.info("Nenhuma empresa cadastrada no sistema. Por favor, cadastre uma empresa no menu **Hierarquia / Deptos** antes de gerenciar os processos seletivos.")
            return

        # Inicializar dicionário de candidatos e customizações por vaga no session_state
        if "candidatos_vagas" not in st.session_state:
            st.session_state["candidatos_vagas"] = {}
            st.session_state["custom_perfis_vagas"] = {}
            st.session_state["custom_categorias_vagas"] = {}
            st.session_state["custom_qualidades_vagas"] = {}
            st.session_state["custom_kan_vagas"] = {}
            st.session_state["equipes_vagas"] = {}
            st.session_state["historico_harmonia_vagas"] = {}
            # Carregar as associações e customizações existentes de processos_seletivos do Supabase
            try:
                try:
                    res_proc = supabase_client.table("processos_seletivos").select("vaga_id, candidatos, perfis_ideais, categorias_ideais, qualidades_ideais, kan_ideal, equipe, historico_harmonia").execute()
                except Exception:
                    res_proc = supabase_client.table("processos_seletivos").select("vaga_id, candidatos, perfis_ideais, categorias_ideais, qualidades_ideais, kan_ideal").execute()
                
                if res_proc and res_proc.data:
                    for r in res_proc.data:
                        v_id = r.get("vaga_id")
                        cands = r.get("candidatos")
                        custom_p = r.get("perfis_ideais")
                        custom_c = r.get("categorias_ideais")
                        custom_q = r.get("qualidades_ideais")
                        custom_k = r.get("kan_ideal")
                        eq_nome = r.get("equipe")
                        hist_harm = r.get("historico_harmonia", [])
                        
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
                                    
                            # Equipe e historico de harmonia
                            st.session_state["equipes_vagas"][v_id_int] = eq_nome
                            st.session_state["historico_harmonia_vagas"][v_id_int] = hist_harm if isinstance(hist_harm, list) else []
                                    
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
                                if isinstance(custom_k, list):
                                    st.session_state["custom_kan_vagas"][v_id_int] = custom_k
                                elif isinstance(custom_k, str):
                                    try:
                                        st.session_state["custom_kan_vagas"][v_id_int] = json.loads(custom_k)
                                    except:
                                        if "," in custom_k:
                                            st.session_state["custom_kan_vagas"][v_id_int] = [x.strip() for x in custom_k.split(",")]
                                        else:
                                            st.session_state["custom_kan_vagas"][v_id_int] = [custom_k.strip()]
            except Exception:
                pass

        if "custom_perfis_vagas" not in st.session_state:
            st.session_state["custom_perfis_vagas"] = {}
        if "custom_categorias_vagas" not in st.session_state:
            st.session_state["custom_categorias_vagas"] = {}
        if "equipes_vagas" not in st.session_state:
            st.session_state["equipes_vagas"] = {}
        if "historico_harmonia_vagas" not in st.session_state:
            st.session_state["historico_harmonia_vagas"] = {}
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
                
                # Manter a vaga ativa selecionada
                try:
                    res_v = supabase_client.table("vagas").select("nome_vaga, senioridade").eq("id", vaga_id_int).execute()
                    if res_v and res_v.data:
                        v_info = res_v.data[0]
                        st.session_state["analise_proc_vaga_sel"] = f"{v_info['nome_vaga']} ({v_info['senioridade']})"
                except Exception:
                    pass
                
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
                        except Exception as e:
                            import traceback
                            st.error(f"Erro ao salvar exclusão no banco de dados para vaga {vaga_id_int}: {e}")
                            st.text(traceback.format_exc())
                            st.stop()
            # Limpar parâmetros específicos de exclusão e recarregar a tela limpa
            del st.query_params["excluir_cand"]
            if "vaga_id" in st.query_params:
                del st.query_params["vaga_id"]
            st.rerun()

        # Verificar se há pedido de associação via URL (query params)
        if "assoc_cand" in st.query_params:
            cand_nome = st.query_params["assoc_cand"]
            vaga_id = st.query_params.get("vaga_id")
            if vaga_id:
                try:
                    vaga_id_int = int(vaga_id)
                except:
                    vaga_id_int = vaga_id
                
                # Manter a vaga ativa selecionada
                try:
                    res_v = supabase_client.table("vagas").select("nome_vaga, senioridade").eq("id", vaga_id_int).execute()
                    if res_v and res_v.data:
                        v_info = res_v.data[0]
                        st.session_state["analise_proc_vaga_sel"] = f"{v_info['nome_vaga']} ({v_info['senioridade']})"
                except Exception:
                    pass
                
                if vaga_id_int not in st.session_state["candidatos_vagas"]:
                    st.session_state["candidatos_vagas"][vaga_id_int] = []
                if cand_nome not in st.session_state["candidatos_vagas"][vaga_id_int]:
                    st.session_state["candidatos_vagas"][vaga_id_int].append(cand_nome)
                    
                    # Atualizar no Supabase
                    new_cands = st.session_state["candidatos_vagas"][vaga_id_int]
                    emp_sel = st.session_state.get("analise_proc_emp_sel", "Mundo Kan")
                    try:
                        check_ex = supabase_client.table("processos_seletivos").select("id").eq("vaga_id", vaga_id_int).execute()
                        if check_ex and check_ex.data:
                            row_id = check_ex.data[0]["id"]
                            supabase_client.table("processos_seletivos").update({
                                "candidatos": new_cands,
                                "empresa": emp_sel,
                                "updated_at": "now()"
                            }).eq("id", row_id).execute()
                        else:
                            supabase_client.table("processos_seletivos").insert({
                                "vaga_id": vaga_id_int,
                                "empresa": emp_sel,
                                "candidatos": new_cands,
                                "tenant_id": st.session_state.get("tenant_id")
                            }).execute()
                    except Exception as e:
                        import traceback
                        st.error(f"Erro ao salvar associação no banco de dados para vaga {vaga_id_int}: {e}")
                        st.text(traceback.format_exc())
                        st.stop()
            
            del st.query_params["assoc_cand"]
            if "vaga_id" in st.query_params:
                del st.query_params["vaga_id"]
            st.rerun()

        # Verificar se há pedido de desassociação via URL (query params)
        if "deassoc_cand" in st.query_params:
            cand_nome = st.query_params["deassoc_cand"]
            vaga_id = st.query_params.get("vaga_id")
            if vaga_id:
                try:
                    vaga_id_int = int(vaga_id)
                except:
                    vaga_id_int = vaga_id
                
                # Manter a vaga ativa selecionada
                try:
                    res_v = supabase_client.table("vagas").select("nome_vaga, senioridade").eq("id", vaga_id_int).execute()
                    if res_v and res_v.data:
                        v_info = res_v.data[0]
                        st.session_state["analise_proc_vaga_sel"] = f"{v_info['nome_vaga']} ({v_info['senioridade']})"
                except Exception:
                    pass
                
                if vaga_id_int in st.session_state["candidatos_vagas"]:
                    if cand_nome in st.session_state["candidatos_vagas"][vaga_id_int]:
                        st.session_state["candidatos_vagas"][vaga_id_int].remove(cand_nome)
                        
                        # Atualizar no Supabase
                        new_cands = st.session_state["candidatos_vagas"][vaga_id_int]
                        emp_sel = st.session_state.get("analise_proc_emp_sel", "Mundo Kan")
                        try:
                            check_ex = supabase_client.table("processos_seletivos").select("id").eq("vaga_id", vaga_id_int).execute()
                            if check_ex and check_ex.data:
                                row_id = check_ex.data[0]["id"]
                                supabase_client.table("processos_seletivos").update({
                                    "candidatos": new_cands,
                                    "empresa": emp_sel,
                                    "updated_at": "now()"
                                }).eq("id", row_id).execute()
                        except Exception as e:
                            import traceback
                            st.error(f"Erro ao salvar desassociação no banco de dados para vaga {vaga_id_int}: {e}")
                            st.text(traceback.format_exc())
                            st.stop()
            
            del st.query_params["deassoc_cand"]
            if "vaga_id" in st.query_params:
                del st.query_params["vaga_id"]
            st.rerun()

        # Verificar se há pedido de seleção de vaga via URL (query params)
        if "vaga_sel" in st.query_params:
            st.session_state["analise_proc_vaga_sel"] = st.query_params["vaga_sel"]
            del st.query_params["vaga_sel"]
            st.rerun()

        # Carregar empresas cadastradas
        lista_empresas_salvas = carregar_empresas()
        nomes_empresas = [e["nome_empresa"] for e in lista_empresas_salvas if e.get("nome_empresa")]
        if not nomes_empresas:
            st.info("Nenhuma empresa cadastrada no sistema. Por favor, cadastre uma empresa no menu **Hierarquia / Deptos** antes de gerenciar os processos seletivos.")
            return

        # Renderizar a seleção da empresa no topo (antes do box do processo selecionado)
        col_filtro1, _ = st.columns([1, 1])
        with col_filtro1:
            empresa_selecionada = st.selectbox("Selecione a Empresa:", options=nomes_empresas, key="analise_proc_emp_sel")

        # Buscar vagas cadastradas da empresa
        try:
            res_vagas = supabase_client.table("vagas").select("*").eq("empresa", empresa_selecionada).order("created_at", desc=True).execute()
            vagas_list = res_vagas.data if res_vagas and res_vagas.data else []
        except Exception as e:
            st.error(f"Erro ao carregar vagas: {e}")
            return

        # Parsing de requisitos da vaga
        def parse_json_list(val):
            if not val: return []
            if isinstance(val, list): return val
            try: return json.loads(val)
            except Exception: return []

        vaga = None
        vaga_selecionada_nome = ""
        vagas_dict = {}
        if vagas_list:
            vagas_dict = {f"{v['nome_vaga']} ({v['senioridade']})": v for v in vagas_list}
            vaga_default_nome = list(vagas_dict.keys())[0]
            vaga_selecionada_nome = st.session_state.get("analise_proc_vaga_sel", vaga_default_nome)
            if vaga_selecionada_nome not in vagas_dict:
                vaga_selecionada_nome = vaga_default_nome
                st.session_state["analise_proc_vaga_sel"] = vaga_default_nome
            vaga = vagas_dict[vaga_selecionada_nome]

        # Injetar CSS e HTML da matching-page-wrapper para o tema Dark Premium
        header_vaga_title = format_vaga_title(vaga['nome_vaga'], vaga['senioridade']) if vaga else "Sem Vaga Selecionada"
        header_vaga_seniority = vaga['senioridade'] if vaga else "N/A"
        header_vaga_status = "Ativo" if vaga else "Inativo"

        # Obter dados do Perfil comportamental desejado para a vaga selecionada
        header_resumo_text = "Nenhum requisito comportamental específico."
        if vaga:
            p_list = parse_json_list(vaga.get('perfis_ideais'))
            c_list = parse_json_list(vaga.get('categorias_ideais'))
            q_list = parse_json_list(vaga.get('qualidades_ideais'))
            
            resumo_parts = []
            
            # 1. KAN
            kan_val = vaga.get('kan_ideal')
            if kan_val and kan_val not in ("Nenhum", "Nenhum / Não Exigido"):
                kan_badge = f'<span class="req-badge-lilac">{kan_val}</span>'
                resumo_parts.append(f'<strong style="color: #F08A00; font-weight: 700;">KAN:</strong> {kan_badge}')
            
            # 2. PERFIL
            if p_list:
                perfis_badges = "".join([f'<span class="req-badge-lilac">{p}</span>' for p in p_list])
                resumo_parts.append(f'<strong style="color: #F08A00; font-weight: 700;">PERFIL:</strong> {perfis_badges}')
                
            # 3. CATEGORIA
            if c_list:
                cats_badges = "".join([f'<span class="req-badge-lilac">{c}</span>' for c in c_list])
                resumo_parts.append(f'<strong style="color: #F08A00; font-weight: 700;">CATEGORIA:</strong> {cats_badges}')
                
            # 4. QUALIDADES
            if q_list:
                quals_badges = "".join([f'<span class="req-badge-lilac">{q}</span>' for q in q_list])
                resumo_parts.append(f'<strong style="color: #F08A00; font-weight: 700;">QUALIDADES:</strong> {quals_badges}')
            
            if resumo_parts:
                header_resumo_text = " &nbsp;|&nbsp; ".join(resumo_parts)
        
        from components.card import premium_card_container

        # Injetar CSS local para layout e detalhes específicos
        st.markdown("""
        <style>
            /* Reset e visual Dark Premium */
            .stApp:has(.matching-page-wrapper) {
                background-color: #0D1016 !important;
            }
            .stApp:has(.matching-page-wrapper) [data-testid="stMain"] {
                background-color: #0D1016 !important;
            }
            
            .matching-page-wrapper {
                background-color: #0D1016 !important;
                color: #F4F7FB !important;
                padding-bottom: 50px;
                max-width: 1200px;
                margin: 0 auto;
            }

            .matching-page-wrapper .highlight-text {
                background: linear-gradient(135deg, #F08A00 0%, #FF9D1F 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            /* Estilo do botão de link de nome de candidato */
            .matching-page-wrapper .talent-link-container div.row-widget.stButton > button {
                border: none !important;
                background: transparent !important;
                padding: 0 !important;
                color: #F4F7FB !important;
                text-decoration: none !important;
                border-bottom: 2px solid transparent !important;
                text-align: center !important;
                font-size: 1.05rem !important;
                font-family: 'Outfit', sans-serif !important;
                font-weight: 700 !important;
                box-shadow: none !important;
                display: inline-block !important;
                margin: 0 auto !important;
                transition: all 0.2s ease !important;
                line-height: 1.2 !important;
            }
            .matching-page-wrapper .talent-link-container div.row-widget.stButton > button:hover {
                color: #FF9D1F !important;
                border-bottom: 2px solid #FF9D1F !important;
            }
            
            /* Botão de excluir posicionado absolutamente e perfeitamente centralizado */
            .matching-page-wrapper div:has(> .btn-excluir-link) {
                position: absolute !important;
                top: 0 !important;
                left: 0 !important;
                width: 0 !important;
                height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
                border: none !important;
                z-index: 10 !important;
            }
            .matching-page-wrapper .btn-excluir-link {
                position: absolute !important;
                top: 12px !important;
                left: 12px !important;
                width: 28px !important;
                height: 28px !important;
                min-width: 28px !important;
                min-height: 28px !important;
                background: rgba(255, 255, 255, 0.03) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                color: #7F8798 !important;
                opacity: 0.7 !important;
                border-radius: 8px !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                text-decoration: none !important;
                box-shadow: none !important;
                transition: all 0.2s ease !important;
                z-index: 11 !important;
            }
            .matching-page-wrapper .btn-excluir-link:hover {
                background: rgba(239, 68, 68, 0.12) !important;
                border-color: rgba(239, 68, 68, 0.25) !important;
                color: #EF4444 !important;
                opacity: 1 !important;
                transform: scale(1.05) !important;
            }
            .matching-page-wrapper .btn-excluir-link i {
                font-family: 'lucide' !important;
                font-size: 14px !important;
                line-height: 1 !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                font-style: normal !important;
                font-weight: normal !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            
            /* Estilização Premium do CTA "Associar Talentos" */
            .matching-page-wrapper div[class*="st-key-btn_add_assoc_talents"] button {
                background: #F08A00 !important;
                color: #0D1016 !important;
                font-family: 'Outfit', sans-serif !important;
                font-weight: 700 !important;
                font-size: 1rem !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 12px !important;
                padding: 14px 28px !important;
                box-shadow: 0 4px 16px rgba(240, 138, 0, 0.3) !important;
                transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
                letter-spacing: 0.5px;
                text-transform: none !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 8px !important;
                height: auto !important;
            }
            .matching-page-wrapper div[class*="st-key-btn_add_assoc_talents"] button:hover {
                background: #FF9D1F !important;
                box-shadow: 0 8px 24px rgba(240, 138, 0, 0.5) !important;
                transform: translateY(-2px) !important;
                color: #0D1016 !important;
            }
            
            /* Avatar Halo compact */
            .matching-page-wrapper .avatar-halo-wrapper {
                display: flex;
                justify-content: center;
                margin-top: 5px;
                margin-bottom: 12px;
            }
            .matching-page-wrapper .avatar-halo {
                width: 56px;
                height: 56px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 2px;
                background: linear-gradient(135deg, #5B1463 0%, #7A2B8A 50%, #F08A00 100%);
                box-shadow: 0 4px 12px rgba(91, 20, 99, 0.2), 0 0 0 3px rgba(255, 255, 255, 0.01);
                position: relative;
                transition: box-shadow 0.3s ease;
            }
            .matching-page-wrapper div[data-testid="stVerticalBlockBorderWrapper"]:hover .avatar-halo {
                box-shadow: 0 6px 16px rgba(240, 138, 0, 0.3), 0 0 0 4px rgba(240, 138, 0, 0.03);
            }
            .matching-page-wrapper .avatar-img {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                object-fit: cover;
                border: 2px solid #171B2A;
            }
            .matching-page-wrapper .font-avatar-bg {
                background: linear-gradient(135deg, #5B1463 0%, #7A2B8A 100%);
            }
            .matching-page-wrapper .avatar-initial {
                font-family: 'Outfit', sans-serif;
                font-size: 1.2rem;
                font-weight: 800;
                color: #F4F7FB;
            }
            
            /* Dob nascimento compact */
            .matching-page-wrapper .dob-text {
                margin: 4px 0 12px 0 !important;
                color: #7F8798 !important;
                font-size: 0.72rem !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 5px !important;
                font-weight: 500;
                letter-spacing: 0.2px;
            }
            .matching-page-wrapper .dob-text i {
                color: #7A2B8A !important;
                font-size: 10px !important;
            }
            
            /* Atributos do candidato compact */
            .matching-page-wrapper .attributes-container {
                border-top: 1px solid rgba(255, 255, 255, 0.08);
                padding-top: 12px;
                margin-bottom: 12px;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            .matching-page-wrapper .attr-row-v {
                display: flex;
                flex-direction: column;
                gap: 4px;
                font-size: 0.76rem;
                align-items: flex-start;
                margin-bottom: 2px;
            }
            .matching-page-wrapper .tags-container {
                display: flex;
                flex-wrap: wrap;
                gap: 3px;
                width: 100%;
            }
            .matching-page-wrapper .attr-label {
                color: #7F8798;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.6px;
                font-size: 0.68rem;
            }
            .matching-page-wrapper .attr-value {
                color: #AAB3C5;
                font-weight: 500;
                font-size: 0.76rem;
            }
            .matching-page-wrapper .badge-tag {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 5px;
                font-size: 0.68rem;
                font-weight: 700;
                margin: 1px;
                letter-spacing: 0.2px;
                text-transform: uppercase;
                background-color: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.05);
                color: #AAB3C5;
            }
            .matching-page-wrapper .perfil-tag {
                background-color: rgba(122, 43, 138, 0.08) !important;
                border: 1px solid rgba(122, 43, 138, 0.2) !important;
                color: #AAB3C5 !important;
            }
            .matching-page-wrapper .cat-tag {
                background-color: rgba(240, 138, 0, 0.08) !important;
                border: 1px solid rgba(240, 138, 0, 0.2) !important;
                color: #FF9D1F !important;
            }
            .matching-page-wrapper .qual-tag {
                background-color: rgba(255, 255, 255, 0.02) !important;
                border: 1px solid rgba(255, 255, 255, 0.06) !important;
                color: #7F8798 !important;
            }
            .matching-page-wrapper .attr-chip {
                padding: 2px 8px;
                border-radius: 6px;
                font-size: 0.68rem;
                font-weight: 700;
                letter-spacing: 0.4px;
                text-transform: uppercase;
            }
            .matching-page-wrapper .kan-chip {
                background: rgba(240, 138, 0, 0.12);
                border: 1px solid rgba(240, 138, 0, 0.25);
                color: #F08A00;
            }
            
            /* Widget de pontuação compact */
            .matching-page-wrapper .score-widget {
                background: linear-gradient(135deg, rgba(23, 27, 42, 0.4) 0%, rgba(13, 16, 22, 0.3) 100%) !important;
                border: 1px solid rgba(255, 255, 255, 0.05) !important;
                border-radius: 10px !important;
                padding: 10px 12px !important;
                margin-top: 12px !important;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.2) !important;
                transition: all 0.25s ease;
            }
            .matching-page-wrapper .score-widget:hover {
                border-color: rgba(240, 138, 0, 0.2) !important;
                background: linear-gradient(135deg, rgba(23, 27, 42, 0.6) 0%, rgba(13, 16, 22, 0.5) 100%) !important;
            }
            .matching-page-wrapper .score-main {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            }
            .matching-page-wrapper .score-title {
                font-size: 0.68rem;
                color: #7F8798;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.6px;
            }
            .matching-page-wrapper .score-badge {
                background: rgba(240, 138, 0, 0.1) !important;
                border: 1px solid rgba(240, 138, 0, 0.25) !important;
                padding: 2px 8px !important;
                border-radius: 6px !important;
                font-weight: 800 !important;
                font-size: 0.8rem !important;
                color: #F08A00 !important;
                display: inline-flex;
                align-items: center;
                gap: 4px;
                font-family: 'Outfit', sans-serif !important;
            }
            .matching-page-wrapper .score-breakdown {
                display: flex;
                justify-content: space-between;
                border-top: 1px solid rgba(255, 255, 255, 0.06);
                padding-top: 8px;
                gap: 4px;
            }
            .matching-page-wrapper .breakdown-item {
                flex: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .matching-page-wrapper .border-l {
                border-left: 1px solid rgba(255, 255, 255, 0.06);
            }
            .matching-page-wrapper .breakdown-label {
                font-size: 0.58rem;
                color: #7F8798;
                text-transform: uppercase;
                font-weight: 700;
                letter-spacing: 0.4px;
            }
            .matching-page-wrapper .breakdown-val {
                font-size: 0.72rem;
                color: #F4F7FB;
                font-weight: 700;
                margin-top: 1px;
            }
            
            /* Dropdowns */
            .matching-page-wrapper div[data-testid="stSelectbox"] div[role="combobox"],
            .matching-page-wrapper div[data-testid="stMultiSelect"] div[role="combobox"] {
                background-color: #171B2A !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                color: #F4F7FB !important;
                border-radius: 12px !important;
            }
            .matching-page-wrapper label {
                color: #AAB3C5 !important;
                font-weight: 600 !important;
                font-size: 0.85rem !important;
            }
            
            /* Contorno laranja para o selectbox da empresa */
            div[class*="st-key-analise_proc_emp_sel"] div[role="combobox"] {
                border: 2px solid #F08A00 !important;
                box-shadow: 0 0 8px rgba(240, 138, 0, 0.2) !important;
                background-color: #171B2A !important;
            }
            div[class*="st-key-analise_proc_emp_sel"] div[role="combobox"]:hover {
                border-color: #FF9D1F !important;
                box-shadow: 0 0 12px rgba(240, 138, 0, 0.4) !important;
            }
            div[class*="st-key-analise_proc_emp_sel"] label {
                color: rgba(255, 255, 255, 0.9) !important;
                font-weight: 600 !important;
                font-size: 0.85rem !important;
            }
            
            /* Dataframe adjustments */
            .matching-page-wrapper div[data-testid="stDataFrame"] {
                background-color: #141824 !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                border-radius: 16px !important;
            }
            
            /* Profile Requirements Table styling */
            .profile-req-table {
                display: flex;
                flex-direction: column;
                gap: 16px;
                margin-top: 20px;
                margin-bottom: 20px;
                width: 100%;
            }
            .profile-req-row {
                display: grid;
                grid-template-columns: 180px 1fr;
                align-items: center;
                gap: 16px;
                padding-bottom: 12px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            }
            .profile-req-row:last-child {
                border-bottom: none;
                padding-bottom: 0;
            }
            .profile-req-label {
                font-family: 'Outfit', sans-serif !important;
                font-size: 0.8rem !important;
                color: #8C96A8 !important;
                text-transform: uppercase !important;
                font-weight: 600 !important;
                letter-spacing: 0.8px !important;
            }
            .profile-req-value-cell {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }
            .profile-req-value {
                background-color: #090C11 !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                color: #FFFFFF !important;
                font-family: 'Outfit', sans-serif !important;
                font-size: 0.85rem !important;
                font-weight: 500 !important;
                padding: 6px 14px !important;
                border-radius: 6px !important;
                display: inline-block !important;
                box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3) !important;
            }
            .profile-req-value.highlight-kan {
                border-color: rgba(240, 138, 0, 0.3) !important;
                color: #F08A00 !important;
                font-weight: 600 !important;
            }
            
            @media (max-width: 768px) {
                .profile-req-row {
                    grid-template-columns: 1fr;
                    align-items: flex-start;
                    gap: 8px;
                }
            }

            /* Candidate Card Table styling (same style as profile, but smaller) */
            .cand-req-table {
                display: flex;
                flex-direction: column;
                gap: 8px;
                margin-top: 10px;
                margin-bottom: 12px;
                width: 100%;
            }
            .cand-req-row {
                display: grid;
                grid-template-columns: 80px 1fr;
                align-items: center;
                gap: 8px;
                padding-bottom: 6px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            }
            .cand-req-row:last-child {
                border-bottom: none;
                padding-bottom: 0;
            }
            .cand-req-label {
                font-family: 'Outfit', sans-serif !important;
                font-size: 0.68rem !important;
                color: #8C96A8 !important;
                text-transform: uppercase !important;
                font-weight: 600 !important;
                letter-spacing: 0.5px !important;
            }
            .cand-req-value-cell {
                display: flex;
                flex-wrap: wrap;
                gap: 4px;
            }
            .cand-req-value {
                background-color: #090C11 !important;
                border: 1px solid rgba(255, 255, 255, 0.06) !important;
                color: #FFFFFF !important;
                font-family: 'Outfit', sans-serif !important;
                font-size: 0.72rem !important;
                font-weight: 500 !important;
                padding: 3px 8px !important;
                border-radius: 4px !important;
                display: inline-block !important;
                box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3) !important;
            }
            .cand-req-value.highlight-kan {
                border-color: rgba(240, 138, 0, 0.25) !important;
                color: #F08A00 !important;
                font-weight: 600 !important;
            }
            
            /* Subtitles */
            .matching-page-wrapper .section-title-sub {
                font-family: 'Outfit', sans-serif !important;
                font-size: 1.6rem !important;
                font-weight: 700 !important;
                color: #F4F7FB !important;
                margin-top: 40px !important;
                margin-bottom: 20px !important;
                letter-spacing: -0.3px;
            }
            
            /* Comparativo */
            .matching-page-wrapper .comp-row {
                font-size: 0.9rem !important;
                color: #AAB3C5 !important;
                margin-bottom: 12px !important;
                display: flex !important;
                justify-content: space-between !important;
                align-items: center !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
                padding-bottom: 8px !important;
            }
            .matching-page-wrapper .code-highlight {
                background-color: rgba(240, 138, 0, 0.1) !important;
                color: #FF9D1F !important;
                padding: 4px 10px !important;
                border-radius: 6px !important;
                font-family: monospace !important;
                border: 1px solid rgba(240, 138, 0, 0.2) !important;
                font-size: 0.85rem !important;
            }
            
            /* Progress bar adjustments */
            .matching-page-wrapper div[data-testid="stProgress"] > div > div > div > div {
                background: linear-gradient(90deg, #5B1463 0%, #F08A00 100%) !important;
            }
            .matching-page-wrapper div[data-testid="stProgress"] {
                background-color: rgba(255, 255, 255, 0.05) !important;
                border-radius: 10px !important;
                height: 10px !important;
            }
            
            /* Centralização vertical das colunas nos cards de processos */
            .stApp div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="column"] {
                display: flex !important;
                flex-direction: column !important;
                justify-content: center !important;
            }
            
            /* Se selecionado / ativo */
            .stApp div[data-testid="stVerticalBlockBorderWrapper"]:has(div[class*="st-key-btn_analisar_active"]) {
                border-color: rgba(122, 43, 138, 0.6) !important;
                box-shadow: 0 12px 35px rgba(122, 43, 138, 0.25) !important;
            }
            
            /* Titulo colorido do processo */
            .stApp .process-card-title {
                font-family: 'Outfit', sans-serif !important;
                font-weight: 800 !important;
                font-size: 1.15rem !important; /* Tamanho do h4 no box de vagas */
                background: linear-gradient(135deg, #F08A00 0%, #FF9D1F 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 4px;
                display: inline-block;
            }
            
            /* Subtitulo / requisitos do processo */
            .stApp .process-card-reqs {
                font-family: 'Inter', sans-serif !important;
                font-size: 0.85rem !important;
                color: #AAB3C5 !important;
                margin-top: 4px;
                line-height: 1.4;
            }
            
            /* Botão de analisar estilizado */
            .stApp div[class*="st-key-btn_analisar_"] button {
                background: rgba(240, 138, 0, 0.1) !important;
                border: 1px solid rgba(240, 138, 0, 0.3) !important;
                color: #FF9D1F !important;
                font-family: 'Outfit', sans-serif !important;
                font-weight: 700 !important;
                border-radius: 8px !important;
                transition: all 0.25s ease !important;
                font-size: 0.85rem !important;
                padding: 6px 16px !important;
                box-shadow: none !important;
            }
            .stApp div[class*="st-key-btn_analisar_"] button:hover {
                background: #F08A00 !important;
                color: #0D1016 !important;
                border-color: #F08A00 !important;
                box-shadow: 0 4px 12px rgba(240, 138, 0, 0.3) !important;
            }
            /* Botão ativo */
            .stApp div[class*="st-key-btn_analisar_active"] button {
                background: #F08A00 !important;
                color: #0D1016 !important;
                border-color: #F08A00 !important;
                font-family: 'Outfit', sans-serif !important;
                font-weight: 700 !important;
                border-radius: 8px !important;
                font-size: 0.85rem !important;
                padding: 6px 16px !important;
                box-shadow: 0 4px 12px rgba(240, 138, 0, 0.3) !important;
            }

            
            /* Badges lilás no estilo da senioridade */
            .stApp .req-badge-lilac {
                background: rgba(122, 43, 138, 0.15) !important;
                border: 1px solid rgba(122, 43, 138, 0.3) !important;
                color: #AAB3C5 !important;
                padding: 3px 10px !important;
                border-radius: 20px !important;
                font-size: 0.72rem !important;
                font-weight: 600 !important;
                letter-spacing: 0.3px !important;
                display: inline-block !important;
                margin: 2px 2px !important;
                text-transform: uppercase !important;
                font-family: 'Outfit', sans-serif !important;
            }
            
            /* Botão Premium IA */
            div[class*="st-key-btn_ia_sug_req_"] button {
                background: linear-gradient(135deg, #7A2B8A 0%, #B92B2B 50%, #F08A00 100%) !important;
                color: #FFFFFF !important;
                font-family: 'Outfit', sans-serif !important;
                font-weight: 700 !important;
                font-size: 0.95rem !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 10px 20px !important;
                box-shadow: 0 4px 15px rgba(122, 43, 138, 0.3) !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 8px !important;
            }
            div[class*="st-key-btn_ia_sug_req_"] button::before {
                font-family: 'lucide' !important;
                content: "\\e412" !important;
                display: inline-block !important;
                margin-right: 8px !important;
                font-size: 18px !important;
                font-style: normal !important;
                font-weight: normal !important;
                color: inherit !important;
                line-height: 1 !important;
            }
            div[class*="st-key-btn_ia_sug_req_"] button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(122, 43, 138, 0.5) !important;
                color: #FFFFFF !important;
            }
            div[class*="st-key-btn_ia_sug_req_"] button:active {
                transform: translateY(0) !important;
            }
            
            /* Overrides para os Cards de Candidatos Associados */
            .stApp:has(.matching-page-wrapper) .avatar-halo-wrapper {
                display: flex !important;
                justify-content: center !important;
                margin-top: 5px !important;
                margin-bottom: 12px !important;
            }
            .stApp:has(.matching-page-wrapper) .avatar-halo {
                width: 86px !important;
                height: 86px !important;
                border-radius: 50% !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                padding: 3px !important;
                background: linear-gradient(135deg, #5B1463 0%, #7A2B8A 50%, #F08A00 100%) !important;
                box-shadow: 0 4px 12px rgba(91, 20, 99, 0.2), 0 0 0 3px rgba(255, 255, 255, 0.01) !important;
                position: relative !important;
                transition: box-shadow 0.3s ease !important;
            }
            .stApp:has(.matching-page-wrapper) div[data-testid="stVerticalBlockBorderWrapper"]:hover .avatar-halo {
                box-shadow: 0 6px 16px rgba(240, 138, 0, 0.3), 0 0 0 4px rgba(240, 138, 0, 0.03) !important;
            }
            .stApp:has(.matching-page-wrapper) .avatar-img {
                width: 80px !important;
                height: 80px !important;
                border-radius: 50% !important;
                object-fit: cover !important;
                border: 2px solid #171B2A !important;
            }
            .stApp:has(.matching-page-wrapper) .font-avatar-bg {
                background: linear-gradient(135deg, #5B1463 0%, #7A2B8A 100%) !important;
            }
            .stApp:has(.matching-page-wrapper) .avatar-initial {
                font-family: 'Outfit', sans-serif !important;
                font-size: 1.5rem !important;
                font-weight: 800 !important;
                color: #F4F7FB !important;
            }
            .stApp:has(.matching-page-wrapper) .dob-text {
                margin: 4px 0 12px 0 !important;
                color: #7F8798 !important;
                font-size: 0.72rem !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                gap: 5px !important;
                font-weight: 500 !important;
                letter-spacing: 0.2px !important;
            }
            .stApp:has(.matching-page-wrapper) .dob-text i {
                color: #7A2B8A !important;
                font-size: 10px !important;
            }
            .stApp:has(.matching-page-wrapper) .talent-link-container div.row-widget.stButton > button {
                border: none !important;
                background: transparent !important;
                padding: 0 !important;
                color: #F4F7FB !important;
                text-decoration: none !important;
                border-bottom: 2px solid transparent !important;
                text-align: center !important;
                font-size: 1.05rem !important;
                font-family: 'Outfit', sans-serif !important;
                font-weight: 700 !important;
                box-shadow: none !important;
                display: inline-block !important;
                margin: 0 auto !important;
                transition: all 0.2s ease !important;
                line-height: 1.2 !important;
            }
            .stApp:has(.matching-page-wrapper) .talent-link-container div.row-widget.stButton > button:hover {
                color: #FF9D1F !important;
                border-bottom: 2px solid #FF9D1F !important;
            }
            .stApp:has(.matching-page-wrapper) .btn-excluir-link {
                position: absolute !important;
                top: 12px !important;
                left: 12px !important;
                width: 28px !important;
                height: 28px !important;
                min-width: 28px !important;
                min-height: 28px !important;
                background: rgba(255, 255, 255, 0.03) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                color: #7F8798 !important;
                opacity: 0.7 !important;
                border-radius: 8px !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                text-decoration: none !important;
                box-shadow: none !important;
                transition: all 0.2s ease !important;
                z-index: 11 !important;
            }
            .stApp:has(.matching-page-wrapper) .btn-excluir-link:hover {
                background: rgba(239, 68, 68, 0.12) !important;
                border-color: rgba(239, 68, 68, 0.25) !important;
                color: #EF4444 !important;
                opacity: 1 !important;
                transform: scale(1.05) !important;
            }
            .stApp:has(.matching-page-wrapper) .score-widget {
                background: linear-gradient(135deg, rgba(23, 27, 42, 0.4) 0%, rgba(13, 16, 22, 0.3) 100%) !important;
                border: 1px solid rgba(255, 255, 255, 0.05) !important;
                border-radius: 8px !important;
                padding: 6px 8px !important;
                margin-top: 8px !important;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.2) !important;
                transition: all 0.25s ease !important;
            }
            .stApp:has(.matching-page-wrapper) .score-widget:hover {
                border-color: rgba(240, 138, 0, 0.2) !important;
                background: linear-gradient(135deg, rgba(23, 27, 42, 0.6) 0%, rgba(13, 16, 22, 0.5) 100%) !important;
            }
            .stApp:has(.matching-page-wrapper) .score-main {
                display: flex !important;
                justify-content: space-between !important;
                align-items: center !important;
                margin-bottom: 6px !important;
            }
            .stApp:has(.matching-page-wrapper) .score-title {
                font-size: 0.58rem !important;
                color: #7F8798 !important;
                font-weight: 700 !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
            }
            .stApp:has(.matching-page-wrapper) .score-badge {
                background: rgba(240, 138, 0, 0.08) !important;
                border: 1px solid rgba(240, 138, 0, 0.20) !important;
                padding: 1px 5px !important;
                border-radius: 4px !important;
                font-weight: 700 !important;
                font-size: 0.68rem !important;
                color: #F08A00 !important;
                display: inline-flex !important;
                align-items: center !important;
                gap: 2px !important;
                font-family: 'Outfit', sans-serif !important;
            }
            .stApp:has(.matching-page-wrapper) .score-breakdown {
                display: flex !important;
                justify-content: space-between !important;
                border-top: 1px solid rgba(255, 255, 255, 0.06) !important;
                padding-top: 6px !important;
                gap: 4px !important;
            }
            .stApp:has(.matching-page-wrapper) .breakdown-item {
                flex: 1 !important;
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
            }
            .stApp:has(.matching-page-wrapper) .border-l {
                border-left: 1px solid rgba(255, 255, 255, 0.06) !important;
            }
            .stApp:has(.matching-page-wrapper) .breakdown-label {
                font-size: 0.52rem !important;
                color: #7F8798 !important;
                text-transform: uppercase !important;
                font-weight: 700 !important;
                letter-spacing: 0.3px !important;
            }
            .stApp:has(.matching-page-wrapper) .breakdown-val {
                font-size: 0.68rem !important;
                color: #F4F7FB !important;
                font-weight: 700 !important;
            }

            /* Estilos customizados da tabela de ranking por aderência (com scroll lateral e vertical) */
            .scrollable-table-wrapper {
                overflow-x: auto !important;
                overflow-y: auto !important;
                max-height: 480px !important;
                width: 100% !important;
                border-radius: 12px !important;
                border: 1px solid var(--panel-border) !important;
                background-color: var(--panel-bg) !important;
                margin-top: 10px !important;
                margin-bottom: 25px !important;
                box-shadow: var(--card-shadow) !important;
            }
            .scrollable-table {
                width: 100% !important;
                border-collapse: collapse !important;
                font-family: 'Inter', sans-serif !important;
                color: var(--text-main) !important;
                min-width: 1050px !important; /* Força scroll horizontal em telas menores */
            }
            .scrollable-table th {
                position: sticky !important;
                top: 0 !important;
                z-index: 10 !important;
                background-color: var(--accent) !important;
                color: var(--button-primary-text) !important;
                font-family: 'Inter', sans-serif !important;
                font-weight: 700 !important;
                font-size: 0.85rem !important;
                text-transform: uppercase !important;
                letter-spacing: 0.6px !important;
                padding: 12px 14px !important;
                text-align: left !important;
                border: 1px solid var(--panel-border) !important;
            }
            .scrollable-table td {
                padding: 10px 14px !important;
                font-size: 0.88rem !important;
                border: 1px solid var(--panel-border) !important;
                background-color: var(--panel-bg) !important;
                vertical-align: middle !important;
                color: var(--text-soft) !important;
            }
            .scrollable-table tr:hover td {
                background-color: var(--hover-bg) !important;
            }

            /* Botão de ação "+" e "✓" circular premium */
            .action-link-btn {
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 26px !important;
                height: 26px !important;
                border-radius: 50% !important;
                font-weight: 800 !important;
                font-size: 1.15rem !important;
                text-decoration: none !important;
                transition: all 0.2s ease !important;
                box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
                cursor: pointer !important;
                margin: 0 auto !important;
                line-height: 1 !important;
            }
            .action-link-btn.btn-assoc {
                background-color: transparent !important;
                color: #F08A00 !important;
                border: 1.5px solid #F08A00 !important;
            }
            .action-link-btn.btn-assoc:hover {
                background-color: #F08A00 !important;
                color: #0D1016 !important;
                transform: scale(1.1) !important;
            }
            .action-link-btn.btn-deassoc {
                background-color: #4CAF50 !important;
                color: #FFFFFF !important;
                border: 1.5px solid #4CAF50 !important;
                font-size: 0.85rem !important;
            }
            .action-link-btn.btn-deassoc:hover {
                background-color: #EF4444 !important;
                border-color: #EF4444 !important;
                color: #FFFFFF !important;
                transform: scale(1.1) !important;
            }
        </style>
        
        <div class="matching-page-wrapper" style="display: none;"></div>
        """, unsafe_allow_html=True)



        if not vagas_list:
            st.info(f"Nenhuma vaga cadastrada para a empresa {empresa_selecionada}. Cadastre vagas no menu Vagas antes de realizar a análise.")
            return

        # Listagem dos Processos Seletivos (Vagas) como boxes horizontais no estilo Vagas, com visual Premium
        st.write("### Processos Seletivos Cadastrados")
        
        for vg in vagas_list:
            vaga_key_name = f"{vg['nome_vaga']} ({vg['senioridade']})"
            is_selected = (vaga_selecionada_nome == vaga_key_name)
            
            try:
                vg_id_int = int(vg["id"])
            except Exception:
                vg_id_int = vg["id"]
                
            # Buscar KAN (customizado ou original)
            if vg_id_int in st.session_state.get("custom_kan_vagas", {}) and st.session_state["custom_kan_vagas"][vg_id_int] is not None:
                kan_val = st.session_state["custom_kan_vagas"][vg_id_int]
            else:
                kan_val = vg.get('kan_ideal')
                
            # Buscar Perfis (customizado ou original)
            if vg_id_int in st.session_state.get("custom_perfis_vagas", {}) and st.session_state["custom_perfis_vagas"][vg_id_int] is not None:
                p_list = st.session_state["custom_perfis_vagas"][vg_id_int]
            else:
                p_list = parse_json_list(vg.get('perfis_ideais'))
                
            # Buscar Categorias (customizado ou original)
            if vg_id_int in st.session_state.get("custom_categorias_vagas", {}) and st.session_state["custom_categorias_vagas"][vg_id_int] is not None:
                c_list = st.session_state["custom_categorias_vagas"][vg_id_int]
            else:
                c_list = parse_json_list(vg.get('categorias_ideais'))
                
            # Buscar Qualidades (customizado ou original)
            if vg_id_int in st.session_state.get("custom_qualidades_vagas", {}) and st.session_state["custom_qualidades_vagas"][vg_id_int] is not None:
                q_list = st.session_state["custom_qualidades_vagas"][vg_id_int]
            else:
                q_list = parse_json_list(vg.get('qualidades_ideais'))
                
            # Garantir que p_list, c_list, q_list sejam de fato listas
            p_list = parse_json_list(p_list) if isinstance(p_list, str) else p_list or []
            c_list = parse_json_list(c_list) if isinstance(c_list, str) else c_list or []
            q_list = parse_json_list(q_list) if isinstance(q_list, str) else q_list or []
            
            # Detalhes na mesma ordem de Vagas (com KAN, PERFIL, CATEGORIA, QUALIDADES destacados e valores em badges lilás)
            resumo_parts = []
            
            # 1. KAN
            if kan_val and kan_val not in ("Nenhum", "Nenhum / Não Exigido"):
                if isinstance(kan_val, list):
                    kan_badges = "".join([f'<span class="req-badge-lilac">{k}</span>' for k in kan_val if k])
                else:
                    if "," in kan_val:
                        kan_badges = "".join([f'<span class="req-badge-lilac">{k.strip()}</span>' for k in kan_val.split(",") if k.strip()])
                    else:
                        kan_badges = f'<span class="req-badge-lilac">{kan_val}</span>'
                resumo_parts.append(f'<strong style="color: #F08A00; font-weight: 700;">KAN:</strong> {kan_badges}')
            
            # 2. PERFIL
            if p_list:
                perfis_badges = "".join([f'<span class="req-badge-lilac">{p}</span>' for p in p_list])
                resumo_parts.append(f'<strong style="color: #F08A00; font-weight: 700;">PERFIL:</strong> {perfis_badges}')
                
            # 3. CATEGORIA
            if c_list:
                cats_badges = "".join([f'<span class="req-badge-lilac">{c}</span>' for c in c_list])
                resumo_parts.append(f'<strong style="color: #F08A00; font-weight: 700;">CATEGORIA:</strong> {cats_badges}')
                
            # 4. QUALIDADES
            if q_list:
                quals_badges = "".join([f'<span class="req-badge-lilac">{q}</span>' for q in q_list])
                resumo_parts.append(f'<strong style="color: #F08A00; font-weight: 700;">QUALIDADES:</strong> {quals_badges}')
            
            resumo_text = " &nbsp;|&nbsp; ".join(resumo_parts) if resumo_parts else "Nenhum requisito comportamental específico."
            
            disp_title = format_vaga_title(vg["nome_vaga"], vg["senioridade"])
            variant = "selected" if is_selected else "interactive"
            
            with premium_card_container(variant=variant):
                col_info, col_action = st.columns([5, 1.2])
                with col_info:
                    st.markdown(
                        f'<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">'
                        f'<h4 style="margin: 0; color: #FFFFFF; font-family: \'Outfit\', sans-serif; font-weight: 700; font-size: 1.15rem;">'
                        f'Processo: <span class="highlight-text">{disp_title}</span>'
                        f'</h4>'
                        f'<span class="premium-badge-status">Ativo</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown(f'<div class="premium-card__reqs">{resumo_text}</div>', unsafe_allow_html=True)
                
                with col_action:
                    if is_selected:
                        st.markdown('<div style="text-align: right; margin-top: 15px;"><span class="premium-badge-selected">Selecionado</span></div>', unsafe_allow_html=True)
                    else:
                        st.write("") # Espaço para alinhar verticalmente
                        if st.button("Analisar", key=f"btn_analisar_{vg['id']}", use_container_width=True):
                            st.session_state["analise_proc_vaga_sel"] = vaga_key_name
                            st.rerun()

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

        # Normalizar para lista de KANs ativos em letras maiúsculas
        if isinstance(raw_kan, list):
            vaga_kan_list = [str(k).strip().upper() for k in raw_kan if k]
        elif isinstance(raw_kan, str):
            if "," in raw_kan:
                vaga_kan_list = [str(k).strip().upper() for k in raw_kan.split(",") if k.strip()]
            else:
                vaga_kan_list = [raw_kan.strip().upper()]
        else:
            vaga_kan_list = []

        vaga_kan_list = [k for k in vaga_kan_list if k not in ("NENHUM", "NENHUM / NÃO EXIGIDO", "")]
        kan_opcoes = ["Criação", "Movimento", "Finalidade"]

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

        def sugerir_requisitos_ia(vaga_dict):
            api_key = st.secrets.get("gemini", {}).get("api_key")
            if not api_key:
                st.error("Chave de API do Gemini não configurada em st.secrets.")
                return None

            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('models/gemini-2.5-flash')

                vaga_nome = vaga_dict.get("nome_vaga", "")
                senioridade = vaga_dict.get("senioridade", "")
                descricao_vaga = vaga_dict.get("descricao_vaga", "")

                prompt = f"""
Você é um especialista em recrutamento e seleção de talentos com foco em perfil comportamental.
Analise a descrição, o título e a senioridade da vaga a seguir para sugerir os requisitos comportamentais mais adequados.

VAGA: {vaga_nome}
SENIORIDADE: {senioridade}
DESCRIÇÃO: {descricao_vaga or "Nenhuma descrição fornecida."}

Opções válidas disponíveis para cada uma das categorias:
- KAN Ideal: {kan_opcoes}
- Perfis Ideais: {perfis_opcoes}
- Categorias: {categorias_opcoes}
- Qualidades: {qualidades_opcoes}

Com base no seu conhecimento técnico e no descritivo da vaga, selecione:
1. Até 2 KAN Ideais (dentre {kan_opcoes})
2. De 1 a 3 Perfis Ideais (dentre {perfis_opcoes})
3. De 1 a 2 Categorias (dentre {categorias_opcoes})
4. De 2 a 5 Qualidades (dentre {qualidades_opcoes})

Instruções cruciais:
- Escolha APENAS opções que estão EXATAMENTE listadas nas opções válidas correspondentes acima (respeitando a grafia exata das opções).
- Não crie novas opções que não estejam presentes nas listas fornecidas.
- Caso a descrição da vaga esteja vazia, infira os requisitos comportamentais ideais apenas com base no título e na senioridade da vaga.
- Retorne EXCLUSIVAMENTE um objeto JSON válido, sem markdown do tipo ```json, sem explicações ou tags extras, no seguinte formato:
{{
  "kan_ideal": ["opção1", ...],
  "perfis_ideais": ["opção1", ...],
  "categorias_ideais": ["opção1", ...],
  "qualidades_ideais": ["opção1", ...]
}}
"""
                response = model.generate_content(prompt)
                res_text = response.text.strip()
                
                # Encontrar a primeira chave '{' e a última '}' para isolar o JSON robustamente
                first_brace = res_text.find('{')
                last_brace = res_text.rfind('}')
                if first_brace != -1 and last_brace != -1:
                    json_str = res_text[first_brace:last_brace+1]
                else:
                    json_str = res_text

                # Fazer o parsing do JSON de forma robusta
                try:
                    data = json.loads(json_str)
                except Exception:
                    import ast
                    data = ast.literal_eval(json_str)

                # Chaves alternativas (fallback se o modelo usar nomes mais simples)
                kan_raw = data.get("kan_ideal", data.get("kan", []))
                perfis_raw = data.get("perfis_ideais", data.get("perfis", []))
                cats_raw = data.get("categorias_ideais", data.get("categorias", []))
                quals_raw = data.get("qualidades_ideais", data.get("qualidades", []))

                # Normalizar usando remoção de acentos e maiúsculas
                def filter_valid(items, valid_options):
                    valid_map = {remover_acentos(v.strip().upper()): v for v in valid_options}
                    filtered = []
                    for item in items:
                        item_norm = remover_acentos(str(item).strip().upper())
                        if item_norm in valid_map:
                            filtered.append(valid_map[item_norm])
                    return filtered

                suggested_kan = filter_valid(kan_raw, kan_opcoes)
                suggested_perfis = filter_valid(perfis_raw, perfis_opcoes)
                suggested_cats = filter_valid(cats_raw, categorias_opcoes)
                suggested_quals = filter_valid(quals_raw, qualidades_opcoes)

                return {
                    "kan_ideal": suggested_kan,
                    "perfis_ideais": suggested_perfis,
                    "categorias_ideais": suggested_cats,
                    "qualidades_ideais": suggested_quals
                }

            except Exception as e:
                st.error(f"Erro ao gerar sugestões com a IA: {e}")
                return None

        # Mapear para obter a capitalização correta dos defaults
        mapped_kan = map_to_options(vaga_kan_list, kan_opcoes)
        mapped_perfis = map_to_options(raw_perfis, perfis_opcoes)
        mapped_cats = map_to_options(raw_cats, categorias_opcoes)
        mapped_quals = map_to_options(raw_quals, qualidades_opcoes)

        vaga_perfis = [p.upper() for p in mapped_perfis]
        vaga_cats = [c.upper() for c in mapped_cats]
        vaga_quals = [q.upper() for q in mapped_quals]

        # Container visual dos requisitos da Vaga
        from components.card import premium_card_container
        with premium_card_container(variant="default"):
            st.markdown('<h3 class="premium-card__title" style="margin-bottom: 20px !important;">Perfil Comportamental Desejado</h3>', unsafe_allow_html=True)
            
            # Renderizar requisitos com HTML estilizado premium (composição editorial)
            kan_badges = "".join([f'<span class="profile-req-value highlight-kan">{k.upper()}</span>' for k in mapped_kan]) if mapped_kan else '<span class="profile-req-value">NENHUM</span>'
            perfis_badges = "".join([f'<span class="profile-req-value">{p.upper()}</span>' for p in vaga_perfis]) if vaga_perfis else '<span class="profile-req-value">NENHUM</span>'
            cats_badges = "".join([f'<span class="profile-req-value">{c.upper()}</span>' for c in vaga_cats]) if vaga_cats else '<span class="profile-req-value">NENHUMA</span>'
            quals_badges = "".join([f'<span class="profile-req-value">{q.upper()}</span>' for q in vaga_quals]) if vaga_quals else '<span class="profile-req-value">NENHUMA</span>'

            req_html = (
                f'<div class="profile-req-table">'
                f'<div class="profile-req-row">'
                f'<div class="profile-req-label">KAN Ideal</div>'
                f'<div class="profile-req-value-cell">{kan_badges}</div>'
                f'</div>'
                f'<div class="profile-req-row">'
                f'<div class="profile-req-label">Perfis Ideais</div>'
                f'<div class="profile-req-value-cell">{perfis_badges}</div>'
                f'</div>'
                f'<div class="profile-req-row">'
                f'<div class="profile-req-label">Categorias</div>'
                f'<div class="profile-req-value-cell">{cats_badges}</div>'
                f'</div>'
                f'<div class="profile-req-row">'
                f'<div class="profile-req-label">Qualidades</div>'
                f'<div class="profile-req-value-cell">{quals_badges}</div>'
                f'</div>'
                f'</div>'
            )
            st.markdown(req_html, unsafe_allow_html=True)
            
            if vaga.get('descricao_vaga'):
                with st.expander("Descritivo da Vaga", expanded=False):
                    st.write(vaga['descricao_vaga'])
            
            # Painel expansivo de customização de requisitos para este processo
            with st.expander("Requisitos Comportamentais para este Processo", expanded=False):
                st.markdown("<p style='font-family: Outfit; font-size: 0.95em;'>Modifique os requisitos específicos para este processo seletivo. Essas alterações afetarão o cálculo de aderência em tempo real e podem ser salvas no banco de dados.</p>", unsafe_allow_html=True)
                
                # Sugestão de Requisitos com IA
                col_ia, _ = st.columns([1.5, 2.5])
                with col_ia:
                    if st.button("Sugerir com IA", key=f"btn_ia_sug_req_{vaga_id_int}", use_container_width=True):
                        with st.spinner("IA analisando a vaga..."):
                            sugestoes = sugerir_requisitos_ia(vaga)
                            if sugestoes:
                                # 1. Atualizar as variáveis de session_state do backup
                                st.session_state["custom_kan_vagas"][vaga_id_int] = sugestoes["kan_ideal"]
                                st.session_state["custom_perfis_vagas"][vaga_id_int] = sugestoes["perfis_ideais"]
                                st.session_state["custom_categorias_vagas"][vaga_id_int] = sugestoes["categorias_ideais"]
                                st.session_state["custom_qualidades_vagas"][vaga_id_int] = sugestoes["qualidades_ideais"]

                                # 2. Atualizar o estado direto dos widgets multiselect com a capitalização correta
                                st.session_state[f"custom_kan_sel_{vaga_id_int}"] = map_to_options(sugestoes["kan_ideal"], kan_opcoes)
                                st.session_state[f"custom_perfis_sel_{vaga_id_int}"] = map_to_options(sugestoes["perfis_ideais"], perfis_opcoes)
                                st.session_state[f"custom_categorias_sel_{vaga_id_int}"] = map_to_options(sugestoes["categorias_ideais"], categorias_opcoes)
                                st.session_state[f"custom_qualidades_sel_{vaga_id_int}"] = map_to_options(sugestoes["qualidades_ideais"], qualidades_opcoes)

                                st.toast("Sugestões geradas com sucesso! Revise e salve abaixo.", icon="✨")
                                st.rerun()

                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

                col_sel1, col_sel2, col_sel3, col_sel4 = st.columns(4)
                with col_sel1:
                    novos_kans = st.multiselect(
                        "KAN Ideal:",
                        options=kan_opcoes,
                        default=mapped_kan,
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
                    if st.button("Salvar Requisitos do Processo", type="primary", use_container_width=True, key=f"btn_save_custom_req_{vaga_id_int}"):
                        st.session_state["custom_perfis_vagas"][vaga_id_int] = novos_perfis
                        st.session_state["custom_categorias_vagas"][vaga_id_int] = novas_categorias
                        st.session_state["custom_qualidades_vagas"][vaga_id_int] = novas_qualidades
                        st.session_state["custom_kan_vagas"][vaga_id_int] = novos_kans
                        
                        try:
                            check_ex = supabase_client.table("processos_seletivos").select("id").eq("vaga_id", vaga_id_int).execute()
                            if check_ex and check_ex.data:
                                row_id = check_ex.data[0]["id"]
                                supabase_client.table("processos_seletivos").update({
                                    "perfis_ideais": novos_perfis,
                                    "categorias_ideais": novas_categorias,
                                    "qualidades_ideais": novas_qualidades,
                                    "kan_ideal": novos_kans,
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
                                    "kan_ideal": novos_kans,
                                    "tenant_id": st.session_state.get("tenant_id")
                                }).execute()
                            st.success("Requisitos personalizados salvos com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar requisitos personalizados no banco de dados: {e}")
                with col_btn2:
                    if st.button("Restaurar Originais da Vaga", use_container_width=True, key=f"btn_canc_restore_req_{vaga_id_int}"):
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
                            st.error(f"Erro ao restaurar requisitos no banco de dados: {e}")

        # Buscar talentos (candidatos) para fazer o matching
        try:
            res_val = supabase_client.table("mapas_salvos_valores").select("*").execute()
            rows_val = res_val.data if res_val and res_val.data else []
            res_ms = supabase_client.table("mapas_salvos").select("nome, empresa, grupo, profissao, cargo, data_nascimento").execute()
            rows_ms = res_ms.data if res_ms and res_ms.data else []
        except Exception as e:
            st.error(f"Erro ao carregar talentos da base de dados: {e}")
            return

        if not rows_val:
            st.warning("Nenhum mapa calculado na base. Calcule os mapas salvos no Painel de Controle antes de realizar a análise.")
            return

        # Dicionário de cargos/grupos/fotos/datas
        ms_dict = {}
        for r in rows_ms:
            is_migrated_profissao = 'profissao' in r
            profissao_val = r.get('profissao') if is_migrated_profissao else r.get('cargo')
            cargo_val = r.get('cargo') if is_migrated_profissao else ''
            
            ms_dict[r.get("nome")] = {
                "empresa": r.get("empresa") or "Mundo Kan",
                "grupo": r.get("grupo") or r.get("empresa") or "Sem Grupo",
                "profissao": profissao_val or "Sem Profissão",
                "cargo": cargo_val or "",
                "data_nascimento": r.get("data_nascimento") or "",
                "foto_base64": ""
            }

        # Carregar fotos em lote apenas para os candidatos associados ao processo seletivo desta vaga
        vaga_id_int = vaga["id"] if vaga else None
        if vaga_id_int:
            associated_names = st.session_state["candidatos_vagas"].get(vaga_id_int, [])
            if associated_names:
                from models.database import fetch_fotos_clientes
                fotos_dict = fetch_fotos_clientes(associated_names)
                for c_nome in associated_names:
                    if c_nome in ms_dict:
                        ms_dict[c_nome]["foto_base64"] = fotos_dict.get(c_nome, "")

        # Calcular scores
        matching_results = []
        for row in rows_val:
            nome = row.get("nome", "Desconhecido")
            info = ms_dict.get(nome, {"empresa": "Mundo Kan", "grupo": "Sem Grupo", "profissao": "Sem Profissão", "cargo": "", "data_nascimento": "", "foto_base64": ""})
            
            # Traços do talento
            talento_kan = str(row.get("kan", "")).strip().upper()
            talento_perfis = [str(x).strip().upper() for x in str(row.get("perfil", "")).split(",") if x.strip()]
            talento_cats = [str(x).strip().upper() for x in str(row.get("categoria", "")).split(",") if x.strip()]
            talento_quals = [str(x).strip().upper() for x in str(row.get("qualidades", "")).split(",") if x.strip()]

            # 1. KAN Match (25%)
            if not vaga_kan_list:
                kan_score = 25.0
                kan_status = "✓ N/A"
            else:
                talento_kan_norm = remover_acentos(talento_kan).upper().strip()
                vaga_kan_list_norm = [remover_acentos(k).upper().strip() for k in vaga_kan_list]
                if talento_kan_norm in vaga_kan_list_norm:
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
                "Profissão": info["profissao"],
                "Grupo": info["grupo"],
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
        if "mostrar_selector_aderencia" not in st.session_state:
            st.session_state["mostrar_selector_aderencia"] = False
        if "aderencia_confirmado" not in st.session_state:
            st.session_state["aderencia_confirmado"] = False

        st.write("---")
        col_sec_title, col_sec_btn = st.columns([2.2, 1.3])
        with col_sec_title:
            st.markdown("<h2 style='margin:0; font-family: Outfit; font-weight: 800; line-height: 1.2; color: #F4F7FB;'>Candidatos Associados ao Processo</h2>", unsafe_allow_html=True)
        with col_sec_btn:
            if st.button("➕ Associar Talentos", key="btn_add_assoc_talents", use_container_width=True):
                st.session_state["mostrar_selector_talentos"] = True
                st.session_state["mostrar_selector_aderencia"] = False
                st.session_state["aderencia_confirmado"] = False
                st.rerun()
            
            st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
            
            if st.button("Associar por Aderência", key="btn_add_assoc_by_match", use_container_width=True):
                st.session_state["mostrar_selector_aderencia"] = True
                st.session_state["mostrar_selector_talentos"] = False
                st.session_state["talentos_aderencia_temporarios"] = list(st.session_state["candidatos_vagas"].get(vaga_id_int, []))
                st.rerun()

        # Renderizar seletor de associação
        if st.session_state["mostrar_selector_talentos"]:
            with st.container(border=True):
                st.markdown("#### Selecionar Talentos para o Processo")
                # Mostrar todos os talentos cadastrados no sistema
                opcoes_talentos = sorted([r["Nome"] for r in matching_results])
                
                candidatos_selecionados = st.multiselect(
                    "Selecione os talentos que participarão deste processo:",
                    options=opcoes_talentos,
                    default=st.session_state["candidatos_vagas"].get(vaga_id_int, []),
                    key="selector_talentos_multiselect"
                )
                
                col_actions1, col_actions2 = st.columns(2)
                with col_actions1:
                    if st.button("Salvar Associação", type="primary", use_container_width=True, key="btn_save_changes_assoc"):
                        st.session_state["candidatos_vagas"][vaga_id_int] = candidatos_selecionados
                        
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
                                    "candidatos": candidatos_selecionados,
                                    "tenant_id": st.session_state.get("tenant_id")
                                }).execute()
                        except Exception as e:
                            # Caso a tabela ainda não exista no banco de dados do usuário, mostramos um aviso útil
                            st.warning(f"Não foi possível salvar no banco de dados (certifique-se de executar o script SQL de atualização de estrutura correspondente): {e}")
                        
                        st.session_state["mostrar_selector_talentos"] = False
                        st.success("Candidatos associados com sucesso!")
                        st.rerun()
                with col_actions2:
                    if st.button("Cancelar", use_container_width=True, key="btn_canc_assoc"):
                        st.session_state["mostrar_selector_talentos"] = False
                        st.rerun()

        # Renderizar seletor de associação por aderência
        if st.session_state.get("mostrar_selector_aderencia", False):
            with st.container(border=True):
                st.markdown("#### Selecionar por Nível de Aderência")
                
                # Slider de percentual
                slider_val = st.slider(
                    "Selecione o percentual (%) mínimo de aderência desejado:",
                    min_value=0,
                    max_value=100,
                    value=st.session_state.get("aderencia_minima_selecionada", 50),
                    step=1,
                    key="slider_match_pct"
                )
                
                col_c1, col_c2 = st.columns([1, 4])
                with col_c1:
                    if st.button("Confirmar", type="primary", key="btn_confirm_aderencia_slider", use_container_width=True):
                        st.session_state["aderencia_confirmado"] = True
                        st.session_state["aderencia_minima_selecionada"] = slider_val
                        st.rerun()
                with col_c2:
                    if st.button("Cancelar Seleção", key="btn_cancel_aderencia_slider"):
                        st.session_state["mostrar_selector_aderencia"] = False
                        st.session_state["aderencia_confirmado"] = False
                        if "talentos_aderencia_temporarios" in st.session_state:
                            del st.session_state["talentos_aderencia_temporarios"]
                        st.rerun()

                # Se clicou em confirmar, mostrar as listas e o box de confirmação
                if st.session_state.get("aderencia_confirmado", False):
                    min_pct = st.session_state.get("aderencia_minima_selecionada", 50)
                    st.write(f"**Exibindo talentos com aderência maior ou igual a {min_pct}%**")
                    
                    # Filtrar os talentos
                    talentos_empresa = [
                        r for r in matching_results 
                        if r["Empresa"] == empresa_selecionada and r["Aderência (%)"] >= min_pct
                    ]
                    
                    is_admin = st.session_state.get("logged_user") == "adminkan"
                    talentos_totais = [
                        r for r in matching_results 
                        if r["Aderência (%)"] >= min_pct
                    ] if is_admin else []

                    # 1. Tabela Talentos da Empresa
                    st.markdown("##### <i class='lucide-inline icon-building-2' style='font-size: 18px;'></i>Talentos da Empresa", unsafe_allow_html=True)
                    if not talentos_empresa:
                        st.info("Nenhum talento da empresa atende ao nível de aderência selecionado.")
                    else:
                        col_h1, col_h2, col_h3, col_h4 = st.columns([1, 4, 3, 2])
                        with col_h1: st.write("**Ação**")
                        with col_h2: st.write("**Nome**")
                        with col_h3: st.write("**Profissão**")
                        with col_h4: st.write("**Aderência**")
                        
                        st.markdown("<hr style='margin: 4px 0;'/>", unsafe_allow_html=True)
                        for idx, t in enumerate(talentos_empresa):
                            t_name = t["Nome"]
                            col_r1, col_r2, col_r3, col_r4 = st.columns([1, 4, 3, 2])
                            with col_r1:
                                is_already_added = t_name in st.session_state.get("talentos_aderencia_temporarios", [])
                                if is_already_added:
                                    st.markdown("<span style='color: #4CAF50; font-weight: bold;'>✓</span>", unsafe_allow_html=True)
                                else:
                                    if st.button("", key=f"btn_add_emp_t_{idx}_{vaga['id']}", use_container_width=True):
                                        if "talentos_aderencia_temporarios" not in st.session_state:
                                            st.session_state["talentos_aderencia_temporarios"] = []
                                        st.session_state["talentos_aderencia_temporarios"].append(t_name)
                                        st.rerun()
                            with col_r2:
                                st.write(t_name)
                            with col_r3:
                                st.write(t["Profissão"])
                            with col_r4:
                                st.write(f"{t['Aderência (%)']}%")
                            st.markdown("<hr style='margin: 2px 0; opacity: 0.3;'/>", unsafe_allow_html=True)
                        
                        # Opção para adicionar todos os talentos filtrados desta tabela
                        st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
                        if st.button("Adicionar Todos da Empresa", key=f"btn_add_all_emp_{vaga['id']}"):
                            if "talentos_aderencia_temporarios" not in st.session_state:
                                st.session_state["talentos_aderencia_temporarios"] = []
                            for t in talentos_empresa:
                                if t["Nome"] not in st.session_state["talentos_aderencia_temporarios"]:
                                    st.session_state["talentos_aderencia_temporarios"].append(t["Nome"])
                            st.toast("Todos os talentos da empresa foram adicionados.", icon="✅")
                            st.rerun()

                    # 2. Tabela Talentos Totais (adminkan apenas)
                    if is_admin:
                        st.write("")
                        st.markdown("##### 🌍 Todos os Talentos do Sistema (Admin Master)")
                        if not talentos_totais:
                            st.info("Nenhum talento no sistema atende ao nível de aderência selecionado.")
                        else:
                            col_th1, col_th2, col_th3, col_th4, col_th5 = st.columns([1, 4, 3, 2, 2])
                            with col_th1: st.write("**Ação**")
                            with col_th2: st.write("**Nome**")
                            with col_th3: st.write("**Profissão**")
                            with col_th4: st.write("**Empresa**")
                            with col_th5: st.write("**Aderência**")
                            
                            st.markdown("<hr style='margin: 4px 0;'/>", unsafe_allow_html=True)
                            for idx, t in enumerate(talentos_totais):
                                t_name = t["Nome"]
                                col_tr1, col_tr2, col_tr3, col_tr4, col_tr5 = st.columns([1, 4, 3, 2, 2])
                                with col_tr1:
                                    is_already_added = t_name in st.session_state.get("talentos_aderencia_temporarios", [])
                                    if is_already_added:
                                        st.markdown("<span style='color: #4CAF50; font-weight: bold;'>✓</span>", unsafe_allow_html=True)
                                    else:
                                        if st.button("", key=f"btn_add_tot_t_{idx}_{vaga['id']}", use_container_width=True):
                                            if "talentos_aderencia_temporarios" not in st.session_state:
                                                st.session_state["talentos_aderencia_temporarios"] = []
                                            st.session_state["talentos_aderencia_temporarios"].append(t_name)
                                            st.rerun()
                                with col_tr2:
                                    st.write(t_name)
                                with col_tr3:
                                    st.write(t["Profissão"])
                                with col_tr4:
                                    st.write(t["Empresa"])
                                with col_tr5:
                                    st.write(f"{t['Aderência (%)']}%")
                                st.markdown("<hr style='margin: 2px 0; opacity: 0.3;'/>", unsafe_allow_html=True)
                            
                            st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
                            if st.button("Adicionar todos os talentos", key=f"btn_add_all_tot_{vaga['id']}"):
                                if "talentos_aderencia_temporarios" not in st.session_state:
                                    st.session_state["talentos_aderencia_temporarios"] = []
                                for t in talentos_totais:
                                    if t["Nome"] not in st.session_state["talentos_aderencia_temporarios"]:
                                        st.session_state["talentos_aderencia_temporarios"].append(t["Nome"])
                                st.toast("Todos os talentos totais foram adicionados.", icon="✅")
                                st.rerun()

                    # Box com os nomes dos selecionados para confirmação ou remoção
                    st.write("")
                    st.markdown("##### 📋 Candidatos Pré-Selecionados")
                    staged_talents = st.session_state.get("talentos_aderencia_temporarios", [])
                    
                    if not staged_talents:
                        st.info("Nenhum candidato selecionado para este processo ainda.")
                    else:
                        with st.container(border=True):
                            st.markdown("<p style='font-size: 0.88em; color: #7F8798; margin-bottom: 12px;'>Revise a lista de candidatos participantes. Clique em '❌' para remover individualmente.</p>", unsafe_allow_html=True)
                            
                            # Renderizar em colunas compactas
                            num_cols = 3
                            for i in range(0, len(staged_talents), num_cols):
                                row_items = staged_talents[i:i+num_cols]
                                cols = st.columns(num_cols)
                                for col_idx, item in enumerate(row_items):
                                    with cols[col_idx]:
                                        with st.container(border=True):
                                            col_card_name, col_card_del = st.columns([4, 1.2])
                                            with col_card_name:
                                                st.markdown(f"<span style='font-family: sans-serif; font-size: 0.9rem; font-weight: 600;'>{item}</span>", unsafe_allow_html=True)
                                            with col_card_del:
                                                if st.button("❌", key=f"btn_remove_staged_{item}_{vaga_id_int}", use_container_width=True):
                                                    st.session_state["talentos_aderencia_temporarios"].remove(item)
                                                    st.rerun()

                    # Ações finais
                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                    col_save1, col_save2 = st.columns(2)
                    with col_save1:
                        if st.button("Salvar Talentos do Processo", type="primary", use_container_width=True, key=f"btn_save_aderencia_talents_{vaga_id_int}"):
                            candidatos_selecionados = st.session_state.get("talentos_aderencia_temporarios", [])
                            st.session_state["candidatos_vagas"][vaga_id_int] = candidatos_selecionados
                            
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
                                        "candidatos": candidatos_selecionados,
                                        "tenant_id": st.session_state.get("tenant_id")
                                    }).execute()
                                
                                st.success("Talentos do processo salvos com sucesso!")
                                st.session_state["mostrar_selector_aderencia"] = False
                                st.session_state["aderencia_confirmado"] = False
                                if "talentos_aderencia_temporarios" in st.session_state:
                                    del st.session_state["talentos_aderencia_temporarios"]
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao salvar associação no banco de dados: {e}")
                    with col_save2:
                        if st.button("Cancelar e Fechar", use_container_width=True, key=f"btn_cancel_aderencia_save_{vaga['id']}"):
                            st.session_state["mostrar_selector_aderencia"] = False
                            st.session_state["aderencia_confirmado"] = False
                            if "talentos_aderencia_temporarios" in st.session_state:
                                del st.session_state["talentos_aderencia_temporarios"]
                            st.rerun()

        # Criar abas do Streamlit para separar Aderência e Harmonia de Equipe
        tab_req, tab_harm = st.tabs(["Aderência aos Requisitos da Vaga", "Escolha por Harmonia de Equipe"])

        with tab_req:
            # Renderizar os Cards dos Candidatos Associados
            associated_names = st.session_state["candidatos_vagas"].get(vaga_id_int, [])
            
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
                        if vaga_kan_list:
                            t_kan_norm = remover_acentos(t_kan).upper().strip()
                            vaga_kan_list_norm = [remover_acentos(k).upper().strip() for k in vaga_kan_list]
                            if talento_kan_norm in vaga_kan_list_norm:
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
                            "perfil_list": t_perfis,
                            "categoria_list": t_cats,
                            "qualidades_list": t_quals,
                            "pts_kan": pts_kan,
                            "pts_perfil": pts_perfil,
                            "pts_qual": pts_qual,
                            "total_pts": total_pts,
                            "aderencia_pct": r["Aderência (%)"]
                        })
                        
                # Ordenar por pontuação descendente
                candidatos_processo = sorted(candidatos_processo, key=lambda x: x["total_pts"], reverse=True)
                
                # Exibir cards lado a lado com tamanho uniforme
                cards_per_row = 4
                for i in range(0, len(candidatos_processo), cards_per_row):
                    chunk = candidatos_processo[i:i + cards_per_row]
                    cols = st.columns(cards_per_row)
                    for idx, cand in enumerate(chunk):
                        with cols[idx]:
                            with st.container(border=True):
                                # Botão de Excluir HTML (posicionado absolutamente via CSS no canto superior esquerdo)
                                import urllib.parse
                                cand_nome_encoded = urllib.parse.quote(cand['Nome'])
                                vaga_id_encoded = urllib.parse.quote(str(vaga['id']))
                                btn_excluir_html = f"""
                                <a href="?excluir_cand={cand_nome_encoded}&vaga_id={vaga_id_encoded}&nav=Processo%20seletivo" target="_self" class="btn-excluir-link" title="Remover do processo">
                                    <i class="icon-user-minus"></i>
                                </a>
                                """
                                st.markdown(btn_excluir_html, unsafe_allow_html=True)
 
                                # Gerar HTML do avatar/foto crop com halo sutil da marca (roxo/laranja)
                                if cand["foto_base64"]:
                                    avatar_html = f"""
                                    <div class="avatar-halo-wrapper">
                                        <div class="avatar-halo">
                                            <img src="data:image/png;base64,{cand["foto_base64"]}" class="avatar-img">
                                        </div>
                                    </div>
                                    """
                                else:
                                    avatar_html = f"""
                                    <div class="avatar-halo-wrapper">
                                        <div class="avatar-halo font-avatar-bg">
                                            <span class="avatar-initial">{cand["Nome"][0].upper()}</span>
                                        </div>
                                    </div>
                                    """
                                st.markdown(avatar_html, unsafe_allow_html=True)
 
                                # Nome do candidato (como link do st.button)
                                st.markdown('<div class="talent-link-container" style="text-align: center; margin-bottom: 2px;">', unsafe_allow_html=True)
                                st.button(cand['Nome'], key=f"lnk_cand_card_{cand['Nome']}_{vaga['id']}", on_click=self.app.ver_cadastro_talento, args=(cand['Nome'],))
                                st.markdown('</div>', unsafe_allow_html=True)
 
                                # Detalhes, Atributos e Score em HTML premium usando o mesmo estilo de tabela
                                kan_badges = f'<span class="cand-req-value highlight-kan">{cand["kan"].upper()}</span>' if cand["kan"] and cand["kan"] not in ("Nenhum", "Nenhum / Não Exigido") else '<span class="cand-req-value">NENHUM</span>'
                                perfis_badges = "".join([f'<span class="cand-req-value">{p.strip().upper()}</span>' for p in cand['perfil_list'] if p.strip()]) if cand['perfil_list'] else '<span class="cand-req-value">NENHUM</span>'
                                cats_badges = "".join([f'<span class="cand-req-value">{c.strip().upper()}</span>' for c in cand['categoria_list'] if c.strip()]) if cand['categoria_list'] else '<span class="cand-req-value">NENHUMA</span>'
                                quals_badges = "".join([f'<span class="cand-req-value">{q.strip().upper()}</span>' for q in cand['qualidades_list'] if q.strip()]) if cand['qualidades_list'] else '<span class="cand-req-value">NENHUMA</span>'
 
                                card_details_html = f"""
                                <p class="dob-text"><i class="icon-calendar"></i> Nascimento: {cand['data_nascimento']}</p>
                                
                                <div class="cand-req-table">
                                    <div class="cand-req-row">
                                        <div class="cand-req-label">KAN</div>
                                        <div class="cand-req-value-cell">{kan_badges}</div>
                                    </div>
                                    <div class="cand-req-row">
                                        <div class="cand-req-label">Perfis</div>
                                        <div class="cand-req-value-cell">{perfis_badges}</div>
                                    </div>
                                    <div class="cand-req-row">
                                        <div class="cand-req-label">Categorias</div>
                                        <div class="cand-req-value-cell">{cats_badges}</div>
                                    </div>
                                    <div class="cand-req-row">
                                        <div class="cand-req-label">Qualidades</div>
                                        <div class="cand-req-value-cell">{quals_badges}</div>
                                    </div>
                                    <div class="cand-req-row">
                                        <div class="cand-req-label">Aderência %</div>
                                        <div class="cand-req-value-cell">
                                            <span class="cand-req-value highlight-kan" style="font-weight: 700;">{cand['aderencia_pct']}%</span>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="score-widget">
                                    <div class="score-main">
                                        <span class="score-title">COMPATIBILIDADE</span>
                                        <div class="score-badge">
                                            <span>⚡ {cand['total_pts']} pts</span>
                                        </div>
                                    </div>
                                    <div class="score-breakdown">
                                        <div class="breakdown-item">
                                            <span class="breakdown-label">KAN</span>
                                            <span class="breakdown-val">+{cand['pts_kan']}</span>
                                        </div>
                                        <div class="breakdown-item border-l">
                                            <span class="breakdown-label">Perfil</span>
                                            <span class="breakdown-val">+{cand['pts_perfil']}</span>
                                        </div>
                                        <div class="breakdown-item border-l">
                                            <span class="breakdown-label">Qualidades</span>
                                            <span class="breakdown-val">+{cand['pts_qual']}</span>
                                        </div>
                                    </div>
                                </div>
                                """
                                st.markdown(card_details_html, unsafe_allow_html=True)
            else:
                st.info("Nenhum talento associado a este processo seletivo ainda. Clique em 'Associar Talentos' acima para selecionar participantes.")
 
            # Ordenar por aderência
            df_matching = pd.DataFrame(matching_results).sort_values(by="Aderência (%)", ascending=False)
            
            # -------------------------------------------------------------------------
            # TABELAS GERAIS E COMPARATIVOS
            # -------------------------------------------------------------------------
            st.write("---")
            st.markdown(f"<h3 class='section-title-sub'>Ranking Geral de Aderência (Todos os Talentos de {empresa_selecionada})</h3>", unsafe_allow_html=True)
            
            # Filtrar o ranking geral pela empresa selecionada
            df_matching_empresa = df_matching[df_matching["Empresa"] == empresa_selecionada]
            
            if not df_matching_empresa.empty:
                associated_cands = st.session_state["candidatos_vagas"].get(vaga_id_int, [])
                
                # Construir a tabela em HTML com scroll lateral e estilo lilás/borda branca
                table_html = """
                <div class="scrollable-table-wrapper">
                    <table class="scrollable-table">
                        <thead>
                            <tr>
                                <th>Nome</th>
                                <th>Profissão</th>
                                <th>Grupo</th>
                                <th style="text-align: center;">Aderência (%)</th>
                                <th style="text-align: center;">KAN</th>
                                <th style="text-align: center;">Perfil</th>
                                <th style="text-align: center;">Categoria</th>
                                <th style="text-align: center;">Qualidades</th>
                                <th style="text-align: center;">Ação</th>
                            </tr>
                        </thead>
                        <tbody>
                """
                
                for idx_row, row in df_matching_empresa.iterrows():
                    nome_cand = row["Nome"]
                    is_assoc = nome_cand in associated_cands
                    
                    # Codificar o nome do candidato de forma segura para URLs
                    import urllib.parse
                    nome_cand_encoded = urllib.parse.quote(nome_cand)
                    
                    # Definir botão de ação (link circular '+' ou '✓')
                    if is_assoc:
                        action_html = f'<a class="action-link-btn btn-deassoc" href="?deassoc_cand={nome_cand_encoded}&vaga_id={vaga_id_int}&nav=Processo%20seletivo" target="_self">✓</a>'
                    else:
                        action_html = f'<a class="action-link-btn btn-assoc" href="?assoc_cand={nome_cand_encoded}&vaga_id={vaga_id_int}&nav=Processo%20seletivo" target="_self">+</a>'
                    
                    table_html += f"""
                            <tr>
                                <td><strong>{nome_cand}</strong></td>
                                <td>{row["Profissão"]}</td>
                                <td>{row["Grupo"]}</td>
                                <td style="text-align: center;"><strong>{row["Aderência (%)"]}%</strong></td>
                                <td style="text-align: center;">{row["KAN"]}</td>
                                <td style="text-align: center;">{row["Perfil"]}</td>
                                <td style="text-align: center;">{row["Categoria"]}</td>
                                <td style="text-align: center;">{row["Qualidades"]}</td>
                                <td style="text-align: center;">{action_html}</td>
                            </tr>
                    """
                    
                table_html += """
                        </tbody>
                    </table>
                </div>
                """
                table_html_minified = "".join(line.strip() for line in table_html.split("\n") if line.strip())
                st.markdown(table_html_minified, unsafe_allow_html=True)
            else:
                st.info(f"Nenhum talento cadastrado originalmente na empresa {empresa_selecionada}. No entanto, você ainda pode associar livremente talentos de outras empresas ao processo usando o botão acima!")
 
            st.write("---")
            st.markdown("<h3 class='section-title-sub'>Comparativo Detalhado Side-by-Side</h3>", unsafe_allow_html=True)
            
            selected_talent_nome = st.selectbox("Selecione um talento para visualizar o comparativo detalhado:", options=df_matching["Nome"].tolist(), key="select_side_by_side_talent")
            
            talent_row = df_matching[df_matching["Nome"] == selected_talent_nome].iloc[0]
            talento_detalhes = talent_row["talento_detalhes"]
 
            col_comp1, col_comp2 = st.columns(2)
            
            with col_comp1:
                with st.container(border=True):
                    st.markdown(f"#### Requisitos da Vaga\n**{vaga_selecionada_nome}**")
                    kan_exigido_str = ", ".join(vaga_kan_list) if vaga_kan_list else "Nenhum"
                    comp_req_html = f"""
                    <div class="comp-row"><strong>KAN Exigido:</strong> <code class="code-highlight">{kan_exigido_str.upper()}</code></div>
                    <div class="comp-row"><strong>Perfis Exigidos:</strong> <code class="code-highlight">{', '.join(vaga_perfis) if vaga_perfis else 'Nenhum'}</code></div>
                    <div class="comp-row"><strong>Categorias Exigidas:</strong> <code class="code-highlight">{', '.join(vaga_cats) if vaga_cats else 'Nenhuma'}</code></div>
                    <div class="comp-row"><strong>Qualidades Exigidas:</strong> <code class="code-highlight">{', '.join(vaga_quals) if vaga_quals else 'Nenhuma'}</code></div>
                    """
                    st.markdown(comp_req_html, unsafe_allow_html=True)
 
            with col_comp2:
                with st.container(border=True):
                    st.markdown(f"#### Perfil do Talento\n**<a href='?ver_talento={selected_talent_nome}' target='_self' style='color: #F4F7FB; text-decoration: none; border-bottom: 1px dashed #F08A00;'>{selected_talent_nome}</a>**", unsafe_allow_html=True)
                    comp_talent_html = f"""
                    <div class="comp-row"><strong>KAN do Talento:</strong> <code class="code-highlight">{talento_detalhes['kan']}</code></div>
                    <div class="comp-row"><strong>Perfis do Talento:</strong> <code class="code-highlight">{', '.join(talento_detalhes['perfis']) if talento_detalhes['perfis'] else 'Nenhum'}</code></div>
                    <div class="comp-row"><strong>Categorias do Talento:</strong> <code class="code-highlight">{', '.join(talento_detalhes['categorias']) if talento_detalhes['categorias'] else 'Nenhuma'}</code></div>
                    <div class="comp-row"><strong>Qualidades do Talento:</strong> <code class="code-highlight">{', '.join(talento_detalhes['qualidades']) if talento_detalhes['qualidades'] else 'Nenhuma'}</code></div>
                    """
                    st.markdown(comp_talent_html, unsafe_allow_html=True)
 
            # Barra de progresso de aderência
            aderencia_percent = talent_row["Aderência (%)"]
            st.markdown(f"### Aderência Geral: **{aderencia_percent}%**")
            st.progress(max(0, min(100, int(aderencia_percent))))

        with tab_harm:
            # 0. Verificar se o tenant possui plano Premium ou se é o adminkan
            is_premium = st.session_state.get("tenant_tier") == "premium" or st.session_state.get("user_rights") == "admin master"
            if not is_premium:
                st.info("🔮 **Recurso Premium**")
                st.markdown("""
                <div style="padding: 20px; border-radius: 10px; background-color: var(--card-bg); border-top: 3px solid var(--card-border-top-color); margin-top: 10px;">
                    <h4 style="margin-top: 0; color: #9B30B3; font-family: 'Outfit', sans-serif;">Análise de Harmonia de Equipe</h4>
                    <p style="font-size: 0.95em; line-height: 1.5; color: var(--text-soft);">
                        O módulo de <b>Análise de Harmonia de Equipes</b> está disponível exclusivamente na versão Premium do KAN.
                    </p>
                    <p style="font-size: 0.95em; line-height: 1.5; color: var(--text-soft);">
                        Com a versão Premium, você poderá:
                    </p>
                    <ul style="font-size: 0.95em; color: var(--text-soft); padding-left: 20px; line-height: 1.6;">
                        <li>Analisar a compatibilidade comportamental de candidatos com as equipes existentes.</li>
                        <li>Identificar a harmonia e o entrosamento do time com base nos triângulos comportamentais.</li>
                        <li>Obter relatórios profundos sobre gaps comportamentais do grupo e complementaridade.</li>
                    </ul>
                    <br>
                    <p style="font-size: 0.95em; margin-bottom: 0; color: var(--text-soft);">
                        Fale com nosso suporte para ativar o upgrade!
                    </p>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                return

            import datetime
            from components.card import premium_card_container
            
            # 1. Carregar as equipes disponíveis da empresa selecionada
            equipes_disponiveis = [eq for eq in carregar_equipes() if eq.get("empresa") == empresa_selecionada]
            nomes_equipes = [eq["nome"] for eq in equipes_disponiveis if eq.get("nome")]
            
            equipe_associada = st.session_state["equipes_vagas"].get(vaga_id_int)
            
            if not equipe_associada or equipe_associada not in nomes_equipes:
                st.info("Nenhuma equipe associada a este processo seletivo ainda. Para realizar a análise de harmonia comportamental de triângulos, associe uma equipe abaixo.")
                if nomes_equipes:
                    col_eq_sel, col_eq_btn = st.columns([3, 1])
                    with col_eq_sel:
                        eq_selecionada = st.selectbox(
                            "Selecione a equipe de destino para esta vaga:",
                            options=["Nenhuma"] + nomes_equipes,
                            key=f"sel_eq_vaga_{vaga_id_int}"
                        )
                    with col_eq_btn:
                        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                        if st.button("Associar Equipe", type="primary", key=f"btn_save_eq_{vaga_id_int}", use_container_width=True):
                            if eq_selecionada != "Nenhuma":
                                st.session_state["equipes_vagas"][vaga_id_int] = eq_selecionada
                                try:
                                    check_ex = supabase_client.table("processos_seletivos").select("id").eq("vaga_id", vaga_id_int).execute()
                                    if check_ex and check_ex.data:
                                        row_id = check_ex.data[0]["id"]
                                        supabase_client.table("processos_seletivos").update({
                                            "equipe": eq_selecionada,
                                            "updated_at": "now()"
                                        }).eq("id", row_id).execute()
                                    else:
                                        supabase_client.table("processos_seletivos").insert({
                                            "vaga_id": vaga_id_int,
                                            "empresa": empresa_selecionada,
                                            "equipe": eq_selecionada,
                                            "candidatos": [],
                                            "tenant_id": st.session_state.get("tenant_id")
                                        }).execute()
                                    st.success(f"Equipe '{eq_selecionada}' associada com sucesso!")
                                    st.rerun()
                                except Exception:
                                    st.success(f"Equipe '{eq_selecionada}' associada localmente na sessão.")
                                    st.rerun()
                else:
                    st.warning("Nenhuma equipe cadastrada para a empresa selecionada. Por favor, crie equipes na tela 'Gestão de Equipes' antes de prosseguir.")
            else:
                # Se tiver equipe associada
                col_eq_info, col_eq_actions = st.columns([3.2, 1.2])
                with col_eq_info:
                    st.markdown(f"<h4 style='margin: 0; padding-top: 8px; font-family: \"Inter\", sans-serif;'>Equipe Associada: <span style='color: #F08A00; font-weight: 700; font-family: \"Inter\", sans-serif;'>{equipe_associada}</span></h4>", unsafe_allow_html=True)
                with col_eq_actions:
                    if st.button("🔄 Alterar Equipe", key=f"btn_change_eq_{vaga_id_int}", use_container_width=True):
                        st.session_state["equipes_vagas"][vaga_id_int] = None
                        try:
                            check_ex = supabase_client.table("processos_seletivos").select("id").eq("vaga_id", vaga_id_int).execute()
                            if check_ex and check_ex.data:
                                row_id = check_ex.data[0]["id"]
                                supabase_client.table("processos_seletivos").update({
                                    "equipe": None,
                                    "updated_at": "now()"
                                }).eq("id", row_id).execute()
                        except Exception:
                            pass
                        st.rerun()
                
                # Carregar os membros da equipe associada
                eq_dados = next((eq for eq in equipes_disponiveis if eq["nome"] == equipe_associada), None)
                membros_equipe = []
                lider_nome = None
                if eq_dados:
                    membros_raw = eq_dados.get("membros", [])
                    if isinstance(membros_raw, str):
                        try:
                            membros_raw = json.loads(membros_raw)
                        except:
                            membros_raw = []
                    
                    if isinstance(membros_raw, list):
                        for m in membros_raw:
                            if isinstance(m, dict):
                                nome_m = m.get("nome")
                                if nome_m:
                                    membros_equipe.append(nome_m)
                                    if m.get("lider"):
                                        lider_nome = nome_m
                            elif m:
                                membros_equipe.append(str(m))
                
                # Filtrar apenas os membros que existem em ms_dict e têm data de nascimento
                membros_validos = []
                for m_nome in membros_equipe:
                    m_info = ms_dict.get(m_nome)
                    if m_info and m_info.get("data_nascimento"):
                        membros_validos.append(m_nome)
                
                if len(membros_validos) < 2:
                    st.warning(f"A equipe '{equipe_associada}' possui apenas {len(membros_validos)} membro(s) com cadastro completo. A análise de harmonia comportamental de triângulos exige pelo menos 2 membros ativos para formar a equipe.")
                    st.info("Por favor, adicione mais membros a esta equipe na tela 'Gestão de Equipes' para habilitar a análise.")
                else:
                    st.write("---")
                    
                    # Candidatos do processo
                    associated_names = st.session_state["candidatos_vagas"].get(vaga_id_int, [])
                    
                    if not associated_names:
                        st.info("Nenhum candidato associado a este processo seletivo ainda. Associe candidatos na aba 'Aderência' para calcular a harmonia.")
                    else:
                        import itertools
                        combinacoes_membros = list(itertools.combinations(membros_validos, 2))
                        
                        # Calcular harmonia para cada candidato consolidando todos os membros
                        ranking_harmonia = []
                        with st.spinner("Calculando harmonia comportamental de triângulos para todos os membros da equipe..."):
                            for c_nome in associated_names:
                                c_info = ms_dict.get(c_nome)
                                if c_info:
                                    # Encontra KAN cadastrado do candidato
                                    t_kan_cadastrado = "Nenhum"
                                    for r in matching_results:
                                        if r["Nome"] == c_nome:
                                            t_kan_cadastrado = r["talento_detalhes"]["kan"]
                                            break
                                    
                                    vc, kc = obter_vertices_triangulo(c_nome, c_info["data_nascimento"])
                                    
                                    # Se o KAN cadastrado for valido, usa ele. Caso contrario, o calculado
                                    kan_candidato = t_kan_cadastrado if t_kan_cadastrado not in ("Nenhum", "", None) else kc
                                    cand_dict = {"nome": c_nome, "vertices": vc, "kan": kan_candidato}
                                    
                                    # Acumuladores ponderados
                                    soma_notas = 0.0
                                    soma_pesos = 0.0
                                    soma_blocos = {
                                        "complementaridade": 0.0,
                                        "integracao": 0.0,
                                        "balanceamento": 0.0,
                                        "entrega": 0.0,
                                        "conflito": 0.0
                                    }
                                    
                                    melhor_trio_harmonia = -1.0
                                    melhor_trio_justificativa = ""
                                    melhor_trio_membros = None
                                    
                                    lider_trio_encontrado = False
                                    melhor_lider_trio_harmonia = -1.0
                                    melhor_lider_trio_justificativa = ""
                                    melhor_lider_trio_membros = None
                                    
                                    for m1_nome, m2_nome in combinacoes_membros:
                                        m1_info = ms_dict[m1_nome]
                                        m2_info = ms_dict[m2_nome]
                                        
                                        v1, k1 = obter_vertices_triangulo(m1_nome, m1_info["data_nascimento"])
                                        v2, k2 = obter_vertices_triangulo(m2_nome, m2_info["data_nascimento"])
                                        
                                        m1_dict = {"nome": m1_nome, "vertices": v1, "kan": k1}
                                        m2_dict = {"nome": m2_nome, "vertices": v2, "kan": k2}
                                        
                                        res_harm_trio = calcular_harmonia_trio(m1_dict, m2_dict, cand_dict)
                                        
                                        # Considere um peso maior para o líder, se houver
                                        contem_lider = (lider_nome and lider_nome in (m1_nome, m2_nome))
                                        peso_trio = 2.0 if contem_lider else 1.0
                                        
                                        soma_notas += res_harm_trio["nota_final"] * peso_trio
                                        soma_pesos += peso_trio
                                        for b_key in soma_blocos:
                                            soma_blocos[b_key] += res_harm_trio["blocos"][b_key] * peso_trio
                                            
                                        if contem_lider:
                                            if res_harm_trio["nota_final"] > melhor_lider_trio_harmonia:
                                                melhor_lider_trio_harmonia = res_harm_trio["nota_final"]
                                                melhor_lider_trio_justificativa = res_harm_trio["justificativa"]
                                                melhor_lider_trio_membros = (m1_nome, m2_nome)
                                                lider_trio_encontrado = True
                                                
                                        if res_harm_trio["nota_final"] > melhor_trio_harmonia:
                                            melhor_trio_harmonia = res_harm_trio["nota_final"]
                                            melhor_trio_justificativa = res_harm_trio["justificativa"]
                                            melhor_trio_membros = (m1_nome, m2_nome)
                                    
                                    # Finais ponderados
                                    nota_final = round(soma_notas / soma_pesos, 1) if soma_pesos > 0 else 0.0
                                    blocos_finais = {}
                                    for b_key in soma_blocos:
                                        blocos_finais[b_key] = round(soma_blocos[b_key] / soma_pesos, 2) if soma_pesos > 0 else 0.0
                                        
                                    if lider_trio_encontrado:
                                        justificativa_base = melhor_lider_trio_justificativa
                                        m_ref1, m_ref2 = melhor_lider_trio_membros
                                        lider_texto = f" Análise prioritária focada na integração com a liderança (**{lider_nome}**) e **{m_ref2 if m_ref1 == lider_nome else m_ref1}**."
                                    else:
                                        justificativa_base = melhor_trio_justificativa
                                        m_ref1, m_ref2 = melhor_trio_membros
                                        lider_texto = ""
                                        
                                    # Formatar string com todos os membros válidos para citar no texto explicativo
                                    if len(membros_validos) > 1:
                                        nomes_formatados = ", ".join(membros_validos[:-1]) + " e " + membros_validos[-1]
                                    else:
                                        nomes_formatados = membros_validos[0] if membros_validos else ""

                                    if len(membros_validos) > 2 and m_ref1 and m_ref2:
                                        alvo_pt1 = f"com a equipe formada por **{m_ref1}** e **{m_ref2}**"
                                        alvo_pt2 = f"com a equipe formada por **{m_ref2}** e **{m_ref1}**"
                                        substituicao = f"com a equipe formada por **{nomes_formatados}**"
                                        justificativa_base = justificativa_base.replace(alvo_pt1, substituicao).replace(alvo_pt2, substituicao)

                                    if len(membros_validos) > 2:
                                        justificativa_final = f"**Análise Consolidada de Equipe ({len(membros_validos)} membros):**\n\n{justificativa_base}{lider_texto}"
                                    else:
                                        justificativa_final = justificativa_base
                                        
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
                                        
                                    ranking_harmonia.append({
                                        "Nome": c_nome,
                                        "nota": nota_final,
                                        "faixa": faixa,
                                        "blocos": blocos_finais,
                                        "justificativa": justificativa_final,
                                        "vertices": vc,
                                        "kan": kan_candidato,
                                        "foto_base64": c_info.get("foto_base64")
                                    })
                        
                        # Ordenar por nota final de harmonia descendente
                        ranking_harmonia = sorted(ranking_harmonia, key=lambda x: x["nota"], reverse=True)
                        membros_trio = membros_validos
                        if True:
                                # Renderizar a lista em cards do ranking de harmonia
                                st.markdown("<h3 class='section-title-sub' style='font-family: \"Inter\", sans-serif !important;'>Ranking de Harmonia Comportamental de Equipe</h3>", unsafe_allow_html=True)
                                
                                # Exibe a tabela de ranking com scroll e barra de rolagem horizontal/vertical
                                table_harm_html = """
                                <div class="scrollable-table-wrapper">
                                    <table class="scrollable-table" style="font-family: 'Inter', sans-serif !important;">
                                        <thead>
                                            <tr>
                                                <th style="font-family: 'Inter', sans-serif !important;">Candidato</th>
                                                <th style="text-align: center; font-family: 'Inter', sans-serif !important;">Nota de Harmonia (%)</th>
                                                <th style="text-align: center; font-family: 'Inter', sans-serif !important;">Nível de Encaixe</th>
                                                <th style="text-align: center; font-family: 'Inter', sans-serif !important;">KAN Principal</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                """
                                for r in ranking_harmonia:
                                    # Cor baseada na nota
                                    n_val = r["nota"]
                                    if n_val >= 85.0:
                                        c_hex = "#4CAF50"
                                    elif n_val >= 70.0:
                                        c_hex = "#9C27B0"
                                    elif n_val >= 55.0:
                                        c_hex = "#8B5CF6" # Lilás
                                    else:
                                        c_hex = "#F44336"
                                        
                                    table_harm_html += f"""
                                            <tr>
                                                <td><strong>{r['Nome']}</strong></td>
                                                <td style="text-align: center; color: {c_hex};"><strong>{r['nota']}%</strong></td>
                                                <td style="text-align: center;"><span style="background: {c_hex}; color: #FFFFFF; font-size: 0.78rem; font-weight: 700; padding: 2px 8px; border-radius: 12px;">{r['faixa']}</span></td>
                                                <td style="text-align: center;">{r['kan']}</td>
                                            </tr>
                                    """
                                table_harm_html += """
                                        </tbody>
                                    </table>
                                </div>
                                """
                                table_harm_html_minified = "".join(line.strip() for line in table_harm_html.split("\n") if line.strip())
                                st.markdown(table_harm_html_minified, unsafe_allow_html=True)
                                
                                st.write("---")
                                
                                # Selectbox para detalhar analise de um candidato
                                cand_nomes_list = [r["Nome"] for r in ranking_harmonia]
                                c_selecionado_nome = st.selectbox(
                                    "Selecione um candidato para visualizar a Análise de Harmonia de Triângulos detalhada:",
                                    options=cand_nomes_list,
                                    key=f"harm_cand_sel_det_{vaga_id_int}"
                                )
                                
                                cand_sel_dados = next((r for r in ranking_harmonia if r["Nome"] == c_selecionado_nome), None)
                                
                                if cand_sel_dados:
                                    # Renderiza o SVG inline interativo
                                    st.markdown("<h4 style='font-family: \"Inter\", sans-serif; font-weight: 600; margin-top: 15px;'>Visualização dos Triângulos Harmônicos</h4>", unsafe_allow_html=True)
                                    
                                    # Prepara dicionario de triangulos com todos os membros da equipe e o candidato
                                    resultados_tri = {}
                                    for m_nome in membros_validos:
                                        m_info = ms_dict.get(m_nome)
                                        if m_info:
                                            v_m, _ = obter_vertices_triangulo(m_nome, m_info["data_nascimento"])
                                            resultados_tri[m_nome] = v_m
                                    
                                    resultados_tri[c_selecionado_nome] = cand_sel_dados["vertices"]
                                    
                                    svg_html = gerar_svg_triangulos_harmonicos(resultados_tri, lider_nome=lider_nome)
                                    st.markdown(svg_html, unsafe_allow_html=True)
                                    
                                    # Detalhes da Análise Premium
                                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                                    
                                    faixa_c = cand_sel_dados["faixa"]
                                    nota_c = cand_sel_dados["nota"]
                                    blocos = cand_sel_dados["blocos"]
                                    justificativa_html = converter_markdown_para_html(cand_sel_dados['justificativa'])

                                    card_diagnostico_html = f"""
<div style="
    background-color: #000000; 
    border: 1px solid #1E1E2E; 
    border-radius: 12px; 
    overflow: hidden; 
    margin-top: 15px; 
    margin-bottom: 25px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    font-family: 'Inter', sans-serif;
">
    <!-- CABEÇALHO -->
    <div style="
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        background-color: #000000;
        min-height: 60px;
    ">
        <!-- LADO ESQUERDO: ABA LARANJA -->
        <div style="
            background-color: #F08A00; 
            color: #000000; 
            padding: 18px 30px; 
            font-weight: 600; 
            font-size: 1.25rem; 
            display: flex;
            align-items: center;
            font-family: 'Inter', sans-serif;
        ">
            Análise de {c_selecionado_nome}
        </div>
        
        <!-- LADO DIREITO: BADGE DE ENCAIXE -->
        <div style="
            display: flex; 
            align-items: center; 
            gap: 12px; 
            padding-right: 30px;
            font-family: 'Inter', sans-serif;
        ">
            <span style="color: #FFFFFF; font-size: 1.15rem; font-weight: 500; font-family: 'Inter', sans-serif;">{faixa_c}</span>
            <span style="
                background-color: #F08A00; 
                color: #000000 !important; 
                padding: 6px 18px; 
                border-radius: 25px; 
                font-weight: 600; 
                font-size: 1.15rem;
                font-family: 'Inter', sans-serif;
            ">
                {round(nota_c, 1)}%
            </span>
        </div>
    </div>

    <!-- CORPO: TEXTO DA JUSTIFICATIVA -->
    <div style="
        padding: 30px; 
        color: #E0E4EC; 
        font-size: 1.05rem; 
        line-height: 1.8; 
        text-align: justify;
        white-space: pre-wrap;
        font-family: 'Inter', sans-serif;
    ">
        {justificativa_html}
    </div>

    <!-- DIVISOR HORIZONTAL LARANJA -->
    <div style="
        background-color: #F08A00; 
        color: #000000; 
        text-align: center; 
        padding: 10px 0; 
        font-weight: 600; 
        font-size: 1.1rem; 
        letter-spacing: 0.5px;
        font-family: 'Inter', sans-serif;
    ">
        Detalhamento por Critério de Equipe
    </div>

    <!-- GRID DE MÉTRICAS (5 COLUNAS) -->
    <div style="
        display: grid; 
        grid-template-columns: repeat(5, 1fr); 
        gap: 15px; 
        padding: 30px; 
        background-color: #000000; 
        text-align: center;
        font-family: 'Inter', sans-serif;
    ">
        <!-- COLUNA 1 -->
        <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
            <span style="color: #AAB3C5; font-size: 0.9rem; font-weight: 500; min-height: 38px; display: flex; align-items: center; justify-content: center; line-height: 1.2;">
                Complementaridade
            </span>
            <div style="
                background-color: #F08A00; 
                color: #000000; 
                font-weight: 600; 
                font-size: 1.6rem; 
                padding: 10px 0; 
                width: 100%; 
                border-radius: 12px;
            ">
                {round(blocos['complementaridade'], 1)}/5.0
            </div>
            <span style="color: #717D96; font-size: 0.82rem; font-weight: 500;">
                Equilíbrio de KANs
            </span>
        </div>

        <!-- COLUNA 2 -->
        <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
            <span style="color: #AAB3C5; font-size: 0.9rem; font-weight: 500; min-height: 38px; display: flex; align-items: center; justify-content: center; line-height: 1.2;">
                Integração Geométrica
            </span>
            <div style="
                background-color: #F08A00; 
                color: #000000; 
                font-weight: 600; 
                font-size: 1.6rem; 
                padding: 10px 0; 
                width: 100%; 
                border-radius: 12px;
            ">
                {round(blocos['integracao'], 1)}/5.0
            </div>
            <span style="color: #717D96; font-size: 0.82rem; font-weight: 500;">
                Conexões de Triângulos
            </span>
        </div>

        <!-- COLUNA 3 -->
        <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
            <span style="color: #AAB3C5; font-size: 0.9rem; font-weight: 500; min-height: 38px; display: flex; align-items: center; justify-content: center; line-height: 1.2;">
                Balanceamento
            </span>
            <div style="
                background-color: #F08A00; 
                color: #000000; 
                font-weight: 600; 
                font-size: 1.6rem; 
                padding: 10px 0; 
                width: 100%; 
                border-radius: 12px;
            ">
                {round(blocos['balanceamento'], 1)}/5.0
            </div>
            <span style="color: #717D96; font-size: 0.82rem; font-weight: 500;">
                Cobertura de Planos
            </span>
        </div>

        <!-- COLUNA 4 -->
        <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
            <span style="color: #AAB3C5; font-size: 0.9rem; font-weight: 500; min-height: 38px; display: flex; align-items: center; justify-content: center; line-height: 1.2;">
                Potencial de Entrega
            </span>
            <div style="
                background-color: #F08A00; 
                color: #000000; 
                font-weight: 600; 
                font-size: 1.6rem; 
                padding: 10px 0; 
                width: 100%; 
                border-radius: 12px;
            ">
                {round(blocos['entrega'], 1)}/5.0
            </div>
            <span style="color: #717D96; font-size: 0.82rem; font-weight: 500;">
                Materialidade/Praticidade
            </span>
        </div>

        <!-- COLUNA 5 -->
        <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
            <span style="color: #AAB3C5; font-size: 0.9rem; font-weight: 500; min-height: 38px; display: flex; align-items: center; justify-content: center; line-height: 1.2;">
                Segurança Relacional
            </span>
            <div style="
                background-color: #F08A00; 
                color: #000000; 
                font-weight: 600; 
                font-size: 1.6rem; 
                padding: 10px 0; 
                width: 100%; 
                border-radius: 12px;
            ">
                {round(blocos['conflito'], 1)}/5.0
            </div>
            <span style="color: #717D96; font-size: 0.82rem; font-weight: 500;">
                Mitigação de Conflitos
            </span>
        </div>
    </div>
</div>
"""
                                    card_diagnostico_html_limpo = "\n".join(line.lstrip() for line in card_diagnostico_html.split("\n"))
                                    st.markdown(card_diagnostico_html_limpo, unsafe_allow_html=True)
                                    
                                    st.write("---")
                                    
                                    # Historico de observacoes anteriores deste candidato para esta vaga
                                    hist_vaga = st.session_state["historico_harmonia_vagas"].get(vaga_id_int, [])
                                    obs_anterior = ""
                                    for h_ent in hist_vaga:
                                        if h_ent.get("candidato") == c_selecionado_nome:
                                            obs_anterior = h_ent.get("observacoes", "")
                                            break
                                            
                                    # Campo de observacoes do analista
                                    st.markdown("##### Observações Manuais do Analista")
                                    obs_text = st.text_area(
                                        "Registre notas de entrevista ou considerações estratégicas (não altera a pontuação matemática):",
                                        value=obs_anterior,
                                        placeholder="Ex: Candidato demonstrou excelente abertura para colaborar com a liderança no KAN de Finalidade, confirmando a estabilidade indicada na geometria...",
                                        key=f"obs_harm_{c_selecionado_nome}_{vaga_id_int}",
                                        height=100
                                    )
                                    
                                    # Botão para salvar
                                    if st.button("💾 Confirmar e Salvar Análise de Harmonia", type="primary", use_container_width=True, key=f"btn_save_harm_obs_{c_selecionado_nome}_{vaga_id_int}"):
                                        nova_entrada = {
                                            "candidato": c_selecionado_nome,
                                            "equipe": equipe_associada,
                                            "membros_trio": membros_trio,
                                            "nota": nota_c,
                                            "faixa": faixa_c,
                                            "data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                                            "observacoes": obs_text.strip(),
                                            "justificativa": cand_sel_dados["justificativa"]
                                        }
                                        
                                        # Atualiza na lista de historico local da vaga
                                        novo_hist = [h for h in hist_vaga if h.get("candidato") != c_selecionado_nome]
                                        novo_hist.append(nova_entrada)
                                        st.session_state["historico_harmonia_vagas"][vaga_id_int] = novo_hist
                                        
                                        # Salvar no Supabase
                                        try:
                                            check_ex = supabase_client.table("processos_seletivos").select("id").eq("vaga_id", vaga_id_int).execute()
                                            if check_ex and check_ex.data:
                                                row_id = check_ex.data[0]["id"]
                                                supabase_client.table("processos_seletivos").update({
                                                    "historico_harmonia": novo_hist,
                                                    "updated_at": "now()"
                                                }).eq("id", row_id).execute()
                                            else:
                                                supabase_client.table("processos_seletivos").insert({
                                                    "vaga_id": vaga_id_int,
                                                    "empresa": empresa_selecionada,
                                                    "candidatos": [],
                                                    "equipe": equipe_associada,
                                                    "historico_harmonia": novo_hist,
                                                    "tenant_id": st.session_state.get("tenant_id")
                                                }).execute()
                                            st.toast("Análise de harmonia salva com sucesso!", icon="✅")
                                            st.rerun()
                                        except Exception as e:
                                            st.toast(f"Análise salva localmente. Nota: Execute o script SQL no Supabase para persistência total: {e}", icon="⚠️")
                                            st.rerun()
                                    
                                    # Seção de Histórico de análises da vaga
                                    if hist_vaga:
                                        st.write("")
                                        st.markdown("#### Histórico de Análises Confirmadas")
                                        for idx_h, h_ent in enumerate(hist_vaga):
                                            with st.expander(f"📋 {h_ent['candidato']} - {h_ent['faixa']} ({h_ent['nota']}%) em {h_ent['data']}", expanded=False):
                                                st.markdown(f"<p style='font-size: 0.95rem; line-height: 1.5; color: var(--text-main); text-align: justify; white-space: pre-wrap;'>{converter_markdown_para_html(h_ent.get('justificativa', ''))}</p>", unsafe_allow_html=True)
                                                if h_ent.get("observacoes"):
                                                    st.markdown(f"<div style='background: rgba(255,255,255,0.02); padding: 10px; border-left: 3px solid #F08A00; border-radius: 4px; font-style: italic; color: #AAB3C5;'>{h_ent['observacoes']}</div>", unsafe_allow_html=True)
                                                else:
                                                    st.write("**Sem observações manuais registradas.**")

        st.markdown("</div>", unsafe_allow_html=True)
