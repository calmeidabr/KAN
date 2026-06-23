import streamlit as st
import datetime
import json
import time
import os
from menus.base_menu import BaseMenu
from models.database import carregar_empresas, carregar_todos_clientes, carregar_hierarquia, carregar_cargos, carregar_equipes, get_supabase_admin
from utils.helpers import compress_image_to_b64
from utils.graphics import gerar_svg_triangulos_harmonicos
from services.harmonia import obter_vertices_triangulo

class EquipesMenu(BaseMenu):
    def render(self):
        st.markdown("<h2 style='text-align: left; margin-bottom: 5px;'>Gestão de Equipes</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.1em; color: rgba(255,255,255,0.7); margin-bottom: 20px;'>Agrupe talentos em equipes personalizadas, importando membros por empresas, departamentos ou individualmente.</p>", unsafe_allow_html=True)
        
        # CSS para formatar os botões de talento como hyperlinks e microações
        st.markdown("""
        <style>
        div.talent-link-container div.row-widget.stButton > button {
            border: none !important;
            background: transparent !important;
            padding: 0 !important;
            color: var(--accent) !important;
            text-decoration: underline !important;
            text-align: left !important;
            font-weight: bold !important;
            box-shadow: none !important;
            display: inline !important;
            margin: 0 !important;
        }
        div.talent-link-container div.row-widget.stButton > button:hover {
            color: var(--accent-hover) !important;
            background: transparent !important;
        }
        div.talent-link-container {
            display: inline-block !important;
        }
        /* Ajuste para ícones de microações nos botões das equipes */
        div[class*="st-key-btn_set_lider_"] button::before {
            content: "\\e1d6" !important;
            font-family: "lucide" !important;
            font-size: 16px !important;
            margin-right: 0 !important;
            color: #ff9f43 !important;
            font-style: normal !important;
            font-weight: normal !important;
            line-height: 1 !important;
            display: inline-block !important;
        }
        div[class*="st-key-btn_rem_"] button::before {
            content: "\\e18d" !important;
            font-family: "lucide" !important;
            font-size: 16px !important;
            margin-right: 0 !important;
            color: #ff3333 !important;
            font-style: normal !important;
            font-weight: normal !important;
            line-height: 1 !important;
            display: inline-block !important;
        }
        </style>
        """, unsafe_allow_html=True)
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
            st.error(f"Erro ao carregar equipes do banco de dados: {st.session_state['equipes_load_error']}")
            st.info("Execute o script de equipes correspondente para criar a tabela.")
            st.session_state.pop("equipes_load_error", None)

        # Inicia variáveis de estado
        if "add_equipe_mode" not in st.session_state:
            st.session_state["add_equipe_mode"] = False
        if "membros_selecionados_temp" not in st.session_state:
            st.session_state["membros_selecionados_temp"] = []

        if st.session_state["add_equipe_mode"]:
            st.subheader("Adicionar Equipe")
            from components.card import premium_card_container
            with premium_card_container(variant="default"):
                # 1. Definir o Nome da Equipe
                sugestao_nome = f"Equipe {len(equipes) + 1}"
                nome_equipe = st.text_input("Nome da Equipe*", value=sugestao_nome, key="add_eq_nome")
                foto_upload = st.file_uploader("Foto da Equipe (Opcional)", type=["png", "jpg", "jpeg", "webp"], key="add_eq_foto")

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
                            # Validação de limite de equipes
                            tenant_id = st.session_state.get("tenant_id")
                            from services.plan_limits import check_limit
                            allowed, current, max_val, msg = check_limit(tenant_id, "teams")
                            if not allowed:
                                st.error(f"⚠️ Limite Atingido: {msg}")
                                return

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
                                    st.error(f"Erro ao salvar no banco de dados: {ex}")
                                    st.info("A tabela 'equipes' pode não existir no banco de dados. Certifique-se de executar o script de equipes correspondente.")

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
                if not nomes_empresas:
                    st.button("Adicionar", type="primary", key="btn_eq_add_start", disabled=True, help="Cadastre uma empresa no menu Hierarquia / Deptos primeiro.")
                else:
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
                    
                    from components.card import premium_card_container
                    with premium_card_container(variant="interactive"):
                        # Padrão KAN de Cards
                        st.markdown('<div class="horizontal-columns-trigger"></div>', unsafe_allow_html=True)
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
                            key_temp_empresa = f"temp_empresa_{idx}"
                            
                            # Inicializa estados temporários se não existirem
                            if key_temp_membros not in st.session_state:
                                st.session_state[key_temp_membros] = list(lista_membros)
                            if key_temp_lider not in st.session_state:
                                st.session_state[key_temp_lider] = lider_atual
                            if key_temp_nome not in st.session_state:
                                st.session_state[key_temp_nome] = eq["nome"]
                            if key_temp_foto not in st.session_state:
                                st.session_state[key_temp_foto] = eq.get("foto_base64") or ""
                            if key_temp_empresa not in st.session_state:
                                st.session_state[key_temp_empresa] = eq.get("empresa") or "Todas"

                            membros_atuais = st.session_state[key_temp_membros]
                            temp_lider = st.session_state[key_temp_lider]

                            # Linha de cabeçalho: Renomear equipe e empresa associada
                            col_nome_eq1, col_emp_eq = st.columns([4, 3])
                            with col_nome_eq1:
                                novo_nome_eq = st.text_input(
                                    "Nome da Equipe:", 
                                    value=st.session_state[key_temp_nome], 
                                    key=f"txt_nome_eq_{idx}"
                                )
                                st.session_state[key_temp_nome] = novo_nome_eq
                            with col_emp_eq:
                                nova_emp_eq = st.selectbox(
                                    "Empresa Associada:",
                                    options=["Todas"] + nomes_empresas,
                                    index=(["Todas"] + nomes_empresas).index(st.session_state[key_temp_empresa]) if st.session_state[key_temp_empresa] in (["Todas"] + nomes_empresas) else 0,
                                    key=f"sb_emp_eq_{idx}"
                                )
                                st.session_state[key_temp_empresa] = nova_emp_eq

                            # Upload e exibição de foto da equipe na edição
                            col_edit_foto1, col_edit_foto2 = st.columns([1, 6])
                            with col_edit_foto1:
                                foto_ed_atual = st.session_state[key_temp_foto]
                                if foto_ed_atual:
                                    st.markdown(f'<div style="display: flex; justify-content: center; align-items: center; height: 100%;"><img src="data:image/png;base64,{foto_ed_atual}" style="width:50px; height:50px; min-width:50px; min-height:50px; max-width:50px; max-height:50px; border-radius:50%; object-fit:cover; border:2px solid #004BFF; flex-shrink:0;"/></div>', unsafe_allow_html=True)
                                else:
                                    st.markdown('<div style="display: flex; justify-content: center; align-items: center; height: 100%;"><div style="font-size: 1.5em; width: 50px; height: 50px; min-width: 50px; min-height: 50px; max-width: 50px; max-height: 50px; border-radius: 50%; background: rgba(0, 75, 255, 0.08); border: 2px solid #004BFF; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #004BFF; flex-shrink: 0;">T</div></div>', unsafe_allow_html=True)
                            with col_edit_foto2:
                                upload_ed_file = st.file_uploader("Alterar Foto da Equipe", type=["png", "jpg", "jpeg", "webp"], key=f"file_edit_foto_{idx}")
                                if upload_ed_file:
                                    foto_ed_b64 = compress_image_to_b64(upload_ed_file, max_width=400)
                                    if foto_ed_b64 and foto_ed_b64 != st.session_state[key_temp_foto]:
                                        st.session_state[key_temp_foto] = foto_ed_b64
                                        st.rerun()

                            st.write("")

                            # Seção para adicionar novos membros temporariamente
                            st.write("---")
                            st.markdown("##### ➕ Adicionar Membros à Equipe")
                            talentos_disponiveis = sorted([nome for nome in clientes.keys() if nome not in membros_atuais])
                            if talentos_disponiveis:
                                col_add_sel, col_add_btn = st.columns([5, 2])
                                with col_add_sel:
                                    membros_a_adicionar = st.multiselect(
                                        "Selecione talentos para adicionar a esta equipe:",
                                        options=talentos_disponiveis,
                                        key=f"ms_add_membros_{idx}",
                                        label_visibility="collapsed"
                                    )
                                with col_add_btn:
                                    if st.button("➕ Adicionar", key=f"btn_add_membros_action_{idx}", use_container_width=True):
                                        if membros_a_adicionar:
                                            st.session_state[key_temp_membros].extend(membros_a_adicionar)
                                            st.toast(f"✅ {len(membros_a_adicionar)} membro(s) adicionado(s) temporariamente! Salve as alterações para confirmar.", icon="✅")
                                            st.rerun()
                            else:
                                st.caption("Todos os talentos cadastrados já pertencem a esta equipe.")
                            
                            st.write("---")

                            if not membros_atuais:
                                st.info("Nenhum membro vinculado a esta equipe no momento.")
                            else:
                                st.caption("Clique no ícone de Coroa para definir a liderança (salva instantaneamente) ou no ícone de Lixeira para remover o membro.")
                                # Cards interativos com controles de Liderança e Exclusão
                                cols = st.columns(3)
                                for m_idx, m_nome in enumerate(sorted(membros_atuais)):
                                    col = cols[m_idx % 3]
                                    m_info = clientes.get(m_nome)
                                    is_lider_m = (temp_lider == m_nome)

                                    with col:
                                        from components.card import premium_card_container
                                        card_variant = "selected" if is_lider_m else "default"
                                        with premium_card_container(variant=card_variant):
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

                                            col_img, col_txt = st.columns([1, 3.5])
                                            with col_img:
                                                st.markdown(avatar_html, unsafe_allow_html=True)
                                            with col_txt:
                                                st.markdown('<div class="talent-link-container" style="display: block; font-size: 0.9em; margin-bottom: 2px;">', unsafe_allow_html=True)
                                                st.button(m_nome, key=f"lnk_eq_m_ed_{idx}_{m_idx}", on_click=self.app.ver_cadastro_talento, args=(m_nome,))
                                                if is_lider_m:
                                                    st.markdown('<span style="color: #ff9f43; font-weight: bold; font-size: 0.8em; display: inline-block; margin-left: 4px;"><i class="icon-crown" style="font-size:12px; margin-right:2px; vertical-align:middle;"></i>Líder</span>', unsafe_allow_html=True)
                                                st.markdown('</div>', unsafe_allow_html=True)
                                                st.markdown(f"<span style='font-size:0.75em; opacity:0.7; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; display:block; margin-top: -2px;'>{m_role}</span>", unsafe_allow_html=True)

                                            col_btn1, col_btn2 = st.columns(2)
                                            with col_btn1:
                                                help_lider = "Remover Liderança" if is_lider_m else "Tornar Líder"
                                                if st.button(" ", key=f"btn_set_lider_eq_{idx}_{m_idx}", help=help_lider, use_container_width=True, type="primary" if is_lider_m else "secondary"):
                                                    novo_lider = None if is_lider_m else m_nome
                                                    st.session_state[key_temp_lider] = novo_lider
                                                    
                                                    # Salva liderança no banco instantaneamente
                                                    novos_membros_payload = []
                                                    for nome_temp in st.session_state[key_temp_membros]:
                                                        novos_membros_payload.append({
                                                            "nome": nome_temp,
                                                            "lider": (nome_temp == novo_lider)
                                                        })
                                                    
                                                    sucesso_lider = False
                                                    payload = {
                                                        "membros": novos_membros_payload,
                                                        "updated_at": datetime.datetime.now().isoformat()
                                                    }
                                                    if supabase_client:
                                                        try:
                                                            supabase_client.table("equipes").update(payload).eq("nome", eq["nome"]).execute()
                                                            sucesso_lider = True
                                                        except Exception as ex:
                                                            st.error(f"Erro ao salvar no banco de dados: {ex}")
                                                    
                                                    if not sucesso_lider:
                                                        if "equipes_local_data" in st.session_state:
                                                            for eq_local in st.session_state["equipes_local_data"]:
                                                                if eq_local["nome"] == eq["nome"]:
                                                                    eq_local["membros"] = json.dumps(novos_membros_payload, ensure_ascii=False)
                                                                    sucesso_lider = True
                                                                    break
                                                    if sucesso_lider:
                                                        st.cache_data.clear()
                                                        st.toast(f"👑 {m_nome} definido como Líder da Equipe!" if novo_lider else "Liderança removida!")
                                                        time.sleep(1)
                                                        st.rerun()

                                            with col_btn2:
                                                if st.button(" ", key=f"btn_rem_eq_{idx}_{m_idx}", help="Excluir da Equipe", use_container_width=True, type="secondary"):
                                                    st.session_state[key_temp_membros].remove(m_nome)
                                                    if temp_lider == m_nome:
                                                        st.session_state[key_temp_lider] = None
                                                    
                                                    # Salva exclusão no banco instantaneamente
                                                    novo_lider = st.session_state[key_temp_lider]
                                                    novos_membros_payload = []
                                                    for nome_temp in st.session_state[key_temp_membros]:
                                                        novos_membros_payload.append({
                                                            "nome": nome_temp,
                                                            "lider": (nome_temp == novo_lider)
                                                        })
                                                    
                                                    sucesso_excluir = False
                                                    payload = {
                                                        "membros": novos_membros_payload,
                                                        "updated_at": datetime.datetime.now().isoformat()
                                                    }
                                                    if supabase_client:
                                                        try:
                                                            supabase_client.table("equipes").update(payload).eq("nome", eq["nome"]).execute()
                                                            sucesso_excluir = True
                                                        except Exception as ex:
                                                            st.error(f"Erro ao salvar no banco de dados: {ex}")
                                                    
                                                    if not sucesso_excluir:
                                                        if "equipes_local_data" in st.session_state:
                                                            for eq_local in st.session_state["equipes_local_data"]:
                                                                if eq_local["nome"] == eq["nome"]:
                                                                    eq_local["membros"] = json.dumps(novos_membros_payload, ensure_ascii=False)
                                                                    sucesso_excluir = True
                                                                    break
                                                    if sucesso_excluir:
                                                        st.cache_data.clear()
                                                        st.toast(f"❌ {m_nome} removido da equipe!")
                                                        time.sleep(1)
                                                        st.rerun()

                            st.write("")
                            # Rodapé com ações de Salvar / Resetar
                            col_save1, col_save2 = st.columns([3, 3])
                            with col_save1:
                                has_changes = (
                                    st.session_state[key_temp_membros] != lista_membros or
                                    st.session_state[key_temp_lider] != lider_atual or
                                    st.session_state[key_temp_nome].strip() != eq["nome"] or
                                    st.session_state[key_temp_foto] != (eq.get("foto_base64") or "") or
                                    st.session_state[key_temp_empresa] != (eq.get("empresa") or "Todas")
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
                                            "empresa": st.session_state[key_temp_empresa] if st.session_state[key_temp_empresa] != "Todas" else None,
                                            "updated_at": datetime.datetime.now().isoformat()
                                        }
                                        if supabase_client:
                                            try:
                                                supabase_client.table("equipes").update(payload).eq("nome", eq["nome"]).execute()
                                                sucesso_save = True
                                            except Exception as ex:
                                                st.error(f"Erro ao salvar no banco de dados: {ex}")
                                                
                                        if not sucesso_save:
                                            # Local fallback
                                            if "equipes_local_data" in st.session_state:
                                                for eq_local in st.session_state["equipes_local_data"]:
                                                    if eq_local["nome"] == eq["nome"]:
                                                        eq_local["nome"] = nome_final
                                                        eq_local["membros"] = json.dumps(novos_membros, ensure_ascii=False)
                                                        eq_local["foto_base64"] = st.session_state[key_temp_foto]
                                                        eq_local["empresa"] = st.session_state[key_temp_empresa] if st.session_state[key_temp_empresa] != "Todas" else None
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
                                            st.session_state.pop(key_temp_empresa, None)
                                            time.sleep(1)
                                            st.rerun()

                                if st.button("Resetar Alterações", key=f"btn_reset_changes_{idx}", use_container_width=True):
                                    st.session_state.pop(key_temp_membros, None)
                                    st.session_state.pop(key_temp_lider, None)
                                    st.session_state.pop(key_temp_nome, None)
                                    st.session_state.pop(key_temp_foto, None)
                                    st.session_state.pop(key_temp_empresa, None)
                                    st.rerun()

                        # ── Seção: Triângulos Harmônicos ────────────────────────
                        if st.session_state.get(f"eq_tri_{idx}", False):
                            st.write("---")
                            st.markdown("### <i class='icon-activity' style='font-size: 20px; vertical-align: middle; margin-right: 8px; color: #F18617;'></i>Triângulos Harmônicos da Equipe", unsafe_allow_html=True)

                            def _calcular_vertices(nome_comp, data_nasc_str):
                                """Retorna lista de 3 vértices do triângulo harmônico usando a função compartilhada."""
                                try:
                                    verts, kan = obter_vertices_triangulo(nome_comp, data_nasc_str)
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
                                    try:
                                        svg_html = gerar_svg_triangulos_harmonicos(resultados_tri, lider_nome=lider_atual)
                                        st.markdown(svg_html, unsafe_allow_html=True)
                                    except Exception as ex:
                                        st.error(f"Erro ao gerar gráfico interativo: {ex}")
                                else:
                                    st.warning("Nenhum triângulo harmônico pôde ser calculado para os membros selecionados.")
