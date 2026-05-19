import streamlit as st
import datetime
import time
from menus.base_menu import BaseMenu
from models.database import carregar_empresas, carregar_hierarquia, get_supabase

class HierarquiaMenu(BaseMenu):
    def render(self):
        st.title("Hierarquia / Departamentos")
        st.info("Estruture e gerencie o organograma de departamentos das empresas cadastradas.")

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
        
        state_key_edit = f"edit_hier_{empresa_selecionada}"
        state_key_builder = f"builder_hier_{empresa_selecionada}"

        if state_key_edit not in st.session_state:
            st.session_state[state_key_edit] = False

        if not st.session_state[state_key_edit]:
            st.write("---")
            if not deptos:
                st.warning(f"Nenhuma hierarquia estruturada para a empresa '{empresa_selecionada}'.")
                if st.button("Adicionar", type="primary", key=f"btn_add_str_{empresa_selecionada}"):
                    st.session_state[state_key_edit] = True
                    st.session_state[state_key_builder] = [
                        {"id": f"dept_{int(time.time()*1000)}_0", "nome": "Presidência / CEO", "parent_id": "Nenhum (Nível Mais Alto)"}
                    ]
                    st.rerun()
            else:
                col_topo1, col_topo2 = st.columns([1, 5])
                with col_topo1:
                    if st.button("Editar", type="primary", key=f"btn_ed_str_{empresa_selecionada}"):
                        st.session_state[state_key_edit] = True
                        st.session_state[state_key_builder] = [
                            {"id": d["departamento_id"], "nome": d["nome"], "parent_id": d.get("parent_id") or "Nenhum (Nível Mais Alto)"}
                            for d in deptos
                        ]
                        st.rerun()
                st.write("---")
                st.subheader(f"Organograma Atual: {empresa_selecionada}")
                
                dept_map = {d["departamento_id"]: d["nome"] for d in deptos}
                
                def render_tree(parent_id, level=0):
                    children = [d for d in deptos if (d.get("parent_id") == parent_id) or (parent_id == "Nenhum (Nível Mais Alto)" and (d.get("parent_id") is None or d.get("parent_id") == "Nenhum (Nível Mais Alto)"))]
                    for ch in sorted(children, key=lambda x: x.get("ordem", 0)):
                        indent = "\u00A0\u00A0\u00A0\u00A0" * level
                        prefix = "└─ " if level > 0 else "⭐ "
                        with st.container(border=True):
                            st.markdown(f"<div style='padding-left: {level * 25}px;'><span style='color: #F18617; font-weight: bold;'>{prefix}</span> <span style='font-size: 1.2em; font-weight: bold; color: #FFFFFF;'>{ch['nome']}</span></div>", unsafe_allow_html=True)
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
                            if st.button("🗑️", key=f"btn_rem_{idx}_{item['id']}", help="Remover Departamento", use_container_width=True):
                                builder_list.pop(idx)
                                st.rerun()

                    if st.button(f"➕ Adicionar Subdepartamento sob '{n_nome}'", key=f"btn_add_sub_{idx}_{item['id']}"):
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
                if st.button("➕ Adicionar Novo Departamento Principal", use_container_width=True, key=f"btn_add_root_{empresa_selecionada}"):
                    novo_id = f"dept_{int(time.time()*1000)}_{len(builder_list)}"
                    builder_list.append({"id": novo_id, "nome": "Novo Departamento", "parent_id": "Nenhum (Nível Mais Alto)"})
                    st.rerun()

            st.write("---")
            col_s1, col_s2, col_s3 = st.columns([2, 2, 4])
            with col_s1:
                if st.button("Salvar", type="primary", use_container_width=True, key=f"btn_save_hier_{empresa_selecionada}"):
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
                            st.success("Hierarquia salva com sucesso no Supabase!")
                            st.session_state[state_key_edit] = False
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Erro ao salvar no Supabase: {ex}\n\nDICA: Certifique-se de executar o script 'hierarquia_schema.sql' no SQL Editor do Supabase para criar a tabela.")
                    else:
                        st.session_state["hier_local_" + empresa_selecionada] = payloads
                        st.success("Hierarquia salva com sucesso!")
                        st.session_state[state_key_edit] = False
                        st.rerun()
            with col_s2:
                if st.button("Cancelar", use_container_width=True, key=f"btn_canc_hier_{empresa_selecionada}"):
                    st.session_state[state_key_edit] = False
                    st.rerun()
