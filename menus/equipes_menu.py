import streamlit as st
import datetime
import json
import time
import os
from collections import Counter
from PIL import Image, ImageDraw, ImageFont
from menus.base_menu import BaseMenu
from models.database import carregar_empresas, carregar_todos_clientes, carregar_hierarquia, carregar_cargos, carregar_equipes, get_supabase_admin
from services.numerologia import calcular_numerologia, reduce_number
from services.perfil import calcular_perfil_comportamental
from utils.helpers import compress_image_to_b64

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

        # Diagnóstico: exibe erro de carregamento se houver
        if st.session_state.get("equipes_load_error"):
            st.error(f"Erro ao carregar equipes do Supabase: {st.session_state['equipes_load_error']}")
            st.info("Execute o script `equipes_schema.sql` no SQL Editor do Supabase para criar a tabela.")
            st.session_state.pop("equipes_load_error", None)

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
                foto_upload = st.file_uploader("Foto da Equipe (Opcional)", type=["png", "jpg", "jpeg"], key="add_eq_foto")

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

                # Busca textual por grupo
                busca_grupo = st.text_input(
                    "Buscar por Grupo:",
                    placeholder="Digite o grupo para filtrar (ex: Beatles, Paralamas do Sucesso)...",
                    key="add_eq_busca_grupo"
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
                    # Filtro de Profissão (Busca Textual) — apenas no campo profissao do cadastro
                    if busca_profissao.strip():
                        c_profissao = str(info.get("profissao") or "").lower().strip()
                        if busca_profissao.lower().strip() not in c_profissao:
                            continue
                    # Filtro de Grupo (Busca Textual) — campo grupo do cadastro
                    if busca_grupo.strip():
                        c_grupo = str(info.get("grupo") or "").lower().strip()
                        if busca_grupo.lower().strip() not in c_grupo:
                            continue
                    candidatos_elegiveis.append(nome)
                
                candidatos_elegiveis = sorted(candidatos_elegiveis)

                # Controla estado dos filtros para pré-seleção automática
                filtro_ativo = (emp_sel != "Todas" or dept_sel != "Todos" or cargo_sel != "Todos" or busca_profissao.strip() != "" or busca_grupo.strip() != "")
                current_filters = f"{emp_sel}_{dept_sel}_{cargo_sel}_{busca_profissao.strip()}_{busca_grupo.strip()}"
                
                # Se for a primeira execução ou se os filtros mudaram, atualizamos a seleção temporária
                if "last_filters_state" not in st.session_state or st.session_state["last_filters_state"] != current_filters:
                    st.session_state["last_filters_state"] = current_filters
                    if filtro_ativo:
                        st.session_state["membros_selecionados_temp"] = candidatos_elegiveis
                        st.session_state["eq_membros_multiselect"] = candidatos_elegiveis

                # Exibe a lista de talentos encontrados pelos filtros (só quando há filtro ativo)
                if filtro_ativo:
                    if candidatos_elegiveis:
                        st.write(f"Membros encontrados pelos filtros ({len(candidatos_elegiveis)}):")
                        st.caption(", ".join(candidatos_elegiveis))
                    else:
                        st.info("Nenhum membro atende aos filtros atuais.")

                st.write("")

                # Botões de Importação Rápida
                col_btn_lote1, col_btn_lote2, col_btn_lote_esp = st.columns([2, 2, 4])
                with col_btn_lote1:
                    if st.button("Adicionar Filtro", key="btn_eq_add_filter_all", use_container_width=True):
                        st.session_state["eq_membros_multiselect"] = list(set(st.session_state.get("eq_membros_multiselect", []) + candidatos_elegiveis))
                        st.session_state["membros_selecionados_temp"] = st.session_state["eq_membros_multiselect"]
                        st.toast(f"{len(candidatos_elegiveis)} membros adicionados!")
                        st.rerun()
                with col_btn_lote2:
                    if st.button("Limpar Seleção", key="btn_eq_clear_temp", use_container_width=True, type="secondary"):
                        st.session_state["eq_membros_multiselect"] = []
                        st.session_state["membros_selecionados_temp"] = []
                        st.toast("Seleção limpa!")
                        st.rerun()

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
                
                col_s1, col_s2, col_s3 = st.columns([1, 1, 5])
                with col_s1:
                    if st.button("Salvar", type="primary", use_container_width=True, key="btn_save_eq_final"):
                        if not nome_equipe or not nome_equipe.strip():
                            st.error("O campo 'Nome da Equipe' é obrigatório.")
                        elif not membros_finais:
                            st.error("Selecione pelo menos um membro para a equipe.")
                        else:
                            foto_b64 = ""
                            if foto_upload:
                                foto_b64 = compress_image_to_b64(foto_upload, max_width=400)

                            payload = {
                                "nome": nome_equipe.strip(),
                                "empresa": emp_sel if emp_sel != "Todas" else None,
                                "departamento": dept_sel if dept_sel != "Todos" else None,
                                "membros": membros_finais,  # lista Python → JSONB direto
                                "foto_base64": foto_b64,
                                "updated_at": datetime.datetime.now().isoformat()
                            }

                            sucesso_salvar = False
                            if supabase_client:
                                try:
                                    supabase_client.table("equipes").insert(payload).execute()
                                    sucesso_salvar = True
                                except Exception as ex:
                                    st.error(f"Erro ao salvar no Supabase: {ex}")
                                    st.info("A tabela 'equipes' pode não existir no Supabase. Execute o script equipes_schema.sql no SQL Editor do Supabase.")

                            if not sucesso_salvar:
                                # Fallback local — guarda como JSON string para compatibilidade
                                if "equipes_local_data" not in st.session_state:
                                    st.session_state["equipes_local_data"] = []
                                payload_local = dict(payload)
                                payload_local["membros"] = json.dumps(membros_finais, ensure_ascii=False)
                                payload_local["created_at"] = datetime.datetime.now().isoformat()
                                st.session_state["equipes_local_data"] = [eq for eq in st.session_state["equipes_local_data"] if eq["nome"] != payload_local["nome"]]
                                st.session_state["equipes_local_data"].append(payload_local)
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
                    lista_membros_raw = eq.get("membros", [])
                    if isinstance(lista_membros_raw, str):
                        try:
                            lista_membros_raw = json.loads(lista_membros_raw)
                        except Exception:
                            lista_membros_raw = []
                    
                    # Normaliza membros suportando lista de strings ou de dicionários (liderança)
                    lista_membros = []
                    lider_atual = None
                    for m in lista_membros_raw:
                        if isinstance(m, dict):
                            nome_m = m.get("nome")
                            lista_membros.append(nome_m)
                            if m.get("lider"):
                                lider_atual = nome_m
                        else:
                            lista_membros.append(m)
                    
                    with st.container(border=True):
                        # Padrão KAN de Cards
                        col_card1, col_card2, col_card3, col_card4, col_card5, col_card6 = st.columns([0.5, 2.6, 2.0, 1.3, 1.5, 0.6])
                        with col_card1:
                            foto_b64 = eq.get("foto_base64")
                            if foto_b64:
                                st.markdown(f'<div style="display: flex; justify-content: center; align-items: center; height: 100%;"><img src="data:image/png;base64,{foto_b64}" style="width:50px; height:50px; min-width:50px; min-height:50px; max-width:50px; max-height:50px; border-radius:50%; object-fit:cover; border:2px solid #004BFF; flex-shrink:0;"/></div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div style="display: flex; justify-content: center; align-items: center; height: 100%;"><div style="font-size: 1.5em; width: 50px; height: 50px; min-width: 50px; min-height: 50px; max-width: 50px; max-height: 50px; border-radius: 50%; background: rgba(0, 75, 255, 0.08); border: 2px solid #004BFF; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #004BFF; flex-shrink: 0;">T</div></div>', unsafe_allow_html=True)
                        with col_card2:
                            st.write(f"**{eq['nome']}**")
                            st.caption(f"{len(lista_membros)} membros cadastrados")
                        with col_card3:
                            st.write(f"Empresa: {eq.get('empresa') or 'Todas'}")
                            st.caption(f"Departamento: {eq.get('departamento') or 'Todos'}")
                        with col_card4:
                            is_open = st.session_state.get(f"eq_open_{idx}", False)
                            btn_label = "Ocultar" if is_open else "Editar"
                            if st.button(btn_label, key=f"btn_v_eq_{idx}", use_container_width=True):
                                st.session_state[f"eq_open_{idx}"] = not is_open
                                st.rerun()
                        with col_card5:
                            tri_open = st.session_state.get(f"eq_tri_{idx}", False)
                            tri_label = "Ocultar" if tri_open else "Triângulos"
                            if st.button(tri_label, key=f"btn_tri_eq_{idx}", use_container_width=True):
                                st.session_state[f"eq_tri_{idx}"] = not tri_open
                                st.rerun()
                        with col_card6:
                            if st.button(" ", key=f"btn_d_eq_{idx}", type="secondary", use_container_width=True):
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

                        if st.session_state.get(f"eq_open_{idx}", False):
                            st.write("---")
                            st.markdown("**Lista de Integrantes da Equipe:**")

                            key_temp_membros = f"temp_membros_{idx}"
                            key_temp_lider = f"temp_lider_{idx}"
                            key_temp_nome = f"temp_nome_{idx}"
                            key_temp_foto = f"temp_foto_{idx}"
                            
                            # Inicializa estados temporários se não existirem
                            if key_temp_membros not in st.session_state:
                                st.session_state[key_temp_membros] = list(lista_membros)
                            if key_temp_lider not in st.session_state:
                                st.session_state[key_temp_lider] = lider_atual
                            if key_temp_nome not in st.session_state:
                                st.session_state[key_temp_nome] = eq["nome"]
                            if key_temp_foto not in st.session_state:
                                st.session_state[key_temp_foto] = eq.get("foto_base64") or ""

                            membros_atuais = st.session_state[key_temp_membros]
                            temp_lider = st.session_state[key_temp_lider]

                            # Linha de cabeçalho: Renomear equipe e checkbox de liderança
                            col_nome_eq1, col_nome_eq2 = st.columns([4, 3])
                            with col_nome_eq1:
                                novo_nome_eq = st.text_input(
                                    "Nome da Equipe:", 
                                    value=st.session_state[key_temp_nome], 
                                    key=f"txt_nome_eq_{idx}"
                                )
                                st.session_state[key_temp_nome] = novo_nome_eq
                            with col_nome_eq2:
                                st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                                edit_lider_mode = st.checkbox("Definir Líder da Equipe", key=f"chk_edit_lider_{idx}")

                            # Upload e exibição de foto da equipe na edição
                            col_edit_foto1, col_edit_foto2 = st.columns([1, 6])
                            with col_edit_foto1:
                                foto_ed_atual = st.session_state[key_temp_foto]
                                if foto_ed_atual:
                                    st.markdown(f'<div style="display: flex; justify-content: center; align-items: center; height: 100%;"><img src="data:image/png;base64,{foto_ed_atual}" style="width:50px; height:50px; min-width:50px; min-height:50px; max-width:50px; max-height:50px; border-radius:50%; object-fit:cover; border:2px solid #004BFF; flex-shrink:0;"/></div>', unsafe_allow_html=True)
                                else:
                                    st.markdown('<div style="display: flex; justify-content: center; align-items: center; height: 100%;"><div style="font-size: 1.5em; width: 50px; height: 50px; min-width: 50px; min-height: 50px; max-width: 50px; max-height: 50px; border-radius: 50%; background: rgba(0, 75, 255, 0.08); border: 2px solid #004BFF; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #004BFF; flex-shrink: 0;">T</div></div>', unsafe_allow_html=True)
                            with col_edit_foto2:
                                upload_ed_file = st.file_uploader("Alterar Foto da Equipe", type=["png", "jpg", "jpeg"], key=f"file_edit_foto_{idx}")
                                if upload_ed_file:
                                    foto_ed_b64 = compress_image_to_b64(upload_ed_file, max_width=400)
                                    if foto_ed_b64 and foto_ed_b64 != st.session_state[key_temp_foto]:
                                        st.session_state[key_temp_foto] = foto_ed_b64
                                        st.rerun()

                            st.write("")

                            if not membros_atuais:
                                st.info("Nenhum membro vinculado a esta equipe no momento.")
                            else:
                                if edit_lider_mode:
                                    st.caption("Clique em **Tornar Líder** para eleger o líder e/ou **Excluir** para remover o membro.")
                                    # Cards interativos com controles de Liderança e Exclusão
                                    cols = st.columns(3)
                                    for m_idx, m_nome in enumerate(sorted(membros_atuais)):
                                        col = cols[m_idx % 3]
                                        m_info = clientes.get(m_nome)
                                        badge_lider_temp = '<span style="color: #ff9f43; font-weight: bold; font-size: 0.85em; display: inline-block; margin-left: 6px;"><i class="icon-crown" style="font-size:14px; margin-right:4px; vertical-align:middle;"></i>Líder</span>' if m_nome == temp_lider else ''

                                        with col:
                                            with st.container(border=True):
                                                avatar_html = ""
                                                m_role = "Cadastro não encontrado"
                                                if m_info:
                                                    m_foto = m_info.get("foto_base64")
                                                    avatar_html = f'<img src="data:image/png;base64,{m_foto}" style="width:50px; height:50px; border-radius:50%; object-fit:cover; border:2px solid #F18617; flex-shrink:0;"/>' if m_foto else '<div style="width:50px; height:50px; border-radius:50%; background:rgba(241,134,23,0.2); border:2px solid #F18617; display:flex; align-items:center; justify-content:center; font-size:1.5em; flex-shrink:0;"><i class="icon-user" style="font-size:24px; color:#F18617;"></i></div>'
                                                    
                                                    m_profissao = m_info.get("profissao", "")
                                                    if "profissao" not in m_info:
                                                        m_profissao = m_info.get("cargo", "")
                                                        m_cargo_oficial = ""
                                                    else:
                                                        m_cargo_oficial = m_info.get("cargo", "")
                                                    
                                                    m_role = m_profissao or "Sem Profissão"
                                                    if m_cargo_oficial:
                                                        m_role = f"{m_role} ({m_cargo_oficial})"
                                                else:
                                                    avatar_html = '<div style="width:50px; height:50px; border-radius:50%; background:rgba(241,134,23,0.2); border:2px solid #F18617; display:flex; align-items:center; justify-content:center; font-size:1.5em; flex-shrink:0;"><i class="icon-help-circle" style="font-size:24px; color:#F18617;"></i></div>'

                                                card_header_html = f"""
                                                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                                                    {avatar_html}
                                                    <div style="min-width: 0; flex-grow: 1;">
                                                        <strong style="display:block; font-size:0.92em; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{m_nome} {badge_lider_temp}</strong>
                                                        <span style="font-size:0.78em; opacity:0.7; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; display:block;">{m_role}</span>
                                                    </div>
                                                </div>
                                                """
                                                card_header_html_clean = "".join(line.strip() for line in card_header_html.split("\n"))
                                                st.markdown(card_header_html_clean, unsafe_allow_html=True)

                                                col_btn1, col_btn2 = st.columns(2)
                                                with col_btn1:
                                                    is_selected = (temp_lider == m_nome)
                                                    if is_selected:
                                                        st.button("Líder", key=f"btn_sel_{idx}_{m_idx}", type="primary", disabled=True, use_container_width=True)
                                                    else:
                                                        if st.button("Tornar Líder", key=f"btn_set_{idx}_{m_idx}", use_container_width=True):
                                                            st.session_state[key_temp_lider] = m_nome
                                                            st.rerun()
                                                with col_btn2:
                                                    if st.button("Excluir", key=f"btn_excluir_ed_{idx}_{m_idx}", use_container_width=True, type="secondary"):
                                                        st.session_state[key_temp_membros].remove(m_nome)
                                                        if temp_lider == m_nome:
                                                            st.session_state[key_temp_lider] = None
                                                        st.rerun()
                                else:
                                    st.caption("Clique em **Excluir da Equipe** para remover o membro.")
                                    # Cards interativos apenas com opção de Exclusão
                                    cols = st.columns(3)
                                    for m_idx, m_nome in enumerate(sorted(membros_atuais)):
                                        col = cols[m_idx % 3]
                                        m_info = clientes.get(m_nome)
                                        badge_lider_temp = '<span style="color: #ff9f43; font-weight: bold; font-size: 0.85em; display: inline-block; margin-left: 6px;"><i class="icon-crown" style="font-size:14px; margin-right:4px; vertical-align:middle;"></i>Líder</span>' if m_nome == temp_lider else ''

                                        with col:
                                            with st.container(border=True):
                                                avatar_html = ""
                                                m_role = "Cadastro não encontrado"
                                                if m_info:
                                                    m_foto = m_info.get("foto_base64")
                                                    avatar_html = f'<img src="data:image/png;base64,{m_foto}" style="width:50px; height:50px; border-radius:50%; object-fit:cover; border:2px solid #F18617; flex-shrink:0;"/>' if m_foto else '<div style="width:50px; height:50px; border-radius:50%; background:rgba(241,134,23,0.2); border:2px solid #F18617; display:flex; align-items:center; justify-content:center; font-size:1.5em; flex-shrink:0;"><i class="icon-user" style="font-size:24px; color:#F18617;"></i></div>'
                                                    
                                                    m_profissao = m_info.get("profissao", "")
                                                    if "profissao" not in m_info:
                                                        m_profissao = m_info.get("cargo", "")
                                                        m_cargo_oficial = ""
                                                    else:
                                                        m_cargo_oficial = m_info.get("cargo", "")
                                                    
                                                    m_role = m_profissao or "Sem Profissão"
                                                    if m_cargo_oficial:
                                                        m_role = f"{m_role} ({m_cargo_oficial})"
                                                else:
                                                    avatar_html = '<div style="width:50px; height:50px; border-radius:50%; background:rgba(241,134,23,0.2); border:2px solid #F18617; display:flex; align-items:center; justify-content:center; font-size:1.5em; flex-shrink:0;"><i class="icon-help-circle" style="font-size:24px; color:#F18617;"></i></div>'

                                                card_header_html = f"""
                                                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                                                    {avatar_html}
                                                    <div style="min-width: 0; flex-grow: 1;">
                                                        <strong style="display:block; font-size:0.92em; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{m_nome} {badge_lider_temp}</strong>
                                                        <span style="font-size:0.78em; opacity:0.7; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; display:block;">{m_role}</span>
                                                    </div>
                                                </div>
                                                """
                                                card_header_html_clean = "".join(line.strip() for line in card_header_html.split("\n"))
                                                st.markdown(card_header_html_clean, unsafe_allow_html=True)

                                                if st.button("Excluir da Equipe", key=f"btn_excluir_{idx}_{m_idx}", use_container_width=True, type="secondary"):
                                                    st.session_state[key_temp_membros].remove(m_nome)
                                                    if temp_lider == m_nome:
                                                        st.session_state[key_temp_lider] = None
                                                    st.rerun()

                            st.write("")
                            # Rodapé com ações de Salvar / Resetar
                            col_save1, col_save2 = st.columns([3, 3])
                            with col_save1:
                                has_changes = (
                                    st.session_state[key_temp_membros] != lista_membros or
                                    st.session_state[key_temp_lider] != lider_atual or
                                    st.session_state[key_temp_nome].strip() != eq["nome"] or
                                    st.session_state[key_temp_foto] != (eq.get("foto_base64") or "")
                                )
                                if has_changes:
                                    st.warning("Há alterações não salvas nesta equipe!")
                                else:
                                    st.info("Nenhuma alteração pendente.")

                                current_temp_lider = st.session_state[key_temp_lider]
                                if current_temp_lider:
                                    st.write(f"Líder atual selecionado: **{current_temp_lider}**")
                                else:
                                    st.write("Líder atual selecionado: *Nenhum*")

                            with col_save2:
                                if st.button("Salvar Alterações da Equipe", key=f"btn_save_changes_{idx}", type="primary", use_container_width=True):
                                    nome_final = st.session_state[key_temp_nome].strip()
                                    if not nome_final:
                                        st.error("O nome da equipe não pode ser vazio.")
                                    else:
                                        novo_lider = st.session_state[key_temp_lider]
                                        novos_membros = []
                                        for nome_m in st.session_state[key_temp_membros]:
                                            novos_membros.append({
                                                "nome": nome_m,
                                                "lider": (nome_m == novo_lider)
                                            })
                                            
                                        sucesso_save = False
                                        payload = {
                                            "nome": nome_final,
                                            "membros": novos_membros,
                                            "foto_base64": st.session_state[key_temp_foto],
                                            "updated_at": datetime.datetime.now().isoformat()
                                        }
                                        if supabase_client:
                                            try:
                                                supabase_client.table("equipes").update(payload).eq("nome", eq["nome"]).execute()
                                                sucesso_save = True
                                            except Exception as ex:
                                                st.error(f"Erro ao salvar no Supabase: {ex}")
                                                
                                        if not sucesso_save:
                                            # Local fallback
                                            if "equipes_local_data" in st.session_state:
                                                for eq_local in st.session_state["equipes_local_data"]:
                                                    if eq_local["nome"] == eq["nome"]:
                                                        eq_local["nome"] = nome_final
                                                        eq_local["membros"] = json.dumps(novos_membros, ensure_ascii=False)
                                                        eq_local["foto_base64"] = st.session_state[key_temp_foto]
                                                        eq_local["updated_at"] = datetime.datetime.now().isoformat()
                                                        sucesso_save = True
                                                        break
                                        
                                        if sucesso_save:
                                            st.cache_data.clear()
                                            st.success("Alterações salvas com sucesso!")
                                            st.session_state.pop(key_temp_membros, None)
                                            st.session_state.pop(key_temp_lider, None)
                                            st.session_state.pop(key_temp_nome, None)
                                            st.session_state.pop(key_temp_foto, None)
                                            time.sleep(1)
                                            st.rerun()

                                if st.button("Resetar Alterações", key=f"btn_reset_changes_{idx}", use_container_width=True):
                                    st.session_state.pop(key_temp_membros, None)
                                    st.session_state.pop(key_temp_lider, None)
                                    st.session_state.pop(key_temp_nome, None)
                                    st.session_state.pop(key_temp_foto, None)
                                    st.rerun()

                        # ── Seção: Triângulos Harmônicos ────────────────────────
                        if st.session_state.get(f"eq_tri_{idx}", False):
                            st.write("---")
                            st.markdown("### <i class='icon-activity' style='font-size: 20px; vertical-align: middle; margin-right: 8px; color: #F18617;'></i>Triângulos Harmônicos da Equipe", unsafe_allow_html=True)

                            def _calcular_vertices(nome_comp, data_nasc_str):
                                """Retorna lista de 3 vértices do triângulo harmônico ou None."""
                                def _clean(v):
                                    if v is None: return None
                                    s = str(v).split(" - ")[0]
                                    return int(s) if s.isdigit() and int(s) > 0 else None
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
                                        if isinstance(v_it, int): todos_num.append(v_it)
                                        elif isinstance(v_it, str) and str(v_it).isdigit(): todos_num.append(int(v_it))
                                    for c_key in ciclos_vida:
                                        num_c = ciclos_vida[c_key].get('numero')
                                        if isinstance(num_c, int): todos_num.append(num_c)
                                    for m_key in momentos_decisivos:
                                        num_m = momentos_decisivos[m_key].get('numero')
                                        if isinstance(num_m, int): todos_num.append(num_m)
                                    num_ps = reduce_number(nasc_tuple[0])
                                    todos_num.append(num_ps)
                                    if isinstance(triangulo_base, int): todos_num.append(triangulo_base)

                                    c_tot = Counter(todos_num)
                                    r_tot = sorted([(n, c) for n, c in c_tot.items()], key=lambda x: (-x[1], x[0]))
                                    r2_v = r_tot[0][0] if r_tot else 0
                                    r3_v = r_tot[1][0] if len(r_tot) > 1 else 0
                                    r4_v = r_tot[2][0] if len(r_tot) > 2 else 0

                                    todos_comp = [
                                        {"campo": "KAN",            "valor": _clean(kan)},
                                        {"campo": "ESTRUTURAL",     "valor": _clean(estrutural)},
                                        {"campo": "DIRECIONAMENTO", "valor": _clean(direcionamento)},
                                        {"campo": "REPETIÇÃO 1",    "valor": _clean(rep1)},
                                        {"campo": "REP. MAPA",      "valor": r2_v if r2_v else None},
                                        {"campo": "REP. MAPA 2",    "valor": r3_v if r3_v else None},
                                        {"campo": "REP. MAPA 3",    "valor": r4_v if r4_v else None},
                                    ]

                                    verts = []
                                    vals_seen = set()
                                    for it in todos_comp:
                                        v_it = it["valor"]
                                        if v_it is not None and v_it not in [11, 22] and v_it not in vals_seen:
                                            verts.append({"campo": it["campo"], "valor": v_it})
                                            vals_seen.add(v_it)
                                        if len(verts) == 3:
                                            break

                                    if len(verts) == 3:
                                        return verts
                                except Exception as ex:
                                    st.warning(f"⚠️ Erro ao calcular {nome_comp}: {ex}")
                                return None

                            # Multiselect para excluir membros da visualização
                            membros_visiveis = st.multiselect(
                                "Membros incluídos na visualização:",
                                options=sorted(lista_membros),
                                default=sorted(lista_membros),
                                key=f"tri_membros_sel_{idx}"
                            )

                            if st.button("Criar Triângulos Harmônicos", key=f"btn_tri_calc_{idx}", type="primary"):
                                st.session_state[f"tri_calcular_{idx}"] = True

                            if st.session_state.get(f"tri_calcular_{idx}", False):
                                coords_map = {
                                    1: (794, 176), 2: (1037, 243), 3: (960, 380),
                                    4: (794, 585), 5: (486, 585), 6: (320, 380),
                                    7: (243, 243), 8: (486, 176), 9: (640, 120),
                                    11: (1037, 243), 22: (794, 585)
                                }

                                path_fundo = os.path.join("images", "plano_kan_fundo.jpg")

                                resultados_tri = {}
                                erros = []
                                with st.spinner("Calculando triângulos dos membros..."):
                                    for m_nome in membros_visiveis:
                                        m_info = clientes.get(m_nome)
                                        if not m_info:
                                            erros.append(f"{m_nome}: cadastro não encontrado")
                                            continue
                                        data_nasc = m_info.get("data_nascimento")
                                        if not data_nasc:
                                            erros.append(f"{m_nome}: sem data de nascimento")
                                            continue
                                        verts = _calcular_vertices(m_nome, data_nasc)
                                        if verts:
                                            resultados_tri[m_nome] = verts
                                        else:
                                            erros.append(f"{m_nome}: triângulo não formado")

                                if erros:
                                    for e_msg in erros:
                                        st.warning(f"<i class='icon-alert-triangle'></i> {e_msg}", unsafe_allow_html=True)

                                if resultados_tri:
                                    # Imagem comparativa
                                    if os.path.exists(path_fundo):
                                        try:
                                            fundo_img = Image.open(path_fundo).convert("RGBA")
                                            try:
                                                font_label = ImageFont.truetype("arial.ttf", 34)
                                            except Exception:
                                                font_label = ImageFont.load_default()

                                            img_final = fundo_img.copy()
                                            layer_notes = Image.new("RGBA", fundo_img.size, (255, 255, 255, 0))
                                            draw_notes = ImageDraw.Draw(layer_notes)

                                            cores = [
                                                (255, 200, 100, 130), (100, 200, 255, 130),
                                                (200, 255, 100, 130), (255, 100, 200, 130),
                                                (100, 255, 200, 130), (255, 160, 100, 130),
                                                (160, 100, 255, 130), (100, 160, 255, 130),
                                            ]

                                            # Ordena os triângulos para que o do líder seja desenhado por último (por cima de todos)
                                            itens_tri = list(resultados_tri.items())
                                            itens_tri_ordenados = sorted(
                                                itens_tri,
                                                key=lambda item: 1 if item[0] == lider_atual else 0
                                            )

                                            for i, (m_nome, verts) in enumerate(itens_tri_ordenados):
                                                poly_points = []
                                                for v in verts:
                                                    val_num = int(v["valor"])
                                                    if val_num in coords_map:
                                                        poly_points.append(coords_map[val_num])
                                                    else:
                                                        val_red = sum(int(d) for d in str(val_num))
                                                        if val_red in coords_map:
                                                            poly_points.append(coords_map[val_red])

                                                if len(poly_points) == 3:
                                                    cor = cores[i % len(cores)]
                                                    layer_m = Image.new("RGBA", fundo_img.size, (255, 255, 255, 0))
                                                    draw_m = ImageDraw.Draw(layer_m)
                                                    
                                                    # Desenha o preenchimento do triângulo
                                                    draw_m.polygon(poly_points, fill=cor)
                                                    
                                                    # Se for o líder, adiciona uma borda (outline) branca e mais fina
                                                    if m_nome == lider_atual:
                                                        draw_m.line(poly_points + [poly_points[0]], fill=(255, 255, 255, 255), width=3)
                                                        
                                                    img_final = Image.alpha_composite(img_final, layer_m)

                                                    cx = sum(p[0] for p in poly_points) // 3
                                                    cy = sum(p[1] for p in poly_points) // 3
                                                    primeiro_nome = str(m_nome).split()[0]
                                                    nome_display = f"L. {primeiro_nome}" if m_nome == lider_atual else primeiro_nome
                                                    draw_notes.text((cx - 20, cy - 12), nome_display, fill=(30, 30, 30), font=font_label)

                                                    # Adiciona a esfera preta no vértice do KAN (poly_points[0])
                                                    k_vertex = poly_points[0]
                                                    draw_notes.ellipse((k_vertex[0]-4, k_vertex[1]-4, k_vertex[0]+4, k_vertex[1]+4), fill=(0, 0, 0))

                                            img_final = Image.alpha_composite(img_final, layer_notes)
                                            st.image(img_final.convert("RGB"), caption=f"Comparativo de Triângulos Harmônicos — {eq['nome']}", use_container_width=True)

                                        except Exception as ex:
                                            st.error(f"Erro ao gerar imagem: {ex}")
                                    else:
                                        st.info("ℹ️ Imagem de fundo não encontrada (images/plano_kan_fundo.jpg). Os dados da tabela acima estão disponíveis.")
                                else:
                                    st.warning("Nenhum triângulo harmônico pôde ser calculado para os membros selecionados.")
