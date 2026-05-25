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

                # Exibe a lista de talentos encontrados pelos filtros
                if candidatos_elegiveis:
                    st.write(f"Membros encontrados pelos filtros ({len(candidatos_elegiveis)}):")
                    st.caption(", ".join(candidatos_elegiveis))
                else:
                    st.info("Nenhum membro atende aos filtros atuais.")

                st.write("")

                # Botões de Importação Rápida
                col_btn_lote1, col_btn_lote2, col_btn_lote_esp = st.columns([2, 2, 4])
                with col_btn_lote1:
                    if st.button("➕ Adicionar Filtro", key="btn_eq_add_filter_all", use_container_width=True):
                        st.session_state["eq_membros_multiselect"] = list(set(st.session_state.get("eq_membros_multiselect", []) + candidatos_elegiveis))
                        st.session_state["membros_selecionados_temp"] = st.session_state["eq_membros_multiselect"]
                        st.toast(f"{len(candidatos_elegiveis)} membros adicionados!")
                        st.rerun()
                with col_btn_lote2:
                    if st.button("🗑 Limpar Seleção", key="btn_eq_clear_temp", use_container_width=True, type="secondary"):
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
                
                st.write("---")
                col_s1, col_s2, col_s3 = st.columns([1, 1, 5])
                with col_s1:
                    if st.button("💾 Salvar", type="primary", use_container_width=True, key="btn_save_eq_final"):
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
                    if st.button("✖ Cancelar", use_container_width=True, key="btn_canc_eq_final"):
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
                        col_card1, col_card2, col_card3, col_card4, col_card5, col_card6 = st.columns([0.5, 2.5, 2.0, 1.3, 1.5, 0.9])
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
                            btn_label = "Ocultar" if is_open else "Ver Membros"
                            if st.button(btn_label, key=f"btn_v_eq_{idx}", use_container_width=True):
                                st.session_state[f"eq_open_{idx}"] = not is_open
                                st.rerun()
                        with col_card5:
                            tri_open = st.session_state.get(f"eq_tri_{idx}", False)
                            tri_label = "⬆ Ocultar" if tri_open else "🔺 Triângulos"
                            if st.button(tri_label, key=f"btn_tri_eq_{idx}", use_container_width=True):
                                st.session_state[f"eq_tri_{idx}"] = not tri_open
                                st.rerun()
                        with col_card6:
                            if st.button("Excluir", key=f"btn_d_eq_{idx}", type="secondary", use_container_width=True):
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

                        # ── Seção: Lista de Membros ──────────────────────────────
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

                        # ── Seção: Triângulos Harmônicos ────────────────────────
                        if st.session_state.get(f"eq_tri_{idx}", False):
                            st.write("---")
                            st.markdown("### 🔺 Triângulos Harmônicos da Equipe")

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

                            if st.button("🔺 Criar Triângulos Harmônicos", key=f"btn_tri_calc_{idx}", type="primary"):
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
                                        st.warning(f"⚠️ {e_msg}")

                                if resultados_tri:
                                    # Tabela resumo
                                    import pandas as pd
                                    rows_tab = []
                                    for m_nome, verts in resultados_tri.items():
                                        rows_tab.append({
                                            "Nome": m_nome,
                                            "Vértice 1 (Campo)": verts[0]["campo"],
                                            "V1": verts[0]["valor"],
                                            "Vértice 2 (Campo)": verts[1]["campo"],
                                            "V2": verts[1]["valor"],
                                            "Vértice 3 (Campo)": verts[2]["campo"],
                                            "V3": verts[2]["valor"],
                                        })
                                    st.dataframe(pd.DataFrame(rows_tab), use_container_width=True, hide_index=True)

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

                                            for i, (m_nome, verts) in enumerate(resultados_tri.items()):
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
                                                    draw_m.polygon(poly_points, fill=cor)
                                                    img_final = Image.alpha_composite(img_final, layer_m)

                                                    cx = sum(p[0] for p in poly_points) // 3
                                                    cy = sum(p[1] for p in poly_points) // 3
                                                    primeiro_nome = str(m_nome).split()[0]
                                                    draw_notes.text((cx - 20, cy - 12), primeiro_nome, fill=(30, 30, 30), font=font_label)

                                            img_final = Image.alpha_composite(img_final, layer_notes)
                                            st.image(img_final.convert("RGB"), caption=f"Comparativo de Triângulos Harmônicos — {eq['nome']}", use_container_width=True)

                                        except Exception as ex:
                                            st.error(f"Erro ao gerar imagem: {ex}")
                                    else:
                                        st.info("ℹ️ Imagem de fundo não encontrada (images/plano_kan_fundo.jpg). Os dados da tabela acima estão disponíveis.")
                                else:
                                    st.warning("Nenhum triângulo harmônico pôde ser calculado para os membros selecionados.")
