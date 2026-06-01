import streamlit as st
import datetime
import time
from menus.base_menu import BaseMenu
from models.database import carregar_empresas, carregar_hierarquia, get_supabase, get_supabase_admin, carregar_todos_clientes, carregar_cargos

@st.dialog("Dados do Talento", width="large")
def modal_detalhes_talento(nome, info, dept_map_list):
    st.markdown(f"### {nome}")
    col1, col2 = st.columns([1, 2])
    with col1:
        foto_b64 = info.get("foto_base64")
        if foto_b64:
            st.markdown(f'<img src="data:image/png;base64,{foto_b64}" style="width: 100%; max-width: 180px; border-radius: 12px; border: 2px solid var(--accent); box-shadow: 0 4px 10px rgba(0,0,0,0.3);">', unsafe_allow_html=True)
        else:
            st.markdown('<div style="width: 150px; height: 150px; border-radius: 12px; background: rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center; border: 1px dashed rgba(255,255,255,0.2);"><span style="font-size: 4em; color: rgba(255,255,255,0.2);"><i class="icon-user"></i></span></div>', unsafe_allow_html=True)
    with col2:
        st.write(f"**Data de Nascimento:** {info.get('data_nascimento', 'Não informada')}")
        st.write(f"**Cargo/Profissão:** {info.get('cargo', 'Não informado')}")
        st.write(f"**Grupo:** {info.get('grupo', 'Não informado')}")
        st.write(f"**Empresa:** {info.get('empresa', 'Não associada')}")
        
        depto_id = info.get("departamento")
        depto_nome = dept_map_list.get(depto_id, "Não associado") if depto_id else "Não associado"
        st.write(f"**Departamento:** {depto_nome}")
        
        linkedin = info.get("linkedin_url")
        if linkedin:
            st.write(f"**LinkedIn:** [Ver Perfil]({linkedin})")
        else:
            st.write("**LinkedIn:** Não informado")
            
    st.write("---")
    st.markdown("**Experiências Profissionais / Bio:**")
    st.info(info.get("experiencias") or "Nenhuma informação adicional cadastrada.")

@st.dialog("Editar Cargo do Talento", width="small")
def modal_editar_cargo(nome, cargo_atual, cargos_list):
    st.markdown(f"**Talento:** `{nome}`")
    novo_cargo = st.selectbox(
        "Selecione o Novo Cargo:",
        options=cargos_list,
        index=cargos_list.index(cargo_atual) if cargo_atual in cargos_list else 0,
        key=f"ed_cargo_sel_{nome}"
    )
    
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Salvar", type="primary", use_container_width=True, key=f"btn_save_ed_cargo_{nome}"):
            client_admin = get_supabase_admin()
            if client_admin:
                try:
                    client_admin.table("mapas_salvos").update({
                        "cargo": novo_cargo
                    }).eq("nome", nome).execute()
                    st.cache_data.clear()
                    st.success("Cargo atualizado!")
                    time.sleep(1)
                    st.rerun()
                except Exception as ex:
                    st.error(f"Erro ao salvar no banco: {ex}")
            else:
                # Fallback local
                if "clientes_local_data" not in st.session_state:
                    st.session_state["clientes_local_data"] = {}
                if nome not in st.session_state["clientes_local_data"]:
                    clientes = carregar_todos_clientes()
                    st.session_state["clientes_local_data"][nome] = clientes.get(nome, {}).copy()
                st.session_state["clientes_local_data"][nome]["cargo"] = novo_cargo
                st.cache_data.clear()
                st.success("Cargo atualizado localmente!")
                time.sleep(1)
                st.rerun()
    with col2:
        if st.button("Cancelar", use_container_width=True, key=f"btn_cancel_ed_cargo_{nome}"):
            st.rerun()

class HierarquiaMenu(BaseMenu):
    def render(self):
        st.markdown("<h2 style='text-align: left; margin-bottom: 5px;'>Hierarquia / Departamentos</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.1em; color: rgba(255,255,255,0.7); margin-bottom: 20px;'>Estruture e gerencie o organograma de departamentos das empresas cadastradas.</p>", unsafe_allow_html=True)
        
        # CSS para formatar os botões de talento como hyperlinks e adicionar estilo dos cards
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
        .hierarquia-card-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: rgba(240, 138, 0, 0.1);
            border: 2px solid var(--accent);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5em;
            flex-shrink: 0;
        }
        /* Ajuste para ícones de microações nos botões da hierarquia */
        div[class*="st-key-btn_edit_cargo_tree_"] button::before,
        div[class*="st-key-btn_rem_"] button::before {
            font-size: 16px !important;
            margin-right: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)


        supabase_client = get_supabase()
        lista_empresas_salvas = carregar_empresas()
        nomes_empresas = [e["nome_empresa"] for e in lista_empresas_salvas if e.get("nome_empresa")]
        if not nomes_empresas:
            nomes_empresas = ["Mundo KAN", "Empresa Cliente A"]

        st.write("---")
        col_sel1, col_sel2 = st.columns([2, 3])
        with col_sel1:
            empresa_selecionada = st.selectbox("Selecione a Empresa (Drill Down):", options=nomes_empresas, key="sel_emp_hier")

        deptos = carregar_hierarquia(empresa_selecionada)
        clientes = carregar_todos_clientes()
        
        # Talentos da empresa (onde 'empresa' == empresa_selecionada)
        talentos_da_empresa = [nome for nome, info in clientes.items() if info.get("empresa") == empresa_selecionada]
        
        # Talentos que não estão associados a esta empresa
        talentos_fora = sorted([nome for nome, info in clientes.items() if info.get("empresa") != empresa_selecionada])

        with col_sel2:
            st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
            with st.popover("Adicionar Talentos à Empresa"):
                if not talentos_fora:
                    st.info("Todos os talentos cadastrados já estão associados a esta empresa.")
                else:
                    talentos_a_adicionar = st.multiselect(
                        "Selecione os Talentos:",
                        options=talentos_fora,
                        key=f"add_talentos_emp_{empresa_selecionada}"
                    )
                    if st.button("Confirmar Associação à Empresa", key=f"btn_add_talentos_emp_{empresa_selecionada}", type="primary", use_container_width=True):
                        if talentos_a_adicionar:
                            sucessos = 0
                            client_admin = get_supabase_admin()
                            for t_nome in talentos_a_adicionar:
                                if client_admin:
                                    try:
                                        client_admin.table("mapas_salvos").update({"empresa": empresa_selecionada}).eq("nome", t_nome).execute()
                                        sucessos += 1
                                    except Exception as ex:
                                        st.error(f"Erro ao salvar no banco: {ex}")
                                else:
                                    # Fallback local
                                    if "clientes_local_data" not in st.session_state:
                                        st.session_state["clientes_local_data"] = {}
                                    if t_nome not in st.session_state["clientes_local_data"]:
                                        st.session_state["clientes_local_data"][t_nome] = clientes.get(t_nome, {}).copy()
                                    st.session_state["clientes_local_data"][t_nome]["empresa"] = empresa_selecionada
                                    sucessos += 1
                            if sucessos > 0:
                                st.cache_data.clear()
                                st.success(f"{sucessos} talentos associados com sucesso!")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.warning("Selecione pelo menos um talento.")

        with st.expander(f"Talentos da Empresa ({len(talentos_da_empresa)})", expanded=False):
            if not talentos_da_empresa:
                st.write("Nenhum talento associado a esta empresa.")
            else:
                dept_map_list = {d["departamento_id"]: d["nome"] for d in deptos}
                for t_nome in sorted(talentos_da_empresa):
                    t_info = clientes[t_nome]
                    t_depto_id = t_info.get("departamento")
                    t_depto_nome = dept_map_list.get(t_depto_id, "Sem Departamento")
                    t_cargo = t_info.get("cargo", "Sem Cargo")
                    foto_b64 = t_info.get("foto_base64")
                    
                    # Layout usando colunas para manter o alinhamento
                    cols_t = st.columns([1, 20])
                    with cols_t[0]:
                        if foto_b64:
                            st.markdown(f'<img src="data:image/png;base64,{foto_b64}" style="width: 24px; height: 24px; border-radius: 50%; object-fit: cover; border: 1px solid var(--accent); vertical-align: middle;">', unsafe_allow_html=True)
                        else:
                            st.markdown('<span style="vertical-align: middle; display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; color: rgba(255,255,255,0.4);"><i class="icon-user" style="font-size:16px;"></i></span>', unsafe_allow_html=True)
                    with cols_t[1]:
                        st.markdown('<div class="talent-link-container" style="display: inline-block; vertical-align: middle;">', unsafe_allow_html=True)
                        st.button(t_nome, key=f"lnk_emp_lst_{t_nome}", on_click=self.app.ver_cadastro_talento, args=(t_nome,))
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown(f"<span style='vertical-align: middle; font-size: 0.95em;'> &mdash; {t_cargo} (<span style='color: var(--accent); font-weight: 500;'>{t_depto_nome}</span>)</span>", unsafe_allow_html=True)
        
        state_key_edit = f"edit_hier_{empresa_selecionada}"
        state_key_builder = f"builder_hier_{empresa_selecionada}"

        if state_key_edit not in st.session_state:
            st.session_state[state_key_edit] = False

        if not st.session_state[state_key_edit]:
            st.write("---")
            if not deptos:
                st.warning(f"Nenhuma hierarquia estruturada para a empresa '{empresa_selecionada}'.")
                if st.button("Adicionar", type="primary", key=f"btn_start_add_str_{empresa_selecionada}"):
                    st.session_state[state_key_edit] = True
                    st.session_state[state_key_builder] = [
                        {"id": f"dept_{int(time.time()*1000)}_0", "nome": "Presidência / CEO", "parent_id": "Nenhum (Nível Mais Alto)"}
                    ]
                    st.rerun()
            else:
                col_topo1, col_topo2 = st.columns([1, 5])
                with col_topo1:
                    if st.button("Editar", type="primary", key=f"btn_edit_str_{empresa_selecionada}"):
                        st.session_state[state_key_edit] = True
                        st.session_state[state_key_builder] = [
                            {"id": d["departamento_id"], "nome": d["nome"], "parent_id": d.get("parent_id") or "Nenhum (Nível Mais Alto)"}
                            for d in deptos
                        ]
                        st.rerun()
                st.write("---")
                st.subheader(f"Organograma Atual: {empresa_selecionada}")
                
                cargos_list = carregar_cargos()
                
                def render_tree(parent_id, level=0):
                    children = [d for d in deptos if (d.get("parent_id") == parent_id) or (parent_id == "Nenhum (Nível Mais Alto)" and (d.get("parent_id") is None or d.get("parent_id") == "Nenhum (Nível Mais Alto)"))]
                    for ch in sorted(children, key=lambda x: x.get("ordem", 0)):
                        indent = "\u00A0\u00A0\u00A0\u00A0" * level
                        prefix = "└─ " if level > 0 else ""
                        
                        # Talentos associados a este departamento
                        dept_talents = [nome for nome, info in clientes.items() if info.get("empresa") == empresa_selecionada and info.get("departamento") == ch["departamento_id"]]
                        
                        with st.container(border=True):
                            st.markdown(f"<div style='padding-left: {level * 25}px;'><span style='color: var(--accent); font-weight: bold;'>{prefix}</span> <span style='font-size: 1.2em; font-weight: bold; color: #FFFFFF;'>{ch['nome']}</span></div>", unsafe_allow_html=True)
                            
                            if dept_talents:
                                for t_nome in sorted(dept_talents):
                                    t_info = clientes[t_nome]
                                    t_cargo = t_info.get("cargo", "Sem Cargo")
                                    foto_b64 = t_info.get("foto_base64")
                                    
                                    cols_tree = st.columns([1, 6, 9])
                                    with cols_tree[0]:
                                        st.markdown(f"<div style='padding-left: {level * 25 + 20}px;'></div>", unsafe_allow_html=True)
                                    with cols_tree[1]:
                                        from components.card import premium_card_container
                                        with premium_card_container(variant="compact"):
                                            card_cols = st.columns([1, 2.8, 0.7])
                                            with card_cols[0]:
                                                if foto_b64:
                                                    st.markdown(f'<img src="data:image/png;base64,{foto_b64}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 2px solid var(--accent); display: block;" />', unsafe_allow_html=True)
                                                else:
                                                    st.markdown('<div class="hierarquia-card-avatar"><i class="icon-user" style="color: var(--accent);"></i></div>', unsafe_allow_html=True)
                                            with card_cols[1]:
                                                st.markdown('<div class="talent-link-container" style="margin-top: -2px;">', unsafe_allow_html=True)
                                                st.button(t_nome, key=f"lnk_tree_{ch['departamento_id']}_{t_nome}", on_click=self.app.ver_cadastro_talento, args=(t_nome,))
                                                st.markdown('</div>', unsafe_allow_html=True)
                                                st.markdown(f"<span style='color: var(--accent); font-weight: bold; font-size: 0.85em; display: block; margin-top: -6px;'>{t_cargo}</span>", unsafe_allow_html=True)
                                            with card_cols[2]:
                                                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                                                if st.button(" ", key=f"btn_edit_cargo_tree_{ch['departamento_id']}_{t_nome}", help="Editar Cargo", use_container_width=True):
                                                    modal_editar_cargo(t_nome, t_cargo, cargos_list)
                            
                            # Botão de popover para adicionar/alterar membro
                            st.markdown("<div style='padding-left: " + str(level * 25 + 20) + "px; margin-top: 8px;'></div>", unsafe_allow_html=True)
                            
                            # Exibir popover alinhado com o nível de indentação do departamento
                            cols_assoc = st.columns([1, 10])
                            with cols_assoc[0]:
                                st.markdown("<div style='width: " + str(level * 25) + "px;'></div>", unsafe_allow_html=True)
                            with cols_assoc[1]:
                                with st.popover("Membros", use_container_width=False):
                                    st.markdown(f"**Departamento: {ch['nome']}**")
                                    company_talents = sorted(talentos_da_empresa)
                                    talento_sel = st.selectbox(
                                        "Selecione o Talento:",
                                        options=["Selecione..."] + company_talents,
                                        key=f"sel_talent_dept_{ch['departamento_id']}"
                                    )
                                    cargo_sel = st.selectbox(
                                        "Selecione o Cargo:",
                                        options=cargos_list,
                                        key=f"sel_cargo_dept_{ch['departamento_id']}"
                                    )
                                    if st.button("Associar ao Departamento", key=f"btn_assoc_dept_{ch['departamento_id']}", type="primary", use_container_width=True):
                                        if talento_sel != "Selecione...":
                                            client_admin = get_supabase_admin()
                                            if client_admin:
                                                try:
                                                    client_admin.table("mapas_salvos").update({
                                                        "departamento": ch["departamento_id"],
                                                        "cargo": cargo_sel
                                                    }).eq("nome", talento_sel).execute()
                                                    st.cache_data.clear()
                                                    st.success(f"{talento_sel} associado como {cargo_sel}!")
                                                    time.sleep(1)
                                                    st.rerun()
                                                except Exception as ex:
                                                    st.error(f"Erro ao salvar no banco: {ex}")
                                            else:
                                                if "clientes_local_data" not in st.session_state:
                                                    st.session_state["clientes_local_data"] = {}
                                                if talento_sel not in st.session_state["clientes_local_data"]:
                                                    st.session_state["clientes_local_data"][talento_sel] = clientes.get(talento_sel, {}).copy()
                                                st.session_state["clientes_local_data"][talento_sel]["departamento"] = ch["departamento_id"]
                                                st.session_state["clientes_local_data"][talento_sel]["cargo"] = cargo_sel
                                                st.cache_data.clear()
                                                st.success(f"{talento_sel} associado localmente!")
                                                time.sleep(1)
                                                st.rerun()
                                        else:
                                            st.warning("Selecione um talento válido.")
                        render_tree(ch["departamento_id"], level + 1)
                
                render_tree("Nenhum (Nível Mais Alto)", 0)

        else:
            st.write("---")
            st.subheader(f"Construtor de Hierarquia da Empresa: {empresa_selecionada}")
            st.info("Crie a hierarquia adicionando retângulos e definindo a quem cada departamento está subordinado.")

            if state_key_builder not in st.session_state or not st.session_state[state_key_builder]:
                st.session_state[state_key_builder] = [
                    {"id": f"dept_{int(time.time()*1000)}_0", "nome": "Presidência / CEO", "parent_id": "Nenhum (Nível Mais Alto)"}
                ]

            builder_list = st.session_state[state_key_builder]

            opcoes_pai = ["Nenhum (Nível Mais Alto)"] + [item["nome"] for item in builder_list]

            novos_dados = []
            for idx, item in enumerate(builder_list):
                with st.container(border=True):
                    r_col1, r_col2, r_col3 = st.columns([3, 3, 1])
                    with r_col1:
                        n_nome = st.text_input("Nome do Departamento", value=item["nome"], key=f"in_nome_{idx}_{item['id']}")
                    with r_col2:
                        current_pai = item.get("parent_id") or "Nenhum (Nível Mais Alto)"
                        pai_nome = "Nenhum (Nível Mais Alto)"
                        if current_pai != "Nenhum (Nível Mais Alto)":
                            for search_item in builder_list:
                                if search_item["id"] == current_pai:
                                    pai_nome = search_item["nome"]
                                    break
                        if pai_nome not in opcoes_pai:
                            pai_nome = "Nenhum (Nível Mais Alto)"
                        
                        n_pai_nome = st.selectbox("Subordinado a (Pai / Nível Superior):", options=opcoes_pai, index=opcoes_pai.index(pai_nome) if pai_nome in opcoes_pai else 0, key=f"in_pai_{idx}_{item['id']}")
                    with r_col3:
                        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                        if len(builder_list) > 1:
                            if st.button(" ", key=f"btn_rem_{idx}_{item['id']}", help="Remover Departamento", use_container_width=True):
                                builder_list.pop(idx)
                                st.rerun()

                    if st.button(f"Adicionar Subdepartamento sob '{n_nome}'", key=f"btn_add_sub_{idx}_{item['id']}"):
                        novo_id = f"dept_{int(time.time()*1000)}_{len(builder_list)}"
                        builder_list.append({"id": novo_id, "nome": f"Subdepartamento de {n_nome}", "parent_id": item["id"]})
                        st.rerun()

                    pai_id = "Nenhum (Nível Mais Alto)"
                    if n_pai_nome != "Nenhum (Nível Mais Alto)":
                        for search_item in builder_list:
                            if search_item["nome"] == n_pai_nome and search_item["id"] != item["id"]:
                                pai_id = search_item["id"]
                                break
                    novos_dados.append({"id": item["id"], "nome": n_nome, "parent_id": pai_id})

            st.session_state[state_key_builder] = novos_dados

            st.write("---")
            col_add_root, col_space = st.columns([3, 5])
            with col_add_root:
                if st.button("Adicionar Novo Departamento Principal", use_container_width=True, key=f"btn_add_root_{empresa_selecionada}"):
                    novo_id = f"dept_{int(time.time()*1000)}_{len(builder_list)}"
                    builder_list.append({"id": novo_id, "nome": "Novo Departamento", "parent_id": "Nenhum (Nível Mais Alto)"})
                    st.rerun()

            st.write("---")
            col_s1, col_s2, col_s3 = st.columns([2, 2, 4])
            with col_s1:
                if st.button("Salvar", type="primary", use_container_width=True, key=f"btn_save_changes_hier_{empresa_selecionada}"):
                    payloads = []
                    for idx_ord, d in enumerate(st.session_state[state_key_builder]):
                        pid = d["parent_id"] if d["parent_id"] != "Nenhum (Nível Mais Alto)" else None
                        payloads.append({
                            "empresa": empresa_selecionada,
                            "departamento_id": d["id"],
                            "nome": d["nome"],
                            "parent_id": pid,
                            "ordem": idx_ord,
                            "updated_at": datetime.datetime.now().isoformat()
                        })
                    
                    if supabase_client:
                        try:
                            supabase_client.table("hierarquia_departamentos").delete().eq("empresa", empresa_selecionada).execute()
                            supabase_client.table("hierarquia_departamentos").insert(payloads).execute()
                            st.success("Hierarquia salva com sucesso!")
                            st.session_state[state_key_edit] = False
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Erro ao salvar no banco de dados: {ex}\n\nDICA: Certifique-se de executar o script SQL correspondente para criar a tabela.")
                    else:
                        st.session_state["hier_local_" + empresa_selecionada] = payloads
                        st.success("Hierarquia salva com sucesso!")
                        st.session_state[state_key_edit] = False
                        st.rerun()
            with col_s2:
                if st.button("Cancelar", use_container_width=True, key=f"btn_canc_hier_{empresa_selecionada}"):
                    st.session_state[state_key_edit] = False
                    st.rerun()
