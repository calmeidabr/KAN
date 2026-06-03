import streamlit as st
import datetime
import time
import json
import os
from collections import Counter
from PIL import Image, ImageDraw, ImageFont
from menus.base_menu import BaseMenu
from models.database import (
    carregar_empresas,
    carregar_hierarquia,
    get_supabase_admin,
    carregar_todos_clientes,
    carregar_cargos,
    carregar_equipes
)
from services.numerologia import calcular_numerologia, reduce_number
from services.perfil import calcular_perfil_comportamental
from utils.helpers import compress_image_to_b64, validar_cnpj

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
        st.markdown("<h2 style='text-align: left; margin-bottom: 5px;'>Organograma & Equipes</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.1em; color: rgba(255,255,255,0.7); margin-bottom: 20px;'>Gerencie Empresas, Hierarquia de Departamentos e Equipes de forma integrada e visual.</p>", unsafe_allow_html=True)
        
        # CSS para formatar os botões e microações
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
        div[class*="st-key-btn_edit_cargo_tree_"] button::before {
            content: "\\e12f" !important;
            font-family: "lucide" !important;
            font-size: 16px !important;
            margin-right: 0 !important;
            font-style: normal !important;
            font-weight: normal !important;
            line-height: 1 !important;
            display: inline-block !important;
        }
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
            content: "\\e18e" !important;
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

        supabase_client = get_supabase_admin()
        
        # 1. Carrega Empresas e Seleciona a Ativa
        lista_empresas_salvas = carregar_empresas()
        nomes_empresas = [e["nome_empresa"] for e in lista_empresas_salvas if e.get("nome_empresa")]
        if not nomes_empresas:
            nomes_empresas = ["Mundo Kan"]

        col_sel1, col_sel2 = st.columns([3, 2])
        with col_sel1:
            empresa_selecionada = st.selectbox("Selecione a Empresa (Foco):", options=nomes_empresas, key="sel_emp_hier")

        # ── SEÇÃO 1: GESTÃO DE EMPRESAS (COLLAPSIBLE) ──────────────────
        with st.expander("🏢 Cadastro e Edição de Empresas", expanded=False):
            self.render_empresas_section(supabase_client, lista_empresas_salvas)

        st.write("---")

        # Dados da Empresa em Foco
        deptos = carregar_hierarquia(empresa_selecionada)
        clientes = carregar_todos_clientes()
        talentos_da_empresa = [nome for nome, info in clientes.items() if info.get("empresa") == empresa_selecionada]
        talentos_fora = sorted([nome for nome, info in clientes.items() if info.get("empresa") != empresa_selecionada])

        # ── SEÇÃO 2: ORGANOGRAMA & DEPARTAMENTOS ──────────────────────
        st.markdown("### 📊 Organograma de Departamentos")
        
        col_org1, col_org2 = st.columns([2, 3])
        with col_org1:
            state_key_edit = f"edit_hier_{empresa_selecionada}"
            state_key_builder = f"builder_hier_{empresa_selecionada}"
            if state_key_edit not in st.session_state:
                st.session_state[state_key_edit] = False
                
            if not st.session_state[state_key_edit]:
                if deptos:
                    if st.button("Editar Departamentos", type="secondary", key=f"btn_edit_str_{empresa_selecionada}"):
                        st.session_state[state_key_edit] = True
                        st.session_state[state_key_builder] = [
                            {"id": d["departamento_id"], "nome": d["nome"], "parent_id": d.get("parent_id") or "Nenhum (Nível Mais Alto)"}
                            for d in deptos
                        ]
                        st.rerun()
                else:
                    if st.button("Criar Departamentos", type="primary", key=f"btn_start_add_str_{empresa_selecionada}"):
                        st.session_state[state_key_edit] = True
                        st.session_state[state_key_builder] = [
                            {"id": f"dept_{int(time.time()*1000)}_0", "nome": "Presidência / CEO", "parent_id": "Nenhum (Nível Mais Alto)"}
                        ]
                        st.rerun()
        with col_org2:
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
                            for t_nome in talentos_a_adicionar:
                                if supabase_client:
                                    try:
                                        supabase_client.table("mapas_salvos").update({"empresa": empresa_selecionada}).eq("nome", t_nome).execute()
                                        sucessos += 1
                                    except Exception as ex:
                                        st.error(f"Erro ao salvar: {ex}")
                                else:
                                    if "clientes_local_data" not in st.session_state: st.session_state["clientes_local_data"] = {}
                                    if t_nome not in st.session_state["clientes_local_data"]: st.session_state["clientes_local_data"][t_nome] = clientes.get(t_nome, {}).copy()
                                    st.session_state["clientes_local_data"][t_nome]["empresa"] = empresa_selecionada
                                    sucessos += 1
                            if sucessos > 0:
                                st.cache_data.clear()
                                st.success(f"{sucessos} talentos associados com sucesso!")
                                time.sleep(1)
                                st.rerun()

        # RENDER DA HIERARQUIA / CONSTRUTOR
        if not st.session_state[state_key_edit]:
            if not deptos:
                st.warning(f"Nenhum departamento estruturado para '{empresa_selecionada}'.")
            else:
                cargos_list = carregar_cargos()
                dept_map_list = {d["departamento_id"]: d["nome"] for d in deptos}

                def render_tree(parent_id, level=0):
                    children = [d for d in deptos if (d.get("parent_id") == parent_id) or (parent_id == "Nenhum (Nível Mais Alto)" and (d.get("parent_id") is None or d.get("parent_id") == "Nenhum (Nível Mais Alto)"))]
                    for ch in sorted(children, key=lambda x: x.get("ordem", 0)):
                        indent = "\u00A0\u00A0\u00A0\u00A0" * level
                        prefix = "└─ " if level > 0 else ""
                        dept_talents = [nome for nome, info in clientes.items() if info.get("empresa") == empresa_selecionada and info.get("departamento") == ch["departamento_id"]]
                        
                        with st.container(border=True):
                            st.markdown(f"<div style='padding-left: {level * 25}px;'><span style='color: var(--accent); font-weight: bold;'>{prefix}</span> <span style='font-size: 1.15em; font-weight: bold; color: #FFFFFF;'>{ch['nome']}</span></div>", unsafe_allow_html=True)
                            
                            if dept_talents:
                                for t_nome in sorted(dept_talents):
                                    t_info = clientes[t_nome]
                                    t_cargo = t_info.get("cargo", "Sem Cargo")
                                    foto_b64 = t_info.get("foto_base64")
                                    is_lider = t_info.get("lider", False)
                                    
                                    cols_tree = st.columns([1, 6, 9])
                                    with cols_tree[0]:
                                        st.markdown(f"<div style='padding-left: {level * 25 + 20}px;'></div>", unsafe_allow_html=True)
                                    with cols_tree[1]:
                                        from components.card import premium_card_container
                                        with premium_card_container(variant="compact"):
                                            card_cols = st.columns([1, 2.4, 1.1])
                                            with card_cols[0]:
                                                if foto_b64:
                                                    st.markdown(f'<img src="data:image/png;base64,{foto_b64}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 2px solid var(--accent); display: block;" />', unsafe_allow_html=True)
                                                else:
                                                    st.markdown('<div class="hierarquia-card-avatar"><i class="icon-user" style="color: var(--accent);"></i></div>', unsafe_allow_html=True)
                                            with card_cols[1]:
                                                st.markdown('<div class="talent-link-container" style="margin-top: -2px;">', unsafe_allow_html=True)
                                                st.button(t_nome, key=f"lnk_tree_{ch['departamento_id']}_{t_nome}", on_click=self.app.ver_cadastro_talento, args=(t_nome,))
                                                if is_lider:
                                                    st.markdown('<span style="color: #ff9f43; font-weight: bold; font-size: 0.8em; display: inline-flex; align-items: center; margin-left: 6px;"><i class="icon-crown" style="font-size:12px; margin-right:2px; vertical-align:middle;"></i>Líder</span>', unsafe_allow_html=True)
                                                st.markdown('</div>', unsafe_allow_html=True)
                                                st.markdown(f"<span style='color: var(--accent); font-weight: bold; font-size: 0.85em; display: block; margin-top: -6px;'>{t_cargo}</span>", unsafe_allow_html=True)
                                            with card_cols[2]:
                                                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                                                btn_cols = st.columns(3)
                                                with btn_cols[0]:
                                                    if st.button(" ", key=f"btn_edit_cargo_tree_{ch['departamento_id']}_{t_nome}", help="Editar Cargo", use_container_width=True):
                                                        modal_editar_cargo(t_nome, t_cargo, cargos_list)
                                                with btn_cols[1]:
                                                    help_lider = "Remover Liderança" if is_lider else "Tornar Líder"
                                                    if st.button(" ", key=f"btn_set_lider_{ch['departamento_id']}_{t_nome}", help=help_lider, use_container_width=True, type="primary" if is_lider else "secondary"):
                                                        novo_estado = not is_lider
                                                        if supabase_client:
                                                            try:
                                                                if novo_estado:
                                                                    supabase_client.table("mapas_salvos").update({"lider": False}).eq("departamento", ch["departamento_id"]).execute()
                                                                supabase_client.table("mapas_salvos").update({"lider": novo_estado}).eq("nome", t_nome).execute()
                                                                st.cache_data.clear()
                                                                st.toast(f"👑 {t_nome} definido como Líder!" if novo_estado else f"Liderança de {t_nome} removida!")
                                                                time.sleep(1)
                                                                st.rerun()
                                                            except Exception as ex:
                                                                st.error(f"Erro ao salvar no banco: {ex}")
                                                        else:
                                                            if "clientes_local_data" not in st.session_state: st.session_state["clientes_local_data"] = {}
                                                            if novo_estado:
                                                                for name, info in clientes.items():
                                                                    if info.get("empresa") == empresa_selecionada and info.get("departamento") == ch["departamento_id"]:
                                                                        if name not in st.session_state["clientes_local_data"]: st.session_state["clientes_local_data"][name] = info.copy()
                                                                        st.session_state["clientes_local_data"][name]["lider"] = False
                                                            if t_nome not in st.session_state["clientes_local_data"]: st.session_state["clientes_local_data"][t_nome] = t_info.copy()
                                                            st.session_state["clientes_local_data"][t_nome]["lider"] = novo_estado
                                                            st.cache_data.clear()
                                                            st.toast("✅ Liderança atualizada localmente!")
                                                            time.sleep(1)
                                                            st.rerun()
                                                with btn_cols[2]:
                                                    if st.button(" ", key=f"btn_rem_dept_{ch['departamento_id']}_{t_nome}", help="Remover do Departamento", use_container_width=True):
                                                        if supabase_client:
                                                            try:
                                                                supabase_client.table("mapas_salvos").update({"departamento": None, "lider": False}).eq("nome", t_nome).execute()
                                                                st.cache_data.clear()
                                                                st.toast(f"❌ {t_nome} removido do departamento!")
                                                                time.sleep(1)
                                                                st.rerun()
                                                            except Exception as ex:
                                                                st.error(f"Erro ao salvar: {ex}")
                                                        else:
                                                            if "clientes_local_data" not in st.session_state: st.session_state["clientes_local_data"] = {}
                                                            if t_nome not in st.session_state["clientes_local_data"]: st.session_state["clientes_local_data"][t_nome] = t_info.copy()
                                                            st.session_state["clientes_local_data"][t_nome]["departamento"] = None
                                                            st.session_state["clientes_local_data"][t_nome]["lider"] = False
                                                            st.cache_data.clear()
                                                            st.toast("✅ Removido localmente!")
                                                            time.sleep(1)
                                                            st.rerun()
                             
                            cols_assoc = st.columns([1, 10])
                            with cols_assoc[0]:
                                st.markdown(f"<div style='width: {level * 25}px;'></div>", unsafe_allow_html=True)
                            with cols_assoc[1]:
                                with st.popover("Vincular Talento", use_container_width=False):
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
                                    lider_sel = st.checkbox("Definir como Líder", key=f"sel_lider_dept_{ch['departamento_id']}")
                                    if st.button("Associar", key=f"btn_assoc_dept_{ch['departamento_id']}", type="primary", use_container_width=True):
                                        if talento_sel != "Selecione...":
                                            if supabase_client:
                                                try:
                                                    if lider_sel:
                                                        supabase_client.table("mapas_salvos").update({"lider": False}).eq("departamento", ch["departamento_id"]).execute()
                                                    supabase_client.table("mapas_salvos").update({
                                                        "departamento": ch["departamento_id"],
                                                        "cargo": cargo_sel,
                                                        "lider": lider_sel
                                                    }).eq("nome", talento_sel).execute()
                                                    st.cache_data.clear()
                                                    st.success(f"{talento_sel} associado com sucesso!")
                                                    time.sleep(1)
                                                    st.rerun()
                                                except Exception as ex:
                                                    st.error(f"Erro ao salvar: {ex}")
                                            else:
                                                if "clientes_local_data" not in st.session_state: st.session_state["clientes_local_data"] = {}
                                                if lider_sel:
                                                    for name, info in clientes.items():
                                                        if info.get("empresa") == empresa_selecionada and info.get("departamento") == ch["departamento_id"]:
                                                            if name not in st.session_state["clientes_local_data"]: st.session_state["clientes_local_data"][name] = info.copy()
                                                            st.session_state["clientes_local_data"][name]["lider"] = False
                                                if talento_sel not in st.session_state["clientes_local_data"]: st.session_state["clientes_local_data"][talento_sel] = clientes.get(talento_sel, {}).copy()
                                                st.session_state["clientes_local_data"][talento_sel]["departamento"] = ch["departamento_id"]
                                                st.session_state["clientes_local_data"][talento_sel]["cargo"] = cargo_sel
                                                st.session_state["clientes_local_data"][talento_sel]["lider"] = lider_sel
                                                st.cache_data.clear()
                                                st.success("Associado localmente!")
                                                time.sleep(1)
                                                st.rerun()
                        render_tree(ch["departamento_id"], level + 1)
                
                render_tree("Nenhum (Nível Mais Alto)", 0)
        else:
            # Construtor da Hierarquia
            st.subheader(f"Construtor de Hierarquia: {empresa_selecionada}")
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
                        n_pai_nome = st.selectbox("Subordinado a:", options=opcoes_pai, index=opcoes_pai.index(pai_nome), key=f"in_pai_{idx}_{item['id']}")
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
            if st.button("Adicionar Departamento Principal", key=f"btn_add_root_{empresa_selecionada}"):
                novo_id = f"dept_{int(time.time()*1000)}_{len(builder_list)}"
                builder_list.append({"id": novo_id, "nome": "Novo Departamento", "parent_id": "Nenhum (Nível Mais Alto)"})
                st.rerun()
                
            st.write("---")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                if st.button("Salvar Estrutura", type="primary", use_container_width=True, key=f"btn_save_changes_hier_{empresa_selecionada}"):
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
                            st.error(f"Erro ao salvar: {ex}")
                    else:
                        st.session_state["hier_local_" + empresa_selecionada] = payloads
                        st.success("Hierarquia salva com sucesso!")
                        st.session_state[state_key_edit] = False
                        st.rerun()
            with col_s2:
                if st.button("Cancelar", use_container_width=True, key=f"btn_canc_hier_{empresa_selecionada}"):
                    st.session_state[state_key_edit] = False
                    st.rerun()

        st.write("---")

        # ── SEÇÃO 3: GESTÃO DE EQUIPES ────────────────────────────────
        st.markdown("### 👥 Equipes da Empresa")
        self.render_equipes_section(supabase_client, empresa_selecionada, talentos_da_empresa, clientes)

    def render_empresas_section(self, supabase_client, lista_empresas):
        # CRUD Simplificado de Empresas
        if "hier_add_empresa_mode" not in st.session_state: st.session_state["hier_add_empresa_mode"] = False
        if "hier_edit_empresa_id" not in st.session_state: st.session_state["hier_edit_empresa_id"] = None

        emp_em_edicao = next((e for e in lista_empresas if e["nome_empresa"] == st.session_state["hier_edit_empresa_id"]), None) if st.session_state["hier_edit_empresa_id"] else None

        if emp_em_edicao:
            st.markdown(f"**Editando: {emp_em_edicao['nome_empresa']}**")
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                ed_emp = st.text_input("Nome da Empresa*", value=emp_em_edicao.get("nome_empresa") or "", key="h_ed_emp_n")
                ed_raz = st.text_input("Razão Social", value=emp_em_edicao.get("razao_social") or "", key="h_ed_emp_r")
                ed_cnpj = st.text_input("CNPJ", value=emp_em_edicao.get("cnpj") or "", key="h_ed_emp_c")
                ed_seg = st.text_input("Segmento", value=emp_em_edicao.get("segmento") or "", key="h_ed_emp_s")
            with col_e2:
                ed_resp = st.text_input("Responsável", value=emp_em_edicao.get("responsavel_nome") or "", key="h_ed_emp_resp")
                ed_resp_cel = st.text_input("Celular do Responsável", value=emp_em_edicao.get("responsavel_celular") or "", key="h_ed_emp_resp_c")
                ed_em = st.text_input("Email", value=emp_em_edicao.get("email") or "", key="h_ed_emp_e")
                ed_status = st.selectbox("Status", options=["Ativa", "Inativa"], index=0 if emp_em_edicao.get("status", "Ativa") == "Ativa" else 1, key="h_ed_emp_status")

            up_logo_ed = st.file_uploader("Logo (PNG/JPG)", type=["png", "jpg", "jpeg"], key="h_up_logo_ed_emp")
            
            col_eb1, col_eb2 = st.columns(2)
            with col_eb1:
                if st.button("Salvar Empresa", type="primary", use_container_width=True, key="h_btn_save_ed_emp"):
                    if not ed_emp.strip():
                        st.error("Nome é obrigatório.")
                    elif ed_cnpj.strip() and not validar_cnpj(ed_cnpj):
                        st.error("CNPJ inválido.")
                    else:
                        novo_logo = emp_em_edicao.get("logo") or ""
                        if up_logo_ed:
                            b64_l = compress_image_to_b64(up_logo_ed, max_width=300)
                            if b64_l: novo_logo = b64_l

                        payload = {
                            "nome_empresa": ed_emp.strip(),
                            "razao_social": ed_raz.strip() or None,
                            "cnpj": ed_cnpj.strip() or None,
                            "segmento": ed_seg.strip() or None,
                            "responsavel_nome": ed_resp.strip() or None,
                            "responsavel_celular": ed_resp_cel.strip() or None,
                            "email": ed_em.strip() or None,
                            "logo": novo_logo,
                            "status": ed_status,
                            "updated_at": datetime.datetime.now().isoformat()
                        }
                        if supabase_client:
                            try:
                                supabase_client.table("empresas").update(payload).eq("nome_empresa", emp_em_edicao["nome_empresa"]).execute()
                                st.cache_data.clear()
                                st.success("Salvo com sucesso!")
                                st.session_state["hier_edit_empresa_id"] = None
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Erro: {ex}")
                        else:
                            emp_em_edicao.update(payload)
                            st.cache_data.clear()
                            st.success("Salvo localmente!")
                            st.session_state["hier_edit_empresa_id"] = None
                            st.rerun()
            with col_eb2:
                if st.button("Cancelar Edição", use_container_width=True, key="h_btn_canc_ed_emp"):
                    st.session_state["hier_edit_empresa_id"] = None
                    st.rerun()

        elif st.session_state["hier_add_empresa_mode"]:
            st.markdown("**Cadastrar Nova Empresa**")
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                n_emp = st.text_input("Nome da Empresa*", key="h_add_emp_n")
                n_raz = st.text_input("Razão Social", key="h_add_emp_r")
                n_cnpj = st.text_input("CNPJ", key="h_add_emp_c")
            with col_a2:
                n_seg = st.text_input("Segmento", key="h_add_emp_s")
                n_resp = st.text_input("Responsável", key="h_add_emp_resp")
                n_em = st.text_input("Email", key="h_add_emp_e")

            up_logo_add = st.file_uploader("Logo (PNG/JPG)", type=["png", "jpg", "jpeg"], key="h_up_logo_add_emp")

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("Salvar Nova", type="primary", use_container_width=True, key="h_btn_save_new_emp"):
                    if not n_emp.strip():
                        st.error("Nome é obrigatório.")
                    elif n_cnpj.strip() and not validar_cnpj(n_cnpj):
                        st.error("CNPJ inválido.")
                    else:
                        novo_logo = ""
                        if up_logo_add:
                            b64_l = compress_image_to_b64(up_logo_add, max_width=300)
                            if b64_l: novo_logo = b64_l

                        payload = {
                            "nome_empresa": n_emp.strip(),
                            "razao_social": n_raz.strip() or None,
                            "cnpj": n_cnpj.strip() or None,
                            "segmento": n_seg.strip() or None,
                            "responsavel_nome": n_resp.strip() or None,
                            "email": n_em.strip() or None,
                            "logo": novo_logo,
                            "status": "Ativa",
                            "created_at": datetime.datetime.now().isoformat(),
                            "updated_at": datetime.datetime.now().isoformat()
                        }
                        if supabase_client:
                            try:
                                supabase_client.table("empresas").insert(payload).execute()
                                st.cache_data.clear()
                                st.success("Cadastrada com sucesso!")
                                st.session_state["hier_add_empresa_mode"] = False
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Erro: {ex}")
                        else:
                            if "empresas_local_data" not in st.session_state: st.session_state["empresas_local_data"] = []
                            st.session_state["empresas_local_data"].append(payload)
                            st.cache_data.clear()
                            st.success("Cadastrada localmente!")
                            st.session_state["hier_add_empresa_mode"] = False
                            st.rerun()
            with col_b2:
                if st.button("Cancelar Cadastro", use_container_width=True, key="h_btn_canc_add_emp"):
                    st.session_state["hier_add_empresa_mode"] = False
                    st.rerun()

        else:
            col_top1, col_top2 = st.columns([1, 4])
            with col_top1:
                if st.button("Adicionar Empresa", type="primary", key="h_btn_add_emp_start"):
                    st.session_state["hier_add_empresa_mode"] = True
                    st.rerun()
            st.write("")
            for emp in lista_empresas:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 4, 1])
                    with c1:
                        logo = emp.get("logo")
                        if logo and len(logo) > 20:
                            st.image(f"data:image/png;base64,{logo}", width=40)
                        else:
                            st.markdown("🏢")
                    with c2:
                        st.write(f"**{emp['nome_empresa']}** &mdash; CNPJ: {emp.get('cnpj') or 'Não cadastrado'}")
                    with c3:
                        if st.button("Editar", key=f"h_btn_edit_emp_{emp['nome_empresa']}", use_container_width=True):
                            st.session_state["hier_edit_empresa_id"] = emp["nome_empresa"]
                            st.rerun()

    def render_equipes_section(self, supabase_client, empresa_selecionada, talentos_da_empresa, clientes):
        all_equipes = carregar_equipes()
        equipes_da_empresa = [eq for eq in all_equipes if eq.get("empresa") == empresa_selecionada]
        cargos = carregar_cargos()

        if "h_add_equipe_mode" not in st.session_state: st.session_state["h_add_equipe_mode"] = False
        if "h_membros_selecionados_temp" not in st.session_state: st.session_state["h_membros_selecionados_temp"] = []

        if st.session_state["h_add_equipe_mode"]:
            st.subheader("Adicionar Nova Equipe")
            with st.container(border=True):
                nome_equipe = st.text_input("Nome da Equipe*", value=f"Equipe {len(equipes_da_empresa) + 1}", key="h_add_eq_nome")
                foto_upload = st.file_uploader("Foto da Equipe (Opcional)", type=["png", "jpg", "jpeg"], key="h_add_eq_foto")

                # Seleção fina de membros da própria empresa
                membros_finais = st.multiselect(
                    "Selecione os Membros da Equipe:",
                    options=sorted(talentos_da_empresa),
                    default=st.session_state["h_membros_selecionados_temp"],
                    key="h_eq_membros_multiselect"
                )
                st.session_state["h_membros_selecionados_temp"] = membros_finais

                col_es1, col_es2 = st.columns(2)
                with col_es1:
                    if st.button("Salvar Equipe", type="primary", use_container_width=True, key="h_btn_save_eq_final"):
                        if not nome_equipe.strip():
                            st.error("Nome é obrigatório.")
                        elif not membros_finais:
                            st.error("Selecione pelo menos um membro.")
                        else:
                            foto_b64 = ""
                            if foto_upload:
                                foto_b64 = compress_image_to_b64(foto_upload, max_width=400)

                            payload = {
                                "nome": nome_equipe.strip(),
                                "empresa": empresa_selecionada,
                                "membros": [{"nome": m, "lider": False} for m in membros_finais],
                                "foto_base64": foto_b64,
                                "updated_at": datetime.datetime.now().isoformat()
                            }

                            sucesso = False
                            if supabase_client:
                                try:
                                    supabase_client.table("equipes").insert(payload).execute()
                                    sucesso = True
                                except Exception as ex:
                                    st.error(f"Erro: {ex}")
                            else:
                                if "equipes_local_data" not in st.session_state: st.session_state["equipes_local_data"] = []
                                payload_local = dict(payload)
                                payload_local["membros"] = json.dumps(payload["membros"], ensure_ascii=False)
                                st.session_state["equipes_local_data"].append(payload_local)
                                sucesso = True

                            if sucesso:
                                st.cache_data.clear()
                                st.success("Equipe cadastrada com sucesso!")
                                st.session_state["h_add_equipe_mode"] = False
                                st.session_state["h_membros_selecionados_temp"] = []
                                time.sleep(1)
                                st.rerun()
                with col_es2:
                    if st.button("Cancelar", use_container_width=True, key="h_btn_canc_eq_final"):
                        st.session_state["h_add_equipe_mode"] = False
                        st.session_state["h_membros_selecionados_temp"] = []
                        st.rerun()
        else:
            col_top1, col_top2 = st.columns([1, 4])
            with col_top1:
                if st.button("Criar Equipe", type="primary", key="h_btn_eq_add_start"):
                    st.session_state["h_add_equipe_mode"] = True
                    st.rerun()

            st.write("")
            if not equipes_da_empresa:
                st.info("Nenhuma equipe cadastrada para esta empresa.")
            else:
                for idx, eq in enumerate(equipes_da_empresa):
                    # Normaliza membros
                    lista_membros_raw = eq.get("membros", [])
                    if isinstance(lista_membros_raw, str):
                        try: lista_membros_raw = json.loads(lista_membros_raw)
                        except Exception: lista_membros_raw = []
                    
                    lista_membros = []
                    lider_atual = None
                    for m in lista_membros_raw:
                        if isinstance(m, dict):
                            nome_m = m.get("nome")
                            lista_membros.append(nome_m)
                            if m.get("lider"): lider_atual = nome_m
                        else:
                            lista_membros.append(m)

                    with st.container(border=True):
                        c1, c2, c3, c4, c5 = st.columns([0.5, 3.5, 1.5, 1.5, 0.5])
                        with c1:
                            foto = eq.get("foto_base64")
                            if foto:
                                st.markdown(f'<img src="data:image/png;base64,{foto}" style="width:40px; height:40px; border-radius:50%; object-fit:cover; border:2px solid var(--accent);" />', unsafe_allow_html=True)
                            else:
                                st.markdown("👥")
                        with c2:
                            st.write(f"**{eq['nome']}**")
                            st.caption(f"{len(lista_membros)} integrantes")
                        with c3:
                            is_open = st.session_state.get(f"h_eq_open_{idx}", False)
                            if st.button("Membros", key=f"h_btn_v_eq_{idx}", use_container_width=True):
                                st.session_state[f"h_eq_open_{idx}"] = not is_open
                                st.rerun()
                        with c4:
                            tri_open = st.session_state.get(f"h_eq_tri_{idx}", False)
                            if st.button("Triângulos", key=f"h_btn_tri_eq_{idx}", use_container_width=True):
                                st.session_state[f"h_eq_tri_{idx}"] = not tri_open
                                st.rerun()
                        with c5:
                            if st.button(" ", key=f"h_btn_d_eq_{idx}", type="secondary", help="Excluir Equipe", use_container_width=True):
                                excluido = False
                                if supabase_client:
                                    try:
                                        supabase_client.table("equipes").delete().eq("nome", eq["nome"]).execute()
                                        excluido = True
                                    except Exception as ex: st.error(f"Erro: {ex}")
                                else:
                                    if "equipes_local_data" in st.session_state:
                                        st.session_state["equipes_local_data"] = [item for item in st.session_state["equipes_local_data"] if item["nome"] != eq["nome"]]
                                    excluido = True
                                if excluido:
                                    st.cache_data.clear()
                                    st.success("Equipe excluída!")
                                    time.sleep(1)
                                    st.rerun()

                        # EDIT DE MEMBROS
                        if st.session_state.get(f"h_eq_open_{idx}", False):
                            st.write("---")
                            st.markdown("**Integrantes da Equipe:**")
                            
                            key_temp_membros = f"h_temp_membros_{idx}"
                            key_temp_lider = f"h_temp_lider_{idx}"
                            key_temp_nome = f"h_temp_nome_{idx}"
                            key_temp_foto = f"h_temp_foto_{idx}"

                            if key_temp_membros not in st.session_state: st.session_state[key_temp_membros] = list(lista_membros)
                            if key_temp_lider not in st.session_state: st.session_state[key_temp_lider] = lider_atual
                            if key_temp_nome not in st.session_state: st.session_state[key_temp_nome] = eq["nome"]
                            if key_temp_foto not in st.session_state: st.session_state[key_temp_foto] = eq.get("foto_base64") or ""

                            membros_atuais = st.session_state[key_temp_membros]
                            temp_lider = st.session_state[key_temp_lider]

                            # Linha de cabeçalho: Renomear equipe
                            col_nome_eq1, col_nome_eq2 = st.columns([5, 2])
                            with col_nome_eq1:
                                novo_nome_eq = st.text_input("Nome da Equipe:", value=st.session_state[key_temp_nome], key=f"h_txt_nome_eq_{idx}")
                                st.session_state[key_temp_nome] = novo_nome_eq

                            upload_ed_file = st.file_uploader("Alterar Foto", type=["png", "jpg", "jpeg"], key=f"h_file_edit_foto_{idx}")
                            if upload_ed_file:
                                foto_ed_b64 = compress_image_to_b64(upload_ed_file, max_width=400)
                                if foto_ed_b64:
                                    st.session_state[key_temp_foto] = foto_ed_b64
                                    st.rerun()

                            # Adicionar Novo Membro
                            candidatos_nao_membros = sorted([n for n in talentos_da_empresa if n not in membros_atuais])
                            if candidatos_nao_membros:
                                col_add_m1, col_add_m2 = st.columns([5, 2])
                                with col_add_m1:
                                    membro_a_adicionar = st.selectbox("Adicionar Talento à Equipe:", options=["Selecione..."] + candidatos_nao_membros, key=f"h_sel_add_member_{idx}")
                                with col_add_m2:
                                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                                    if st.button("Adicionar", key=f"h_btn_add_member_submit_{idx}", use_container_width=True):
                                        if membro_a_adicionar != "Selecione...":
                                            st.session_state[key_temp_membros].append(membro_a_adicionar)
                                            # Salva no banco instantaneamente
                                            novos_membros_payload = [{"nome": n, "lider": (n == temp_lider)} for n in st.session_state[key_temp_membros]]
                                            if supabase_client:
                                                try:
                                                    supabase_client.table("equipes").update({"membros": novos_membros_payload}).eq("nome", eq["nome"]).execute()
                                                    st.cache_data.clear()
                                                    st.toast(f"✅ {membro_a_adicionar} adicionado!")
                                                    time.sleep(1)
                                                    st.rerun()
                                                except Exception as ex: st.error(f"Erro: {ex}")
                                            else:
                                                if "equipes_local_data" in st.session_state:
                                                    for eq_local in st.session_state["equipes_local_data"]:
                                                        if eq_local["nome"] == eq["nome"]:
                                                            eq_local["membros"] = json.dumps(novos_membros_payload, ensure_ascii=False)
                                                            break
                                                st.cache_data.clear()
                                                st.toast(f"✅ {membro_a_adicionar} adicionado localmente!")
                                                time.sleep(1)
                                                st.rerun()

                            st.write("")
                            cols = st.columns(3)
                            for m_idx, m_nome in enumerate(sorted(membros_atuais)):
                                col = cols[m_idx % 3]
                                m_info = clientes.get(m_nome)
                                is_lider_m = (temp_lider == m_nome)

                                with col:
                                    with st.container(border=True):
                                        c_img, c_txt = st.columns([1, 3.5])
                                        with c_img:
                                            m_foto = m_info.get("foto_base64") if m_info else None
                                            if m_foto:
                                                st.markdown(f'<img src="data:image/png;base64,{m_foto}" style="width:40px; height:40px; border-radius:50%; object-fit:cover;" />', unsafe_allow_html=True)
                                            else:
                                                st.markdown("👤")
                                        with c_txt:
                                            st.markdown('<div class="talent-link-container">', unsafe_allow_html=True)
                                            st.button(m_nome, key=f"lnk_h_eq_m_{idx}_{m_idx}", on_click=self.app.ver_cadastro_talento, args=(m_nome,))
                                            if is_lider_m:
                                                st.markdown('<span style="color: #ff9f43; font-weight: bold; font-size: 0.8em; margin-left: 4px;">👑</span>', unsafe_allow_html=True)
                                            st.markdown('</div>', unsafe_allow_html=True)
                                            st.caption(m_info.get("cargo", "Sem Cargo") if m_info else "Sem cadastro")
                                        
                                        col_btn1, col_btn2 = st.columns(2)
                                        with col_btn1:
                                            # Botão Coroa
                                            if st.button(" ", key=f"btn_set_lider_eq_{idx}_{m_idx}", help="Definir Líder", use_container_width=True, type="primary" if is_lider_m else "secondary"):
                                                novo_lider = None if is_lider_m else m_nome
                                                st.session_state[key_temp_lider] = novo_lider
                                                novos_payload = [{"nome": n, "lider": (n == novo_lider)} for n in st.session_state[key_temp_membros]]
                                                if supabase_client:
                                                    try:
                                                        supabase_client.table("equipes").update({"membros": novos_payload}).eq("nome", eq["nome"]).execute()
                                                        st.cache_data.clear()
                                                        st.toast("👑 Líder atualizado!")
                                                        time.sleep(1)
                                                        st.rerun()
                                                    except Exception as ex: st.error(f"Erro: {ex}")
                                                else:
                                                    if "equipes_local_data" in st.session_state:
                                                        for eq_local in st.session_state["equipes_local_data"]:
                                                            if eq_local["nome"] == eq["nome"]:
                                                                eq_local["membros"] = json.dumps(novos_payload, ensure_ascii=False)
                                                                break
                                                    st.cache_data.clear()
                                                    st.toast("Líder atualizado localmente!")
                                                    time.sleep(1)
                                                    st.rerun()
                                        with col_btn2:
                                            # Botão Excluir
                                            if st.button(" ", key=f"btn_rem_eq_{idx}_{m_idx}", help="Excluir Membro", use_container_width=True, type="secondary"):
                                                st.session_state[key_temp_membros].remove(m_nome)
                                                if temp_lider == m_nome: st.session_state[key_temp_lider] = None
                                                novos_payload = [{"nome": n, "lider": (n == st.session_state[key_temp_lider])} for n in st.session_state[key_temp_membros]]
                                                if supabase_client:
                                                    try:
                                                        supabase_client.table("equipes").update({"membros": novos_payload}).eq("nome", eq["nome"]).execute()
                                                        st.cache_data.clear()
                                                        st.toast("❌ Membro removido!")
                                                        time.sleep(1)
                                                        st.rerun()
                                                    except Exception as ex: st.error(f"Erro: {ex}")
                                                else:
                                                    if "equipes_local_data" in st.session_state:
                                                        for eq_local in st.session_state["equipes_local_data"]:
                                                            if eq_local["nome"] == eq["nome"]:
                                                                eq_local["membros"] = json.dumps(novos_payload, ensure_ascii=False)
                                                                break
                                                    st.cache_data.clear()
                                                    st.toast("Removido localmente!")
                                                    time.sleep(1)
                                                    st.rerun()

                            # Rodapé de salvamento de nome/foto geral
                            col_save1, col_save2 = st.columns(2)
                            with col_save1:
                                has_changes = (
                                    st.session_state[key_temp_membros] != lista_membros or
                                    st.session_state[key_temp_lider] != lider_atual or
                                    st.session_state[key_temp_nome].strip() != eq["nome"] or
                                    st.session_state[key_temp_foto] != (eq.get("foto_base64") or "")
                                )
                                if has_changes: st.warning("Alterações de nome/foto não salvas!")
                            with col_save2:
                                if st.button("Salvar Nome/Foto", key=f"h_btn_save_changes_{idx}", type="primary", use_container_width=True):
                                    nome_final = st.session_state[key_temp_nome].strip()
                                    if not nome_final: st.error("Nome da equipe inválido.")
                                    else:
                                        payload = {
                                            "nome": nome_final,
                                            "foto_base64": st.session_state[key_temp_foto],
                                            "updated_at": datetime.datetime.now().isoformat()
                                        }
                                        if supabase_client:
                                            try:
                                                supabase_client.table("equipes").update(payload).eq("nome", eq["nome"]).execute()
                                                st.cache_data.clear()
                                                st.success("Salvo com sucesso!")
                                                time.sleep(1)
                                                st.rerun()
                                            except Exception as ex: st.error(f"Erro: {ex}")
                                        else:
                                            if "equipes_local_data" in st.session_state:
                                                for eq_local in st.session_state["equipes_local_data"]:
                                                    if eq_local["nome"] == eq["nome"]:
                                                        eq_local["nome"] = nome_final
                                                        eq_local["foto_base64"] = st.session_state[key_temp_foto]
                                                        break
                                            st.cache_data.clear()
                                            st.success("Salvo localmente!")
                                            time.sleep(1)
                                            st.rerun()

                        # TRIÂNGULOS HARMÔNICOS
                        if st.session_state.get(f"h_eq_tri_{idx}", False):
                            st.write("---")
                            st.markdown("#### Triângulos Harmônicos da Equipe")

                            def _calcular_vertices(nome_comp, data_nasc_str):
                                def _clean(v):
                                    if v is None: return None
                                    s = str(v).split(" - ")[0]
                                    return int(s) if s.isdigit() and int(s) > 0 else None
                                try:
                                    if isinstance(data_nasc_str, (datetime.datetime, datetime.date)):
                                        nasc_dt = data_nasc_str
                                    else:
                                        try: nasc_dt = datetime.datetime.strptime(data_nasc_str, "%d/%m/%Y")
                                        except ValueError: nasc_dt = datetime.datetime.strptime(data_nasc_str, "%Y-%m-%d")
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
                                        if len(verts) == 3: break
                                    if len(verts) == 3: return verts
                                except Exception as ex: st.warning(f"Erro em {nome_comp}: {ex}")
                                return None

                            membros_visiveis = st.multiselect(
                                "Membros incluídos na visualização:",
                                options=sorted(lista_membros),
                                default=sorted(lista_membros),
                                key=f"h_tri_membros_sel_{idx}"
                            )

                            if st.button("Criar Triângulos Harmônicos", key=f"h_btn_tri_calc_{idx}", type="primary"):
                                st.session_state[f"h_tri_calcular_{idx}"] = True

                            if st.session_state.get(f"h_tri_calcular_{idx}", False):
                                coords_map = {
                                    1: (794, 176), 2: (1037, 243), 3: (960, 380),
                                    4: (794, 585), 5: (486, 585), 6: (320, 380),
                                    7: (243, 243), 8: (486, 176), 9: (640, 120),
                                    11: (1037, 243), 22: (794, 585)
                                }
                                path_fundo = os.path.join("images", "plano_kan_fundo.jpg")
                                resultados_tri = {}
                                erros = []

                                with st.spinner("Calculando triângulos..."):
                                    for m_nome in membros_visiveis:
                                        m_info = clientes.get(m_nome)
                                        if not m_info or not m_info.get("data_nascimento"):
                                            erros.append(f"{m_nome}: sem data ou cadastro")
                                            continue
                                        verts = _calcular_vertices(m_nome, m_info["data_nascimento"])
                                        if verts: resultados_tri[m_nome] = verts
                                        else: erros.append(f"{m_nome}: triângulo não formado")

                                if erros:
                                    for e_msg in erros: st.warning(e_msg)

                                if resultados_tri:
                                    if os.path.exists(path_fundo):
                                        try:
                                            fundo_img = Image.open(path_fundo).convert("RGBA")
                                            try: font_label = ImageFont.truetype("arial.ttf", 34)
                                            except Exception: font_label = ImageFont.load_default()

                                            img_final = fundo_img.copy()
                                            layer_notes = Image.new("RGBA", fundo_img.size, (255, 255, 255, 0))
                                            draw_notes = ImageDraw.Draw(layer_notes)

                                            cores = [
                                                (255, 200, 100, 130), (100, 200, 255, 130),
                                                (200, 255, 100, 130), (255, 100, 200, 130),
                                                (100, 255, 200, 130), (255, 160, 100, 130),
                                                (160, 100, 255, 130), (100, 160, 255, 130),
                                            ]

                                            itens_tri = list(resultados_tri.items())
                                            itens_tri_ordenados = sorted(itens_tri, key=lambda item: 1 if item[0] == lider_atual else 0)

                                            for i, (m_nome, verts) in enumerate(itens_tri_ordenados):
                                                poly_points = []
                                                for v in verts:
                                                    val_num = int(v["valor"])
                                                    if val_num in coords_map: poly_points.append(coords_map[val_num])
                                                    else:
                                                        val_red = sum(int(d) for d in str(val_num))
                                                        if val_red in coords_map: poly_points.append(coords_map[val_red])

                                                if len(poly_points) == 3:
                                                    cor = cores[i % len(cores)]
                                                    layer_m = Image.new("RGBA", fundo_img.size, (255, 255, 255, 0))
                                                    draw_m = ImageDraw.Draw(layer_m)
                                                    
                                                    draw_m.polygon(poly_points, fill=cor)
                                                    if m_nome == lider_atual:
                                                        draw_m.line(poly_points + [poly_points[0]], fill=(255, 255, 255, 255), width=5)

                                                    img_final = Image.alpha_composite(img_final, layer_m)

                                                    cx = sum(p[0] for p in poly_points) // 3
                                                    cy = sum(p[1] for p in poly_points) // 3
                                                    primeiro_nome = str(m_nome).split()[0]
                                                    nome_display = f"👑 {primeiro_nome}" if m_nome == lider_atual else primeiro_nome
                                                    draw_notes.text((cx - 20, cy - 12), nome_display, fill=(30, 30, 30), font=font_label)

                                                    # Esfera preta no vértice do KAN (poly_points[0])
                                                    draw_notes.ellipse(
                                                        [poly_points[0][0] - 6, poly_points[0][1] - 6, poly_points[0][0] + 6, poly_points[0][1] + 6],
                                                        fill=(0, 0, 0, 255)
                                                    )

                                            img_final = Image.alpha_composite(img_final, layer_notes)
                                            st.image(img_final, use_column_width=True)
                                        except Exception as ex: st.error(f"Erro ao desenhar imagem: {ex}")
                                    else:
                                        st.warning("Plano de fundo não encontrado em `images/plano_kan_fundo.jpg`.")
