import streamlit as st
import datetime
import json
from menus.base_menu import BaseMenu
from models.database import (
    carregar_empresas, get_supabase_admin, PERFIS_DB, LISTA_CATEGORIA_DB, QUALIDADES_DB
)
from utils.helpers import format_vaga_title


class ProcessosMenu(BaseMenu):
    def render(self):
        st.markdown("<h2 style='text-align: left; margin-bottom: 5px;'>Vagas</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.1em; color: rgba(255,255,255,0.7); margin-bottom: 20px;'>Cadastre e consulte perfis ideais de vagas para alinhamento comportamental.</p>", unsafe_allow_html=True)
        st.write("---")

        supabase_client = get_supabase_admin()
        lista_empresas_salvas = carregar_empresas()
        nomes_empresas = [e["nome_empresa"] for e in lista_empresas_salvas if e.get("nome_empresa")]

        empresa_selecionada = None
        if nomes_empresas:
            col_e1, col_e2 = st.columns([2, 2])
            with col_e1:
                empresa_selecionada = st.selectbox("Selecione a Empresa:", options=nomes_empresas, key="proc_emp_sel")
        else:
            st.info("Nenhuma empresa cadastrada no sistema. Cadastre sua primeira vaga abaixo e a respectiva empresa será criada automaticamente.")

        departamentos = ["Geral / Sem Departamento"]
        if supabase_client and empresa_selecionada:
            try:
                res_depts = supabase_client.table("hierarquia_departamentos").select("nome").eq("empresa", empresa_selecionada).order("ordem").execute()
                if res_depts.data:
                    depts_banco = [d["nome"] for d in res_depts.data if d.get("nome")]
                    if depts_banco:
                        departamentos = depts_banco
            except Exception:
                pass

        opcoes_kans = ["Nenhum / Não Exigido", "Criação", "Movimento", "Finalidade"]

        opcoes_perfis = sorted(list(set(PERFIS_DB))) if PERFIS_DB else ["Lider", "Criativo", "Executor", "Resultado", "Vendedor", "Influenciador", "Comunicador"]
        opcoes_categorias = sorted(list(set(LISTA_CATEGORIA_DB))) if LISTA_CATEGORIA_DB else ["Justo", "Inovador", "Diplomático", "Realizador", "Versátil", "Visionário", "Magnético", "Analítico", "Organizado", "Harmônico", "Comunicativo", "Intuitivo", "Conhecimento"]
        opcoes_qualidades = sorted(list(set(QUALIDADES_DB.keys()))) if QUALIDADES_DB else ["Relacionamento", "Execução", "Análise", "Coletividade", "Justiça", "Praticidade e disciplina", "Comunicação", "Versatilidade", "Intuição", "Organização", "Serviço"]

        with st.expander("Cadastrar Nova Vaga", expanded=(not nomes_empresas)):
            with st.container(border=True):
                # Se não há empresas cadastradas, pede o nome da empresa a ser criada
                empresa_selecionada_input = ""
                if not nomes_empresas:
                    st.markdown("##### Dados da Empresa")
                    empresa_selecionada_input = st.text_input("Nome da Empresa*", placeholder="Ex: Minha Empresa", key="proc_vaga_empresa_new")
                    st.write("---")

                st.markdown("##### Dados da Vaga")
                col_v1, col_v2, col_v3 = st.columns([2, 1, 2])
                with col_v1:
                    vaga_nome = st.text_input("Nome da Vaga*:", key="proc_vaga_n")
                with col_v2:
                    vaga_senioridade = st.selectbox("Senioridade*:", ["Junior", "Pleno", "Senior"], key="proc_vaga_s")
                with col_v3:
                    vaga_link = st.text_input("Link da Vaga (URL):", placeholder="https://...", key="proc_vaga_l")

                col_d1, col_d2 = st.columns([2, 2])
                with col_d1:
                    vaga_depto = st.selectbox("Departamento*:", options=departamentos, key="proc_vaga_d")
                with col_d2:
                    vaga_kan = st.selectbox("KAN Ideal*:", options=opcoes_kans, key="proc_vaga_k")

                col_p1, col_p2, col_p3 = st.columns([1, 1, 1])
                with col_p1:
                    vaga_perfis = st.multiselect("Tipos de Perfis ideais:", options=opcoes_perfis, key="proc_vaga_perf")
                with col_p2:
                    vaga_cats = st.multiselect("Categorias de Perfil ideais:", options=opcoes_categorias, key="proc_vaga_cat")
                with col_p3:
                    vaga_quals = st.multiselect("Qualidades ideais:", options=opcoes_qualidades, key="proc_vaga_qual")

                vaga_desc = st.text_area("Descrição da vaga:", height=100, key="proc_vaga_desc")

                st.write("---")
                if st.button("Salvar", type="primary", key="btn_save_vaga"):
                    # Define a empresa de destino
                    target_empresa = empresa_selecionada_input.strip() if not nomes_empresas else (empresa_selecionada or "")
                    
                    if not target_empresa:
                        st.error("O Nome da Empresa é obrigatório.")
                    elif not vaga_nome or not vaga_nome.strip():
                        st.error("O Nome da Vaga é obrigatório.")
                    else:
                        # Validação de limite de processos seletivos por ano civil
                        tenant_id = st.session_state.get("tenant_id")
                        from services.plan_limits import check_limit
                        allowed, current, max_val, msg = check_limit(tenant_id, "processes")
                        if not allowed:
                            st.error(f"⚠️ Limite Atingido: {msg}")
                            return

                        payload = {
                            "nome_vaga": vaga_nome.strip(),
                            "senioridade": vaga_senioridade,
                            "link_vaga": vaga_link.strip() if vaga_link else None,
                            "empresa": target_empresa,
                            "departamento": vaga_depto,
                            "kan_ideal": str(vaga_kan) if vaga_kan != "Nenhum / Não Exigido" else "Nenhum",
                            "perfis_ideais": json.dumps(vaga_perfis, ensure_ascii=False),
                            "categorias_ideais": json.dumps(vaga_cats, ensure_ascii=False),
                            "qualidades_ideais": json.dumps(vaga_quals, ensure_ascii=False),
                            "descricao_vaga": vaga_desc.strip() if vaga_desc else None,
                            "created_at": datetime.datetime.now().isoformat(),
                            "tenant_id": tenant_id
                        }
                        if supabase_client:
                            try:
                                # Se a empresa é nova, cria ela primeiro
                                if not nomes_empresas:
                                    supabase_client.table("empresas").insert({
                                        "nome_empresa": target_empresa,
                                        "status": "Ativa",
                                        "tenant_id": tenant_id
                                    }).execute()

                                supabase_client.table("vagas").insert(payload).execute()
                                st.cache_data.clear()
                                st.success("vaga cadastrada com sucesso.")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Erro ao salvar no banco de dados: {ex}")
                        else:
                            st.success("vaga cadastrada com sucesso.")

        st.write("### Vagas Cadastradas")
        if supabase_client and empresa_selecionada:
            try:
                res_vagas = supabase_client.table("vagas").select("*").eq("empresa", empresa_selecionada).order("created_at", desc=True).execute()
                if res_vagas.data and len(res_vagas.data) > 0:
                    for vg in res_vagas.data:
                        with st.container(border=True):
                            col_c1, col_c2 = st.columns([4, 1])
                            
                            def parse_json_list(val):
                                if not val: return []
                                if isinstance(val, list): return val
                                try: return json.loads(val)
                                except Exception: return []
                                
                            p_list = parse_json_list(vg.get('perfis_ideais'))
                            c_list = parse_json_list(vg.get('categorias_ideais'))
                            q_list = parse_json_list(vg.get('qualidades_ideais'))
                            
                            with col_c1:
                                st.markdown(f"#### {format_vaga_title(vg['nome_vaga'], vg.get('senioridade'))}")
                                
                                resumo_parts = []
                                if vg.get('kan_ideal') and vg['kan_ideal'] not in ("Nenhum", "Nenhum / Não Exigido"):
                                    resumo_parts.append(f"**KAN**: {vg['kan_ideal']}")
                                if p_list: resumo_parts.append(f"**Perfil**: {', '.join(p_list)}")
                                if c_list: resumo_parts.append(f"**Categoria**: {', '.join(c_list)}")
                                if q_list: resumo_parts.append(f"**Qualidade**: {', '.join(q_list[:3])}{'...' if len(q_list)>3 else ''}")
                                
                                st.write(" | ".join(resumo_parts) if resumo_parts else "Nenhum requisito comportamental específico.")
                                
                            with col_c2:
                                is_open = st.session_state.get(f"vaga_open_{vg['id']}", False)
                                btn_label = "Ocultar Detalhes" if is_open else "Ver Detalhes"
                                btn_key = f"btn_vaga_open_{vg['id']}" if is_open else f"btn_vaga_closed_{vg['id']}"
                                if st.button(btn_label, key=btn_key, use_container_width=True):
                                    st.session_state[f"vaga_open_{vg['id']}"] = not is_open
                                    st.rerun()
                                    
                            if st.session_state.get(f"vaga_open_{vg['id']}", False):
                                st.write("---")
                                col_d1, col_d2 = st.columns([3, 1])
                                with col_d1:
                                    st.write(f"**Departamento:** {vg.get('departamento') or 'Não informado'}")
                                    st.write(f"**KAN Ideal Completo:** {vg.get('kan_ideal') or 'Nenhum'}")
                                    if p_list: st.write(f"**Perfis Ideais:** {', '.join(p_list)}")
                                    if c_list: st.write(f"**Categorias Ideais:** {', '.join(c_list)}")
                                    if q_list: st.write(f"**Qualidades Ideais:** {', '.join(q_list)}")
                                    if vg.get('descricao_vaga'):
                                        st.write(f"**Descrição da Vaga:**\n{vg['descricao_vaga']}")
                                with col_d2:
                                    if vg.get('link_vaga'):
                                        st.markdown(f"[Link da Vaga]({vg['link_vaga']})")
                                    if st.button("Excluir Vaga", key=f"btn_delete_vaga_{vg['id']}", type="secondary", use_container_width=True):
                                        supabase_client.table("vagas").delete().eq("id", vg['id']).execute()
                                        st.rerun()
                else:
                    st.info(f"Nenhuma vaga cadastrada para a empresa {empresa_selecionada}.")
            except Exception as e:
                st.error(f"Erro ao consultar vagas: {e}")
        else:
            st.info("Selecione uma empresa para visualizar as vagas.")
