import streamlit as st
import datetime
from menus.base_menu import BaseMenu
from models.database import carregar_empresas, get_supabase
from utils.helpers import compress_image_to_b64, validar_cnpj

class EmpresasMenu(BaseMenu):
    def render(self):
        st.title("Gestão de Empresas")
        st.info("Aqui você pode gerenciar as empresas cadastradas no sistema KAN.")
        
        supabase_client = get_supabase()
        
        if "add_empresa_mode" not in st.session_state:
            st.session_state["add_empresa_mode"] = False
        if "edit_empresa_id" not in st.session_state:
            st.session_state["edit_empresa_id"] = None
        if "view_empresa_selected" not in st.session_state:
            st.session_state["view_empresa_selected"] = None

        lista_empresas = carregar_empresas()
        emp_em_edicao = next((e for e in lista_empresas if e["nome_empresa"] == st.session_state["edit_empresa_id"]), None) if st.session_state["edit_empresa_id"] else None
        emp_em_visualizacao = next((e for e in lista_empresas if e["nome_empresa"] == st.session_state["view_empresa_selected"]), None) if st.session_state["view_empresa_selected"] else None

        if emp_em_visualizacao and not emp_em_edicao:
            col_btn1, col_btn2 = st.columns([1, 5])
            with col_btn1:
                if st.button("⭠ \u00A0 Voltar à Lista", key="btn_back_emp_list", use_container_width=True):
                    st.session_state["view_empresa_selected"] = None
                    st.rerun()
            st.write("---")

            with st.container(border=True):
                top_c1, top_c2 = st.columns([1, 4])
                with top_c1:
                    logo_val = emp_em_visualizacao.get('logo') or '⛶'
                    if len(logo_val) > 20:
                        st.image(f"data:image/png;base64,{logo_val}", width=80)
                    else:
                        st.markdown(f"<div style='font-size: 2.5em; text-align: center; background: rgba(241,134,23,0.2); border-radius: 10px; padding: 10px;'>{logo_val}</div>", unsafe_allow_html=True)
                with top_c2:
                    st.markdown(f"<h3 style='margin: 0; color: #FFFFFF;'>{emp_em_visualizacao['nome_empresa']}</h3>", unsafe_allow_html=True)
                    st.caption(f"CNPJ: {emp_em_visualizacao.get('cnpj') or 'Não informado'} | Segmento: {emp_em_visualizacao.get('segmento') or 'Não informado'}")
                
                st.write("---")
                ecol1, ecol2, ecol3 = st.columns(3)
                with ecol1:
                    st.write("**Razão Social:**")
                    st.write(emp_em_visualizacao.get("razao_social") or "Não informada")
                    st.write("**CNPJ:**")
                    st.write(emp_em_visualizacao.get("cnpj") or "Não informado")
                    st.write("**Segmento:**")
                    st.write(emp_em_visualizacao.get("segmento") or "Não informado")
                    st.write("**Responsável:**")
                    st.write(emp_em_visualizacao.get("responsavel_nome") or "Não informado")
                with ecol2:
                    st.write("**Colaboradores:**")
                    st.write(emp_em_visualizacao.get("num_colaboradores") or "Não informado")
                    st.write("**Site:**")
                    st.write(emp_em_visualizacao.get("site") or "Não informado")
                    st.write("**Celular do Responsável:**")
                    st.write(emp_em_visualizacao.get("responsavel_celular") or "Não informado")
                with ecol3:
                    st.write("**Telefone:**")
                    st.write(emp_em_visualizacao.get("telefone") or "Não informado")
                    st.write("**E-mail:**")
                    st.write(emp_em_visualizacao.get("email") or "Não informado")
                    st.write("**E-mail do Responsável:**")
                    st.write(emp_em_visualizacao.get("responsavel_email") or "Não informado")

                st.write("---")
                if st.button("Editar Empresa", type="primary", key=f"btn_ed_emp_{emp_em_visualizacao['nome_empresa']}"):
                    st.session_state["edit_empresa_id"] = emp_em_visualizacao["nome_empresa"]
                    st.rerun()

        elif emp_em_edicao:
            st.write("---")
            st.subheader(f"Editando Empresa: {emp_em_edicao['nome_empresa']}")
            with st.container(border=True):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    ed_emp = st.text_input("Nome da Empresa*", value=emp_em_edicao.get("nome_empresa") or "", key="ed_emp_n")
                    ed_raz = st.text_input("Razão Social", value=emp_em_edicao.get("razao_social") or "", key="ed_emp_r")
                    ed_cnpj = st.text_input("CNPJ (com ou sem pontuação)", value=emp_em_edicao.get("cnpj") or "", key="ed_emp_c")
                    ed_seg = st.text_input("Segmento", value=emp_em_edicao.get("segmento") or "", key="ed_emp_s")
                    ed_resp = st.text_input("Nome do Responsável", value=emp_em_edicao.get("responsavel_nome") or "", key="ed_emp_resp")
                    ed_resp_cel = st.text_input("Celular do Responsável", value=emp_em_edicao.get("responsavel_celular") or "", key="ed_emp_resp_c")
                with col_e2:
                    ed_col = st.text_input("Número de Colaboradores", value=emp_em_edicao.get("num_colaboradores") or "", key="ed_emp_col")
                    ed_sit = st.text_input("Site", value=emp_em_edicao.get("site") or "", key="ed_emp_sit")
                    ed_tel = st.text_input("Telefone de contato", value=emp_em_edicao.get("telefone") or "", key="ed_emp_t")
                    ed_em = st.text_input("Email de contato", value=emp_em_edicao.get("email") or "", key="ed_emp_e")
                    ed_resp_em = st.text_input("Email do Responsável", value=emp_em_edicao.get("responsavel_email") or "", key="ed_emp_resp_e")

                st.write("**Logo da Empresa:**")
                up_logo_ed = st.file_uploader("Fazer upload do logo (PNG/JPG)", type=["png", "jpg", "jpeg"], key="up_logo_ed_emp")

                st.write("---")
                col_eb1, col_eb2, col_eb3 = st.columns([2, 2, 4])
                with col_eb1:
                    if st.button("Salvar", type="primary", use_container_width=True, key="btn_save_ed_emp_final"):
                        ed_emp_str = ed_emp or ""
                        ed_cnpj_str = ed_cnpj or ""
                        ed_raz_str = ed_raz or ""
                        ed_seg_str = ed_seg or ""
                        ed_col_str = ed_col or ""
                        ed_sit_str = ed_sit or ""
                        ed_tel_str = ed_tel or ""
                        ed_em_str = ed_em or ""
                        ed_resp_str = ed_resp or ""
                        ed_resp_cel_str = ed_resp_cel or ""
                        ed_resp_em_str = ed_resp_em or ""
                        
                        if not ed_emp_str.strip():
                            st.error("O campo 'Nome da Empresa' é obrigatório.")
                        elif ed_cnpj_str.strip() and not validar_cnpj(ed_cnpj_str):
                            st.error("CNPJ inválido. Verifique a numeração informada.")
                        else:
                            novo_logo = emp_em_edicao.get("logo") or "⛶"
                            if up_logo_ed:
                                b64_l = compress_image_to_b64(up_logo_ed, max_width=300)
                                if b64_l: novo_logo = b64_l

                            payload = {
                                "nome_empresa": ed_emp_str.strip(),
                                "razao_social": ed_raz_str.strip() if ed_raz_str.strip() else None,
                                "cnpj": ed_cnpj_str.strip() if ed_cnpj_str.strip() else None,
                                "segmento": ed_seg_str.strip() if ed_seg_str.strip() else None,
                                "num_colaboradores": ed_col_str.strip() if ed_col_str.strip() else None,
                                "site": ed_sit_str.strip() if ed_sit_str.strip() else None,
                                "telefone": ed_tel_str.strip() if ed_tel_str.strip() else None,
                                "email": ed_em_str.strip() if ed_em_str.strip() else None,
                                "responsavel_nome": ed_resp_str.strip() if ed_resp_str.strip() else None,
                                "responsavel_celular": ed_resp_cel_str.strip() if ed_resp_cel_str.strip() else None,
                                "responsavel_email": ed_resp_em_str.strip() if ed_resp_em_str.strip() else None,
                                "logo": novo_logo,
                                "updated_at": datetime.datetime.now().isoformat()
                            }
                            if supabase_client:
                                try:
                                    supabase_client.table("empresas").update(payload).eq("nome_empresa", emp_em_edicao["nome_empresa"]).execute()
                                    st.success("empresa salva com sucesso.")
                                    emp_em_edicao.update(payload)
                                    st.session_state["edit_empresa_id"] = None
                                    st.rerun()
                                except Exception as ex:
                                    st.error(f"Erro ao salvar no Supabase: {ex}\n\nDICA: Lembre-se de rodar o script 'empresas_schema.sql' no SQL Editor do Supabase para atualizar a tabela e o cache.")
                            else:
                                emp_em_edicao.update(payload)
                                st.success("empresa salva com sucesso.")
                                st.session_state["edit_empresa_id"] = None
                                st.rerun()
                with col_eb2:
                    if st.button("Cancelar", use_container_width=True, key="btn_canc_ed_emp_final"):
                        st.session_state["edit_empresa_id"] = None
                        st.rerun()

        elif st.session_state["add_empresa_mode"]:
            st.write("---")
            st.subheader("Adicionar nova empresa")
            with st.container(border=True):
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    n_emp = st.text_input("Nome da Empresa*", key="add_emp_n")
                    n_raz = st.text_input("Razão Social", key="add_emp_r")
                    n_cnpj = st.text_input("CNPJ (com ou sem pontuação)", key="add_emp_c")
                    n_seg = st.text_input("Segmento", key="add_emp_s")
                    n_resp = st.text_input("Nome do Responsável", key="add_emp_resp")
                    n_resp_cel = st.text_input("Celular do Responsável", key="add_emp_resp_c")
                with col_a2:
                    n_col = st.text_input("Número de Colaboradores", key="add_emp_col")
                    n_sit = st.text_input("Site", key="add_emp_sit")
                    n_tel = st.text_input("Telefone de contato", key="add_emp_t")
                    n_em = st.text_input("Email de contato", key="add_emp_e")
                    n_resp_em = st.text_input("Email do Responsável", key="add_emp_resp_e")

                st.write("**Logo da Empresa:**")
                up_logo_add = st.file_uploader("Fazer upload do logo (PNG/JPG)", type=["png", "jpg", "jpeg"], key="up_logo_add_emp")

                st.write("---")
                col_b1, col_b2, col_b3 = st.columns([2, 2, 4])
                with col_b1:
                    if st.button("Salvar", type="primary", use_container_width=True, key="btn_save_emp_final"):
                        n_emp_str = n_emp or ""
                        n_cnpj_str = n_cnpj or ""
                        n_raz_str = n_raz or ""
                        n_seg_str = n_seg or ""
                        n_col_str = n_col or ""
                        n_sit_str = n_sit or ""
                        n_tel_str = n_tel or ""
                        n_em_str = n_em or ""
                        n_resp_str = n_resp or ""
                        n_resp_cel_str = n_resp_cel or ""
                        n_resp_em_str = n_resp_em or ""

                        if not n_emp_str.strip():
                            st.error("O campo 'Nome da Empresa' é obrigatório.")
                        elif n_cnpj_str.strip() and not validar_cnpj(n_cnpj_str):
                            st.error("CNPJ inválido. Verifique a numeração informada.")
                        else:
                            novo_logo = "⛶"
                            if up_logo_add:
                                b64_l = compress_image_to_b64(up_logo_add, max_width=300)
                                if b64_l: novo_logo = b64_l

                            payload = {
                                "nome_empresa": n_emp_str.strip(),
                                "razao_social": n_raz_str.strip() if n_raz_str.strip() else None,
                                "cnpj": n_cnpj_str.strip() if n_cnpj_str.strip() else None,
                                "segmento": n_seg_str.strip() if n_seg_str.strip() else None,
                                "num_colaboradores": n_col_str.strip() if n_col_str.strip() else None,
                                "site": n_sit_str.strip() if n_sit_str.strip() else None,
                                "telefone": n_tel_str.strip() if n_tel_str.strip() else None,
                                "email": n_em_str.strip() if n_em_str.strip() else None,
                                "responsavel_nome": n_resp_str.strip() if n_resp_str.strip() else None,
                                "responsavel_celular": n_resp_cel_str.strip() if n_resp_cel_str.strip() else None,
                                "responsavel_email": n_resp_em_str.strip() if n_resp_em_str.strip() else None,
                                "logo": novo_logo,
                                "created_at": datetime.datetime.now().isoformat(),
                                "updated_at": datetime.datetime.now().isoformat()
                            }
                            if supabase_client:
                                try:
                                    supabase_client.table("empresas").insert(payload).execute()
                                    st.success("empresa salva com sucesso.")
                                    st.session_state["add_empresa_mode"] = False
                                    st.rerun()
                                except Exception as ex:
                                    st.error(f"Erro ao salvar no Supabase: {ex}")
                            else:
                                if "empresas_local_data" not in st.session_state: st.session_state["empresas_local_data"] = []
                                st.session_state["empresas_local_data"].append(payload)
                                st.success("empresa salva com sucesso.")
                                st.session_state["add_empresa_mode"] = False
                                st.rerun()
                with col_b2:
                    if st.button("Cancelar", use_container_width=True, key="btn_canc_emp_final"):
                        st.session_state["add_empresa_mode"] = False
                        st.rerun()
        else:
            col_topo1, col_topo2 = st.columns([1, 5])
            with col_topo1:
                if st.button("Adicionar", type="primary", key="btn_add_emp_start"):
                    st.session_state["add_empresa_mode"] = True
                    st.rerun()

            st.write("---")
            if not lista_empresas:
                st.info("Nenhuma empresa cadastrada no sistema.")
            else:
                for emp in lista_empresas:
                    with st.container(border=True):
                        col_c1, col_c2, col_c3, col_c4 = st.columns([1, 3, 2, 2])
                        with col_c1:
                            logo_v = emp.get('logo') or '⛶'
                            if len(logo_v) > 20:
                                st.image(f"data:image/png;base64,{logo_v}", width=45)
                            else:
                                st.markdown(f"<span style='font-size: 1.5em;'>{logo_v}</span>", unsafe_allow_html=True)
                        with col_c2:
                            st.write(f"**{emp['nome_empresa']}**")
                            st.caption(f"{emp.get('razao_social') or ''}")
                        with col_c3:
                            st.write(f"**CNPJ:** {emp.get('cnpj') or 'N/I'}")
                            st.caption(f"Segmento: {emp.get('segmento') or 'N/I'}")
                        with col_c4:
                            if st.button("Visualizar Detalhes", key=f"v_emp_{emp['nome_empresa']}", use_container_width=True):
                                st.session_state["view_empresa_selected"] = emp["nome_empresa"]
                                st.rerun()
