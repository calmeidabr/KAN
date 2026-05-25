import streamlit as st
import datetime
import json
import time
from menus.base_menu import BaseMenu
from models.database import carregar_empresas, carregar_todos_clientes, carregar_hierarquia, carregar_cargos, carregar_equipes, get_supabase_admin

class EquipesMenu(BaseMenu):
    def render(self):
        st.title("Gestão de Equipes")
        st.info("Agrupe talentos em equipes personalizadas, importando membros por empresas, departamentos ou individualmente.")
        st.write("---")

        supabase_client = get_supabase_admin()
        
        # Carrega dados necessários
        empresas_list = carregar_empresas()
        nomes_empresas = [e["nome_empresa"] for e in empresas_list if e.get("nome_empresa")]
        clientes = carregar_todos_clientes()
        cargos = carregar_cargos()
        equipes = carregar_equipes()

        # Inicia variáveis de estado
        if "add_equipe_mode" not in st.session_state:
            st.session_state["add_equipe_mode"] = False
        if "membros_selecionados_temp" not in st.session_state:
            st.session_state["membros_selecionados_temp"] = []

        if st.session_state["add_equipe_mode"]:
            st.subheader("Adicionar Equipe")
            with st.container(border=True):
                # 1. Definir o Nome da Equipe
                sugestao_nome = f"Equipe {len(equipes) + 1}"
                nome_equipe = st.text_input("Nome da Equipe*", value=sugestao_nome, key="add_eq_nome")

                st.write("---")
                st.markdown("**Filtros e Adição em Lote**")
                
                # Selecionar Empresa para escopo
                emp_sel = st.selectbox(
                    "Selecione a Empresa Base:",
                    options=["Todas"] + nomes_empresas,
                    key="add_eq_emp_sel"
                )

                # Carrega departamentos da empresa selecionada
                opcoes_depto = ["Todos"]
                if emp_sel != "Todas":
                    deptos_emp = carregar_hierarquia(emp_sel)
                    opcoes_depto += [d["nome"] for d in deptos_emp if d.get("nome")]
                
                dept_sel = st.selectbox(
                    "Selecione o Departamento Base:",
                    options=opcoes_depto,
                    key="add_eq_dept_sel"
                )

                # Filtro por cargo (selectbox)
                cargo_sel = st.selectbox(
                    "Filtrar por Cargo (Lista):",
                    options=["Todos"] + sorted(cargos),
                    key="add_eq_cargo_sel"
                )

                # Busca textual por profissão
                busca_profissao = st.text_input(
                    "Buscar por Profissão:",
                    placeholder="Digite a profissão para filtrar (ex: Piloto, Cantor)...",
                    key="add_eq_busca_profissao"
                )

                # Filtragem de candidatos elegíveis com base nos filtros selecionados
                candidatos_elegiveis = []
                for nome, info in clientes.items():
                    # Filtro de Empresa
                    if emp_sel != "Todas" and info.get("empresa") != emp_sel:
                        continue
                    # Filtro de Departamento
                    if dept_sel != "Todos" and emp_sel != "Todas":
                        deptos_emp = carregar_hierarquia(emp_sel)
                        dept_id_map = {d["nome"]: d["departamento_id"] for d in deptos_emp}
                        target_dept_id = dept_id_map.get(dept_sel)
                        if info.get("departamento") != target_dept_id:
                            continue
                    # Filtro de Cargo (Selectbox)
                    if cargo_sel != "Todos" and info.get("cargo") != cargo_sel:
                        continue
                    # Filtro de Profissão (Busca Textual)
                    if busca_profissao.strip():
                        c_profissao = str(info.get("profissao") or info.get("cargo") or "").lower().strip()
                        if busca_profissao.lower().strip() not in c_profissao:
                            continue
                    candidatos_elegiveis.append(nome)
                
                candidatos_elegiveis = sorted(candidatos_elegiveis)

                # Botões de Importação Rápida
                col_btn_lote1, col_btn_lote2 = st.columns(2)
                with col_btn_lote1:
                    if st.button("Adicionar Todos do Filtro em Lote", key="btn_eq_add_filter_all", use_container_width=True):
                        st.session_state["membros_selecionados_temp"] = list(set(st.session_state["membros_selecionados_temp"] + candidatos_elegiveis))
                        st.toast(f"{len(candidatos_elegiveis)} membros adicionados!")
                with col_btn_lote2:
                    if st.button("Limpar Seleção Atual", key="btn_eq_clear_temp", use_container_width=True, type="secondary"):
                        st.session_state["membros_selecionados_temp"] = []
                        st.toast("Seleção limpa!")

                st.write("---")
                st.markdown("**Seleção Fina (Um a Um)**")

                # Seleção individual (filtrada pelos critérios)
                opcoes_multiselect = sorted(list(set(candidatos_elegiveis + st.session_state["membros_selecionados_temp"])))
                membros_finais = st.multiselect(
                    "Selecione os Membros da Equipe:",
                    options=opcoes_multiselect,
                    default=st.session_state["membros_selecionados_temp"],
                    key="eq_membros_multiselect"
                )
                
                # Mantém sincronizado com o multiselect
                st.session_state["membros_selecionados_temp"] = membros_finais

                st.write(f"Total de integrantes selecionados: **{len(membros_finais)}**")
                
                st.write("---")
                col_s1, col_s2, col_s3 = st.columns([2, 2, 4])
                with col_s1:
                    if st.button("Salvar", type="primary", use_container_width=True, key="btn_save_eq_final"):
                        if not nome_equipe or not nome_equipe.strip():
                            st.error("O campo 'Nome da Equipe' é obrigatório.")
                        elif not membros_finais:
                            st.error("Selecione pelo menos um membro para a equipe.")
                        else:
                            payload = {
                                "nome": nome_equipe.strip(),
                                "empresa": emp_sel if emp_sel != "Todas" else None,
                                "departamento": dept_sel if dept_sel != "Todos" else None,
                                "membros": json.dumps(membros_finais, ensure_ascii=False),
                                "updated_at": datetime.datetime.now().isoformat()
                            }
                            
                            sucesso_salvar = False
                            if supabase_client:
                                try:
                                    supabase_client.table("equipes").insert(payload).execute()
                                    sucesso_salvar = True
                                except Exception as ex:
                                    st.error(f"Erro ao salvar no Supabase: {ex}")
                            
                            if not sucesso_salvar:
                                # Fallback local
                                if "equipes_local_data" not in st.session_state:
                                    st.session_state["equipes_local_data"] = []
                                payload["created_at"] = datetime.datetime.now().isoformat()
                                # Se já existir equipe com o mesmo nome localmente, substitui
                                st.session_state["equipes_local_data"] = [eq for eq in st.session_state["equipes_local_data"] if eq["nome"] != payload["nome"]]
                                st.session_state["equipes_local_data"].append(payload)
                                sucesso_salvar = True
                            
                            if sucesso_salvar:
                                st.cache_data.clear()
                                st.success("Equipe salva com sucesso!")
                                st.session_state["add_equipe_mode"] = False
                                st.session_state["membros_selecionados_temp"] = []
                                time.sleep(1)
                                st.rerun()
                with col_s2:
                    if st.button("Cancelar", use_container_width=True, key="btn_canc_eq_final"):
                        st.session_state["add_equipe_mode"] = False
                        st.session_state["membros_selecionados_temp"] = []
                        st.rerun()

        else:
            # Lista as Equipes Cadastradas
            col_topo1, col_topo2 = st.columns([1, 5])
            with col_topo1:
                if st.button("Adicionar", type="primary", key="btn_eq_add_start"):
                    st.session_state["add_equipe_mode"] = True
                    st.rerun()

            st.write("---")

            if not equipes:
                st.info("Nenhuma equipe cadastrada no sistema.")
            else:
                for idx, eq in enumerate(equipes):
                    # Garante conversão segura da lista de membros do JSON
                    lista_membros = eq.get("membros", [])
                    if isinstance(lista_membros, str):
                        try:
                            lista_membros = json.loads(lista_membros)
                        except Exception:
                            lista_membros = []
                    
                    with st.container(border=True):
                        # Padrão KAN de Cards
                        col_card1, col_card2, col_card3, col_card4 = st.columns([1, 3, 2, 2])
                        with col_card1:
                            st.markdown("<div style='font-size: 2.2em; text-align: center; background: rgba(241,134,23,0.15); border-radius: 10px; padding: 2px;'>T</div>", unsafe_allow_html=True)
                        with col_card2:
                            st.write(f"**{eq['nome']}**")
                            st.caption(f"{len(lista_membros)} membros cadastrados")
                        with col_card3:
                            st.write(f"Empresa: {eq.get('empresa') or 'Todas'}")
                            st.caption(f"Departamento: {eq.get('departamento') or 'Todos'}")
                        with col_card4:
                            is_open = st.session_state.get(f"eq_open_{idx}", False)
                            btn_label = "Ocultar Integrantes" if is_open else "Ver Integrantes"
                            
                            col_sub_btn1, col_sub_btn2 = st.columns(2)
                            with col_sub_btn1:
                                if st.button(btn_label, key=f"btn_v_eq_{idx}", use_container_width=True):
                                    st.session_state[f"eq_open_{idx}"] = not is_open
                                    st.rerun()
                            with col_sub_btn2:
                                if st.button("Excluir Equipe", key=f"btn_d_eq_{idx}", type="secondary", use_container_width=True):
                                    excluido = False
                                    if supabase_client:
                                        try:
                                            supabase_client.table("equipes").delete().eq("nome", eq["nome"]).execute()
                                            excluido = True
                                        except Exception as ex:
                                            st.error(f"Erro ao excluir: {ex}")
                                    if not excluido:
                                        if "equipes_local_data" in st.session_state:
                                            st.session_state["equipes_local_data"] = [item for item in st.session_state["equipes_local_data"] if item["nome"] != eq["nome"]]
                                        excluido = True
                                    if excluido:
                                        st.cache_data.clear()
                                        st.success("Equipe excluída!")
                                        time.sleep(1)
                                        st.rerun()
                                        
                        # Conteúdo expansível / colapsável
                        if st.session_state.get(f"eq_open_{idx}", False):
                            st.write("---")
                            st.markdown("**Lista de Integrantes da Equipe:**")
                            
                            if not lista_membros:
                                st.write("Nenhum membro vinculado a esta equipe.")
                            else:
                                for m_nome in sorted(lista_membros):
                                    m_info = clientes.get(m_nome)
                                    if m_info:
                                        m_profissao = m_info.get("profissao", "")
                                        if "profissao" not in m_info:
                                            m_profissao = m_info.get("cargo", "")
                                            m_cargo_oficial = ""
                                        else:
                                            m_cargo_oficial = m_info.get("cargo", "")
                                        
                                        m_role = m_profissao or "Sem Profissão"
                                        if m_cargo_oficial:
                                            m_role = f"{m_role} ({m_cargo_oficial})"
                                            
                                        m_foto = m_info.get("foto_base64")
                                        
                                        # Renderiza membro com miniatura de foto
                                        col_m_avatar, col_m_desc = st.columns([1, 20])
                                        with col_m_avatar:
                                            if m_foto:
                                                st.markdown(f'<img src="data:image/png;base64,{m_foto}" style="width: 20px; height: 20px; border-radius: 50%; object-fit: cover; border: 1px solid #F18617; vertical-align: middle;">', unsafe_allow_html=True)
                                            else:
                                                st.markdown('<span style="font-size: 1.1em; vertical-align: middle;">👤</span>', unsafe_allow_html=True)
                                        with col_m_desc:
                                            st.markdown(f"<span style='vertical-align: middle;'>**{m_nome}** — {m_role}</span>", unsafe_allow_html=True)
                                    else:
                                        st.write(f"• **{m_nome}** (Cadastro não encontrado na base)")
