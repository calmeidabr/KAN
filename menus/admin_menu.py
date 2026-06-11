import streamlit as st
import pandas as pd
import datetime
from PIL import Image, ImageDraw, ImageFont
import os

from menus.base_menu import BaseMenu
from menus.empresas_menu import EmpresasMenu
from models.database import (
    get_supabase, get_supabase_admin, carregar_empresas, carregar_todos_clientes,
    fetch_banners, fetch_assets_list, fetch_descricoes_mapa,
    KAN_DB, PERFIS_DB, LISTA_CATEGORIA_DB, QUALIDADES_DB, MENU_PRINCIPAL
)
from services.numerologia import calcular_numerologia, reduce_number
from services.perfil import realizar_calculos_completos, calcular_perfil_comportamental
from utils.helpers import compress_image_to_b64, remover_acentos, validar_cnpj
from utils.graphics import gerar_svg_triangulos_harmonicos

class AdminMenu(BaseMenu):
    def render(self):
        st.markdown("<h2 style='text-align: left; margin-bottom: 5px;'>Painel de Controle Administrativo</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.1em; color: rgba(255,255,255,0.7); margin-bottom: 20px;'>Central de comando administrativa do sistema KAN.</p>", unsafe_allow_html=True)
        
        if st.session_state.get("logged_user") == "adminkan":
            st.session_state["admin_authenticated"] = True

        if "admin_authenticated" not in st.session_state:
            st.session_state["admin_authenticated"] = False

        if not st.session_state["admin_authenticated"]:
            st.warning("Área restrita. Identifique-se para acessar o Painel.")
            col_auth1, col_auth2 = st.columns(2)
            with col_auth1:
                user_admin = st.text_input("Usuário de Administrador", key="admin_user_input")
            with col_auth2:
                pass_admin = st.text_input("Senha de Administrador", type="password", key="admin_pass_input")
                
            if st.button("Validar Acesso Administrativo"):
                if user_admin == "adminkan" and pass_admin == "K@nAdmin#2026*":
                    st.session_state["admin_authenticated"] = True
                    st.session_state["admin_user"] = user_admin
                    st.success(f"Bem-vindo, {user_admin}!")
                    st.rerun()
                else:
                    st.error("Usuário ou Senha incorretos!")
            return
        

        
        supabase_client = get_supabase_admin()
        
        t_tab1, t_tab2, t_tab3, t_tab4, t_tab_auditoria, t_tab_mapas, t_tab_mapa_num, t_tab5, t_tab_soft, t_tab_estudos = st.tabs(["Tabelas", "Base", "Usuários", "Empresas", "Auditoria", "Mapas Salvos", "Mapa Numerológico", "Banners", "Soft Skills", "Estudos"])
        
        with t_tab1:
            st.subheader("Editor de Configurações (Tabelas)")
            
            with st.expander("Inserção em Lote (Upload de Perfis via CSV)", expanded=False):
                st.markdown("""
                **Instruções:** Carregue um arquivo CSV com as seguintes colunas:
                `Nome completo`, `Data de Nascimento`, `Cargo/Profissao`, `Grupo` (ou `Empresa/Grupo`).
                """)
                arquivo_csv = st.file_uploader("Escolha o arquivo CSV:", type=["csv"])
                if arquivo_csv is not None:
                    try:
                        df_lote = pd.read_csv(arquivo_csv, sep=";")
                        if df_lote.shape[1] <= 1:
                            df_lote = pd.read_csv(arquivo_csv, sep=",")
                        
                        col_grupo_name = next((c for c in df_lote.columns if c in ["Grupo", "Empresa/Grupo"]), None)
                        col_cargo_name = next((c for c in df_lote.columns if c in ["Cargo/Profissao", "Profissao", "Cargo/Profissão"]), None)
                        colunas_obrigatorias = ["Nome completo", "Data de Nascimento"]
                        colunas_validas = True
                        for col in colunas_obrigatorias:
                            if col not in df_lote.columns:
                                colunas_validas = False
                                st.error(f"Coluna obrigatória ausente no CSV: `{col}`")
                        if not col_cargo_name:
                            colunas_validas = False
                            st.error("Coluna obrigatória ausente no CSV: `Profissao` ou `Cargo/Profissao`")
                        if not col_grupo_name:
                            colunas_validas = False
                            st.error("Coluna obrigatória ausente no CSV: `Grupo` (ou `Empresa/Grupo`) ")
                        
                        if colunas_validas:
                            st.dataframe(df_lote, use_container_width=True)
                            if st.button("Confirmar Inserção em Lote"):
                                with st.spinner("Gravando perfis no banco de dados..."):
                                    sucessos = 0
                                    for _, row in df_lote.iterrows():
                                        n_nome = str(row["Nome completo"]).strip()
                                        n_data = str(row["Data de Nascimento"]).strip()
                                        n_profissao = str(row[col_cargo_name]).strip()
                                        n_empresa = str(row[col_grupo_name]).strip() if col_grupo_name else ""
                                        
                                        if n_nome and n_data:
                                            try:
                                                if supabase_client:
                                                    resp_chk = supabase_client.table("mapas_salvos").select("id").eq("nome", n_nome).execute()
                                                    if resp_chk.data:
                                                        supabase_client.table("mapas_salvos").update({
                                                            "data_nascimento": n_data,
                                                            "profissao": n_profissao,
                                                            "grupo": n_empresa
                                                        }).eq("nome", n_nome).execute()
                                                    else:
                                                        supabase_client.table("mapas_salvos").insert({
                                                            "nome": n_nome,
                                                            "data_nascimento": n_data,
                                                            "profissao": n_profissao,
                                                            "grupo": n_empresa
                                                        }).execute()
                                                    sucessos += 1
                                            except Exception as ex:
                                                st.error(f"Erro ao inserir `{n_nome}`: {ex}")
                                    st.success(f"Processamento concluído! {sucessos} perfis integrados.")
                                    st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Erro ao ler CSV: {e}")

            st.markdown("---")
            tabelas_config = ["matriz", "atributos", "repeticao", "peso", "perfis", "lista_categoria", "qualidades", "categoria_descricao", "descricoes_mapa", "campo_definicao"]
            tab_selecionada = st.selectbox("Selecione a tabela para editar:", tabelas_config)
            
            if supabase_client:
                try:
                    res_tab = supabase_client.table(tab_selecionada).select("*").execute()
                    df_edit = pd.DataFrame(res_tab.data)
                    
                    if df_edit.empty and tab_selecionada == "descricoes_mapa":
                        dict_mapa = fetch_descricoes_mapa()
                        flat_data = []
                        for cat, subdict in dict_mapa.items():
                            for val, desc in subdict.items():
                                flat_data.append({"categoria": cat, "valor": val, "descricao": desc.get('descricao', desc) if isinstance(desc, dict) else desc})
                        df_edit = pd.DataFrame(flat_data)
                    
                    if not df_edit.empty or tab_selecionada == "descricoes_mapa":
                        st.write(f"Editando: `{tab_selecionada}`")
                        if df_edit.empty:
                            df_edit = pd.DataFrame(columns=["categoria", "valor", "descricao"])
                        
                        disabled_cols = []
                        if tab_selecionada == "descricoes_mapa":
                            disabled_cols = [c for c in df_edit.columns if c not in ["descricao", "resumo"]]
                        elif tab_selecionada == "campo_definicao":
                            disabled_cols = [c for c in df_edit.columns if c not in ["explicacao"]]
                        else:
                            disabled_cols = [c for c in ["id", "categoria", "valor", "campo"] if c in df_edit.columns]
                        
                        edited_df = st.data_editor(df_edit, use_container_width=True, disabled=disabled_cols, num_rows="dynamic")
                        
                        if st.button(f"Salvar Alterações em {tab_selecionada}"):
                            with st.spinner("Sincronizando com o banco de dados..."):
                                try:
                                    supabase_client.table(tab_selecionada).delete().neq("id", -1).execute() 
                                    novos_dados = edited_df.to_dict(orient='records')
                                    cleaned_dados = []
                                    for d in novos_dados:
                                        d_clean = {k: v for k, v in d.items() if not (k == 'id' and pd.isna(v))}
                                        cleaned_dados.append(d_clean)
                                    if cleaned_dados:
                                        supabase_client.table(tab_selecionada).insert(cleaned_dados).execute()
                                    st.success(f"Tabela `{tab_selecionada}` atualizada com sucesso!")
                                    st.cache_data.clear() 
                                except Exception as e:
                                    st.error(f"Erro ao salvar: {e}")
                    else:
                        st.warning("Tabela vazia ou não encontrada.")
                except Exception as e:
                    st.error(f"Erro ao carregar tabela: {e}")
                    
        with t_tab2:
            st.subheader("Visualização da Base de Mapas Salvos")
            if supabase_client:
                try:
                    res_mapas = supabase_client.table("mapas_salvos").select("*").order("id", desc=True).execute()
                    if res_mapas.data:
                        df_view = pd.DataFrame(res_mapas.data)
                        st.dataframe(df_view, use_container_width=True)
                    else:
                        st.info("Nenhum mapa salvo encontrado.")
                except Exception as e:
                    st.error(f"Erro ao carregar mapas: {e}")

        with t_tab3:
            st.subheader("Gerenciamento de Usuários")
            
            def carregar_usuarios():
                if supabase_client:
                    try:
                        res = supabase_client.table("usuarios").select("*").order("usuario").execute()
                        if res.data:
                            return res.data
                        else:
                            iniciais = [
                                {"usuario": "adminkan", "nome_completo": "Administrador Master KAN", "email": "adminkan@mundokan.com.br", "celular": "(11) 99999-9999", "data_nascimento": "01/01/1980", "empresa": "Mundo Kan", "cargo": "CEO / Master Admin", "departamento": "Diretoria", "direitos": "admin master", "status": "Ativo", "foto": "☖", "grupo": "Geral"},
                                {"usuario": "cristiano", "nome_completo": "Cristiano Almeida", "email": "cristiano@mundokan.com.br", "celular": "(11) 98888-8888", "data_nascimento": "15/05/1985", "empresa": "Mundo Kan", "cargo": "Gestor de Sistemas", "departamento": "Tecnologia", "direitos": "Editor", "status": "Ativo", "foto": "☖", "grupo": "Geral"},
                                {"usuario": "maria", "nome_completo": "Maria da Silva", "email": "maria@mundokan.com.br", "celular": "(11) 97777-7777", "data_nascimento": "20/08/1990", "empresa": "Empresa Cliente A", "cargo": "Analista de RH", "departamento": "Recursos Humanos", "direitos": "Analista", "status": "Ativo", "foto": "☖", "grupo": "Geral"},
                                {"usuario": "empresa_demo", "nome_completo": "Tech Corp Brasil Ltda", "email": "contato@techcorp.com", "celular": "(11) 96666-6666", "data_nascimento": "10/10/2000", "empresa": "Tech Corp", "cargo": "Conta Empresarial", "departamento": "Operações", "direitos": "Comum", "status": "Ativo", "foto": "⛶", "grupo": "Empresas"}
                            ]
                            for item in iniciais:
                                supabase_client.table("usuarios").insert(item).execute()
                            return iniciais
                    except Exception as ex:
                        st.warning("A tabela 'usuarios' ainda não existe ou erro ao ler do banco de dados. Executando modo em cache local.")
                if "usuarios_data" not in st.session_state:
                    st.session_state.usuarios_data = [
                        {"usuario": "adminkan", "nome_completo": "Administrador Master KAN", "email": "adminkan@mundokan.com.br", "celular": "(11) 99999-9999", "data_nascimento": "01/01/1980", "empresa": "Mundo Kan", "cargo": "CEO / Master Admin", "departamento": "Diretoria", "direitos": "admin master", "status": "Ativo", "foto": "☖", "grupo": "Geral"},
                        {"usuario": "cristiano", "nome_completo": "Cristiano Almeida", "email": "cristiano@mundokan.com.br", "celular": "(11) 98888-8888", "data_nascimento": "15/05/1985", "empresa": "Mundo Kan", "cargo": "Gestor de Sistemas", "departamento": "Tecnologia", "direitos": "Editor", "status": "Ativo", "foto": "☖", "grupo": "Geral"},
                        {"usuario": "maria", "nome_completo": "Maria da Silva", "email": "maria@mundokan.com.br", "celular": "(11) 97777-7777", "data_nascimento": "20/08/1990", "empresa": "Empresa Cliente A", "cargo": "Analista de RH", "departamento": "Recursos Humanos", "direitos": "Analista", "status": "Ativo", "foto": "☖", "grupo": "Geral"},
                        {"usuario": "empresa_demo", "nome_completo": "Tech Corp Brasil Ltda", "email": "contato@techcorp.com", "celular": "(11) 96666-6666", "data_nascimento": "10/10/2000", "empresa": "Tech Corp", "cargo": "Conta Empresarial", "departamento": "Operações", "direitos": "Comum", "status": "Ativo", "foto": "⛶", "grupo": "Empresas"}
                    ]
                return st.session_state.usuarios_data
 
            lista_usuarios_atual = carregar_usuarios()
            lista_empresas_salvas = carregar_empresas()
            nomes_empresas = [e["nome_empresa"] for e in lista_empresas_salvas if e.get("nome_empresa")]
            if not nomes_empresas:
                nomes_empresas = ["Mundo Kan", "Empresa Cliente A", "Tech Corp"]

            if "view_selected_user" not in st.session_state:
                st.session_state["view_selected_user"] = None
            if "edit_mode_user" not in st.session_state:
                st.session_state["edit_mode_user"] = None
            if "add_user_mode" not in st.session_state:
                st.session_state["add_user_mode"] = False

            sel_user_id = st.session_state["view_selected_user"]
            if sel_user_id:
                u_obj = next((u for u in lista_usuarios_atual if u["usuario"] == sel_user_id), None)
                if not u_obj:
                    st.session_state["view_selected_user"] = None
                    st.rerun()

                col_btn1, col_btn2 = st.columns([1, 5])
                with col_btn1:
                    if st.button("Voltar à Lista", key="btn_back_list", use_container_width=True):
                        st.session_state["view_selected_user"] = None
                        st.session_state["edit_mode_user"] = None
                        st.rerun()

                st.write("---")

                is_editing = (st.session_state["edit_mode_user"] == sel_user_id)
                logged_adm = st.session_state.get("logged_user")

                if is_editing:
                    st.markdown(f"<h3 style='color: #F18617;'>Editando Usuário: {u_obj['usuario']}</h3>", unsafe_allow_html=True)
                    with st.container(border=True):
                        e_col1, e_col2 = st.columns(2)
                        with e_col1:
                            ed_user = st.text_input("Nome de usuário (@)", value=u_obj["usuario"], disabled=True, key="ed_usr")
                            ed_nome = st.text_input("Nome completo (como na certidão de nascimento)", value=u_obj.get("nome_completo", ""), key="ed_nome")
                            ed_email = st.text_input("E-mail", value=u_obj.get("email", ""), key="ed_email")
                            ed_data = st.text_input("Data de Nascimento (DD/MM/AAAA)", value=u_obj.get("data_nascimento", ""), key="ed_data")
                            
                            emp_atual = u_obj.get("empresa") or ""
                            if emp_atual not in nomes_empresas and emp_atual:
                                opcoes_emp = [emp_atual] + [n for n in nomes_empresas if n != emp_atual]
                            else:
                                opcoes_emp = nomes_empresas
                            idx_emp = opcoes_emp.index(emp_atual) if emp_atual in opcoes_emp else 0
                            ed_emp = st.selectbox("Empresa", options=opcoes_emp, index=idx_emp, key="ed_emp")
                            
                            ed_grupo = st.selectbox("Subgrupo de Exibição", ["Geral", "Empresas"], index=["Geral", "Empresas"].index(u_obj.get("grupo", "Geral")), key="ed_grp")
                        with e_col2:
                            ed_cel = st.text_input("Celular", value=u_obj.get("celular", ""), key="ed_cel")
                            ed_cargo = st.text_input("Cargo/Função", value=u_obj.get("cargo", ""), key="ed_cargo")
                            ed_depto = st.text_input("Departamento", value=u_obj.get("departamento", ""), key="ed_depto")
                            ed_dir = st.selectbox("Direitos", ["Editor", "Analista", "Comum"], index=["Editor", "Analista", "Comum"].index(u_obj.get("direitos", "Comum")) if u_obj.get("direitos", "Comum") in ["Editor", "Analista", "Comum"] else 2, key="ed_dir")
                            ed_st = st.selectbox("Status", ["Ativo", "Inativo"], index=0 if u_obj.get("status", "Ativo") == "Ativo" else 1, key="ed_st")

                        st.write("**Foto de Perfil:**")
                        up_foto = st.file_uploader("Fazer upload de nova foto (PNG/JPG)", type=["png", "jpg", "jpeg", "webp"], key="up_foto_usr")
                        
                        col_s1, col_s2, col_s3 = st.columns([2, 2, 4])
                        with col_s1:
                            if st.button("Salvar", type="primary", use_container_width=True, key="btn_save_ed"):
                                nova_foto = u_obj.get("foto", "☖")
                                if up_foto:
                                    b64_f = compress_image_to_b64(up_foto, max_width=300)
                                    if b64_f: nova_foto = b64_f
                                
                                update_payload = {
                                    "nome_completo": ed_nome,
                                    "email": ed_email,
                                    "celular": ed_cel,
                                    "data_nascimento": ed_data,
                                    "empresa": ed_emp,
                                    "cargo": ed_cargo,
                                    "departamento": ed_depto,
                                    "direitos": ed_dir,
                                    "status": ed_st,
                                    "foto": nova_foto,
                                    "grupo": ed_grupo,
                                    "updated_at": datetime.datetime.now().isoformat()
                                }
                                
                                if supabase_client:
                                    try:
                                        chk_exist = supabase_client.table("usuarios").select("id").eq("usuario", u_obj["usuario"]).execute()
                                        if chk_exist.data:
                                            supabase_client.table("usuarios").update(update_payload).eq("usuario", u_obj["usuario"]).execute()
                                        else:
                                            insert_payload = update_payload.copy()
                                            insert_payload["usuario"] = u_obj["usuario"]
                                            supabase_client.table("usuarios").insert(insert_payload).execute()
                                        st.success("usuário salvo com sucesso.")
                                        u_obj.update(update_payload)
                                        st.session_state["edit_mode_user"] = None
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao salvar no banco de dados: {e}\n\nDICA: Certifique-se de executar o script SQL de atualização de estrutura correspondente.")
                                else:
                                    u_obj.update(update_payload)
                                    st.session_state["edit_mode_user"] = None
                                    st.rerun()
                        with col_s2:
                            if st.button("Cancelar", use_container_width=True, key="btn_canc_ed"):
                                st.session_state["edit_mode_user"] = None
                                st.rerun()
                else:
                    with st.container(border=True):
                        v_c1, v_c2 = st.columns([1, 4])
                        with v_c1:
                            foto_val = u_obj.get('foto', '☖')
                            if len(foto_val) > 20:
                                st.image(f"data:image/png;base64,{foto_val}", width=100)
                            else:
                                st.markdown(f"<div style='font-size: 3.5em; text-align: center; background: rgba(241,134,23,0.2); border-radius: 50%; padding: 10px;'>{foto_val}</div>", unsafe_allow_html=True)
                        with v_c2:
                            st.markdown(f"<h2 style='margin: 0; color: #FFFFFF;'>{u_obj.get('nome_completo', u_obj['usuario'])}</h2>", unsafe_allow_html=True)
                            st.markdown(f"<p style='color: #F18617; font-size: 1.1em; font-weight: bold;'>@{u_obj['usuario']} • <span style='color: #39ff14;'>{u_obj.get('status', 'Ativo')}</span></p>", unsafe_allow_html=True)

                        st.write("---")
                        d_col1, d_col2, d_col3, d_col4 = st.columns(4)
                        with d_col1:
                            st.write("**E-mail:**")
                            st.write(u_obj.get("email", "Não informado"))
                            st.write("**Empresa:**")
                            st.write(u_obj.get("empresa", "Não informada"))
                            st.write("**Departamento:**")
                            st.write(u_obj.get("departamento", "Não informado"))
                        with d_col2:
                            st.write("**Celular:**")
                            st.write(u_obj.get("celular", "Não informado"))
                            st.write("**Cargo/Função:**")
                            st.write(u_obj.get("cargo", "Não informado"))
                            st.write("**Nascimento:**")
                            st.write(u_obj.get("data_nascimento", "Não informado"))
                        with d_col3:
                            st.write("**Subgrupo:**")
                            st.write(u_obj.get("grupo", "Geral"))
                        with d_col4:
                            st.write("**Direitos:**")
                            st.write(str(u_obj.get("direitos", "Comum")).upper())

                        st.write("---")
                        
                        if u_obj["usuario"] == "adminkan":
                            st.warning("O usuário master (adminkan) é o controlador do sistema e não pode ser editado.")
                        elif logged_adm != "adminkan":
                            st.warning("Apenas o administrador master (adminkan) tem permissão para editar usuários.")
                        else:
                            if st.button("Editar Usuário", type="primary", key="btn_start_edit"):
                                st.session_state["edit_mode_user"] = sel_user_id
                                st.rerun()

            elif st.session_state["add_user_mode"]:
                st.subheader("Adicionar novo usuário")
                with st.container(border=True):
                    a_col1, a_col2 = st.columns(2)
                    with a_col1:
                        add_user = st.text_input("Nome de usuário (@)*", key="add_usr_in")
                        add_nome = st.text_input("Nome completo (como na certidão de nascimento)", key="add_nome_in")
                        add_email = st.text_input("E-mail", key="add_email_in")
                        add_data = st.text_input("Data de Nascimento (DD/MM/AAAA)", key="add_data_in")
                        add_emp = st.selectbox("Empresa", options=nomes_empresas, index=0, key="add_emp_in")
                        add_grupo = st.selectbox("Subgrupo de Exibição", ["Geral", "Empresas"], index=0, key="add_grp_in")
                    with a_col2:
                        add_cel = st.text_input("Celular", key="add_cel_in")
                        add_cargo = st.text_input("Cargo/Função", key="add_cargo_in")
                        add_depto = st.text_input("Departamento", key="add_depto_in")
                        add_dir = st.selectbox("Direitos", ["Editor", "Analista", "Comum"], index=2, key="add_dir_in")
                        add_st = st.selectbox("Status", ["Ativo", "Inativo"], index=0, key="add_st_in")

                    st.write("**Foto de Perfil:**")
                    up_foto_add = st.file_uploader("Fazer upload de foto (PNG/JPG)", type=["png", "jpg", "jpeg", "webp"], key="up_foto_add_usr")
                    
                    col_sa1, col_sa2, col_sa3 = st.columns([2, 2, 4])
                    with col_sa1:
                        if st.button("Salvar", type="primary", use_container_width=True, key="btn_save_add_usr"):
                            add_user_str = add_user or ""
                            if not add_user_str.strip():
                                st.error("O campo 'Nome de usuário (@)' é obrigatório.")
                            else:
                                nova_foto = "☖"
                                if up_foto_add:
                                    b64_f = compress_image_to_b64(up_foto_add, max_width=300)
                                    if b64_f: nova_foto = b64_f
                                
                                insert_payload = {
                                    "usuario": add_user_str.strip(),
                                    "nome_completo": add_nome.strip() if add_nome else None,
                                    "email": add_email.strip() if add_email else None,
                                    "celular": add_cel.strip() if add_cel else None,
                                    "data_nascimento": add_data.strip() if add_data else None,
                                    "empresa": add_emp,
                                    "cargo": add_cargo.strip() if add_cargo else None,
                                    "departamento": add_depto.strip() if add_depto else None,
                                    "direitos": add_dir,
                                    "status": add_st,
                                    "foto": nova_foto,
                                    "grupo": add_grupo,
                                    "created_at": datetime.datetime.now().isoformat(),
                                    "updated_at": datetime.datetime.now().isoformat()
                                }
                                
                                if supabase_client:
                                    try:
                                        supabase_client.table("usuarios").insert(insert_payload).execute()
                                        st.success("usuário salvo com sucesso.")
                                        st.session_state["add_user_mode"] = False
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao salvar no banco de dados: {e}")
                                else:
                                    if "usuarios_data" not in st.session_state: st.session_state.usuarios_data = []
                                    st.session_state.usuarios_data.append(insert_payload)
                                    st.success("usuário salvo com sucesso.")
                                    st.session_state["add_user_mode"] = False
                                    st.rerun()
                    with col_sa2:
                        if st.button("Cancelar", use_container_width=True, key="btn_canc_add_usr"):
                            st.session_state["add_user_mode"] = False
                            st.rerun()

            else:
                col_topo_u1, col_topo_u2 = st.columns([1, 5])
                with col_topo_u1:
                    if st.button("Adicionar", type="primary", key="btn_add_usr_start"):
                        st.session_state["add_user_mode"] = True
                        st.rerun()
                st.write("---")
                sub_grupo = st.radio("Selecione o Subgrupo:", ["Geral", "Empresas"], horizontal=True, key="radio_subgrupo")
                st.write("---")

                lista_filtrada = [u for u in lista_usuarios_atual if u.get("grupo", "Geral") == sub_grupo]
                
                if not lista_filtrada:
                    st.info(f"Nenhum usuário cadastrado no subgrupo '{sub_grupo}'.")
                else:
                    for u in lista_filtrada:
                        with st.container(border=True):
                            col_u1, col_u2, col_u3, col_u4 = st.columns([1, 3, 2, 2])
                            with col_u1:
                                f_v = u.get('foto', '☖')
                                if len(f_v) > 20: st.image(f"data:image/png;base64,{f_v}", width=45)
                                else: st.markdown(f"<span style='font-size: 1.5em;'>{f_v}</span>", unsafe_allow_html=True)
                            with col_u2:
                                st.write(f"**{u.get('nome_completo', u['usuario'])}**")
                                st.caption(f"@{u['usuario']} | {u.get('cargo', '')}")
                            with col_u3:
                                st.write(f"**Direitos:** {str(u.get('direitos', 'Comum')).upper()}")
                                status_color = "#39ff14" if u.get('status', 'Ativo') == "Ativo" else "#ff3333"
                                st.markdown(f"Status: <span style='color: {status_color}; font-weight: bold;'>{u.get('status', 'Ativo')}</span>", unsafe_allow_html=True)
                            with col_u4:
                                if st.button("Visualizar Detalhes", key=f"view_{u['usuario']}", use_container_width=True):
                                    st.session_state["view_selected_user"] = u["usuario"]
                                    st.rerun()

        with t_tab4:
            st.subheader("Gerenciamento de Empresas")
            EmpresasMenu(self.app).render()

        with t_tab_auditoria:
            st.subheader("Auditoria e Verificação de Perfis")
            
            if st.button("CALCULAR MAPAS SALVOS (POPULAR TABELA DE VALORES)", use_container_width=True):
                st.info("Iniciando cálculo em lote... Isso pode demorar alguns instantes.")

                clientes_para_calc = carregar_todos_clientes()
                rows_to_insert = []
                data_atual_tup = (datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)

                def map_kan_name(k):
                    res = KAN_DB.get(str(k), {})
                    return res.get("kan", str(k))

                for n_aud, c_info in clientes_para_calc.items():
                    nasc_dt = c_info.get('data_nascimento')
                    try:
                        if isinstance(nasc_dt, (datetime.datetime, datetime.date)):
                            nascimento_tup = (nasc_dt.day, nasc_dt.month, nasc_dt.year)
                        elif isinstance(nasc_dt, str):
                            try: dt_obj = datetime.datetime.strptime(nasc_dt, "%d/%m/%Y")
                            except ValueError: dt_obj = datetime.datetime.strptime(nasc_dt, "%Y-%m-%d")
                            nascimento_tup = (dt_obj.day, dt_obj.month, dt_obj.year)
                        else:
                            continue
                            
                        res_calc = realizar_calculos_completos(n_aud, nascimento_tup, data_atual_tup, c_info.get('profissao', c_info.get('cargo', '')), c_info.get('grupo'))
                        dados, dados_perfil, kan, estrutural, direcionamento, rep1, rep2, rep3, rep4, _, _, _, _ = res_calc
                        
                        def ext_val(label):
                            for d in dados:
                                if str(d.get("Campo")).startswith(label):
                                    return str(d.get("Valor"))
                            return ""
                            
                        def ext_perfil(label, just_value=False):
                            for d in dados_perfil:
                                if str(d.get("Campo")).lower() == label.lower():
                                    if just_value:
                                        return str(d.get("Valor", ""))
                                    return str(d.get("Resultado", d.get("Valor", "")))
                            return ""

                        row_val = {
                            "nome": n_aud,
                            "data_nascimento": nasc_dt,
                            "kan": str(map_kan_name(kan)),
                            "perfil": ext_perfil("perfil", just_value=True),
                            "categoria": ext_perfil("categoria", just_value=True),
                            "qualidades": ext_perfil("qualidades", just_value=True),
                            "diferenciais": ext_perfil("diferenciais", just_value=True),
                            "motivacao": ext_val("Motivação"),
                            "impressao": ext_val("Impressão"),
                            "expressao": ext_val("Expressão"),
                            "dia_natalicio": ext_val("Dia Natalício"),
                            "numero_psiquico": ext_val("Número Psíquico"),
                            "destino": ext_val("Destino"),
                            "missao": ext_val("Missão"),
                            "direcionamento": str(direcionamento),
                            "estrutural": str(estrutural),
                            "repeticao_1": str(rep1),
                            "repeticao_2": str(rep2),
                            "repeticao_mapa": ext_val("Repetição Mapa"),
                            "repeticao_mapa_2": ext_val("Repetição 2 Mapa"),
                            "vertice_triangulo_1": "",
                            "vertice_triangulo_2": "",
                            "vertice_triangulo_3": ext_val("Triângulo Harmônico"),
                            "dividas_carmicas": ext_val("Dívidas Cármicas"),
                            "licoes_carmicas": ext_val("Lições Cármicas"),
                            "tendencias_ocultas": ext_val("Tendências Ocultas"),
                            "resposta_subconsciente": ext_val("Resposta Subconsciente")
                        }
                        rows_to_insert.append(row_val)
                    except Exception as e:
                        pass
                
                if rows_to_insert:
                    try:
                        supabase_client.table("mapas_salvos_valores").upsert(rows_to_insert, on_conflict="nome").execute()
                        st.success(f"{len(rows_to_insert)} mapas calculados e salvos com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao inserir: {e}. Certifique-se de executar o script SQL para criar as tabelas necessárias.")
                        
            st.write("---")
            st.subheader("Tabela de Mapas Salvos Valores")
            try:
                res_valores = supabase_client.table("mapas_salvos_valores").select("*").execute()
                if res_valores.data:
                    df_valores = pd.DataFrame(res_valores.data)
                    st.dataframe(df_valores, use_container_width=True)
                else:
                    st.info("A tabela 'mapas_salvos_valores' está vazia. Clique no botão acima para popular.")
            except Exception as e:
                st.error("Tabela mapas_salvos_valores não encontrada. Crie-a executando o script SQL correspondente.")
                
            st.write("---")
            st.subheader("Análise Individual")
            
            clientes_salvos_aud = carregar_todos_clientes()
            nomes_disp_aud = sorted(list(clientes_salvos_aud.keys()))
            
            if not nomes_disp_aud:
                st.warning("Nenhum perfil cadastrado na base de dados.")
            else:
                col_sel1, col_sel2 = st.columns([2, 2])
                with col_sel1:
                    nome_aud = st.selectbox("Selecione o Cliente / Perfil a ser analisado:", options=nomes_disp_aud, key="sel_aud_nome")
                
                if nome_aud:
                    c_info = clientes_salvos_aud[nome_aud]
                    nasc_dt = c_info['data_nascimento']
                    try:
                        from collections import Counter
                        if isinstance(nasc_dt, (datetime.datetime, datetime.date)):
                            nascimento_tup = (nasc_dt.day, nasc_dt.month, nasc_dt.year)
                        elif isinstance(nasc_dt, str):
                            try: dt_obj = datetime.datetime.strptime(nasc_dt, "%d/%m/%Y")
                            except ValueError: dt_obj = datetime.datetime.strptime(nasc_dt, "%Y-%m-%d")
                            nascimento_tup = (dt_obj.day, dt_obj.month, dt_obj.year)
                        else:
                            raise ValueError("Data inválida")
                            
                        now_dt = datetime.datetime.now()
                        data_atual_tup = (now_dt.day, now_dt.month, now_dt.year)
                        
                        res_calc_aud = realizar_calculos_completos(nome_aud, nascimento_tup, data_atual_tup, c_info.get('profissao', c_info.get('cargo', '')), c_info.get('grupo', ''))
                        dados, dados_perfil, kan, estrutural, direcionamento, rep1, rep2, rep3, rep4, score_df_calc, score_cat_df, score_qual_df, auditoria_qual_df = res_calc_aud
                        
                        clientes_salvos = clientes_salvos_aud
                        
                        with st.expander("Busca de Perfis Cadastrados (Auditoria)", expanded=False):
                            st.markdown("### Selecione os filtros desejados")
                            st.caption("Você pode escolher mais de uma opção em cada filtro ou deixá-los em branco para buscar todos.")
                            
                            kan_display_map = {"3": "CRIAÇÃO", "6": "MOVIMENTO", "9": "FINALIDADE"}
                            all_kans_raw = sorted([str(k) for k in KAN_DB.keys()], key=lambda x: int(x)) if KAN_DB else ['1', '2', '3', '4', '5', '6', '7', '8', '9', '11', '22']
                            all_kans = [kan_display_map.get(k, k) for k in all_kans_raw]
                            
                            def limpa_lista(lst):
                                return sorted(list(set(str(x).strip() for x in lst if x and str(x).strip())))
                            
                            perfis_db_lista = PERFIS_DB if PERFIS_DB else ["Lider", "Criativo", "Executor", "Resultado", "Vendedor", "Influenciador", "Comunicador"]
                            all_perfis = limpa_lista(perfis_db_lista)
                            
                            cats_db_lista = LISTA_CATEGORIA_DB if LISTA_CATEGORIA_DB else ["Justo", "Inovador", "Diplomático", "Realizador", "Versátil", "Visionário", "Magnético", "Analítico", "Organizado", "Harmônico", "Comunicativo", "Intuitivo", "Conhecimento"]
                            all_cats = limpa_lista(cats_db_lista)
                            
                            quals_db_lista = list(QUALIDADES_DB.keys()) if QUALIDADES_DB else ["Relacionamento", "Execução", "Análise", "Coletividade", "Justiça", "Praticidade e disciplina", "Comunicação", "Versatilidade", "Intuição", "Organização", "Serviço"]
                            all_quals = limpa_lista(quals_db_lista)
                            
                            all_profissoes = limpa_lista([c.get('profissao', c.get('cargo', '')) for c in clientes_salvos.values()])
                            all_grupos = limpa_lista([c.get('grupo', '') for c in clientes_salvos.values()])
                            
                            col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                            with col_b1: filtro_kan = st.multiselect("KAN", options=all_kans, key="f_kan_aud")
                            with col_b2: filtro_perfil = st.multiselect("PERFIL", options=all_perfis, key="f_perf_aud")
                            with col_b3: filtro_cat = st.multiselect("Categoria", options=all_cats, key="f_cat_aud")
                            with col_b4: filtro_qual = st.multiselect("Qualidades", options=all_quals, key="f_qual_aud")
                            
                            col_b5, col_b6 = st.columns(2)
                            with col_b5: filtro_profissao = st.multiselect("Profissão", options=all_profissoes, key="f_profissao_aud")
                            with col_b6: filtro_grupo = st.multiselect("Grupo", options=all_grupos, key="f_emp_aud")
                            
                            if st.button("Realizar Busca de Perfis", key="btn_busca_aud"):
                                resultados_busca = []
                                for n, c in clientes_salvos.items():
                                    match_kan = True
                                    if filtro_kan:
                                        inv_kan_map = {v: k for k, v in kan_display_map.items()}
                                        f_kan_raw = [inv_kan_map.get(f, f) for f in filtro_kan]
                                        f_kan_norm = [str(f).strip() for f in f_kan_raw]
                                        match_kan = str(c.get('kan')).strip() in f_kan_norm
                                    
                                    match_perfil = True
                                    if filtro_perfil:
                                        f_perfis_norm = [remover_acentos(str(f)).upper().strip() for f in filtro_perfil]
                                        c_perfis = [remover_acentos(str(p)).upper().strip() for p in str(c.get('perfil', '')).split(',')]
                                        match_perfil = any(p in f_perfis_norm for p in c_perfis)
                                        
                                    match_cat = True
                                    if filtro_cat:
                                        f_cats_norm = [remover_acentos(str(f)).upper().strip() for f in filtro_cat]
                                        c_cats = [remover_acentos(str(p)).upper().strip() for p in str(c.get('categoria', '')).split(',')]
                                        match_cat = any(p in f_cats_norm for p in c_cats)
                                        
                                    match_qual = True
                                    if filtro_qual:
                                        f_quals_norm = [remover_acentos(str(f)).upper().strip() for f in filtro_qual]
                                        c_quals = [remover_acentos(str(q)).upper().strip() for q in str(c.get('qualidades', '')).split(',')]
                                        match_qual = any(q in f_quals_norm for q in c_quals)
                                    
                                    match_profissao = True
                                    if filtro_profissao:
                                        c_prof = c.get('profissao') if 'profissao' in c else c.get('cargo', '')
                                        match_profissao = str(c_prof).strip() in filtro_profissao
                                        
                                    match_empresa = True
                                    if filtro_grupo:
                                        match_empresa = str(c.get('grupo', '')).strip() in filtro_grupo
                                        
                                    if match_kan and match_perfil and match_cat and match_qual and match_profissao and match_empresa:
                                        row_res = {
                                            "Nome": n,
                                            "Data Nasc.": c.get('data_nascimento', ''),
                                            "KAN": kan_display_map.get(str(c.get('kan')), str(c.get('kan'))),
                                            "Perfil": c.get('perfil', ''),
                                            "Categoria": c.get('categoria', ''),
                                            "Qualidades": c.get('qualidades', ''),
                                            "Estrutural": c.get('estrutural', ''),
                                            "Direcionamento": c.get('direcionamento', ''),
                                            "REPETIÇÃO 1": c.get('repeticao_1', ''),
                                            "REPETIÇÃO 2": c.get('repeticao_2', ''),
                                            "Fortaleza": c.get('fortaleza', ''),
                                            "Desafio": c.get('desafio', '')
                                        }
                                        if c.get('mapa_detalhado'):
                                            for k_mapa, v_mapa in c['mapa_detalhado'].items():
                                                row_res[k_mapa] = v_mapa
                                        
                                        resultados_busca.append(row_res)
                                
                                if resultados_busca:
                                    st.success(f"{len(resultados_busca)} perfil(is) encontrado(s)!")
                                    df_final = pd.DataFrame(resultados_busca)
                                    st.dataframe(df_final, use_container_width=True, column_config={"Nome": st.column_config.Column(pinned=True)})
                                else:
                                    st.warning("Nenhum perfil encontrado com os critérios selecionados.")
                                    
                        with st.expander("Ver Scores Técnicos (Auditoria)", expanded=False):
                            p_val = next((item['Valor'] for item in dados_perfil if item['Campo'] == 'Perfil'), '')
                            c_val = next((item['Valor'] for item in dados_perfil if item['Campo'] == 'Categoria'), '')
                            q_val = next((item['Valor'] for item in dados_perfil if item['Campo'] == 'Qualidades'), '')

                            st.header("Score Perfil")
                            st.table(score_df_calc)
                            st.info(f"**Perfil Selecionado:** {p_val}")
                            
                            st.header("Score Categoria")
                            st.table(score_cat_df)
                            st.info(f"**Categoria Selecionada:** {c_val}")
                            
                            st.header("Score Qualidades")
                            st.table(score_qual_df)
                            st.info(f"**Qualidades Selecionadas:** {q_val}")
                            
                            st.header("Detalhamento dos Atributos")
                            st.table(auditoria_qual_df)
                            
                            st.header("Plano KAN")
                            df_plano_kan = pd.DataFrame({
                                "Campo": ["KAN", "ESTRUTURAL", "DIRECIONAMENTO", "REPETIÇÃO 1", "REPETICAO MAPA", "REPETICAO 2 MAPA", "REPETICAO 3 MAPA"],
                                "Valor": [
                                    kan, 
                                    estrutural, 
                                    direcionamento, 
                                    str(rep1).split(" - ")[0] if " - " in str(rep1) else str(rep1), 
                                    str(rep2).split(" - ")[0] if " - " in str(rep2) else str(rep2),
                                    str(rep3).split(" - ")[0] if " - " in str(rep3) else str(rep3),
                                    str(rep4).split(" - ")[0] if " - " in str(rep4) else str(rep4)
                                ]
                            })
                            st.table(df_plano_kan)
                            
                            st.header("Triângulo Harmônico")
                            
                            def clean_val(v):
                                if v is None or str(v).strip() in ("", "0", "None"): return None
                                s = str(v).split(" - ")[0]
                                return int(s) if s.isdigit() and int(s) > 0 else None

                            k_val = clean_val(kan)
                            e_val = clean_val(estrutural)
                            d_val = clean_val(direcionamento)
                            r1_val = clean_val(rep1)
                            r2_val = clean_val(rep2)
                            r3_val = clean_val(rep3)
                            r4_val = clean_val(rep4)
                            
                            todos_campos = [
                                {"campo": "KAN", "valor": k_val},
                                {"campo": "ESTRUTURAL", "valor": e_val},
                                {"campo": "DIRECIONAMENTO", "valor": d_val},
                                {"campo": "REPETIÇÃO 1", "valor": r1_val},
                                {"campo": "REPETICAO MAPA", "valor": r2_val},
                                {"campo": "REPETICAO 2 MAPA", "valor": r3_val},
                                {"campo": "REPETICAO 3 MAPA", "valor": r4_val}
                            ]
                            
                            vertices = []
                            valores_adicionados = set()
                            
                            for item in todos_campos:
                                val = item["valor"]
                                if val is not None and val not in [11, 22] and val not in valores_adicionados:
                                    vertices.append(item)
                                    valores_adicionados.add(val)
                                if len(vertices) == 3:
                                    break
                                    
                            valores_finais = [v["valor"] for v in vertices]
                            df_triangulo = pd.DataFrame({
                                "Vértice": [v["campo"] for v in vertices],
                                "Valor": [v["valor"] for v in vertices]
                            })
                            st.table(df_triangulo)
                            
                            if len(set(valores_finais)) == 3:
                                try:
                                    membros_tri = {nome_aud: [v['valor'] for v in vertices]}
                                    svg_html = gerar_svg_triangulos_harmonicos(membros_tri, lider_nome=nome_aud)
                                    st.markdown(svg_html, unsafe_allow_html=True)
                                            
                                    st.markdown("### <i class='icon-users' style='font-size: 20px; vertical-align: middle; margin-right: 8px; color: #F18617;'></i>Adicionar perfil para comparação", unsafe_allow_html=True)
                                    
                                    def obter_vertices_triangulo(nome_comp, data_nasc_str):
                                        def clean_val(v):
                                            if v is None: return None
                                            s = str(v).split(" - ")[0]
                                            return int(s) if s.isdigit() else None
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
                                                destino, missao, ciclos_vida['ciclo2']['numero'], momentos_decisivos['momento3']['numero'],
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
                                            
                                            from collections import Counter
                                            c_tot = Counter(todos_num)
                                            r_tot = sorted([(n, c) for n, c in c_tot.items()], key=lambda x: (-x[1], x[0]))
                                            
                                            r2_v = r_tot[0][0] if r_tot else 0
                                            r3_v = r_tot[1][0] if len(r_tot) > 1 else 0
                                            r4_v = r_tot[2][0] if len(r_tot) > 2 else 0
                                            
                                            k_v = clean_val(kan)
                                            e_v = clean_val(estrutural)
                                            d_v = clean_val(direcionamento)
                                            r1_v = clean_val(rep1)
                                            
                                            todos_comp = [
                                                {"campo": "KAN", "valor": k_v},
                                                {"campo": "ESTRUTURAL", "valor": e_v},
                                                {"campo": "DIRECIONAMENTO", "valor": d_v},
                                                {"campo": "REPETIÇÃO 1", "valor": r1_v},
                                                {"campo": "REPETICAO MAPA", "valor": r2_v},
                                                {"campo": "REPETICAO 2 MAPA", "valor": r3_v},
                                                {"campo": "REPETICAO 3 MAPA", "valor": r4_v}
                                            ]
                                            
                                            vertices_comp = []
                                            vals_comp = set()
                                            for it in todos_comp:
                                                v_it = it["valor"]
                                                if v_it is not None and v_it not in [11, 22] and v_it not in vals_comp:
                                                    vertices_comp.append(v_it)
                                                    vals_comp.add(v_it)
                                                if len(vertices_comp) == 3:
                                                    break
                                                    
                                            if len(vertices_comp) == 3:
                                                return vertices_comp
                                        except Exception as ex:
                                            st.error(f"Erro ao processar {nome_comp}: {ex}")
                                        return None

                                    perfis_disp = sorted([n for n in clientes_salvos.keys() if n != nome_aud])
                                    perfis_selecionados = st.multiselect("Pesquise e selecione os perfis:", options=perfis_disp, key="multi_comp_aud")
                                    
                                    if perfis_selecionados:
                                        try:
                                            comparativo_triangulos = {
                                                nome_aud: [v['valor'] for v in vertices]
                                            }
                                            for p_nome in perfis_selecionados:
                                                p_dados = clientes_salvos[p_nome]
                                                p_vertices = obter_vertices_triangulo(p_nome, p_dados['data_nascimento'])
                                                if p_vertices and len(p_vertices) == 3:
                                                    comparativo_triangulos[p_nome] = p_vertices
                                            
                                            svg_html = gerar_svg_triangulos_harmonicos(comparativo_triangulos, lider_nome=nome_aud)
                                            st.markdown(svg_html, unsafe_allow_html=True)
                                        except Exception as e:
                                            st.error(f"Erro ao gerar comparativo interativo: {e}")
                                            
                                except Exception as e:
                                    st.error(f"Erro ao gerar triângulo visual: {e}")
                            else:
                                st.warning("O triângulo harmônico não foi formado.")
                    except Exception as ex:
                        st.error(f"Erro ao processar dados de auditoria para {nome_aud}: {ex}")

        with t_tab_mapas:
            st.subheader("Mapas Salvos (Banco de Dados)")
            st.markdown("Visão geral de todos os perfis e mapas salvos na tabela `mapas_salvos`.")
            if st.button("Atualizar Tabela de Mapas Salvos"):
                st.rerun()
                
            try:
                res_mapas = supabase_client.table("mapas_salvos").select("*").order("id", desc=True).execute()
                if res_mapas.data:
                    df_mapas = pd.DataFrame(res_mapas.data)
                    # Remover colunas pesadas para exibição mais limpa
                    if "mapa_json" in df_mapas.columns:
                        df_mapas = df_mapas.drop(columns=["mapa_json"])
                    if "perfil_json" in df_mapas.columns:
                        df_mapas["perfil_json"] = df_mapas["perfil_json"].apply(lambda x: "JSON Calculado" if x else "Vazio")
                    if "foto_base64" in df_mapas.columns:
                        df_mapas["foto_base64"] = df_mapas["foto_base64"].apply(lambda x: "Foto Presente" if x else "Sem Foto")
                        
                    st.dataframe(df_mapas, use_container_width=True)
                    st.caption(f"Total de mapas salvos: {len(df_mapas)}")
                else:
                    st.info("Nenhum mapa salvo na base de dados.")
            except Exception as e:
                st.error(f"Erro ao carregar mapas salvos: {e}")

        with t_tab_mapa_num:
            st.subheader("Visualizador de Mapa Numerológico")
            st.markdown("Gere e visualize o Mapa Numerológico Cabalístico completo de qualquer talento cadastrado na base de dados.")
            
            clientes_salvos = carregar_todos_clientes()
            opcoes_clientes = sorted(list(clientes_salvos.keys()))
            if not opcoes_clientes:
                st.info("Nenhum talento cadastrado na base de dados.")
            else:
                cliente_selecionado = st.selectbox(
                    "Selecione um talento para visualizar o mapa:", 
                    options=opcoes_clientes, 
                    key="admin_mapa_num_select"
                )
                
                # Botão gerar mapa numerológico
                btn_gerar = st.button("Gerar Mapa Numerológico", key="btn_admin_mapa_num_gerar", type="primary")
                
                # Mantém controle do estado de exibição
                if "admin_show_mapa" not in st.session_state:
                    st.session_state["admin_show_mapa"] = False
                if "admin_last_selected_talento" not in st.session_state:
                    st.session_state["admin_last_selected_talento"] = cliente_selecionado
                
                if st.session_state["admin_last_selected_talento"] != cliente_selecionado:
                    st.session_state["admin_show_mapa"] = False
                    st.session_state["admin_last_selected_talento"] = cliente_selecionado
                    
                if btn_gerar:
                    st.session_state["admin_show_mapa"] = True
                    
                if st.session_state["admin_show_mapa"]:
                    st.write("---")
                    
                    nome = cliente_selecionado
                    info_cliente = clientes_salvos[nome]
                    data_str = info_cliente['data_nascimento']
                    
                    profissao = info_cliente.get('profissao', '')
                    if 'profissao' not in info_cliente:
                        profissao = info_cliente.get('cargo', '')
                        cargo = ''
                    else:
                        cargo = info_cliente.get('cargo', '')
                        
                    grupo = info_cliente.get('grupo', info_cliente.get('empresa', ''))
                    linkedin = info_cliente.get('linkedin_url', '')
                    experiencias = info_cliente.get('experiencias', '')
                    
                    try:
                        dia, mes, ano = map(int, data_str.split('/'))
                        data_input = datetime.date(ano, mes, dia)
                    except Exception:
                        data_input = datetime.date.today()

                    hoje = datetime.date.today()
                    data_atual_tup = (hoje.day, hoje.month, hoje.year)
                    nascimento_tup = (data_input.day, data_input.month, data_input.year)

                    empresa = info_cliente.get('empresa', '')
                    res_calc = realizar_calculos_completos(nome, nascimento_tup, data_atual_tup, profissao, empresa)
                    dados, dados_perfil, kan, estrutural, direcionamento, rep1, rep2, rep3, rep4, score_df_calc, score_cat_df, score_qual_df, auditoria_qual_df = res_calc
                    
                    # Exibição do Header do Talento (Foto, Nome e Info)
                    foto_b64 = info_cliente.get('foto_base64')
                    if foto_b64 and "base64," in foto_b64:
                        foto_b64 = foto_b64.split("base64,")[1]
                        
                    subinfo_parts = [data_str]
                    for p in [profissao, cargo, grupo]:
                        if p and str(p).lower() != "nan" and str(p).strip() != "":
                            subinfo_parts.append(str(p))
                    subinfo_text = " | ".join(subinfo_parts)
                    
                    # Injeção de CSS para formatação de links de talentos
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
                    </style>
                    """, unsafe_allow_html=True)
                    
                    if foto_b64:
                        col_img_diag, col_txt_diag = st.columns([1, 4])
                        with col_img_diag:
                            st.markdown(f'''
                            <div style="width: 120px; height: 120px; min-width: 120px; min-height: 120px; border-radius: 50%; overflow: hidden; border: 3px solid var(--accent); box-shadow: 0px 4px 10px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; background-color: var(--panel-bg); margin-bottom: 25px;">
                                <img src="data:image/png;base64,{foto_b64}" style="width: 100%; height: 100%; object-fit: cover; display: block;">
                            </div>
                            ''', unsafe_allow_html=True)
                        with col_txt_diag:
                            st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)
                            st.markdown('<div class="talent-link-container" style="font-size: 1.6em; font-weight: bold; display: inline-block;">', unsafe_allow_html=True)
                            st.button(nome, key="lnk_admin_mapa_header_nome_foto", on_click=self.app.ver_cadastro_talento, args=(nome,))
                            st.markdown('</div>', unsafe_allow_html=True)
                            st.markdown(f"<p style='font-size: 1.1em; color: var(--text-soft); font-weight: 500; margin-top: 5px;'>{subinfo_text}</p>", unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="talent-link-container" style="font-size: 1.6em; font-weight: bold; display: inline-block;">', unsafe_allow_html=True)
                        st.button(nome, key="lnk_admin_mapa_header_nome_nofoto", on_click=self.app.ver_cadastro_talento, args=(nome,))
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown(f"<p style='font-size: 1.1em; color: var(--text-soft); font-weight: 500; margin-top: 5px;'>{subinfo_text}</p>", unsafe_allow_html=True)
                        
                    st.write("---")
                    st.subheader("Mapa Numerológico Cabalístico")
                    
                    # CSS do Mapa
                    st.markdown("""
                    <style>
                    .mapa-table { 
                        width: 100%; 
                        border-collapse: collapse; 
                        margin-top: 15px; 
                        background: var(--panel-bg); 
                        border: 1px solid var(--panel-border);
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: var(--card-shadow);
                    }
                    .mapa-table th { 
                        background-color: var(--accent); 
                        color: var(--button-primary-text); 
                        padding: 14px 20px; 
                        text-align: left; 
                        font-size: 1.05em; 
                        font-weight: 800;
                    }
                    .mapa-table td { 
                        border-bottom: 1px solid var(--divider); 
                        vertical-align: top; 
                        padding: 16px 20px; 
                    }
                    .mapa-campo-titulo { 
                        color: var(--accent); 
                        font-weight: 800; 
                        font-size: 1.1em; 
                        margin-bottom: 8px;
                    }
                    .mapa-numero-destaque { 
                        display: inline-block; 
                        background: linear-gradient(135deg, var(--accent) 0%, #D97706 100%); 
                        color: var(--button-primary-text); 
                        font-weight: 900; 
                        font-size: 1.3em; 
                        padding: 3px 12px; 
                        border-radius: 6px; 
                        box-shadow: 0 3px 8px rgba(240, 138, 0, 0.3);
                        margin-bottom: 8px;
                    }
                    .mapa-explicacao { 
                        font-size: 0.82em; 
                        color: var(--text-muted); 
                        font-style: italic; 
                        line-height: 1.4;
                    }
                    .mapa-desc-cel { 
                        color: var(--text-main); 
                        font-size: 0.95em; 
                        line-height: 1.6; 
                        text-align: justify; 
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    html_mapa = '<table class="mapa-table"><thead><tr><th style="width:28%">Campo / Número / Definição</th><th>Descrição Detalhada</th></tr></thead><tbody>'
                    for item in dados:
                        campo_raw = item['Campo']
                        resultado_raw = item['Resultado']

                        if ' - ' in campo_raw:
                            partes_campo = campo_raw.rsplit(' - ', 1)
                            label_campo = partes_campo[0]
                            numero_badge = f"<div class='mapa-numero-destaque'>{partes_campo[1]}</div>"
                        else:
                            label_campo = campo_raw
                            numero_badge = ""

                        explicacao_html = ""
                        if item.get("Explicacao"):
                            explicacao_html = f"<div class='mapa-explicacao'>{item['Explicacao']}</div>"

                        cel_resultado = f"<div class='mapa-desc-cel'>{resultado_raw}</div>" if resultado_raw else ""

                        html_mapa += (
                            f"<tr>"
                            f"<td>"
                            f"<div class='mapa-campo-titulo'>{label_campo}</div>"
                            f"{numero_badge}"
                            f"{explicacao_html}"
                            f"</td>"
                            f"<td>{cel_resultado}</td>"
                            f"</tr>"
                        )
                    html_mapa += "</tbody></table>"
                    st.markdown(html_mapa, unsafe_allow_html=True)
                    
                    # Seção de download
                    st.markdown("---")
                    st.subheader("Baixar Resultados do Mapa")
                    col1, col2 = st.columns(2)
                    nome_limpo = remover_acentos(nome).replace(' ', '_')
                    df = pd.DataFrame(dados)
                    
                    from services.pdf_generator import gerar_pdf
                    with col1:
                        csv = df.to_csv(sep=';', index=False).encode('utf-8')
                        st.download_button("Baixar Mapa como CSV", data=csv, file_name=f"mapa_{nome_limpo}.csv", mime="text/csv", key=f"dl_admin_mapa_csv_{nome}", use_container_width=True)
                    with col2:
                        data_str_pdf = data_input.strftime('%d/%m/%Y')
                        pdf_bytes = gerar_pdf(nome, data_str_pdf, dados, titulo="Mapa Numerologico Cabalístico")
                        st.download_button("Baixar Mapa como PDF", data=pdf_bytes, file_name=f"mapa_{nome_limpo}.pdf", mime="application/pdf", key=f"dl_admin_mapa_pdf_{nome}", use_container_width=True)

        with t_tab5:
            st.subheader("Gerenciamento de Banners e Imagens")
            
            with st.expander("Biblioteca de Imagens (Assets)", expanded=False):
                st.write("Suba novas imagens para usar nos banners.")
                new_asset_file = st.file_uploader("Upload de nova imagem para biblioteca", type=["png", "jpg", "jpeg", "webp"], key="upload_asset")
                new_asset_name = st.text_input("Nome da imagem no sistema", key="asset_name")
                if st.button("Adicionar à Biblioteca"):
                    if new_asset_file and new_asset_name:
                        with st.spinner("Otimizando e enviando imagem..."):
                            b64_data = compress_image_to_b64(new_asset_file)
                            if b64_data:
                                try:
                                    supabase_client.table("kan_assets").insert({"nome": new_asset_name, "data_base64": b64_data}).execute()
                                    st.success(f"Imagem '{new_asset_name}' salva na biblioteca!")
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao salvar asset: {e}")
                    else:
                        st.warning("Preencha o nome e selecione um arquivo.")

                assets_list = fetch_assets_list()
                if assets_list:
                    st.write("**Imagens Disponíveis:**")
                    for asset in assets_list:
                        st.write(f"- {asset['nome']} (ID: {asset['id']})")

            st.markdown("---")
            
            db_banners = fetch_banners()
            assets_list = fetch_assets_list()
            asset_options = {a['nome']: a['id'] for a in assets_list} if assets_list else {}
            
            current_data = db_banners if db_banners else st.session_state.get('banners_data', [])
            
            for i, b in enumerate(current_data):
                b_id = b.get('id', i+1)
                b_title = b.get('title', '')
                b_sub = b.get('subtitle', '')
                b_cta = b.get('cta_text', b.get('cta', ''))
                b_link = b.get('cta_link', b.get('link', '#'))
                
                # Validação robusta de cor hexadecimal para evitar StreamlitAPIException no st.color_picker
                raw_accent = b.get('accent_color') or b.get('accent') or '#F18617'
                if not isinstance(raw_accent, str):
                    raw_accent = '#F18617'
                raw_accent = raw_accent.strip()
                if raw_accent and not raw_accent.startswith('#'):
                    raw_accent = '#' + raw_accent
                import re
                if re.match(r"^#[0-9a-fA-F]{3}$|^#[0-9a-fA-F]{6}$", raw_accent):
                    b_accent = raw_accent
                else:
                    b_accent = '#F18617'
                
                b_asset_id = b.get('asset_id')
                
                with st.expander(f"Banner {b_id}: {b_title}"):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        n_title = st.text_input("Título", value=b_title, key=f"db_b_title_{i}")
                        n_sub = st.text_area("Subtítulo", value=b_sub, key=f"db_b_sub_{i}")
                    with col_e2:
                        n_cta = st.text_input("Texto do Botão", value=b_cta, key=f"db_b_cta_{i}")
                        n_accent = st.color_picker("Cor de Destaque", value=b_accent, key=f"db_b_acc_{i}")
                        
                        is_internal = b_link.startswith("?nav=") if b_link else False
                        dest_type = st.radio("Destino do Clique", ["Página do Sistema", "Link Externo"], 
                                             index=0 if is_internal else 1, key=f"db_b_dest_type_{i}")
                        
                        if dest_type == "Página do Sistema":
                            current_nav_page = b_link.replace("?nav=", "") if is_internal else "Home"
                            available_pages = MENU_PRINCIPAL + (["Painel de Controle"] if st.session_state.get("logged_user") == "adminkan" else [])
                            
                            try:
                                default_nav_idx = available_pages.index(current_nav_page)
                            except:
                                default_nav_idx = 0
                                
                            n_page = st.selectbox("Selecione a Página", options=available_pages, index=default_nav_idx, key=f"db_b_page_{i}")
                            n_link = f"?nav={n_page}"
                        else:
                            n_link = st.text_input("URL Externa", value=b_link if not is_internal else "https://", key=f"db_b_link_{i}")
                    
                    if asset_options:
                        default_idx = 0
                        if b_asset_id:
                            for idx, (name, aid) in enumerate(asset_options.items()):
                                if aid == b_asset_id:
                                    default_idx = idx
                                    break
                        
                        selected_asset_name = st.selectbox("Selecionar Imagem da Biblioteca", options=list(asset_options.keys()), index=default_idx, key=f"db_b_asset_{i}")
                        selected_asset_id = asset_options[selected_asset_name]
                    else:
                        st.warning("Nenhuma imagem na biblioteca. Faça um upload acima.")
                        selected_asset_id = None

                    if st.button(f"Salvar Banner {b_id}", key=f"btn_save_db_b_{i}"):
                        if supabase_client:
                            try:
                                update_data = {
                                    "title": n_title,
                                    "subtitle": n_sub,
                                    "cta_text": n_cta,
                                    "cta_link": n_link,
                                    "accent_color": n_accent,
                                    "asset_id": selected_asset_id,
                                    "updated_at": datetime.datetime.now().isoformat()
                                }
                                supabase_client.table("kan_banners").update(update_data).eq("id", b_id).execute()
                                st.success(f"Banner {b_id} atualizado no banco de dados!")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao salvar no BD: {e}")
        with t_tab_soft:
            st.subheader("Mapeamento Comportamental de Soft Skills")
            st.markdown("Visão consolidada do banco de Soft Skills cruzado com a metodologia KAN (Perfis, Categorias e Qualidades).")
            
            if supabase_client:
                try:
                    resp_soft = supabase_client.table("soft_skills").select("*").execute()
                    if resp_soft and resp_soft.data:
                        df_soft = pd.DataFrame(resp_soft.data)
                        
                        # Reordenando colunas para melhor visualização
                        colunas_ordem = ['nome', 'explicacao', 'modelo_analise', 'kan_relacionado', 'perfis_relacionados', 'categorias_relacionadas', 'qualidades_relacionadas']
                        # Só seleciona se a coluna kan_relacionado existir (para não quebrar enquanto ele não rodar o SQL)
                        colunas_presentes = [c for c in colunas_ordem if c in df_soft.columns]
                        df_soft = df_soft[colunas_presentes]
                        
                        df_soft.rename(columns={
                            'nome': 'Soft Skill',
                            'explicacao': 'Explicação Prática',
                            'modelo_analise': 'Modelo de Análise',
                            'kan_relacionado': 'KAN Relacionado',
                            'perfis_relacionados': 'Perfis Relacionados',
                            'categorias_relacionadas': 'Categorias Relacionadas',
                            'qualidades_relacionadas': 'Qualidades Relacionadas'
                        }, inplace=True)
                        
                        st.dataframe(df_soft, use_container_width=True, hide_index=True)
                    else:
                        st.info("A tabela de Soft Skills está vazia ou não foi carregada no banco.")
                except Exception as e:
                    st.error(f"Erro ao buscar soft skills: {e}")
            else:
                st.warning("Conexão com o banco indisponível.")

        with t_tab_estudos:
            st.subheader("Central de Estudos Metodológicos KAN")
            st.markdown("Guia conceitual, referências e ferramentas interativas para o aprimoramento na análise comportamental KAN.")
            
            from components.card import premium_card_container
            
            sub_estudos_tab1, sub_estudos_tab2, sub_estudos_tab3, sub_estudos_tab4 = st.tabs(["📚 Metodologia KAN", "🧬 Guia Comportamental", "🧮 Calculadora de Estudo", "🧪 Simulação"])
            
            with sub_estudos_tab1:
                st.markdown("### As Três Forças Primordiais do KAN")
                st.markdown("A metodologia KAN baseia-se no equilíbrio e na dinâmica entre três forças fundamentais, representadas pelos números correspondentes:")
                
                col_k1, col_k2, col_k3 = st.columns(3)
                with col_k1:
                    with premium_card_container(variant="default"):
                        st.markdown("<h4 style='color: #F08A00; margin-top:0;'>🎨 Criação (KAN 3)</h4>", unsafe_allow_html=True)
                        st.write("**Foco:** Comunicação, expressividade, inovação, sociabilidade e originalidade artística.")
                        st.write("**Perfil Típico:** Ideadores, comunicadores natos, profissionais de marketing e relações públicas.")
                        st.caption("Representa o início de novas ideias e a habilidade de conectá-las socialmente.")
                with col_k2:
                    with premium_card_container(variant="default"):
                        st.markdown("<h4 style='color: #8B5CF6; margin-top:0;'>⚡ Movimento (KAN 6)</h4>", unsafe_allow_html=True)
                        st.write("**Foco:** Conciliação, harmonia, responsabilidade, acolhimento e suporte social.")
                        st.write("**Perfil Típico:** Mediadores, psicólogos, gestores de RH e líderes comunitários.")
                        st.caption("Representa a sustentação das relações, empatia e o zelo pelo equilíbrio do time.")
                with col_k3:
                    with premium_card_container(variant="default"):
                        st.markdown("<h4 style='color: #EF4444; margin-top:0;'>🎯 Finalidade (KAN 9)</h4>", unsafe_allow_html=True)
                        st.write("**Foco:** Altruísmo, entrega, conclusão, propósito elevado e visão humanitária.")
                        st.write("**Perfil Típico:** Diretores estratégicos, mentores, filósofos e líderes visionários.")
                        st.caption("Representa a concretização dos propósitos, desapego e foco em resultados coletivos.")
                
                st.markdown("---")
                st.markdown("### 📐 Triângulos Harmônicos no Plano de Tesla")
                st.markdown("""
                Os triângulos harmônicos mapeiam os três principais vértices de competência de cada indivíduo no Plano de Tesla. A interação espacial desses triângulos define o grau de harmonia de uma equipe:
                
                *   **Sobreposição Idêntica:** Alinhamento absoluto de propósitos e estilos, mas com potencial de redundância ou pontos cegos comuns.
                *   **Lateral em Comum / Vértice em Comum:** Forte sinergia e cooperação imediata sobre pontos de apoio semelhantes.
                *   **Atravessamento:** Alta interdependência dinâmica que exige boa comunicação para não gerar atrito operacional.
                *   **Afastamento:** Estilos muito distintos. Excelente para complementaridade estratégica, mas requer mediação do líder para evitar ruídos.
                """)
            
            with sub_estudos_tab2:
                st.markdown("### Guia de Interpretação Numerológica")
                st.markdown("Cada indicador do mapa desempenha um papel único na constituição da personalidade e atitude profissional:")
                
                with st.container(border=True):
                    st.markdown("**1. Número Psíquico** (Dia de Nascimento reduzido):")
                    st.write("Representa como o indivíduo se enxerga interiormente, suas motivações mais profundas, hábitos cotidianos e preferências de conduta.")
                    
                    st.markdown("**2. Destino** (Soma total da Data de Nascimento):")
                    st.write("Indica o caminho de vida, os tipos de oportunidades e aprendizados que o indivíduo encontrará ao longo de sua trajetória profissional.")
                    
                    st.markdown("**3. Expressão** (Soma do valor de todas as letras do Nome Completo):")
                    st.write("Como a pessoa se expressa e interage com o mundo externo, seus talentos naturais de comunicação e competências visíveis.")
                    
                    st.markdown("**4. Motivação** (Soma apenas das Vogais do Nome Completo):")
                    st.write("Os desejos íntimos da alma, aquilo que realmente move e apaixona o indivíduo por trás das cortinas operacionais.")
                    
                    st.markdown("**5. Impressão** (Soma apenas das Consoantes do Nome Completo):")
                    st.write("A primeira impressão que o indivíduo transmite aos outros no ambiente corporativo e social, a imagem externa.")
                    
                    st.markdown("**6. Missão** (Soma da Expressão e do Destino):")
                    st.write("O propósito final de realização nesta existência, o legado que o profissional aspira a consolidar.")
            
            with sub_estudos_tab3:
                st.markdown("### 🧮 Calculadora de Estudo e Simulação")
                st.markdown("Utilize esta ferramenta para simular cálculos numerológicos e entender a decomposição da metodologia KAN para qualquer indivíduo.")
                
                col_calc1, col_calc2 = st.columns(2)
                with col_calc1:
                    nome_simul = st.text_input("Nome Completo para Simulação:", value="Nome de Teste Exemplo", key="estudos_nome_simul")
                with col_calc2:
                    data_simul = st.date_input("Data de Nascimento para Simulação:", datetime.date(1990, 1, 1), key="estudos_data_simul")
                
                if st.button("Executar Simulação de Estudo", type="primary", key="estudos_btn_calc"):
                    nasc_tuple = (data_simul.day, data_simul.month, data_simul.year)
                    now_dt = datetime.datetime.now()
                    data_at = (now_dt.day, now_dt.month, now_dt.year)
                    
                    try:
                        res = calcular_numerologia(nome_simul, nasc_tuple, data_at)
                        (expressao, motivacao, impressao, destino, _, _, _, missao, _, _, 
                         _, _, _, _, _, _, ciclos_vida, momentos_decisivos, triangulo_base, _, _, _) = res
                        
                        estrutural, direcionamento, kan_num, rep1, rep2 = calcular_perfil_comportamental(
                            expressao, motivacao, impressao, nasc_tuple[0],
                            destino, missao, ciclos_vida['ciclo2']['numero'], momentos_decisivos['momento3']['numero'],
                            triangulo_base
                        )
                        
                        st.write("---")
                        st.markdown("#### 📊 Resultados Obtidos na Simulação")
                        
                        col_r1, col_r2, col_r3 = st.columns(3)
                        with col_r1:
                            with premium_card_container(variant="compact"):
                                st.write("**Motivação (Alma):**")
                                st.markdown(f"<span style='font-size: 1.5em; font-weight: bold; color: var(--accent);'>{motivacao}</span>", unsafe_allow_html=True)
                        with col_r2:
                            with premium_card_container(variant="compact"):
                                st.write("**Impressão (Aparência):**")
                                st.markdown(f"<span style='font-size: 1.5em; font-weight: bold; color: var(--accent);'>{impressao}</span>", unsafe_allow_html=True)
                        with col_r3:
                            with premium_card_container(variant="compact"):
                                st.write("**Expressão (Atitude):**")
                                st.markdown(f"<span style='font-size: 1.5em; font-weight: bold; color: var(--accent);'>{expressao}</span>", unsafe_allow_html=True)
                                
                        col_r4, col_r5, col_r6 = st.columns(3)
                        with col_r4:
                            with premium_card_container(variant="compact"):
                                st.write("**Destino (Caminho):**")
                                st.markdown(f"<span style='font-size: 1.5em; font-weight: bold; color: var(--accent);'>{destino}</span>", unsafe_allow_html=True)
                        with col_r5:
                            with premium_card_container(variant="compact"):
                                st.write("**Número Psíquico:**")
                                st.markdown(f"<span style='font-size: 1.5em; font-weight: bold; color: var(--accent);'>{reduce_number(nasc_tuple[0])}</span>", unsafe_allow_html=True)
                        with col_r6:
                            with premium_card_container(variant="compact"):
                                st.write("**Missão (Propósito):**")
                                st.markdown(f"<span style='font-size: 1.5em; font-weight: bold; color: var(--accent);'>{missao}</span>", unsafe_allow_html=True)
                        
                        st.markdown("#### 📐 Vetices Comportamentais do Trio")
                        
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
                        
                        from collections import Counter
                        c_tot = Counter(todos_num)
                        r_tot = sorted([(n, c) for n, c in c_tot.items()], key=lambda x: (-x[1], x[0]))
                        
                        r2_v = r_tot[0][0] if r_tot else 0
                        r3_v = r_tot[1][0] if len(r_tot) > 1 else 0
                        r4_v = r_tot[2][0] if len(r_tot) > 2 else 0
                        
                        def clean_val(v):
                            if v is None: return None
                            s = str(v).split(" - ")[0]
                            return int(s) if s.isdigit() and int(s) > 0 else None
                            
                        k_v = clean_val(kan_num)
                        e_v = clean_val(estrutural)
                        d_v = clean_val(direcionamento)
                        r1_v = clean_val(rep1)
                        
                        todos_comp = [
                            {"campo": "KAN", "valor": k_v},
                            {"campo": "ESTRUTURAL", "valor": e_v},
                            {"campo": "DIRECIONAMENTO", "valor": d_v},
                            {"campo": "REPETIÇÃO 1", "valor": r1_v},
                            {"campo": "REPETICAO MAPA", "valor": r2_v},
                            {"campo": "REPETICAO 2 MAPA", "valor": r3_v},
                            {"campo": "REPETICAO 3 MAPA", "valor": r4_v}
                        ]
                        
                        vertices_comp = []
                        vals_comp = set()
                        for it in todos_comp:
                            v_it = it["valor"]
                            if v_it is not None and v_it not in [11, 22] and v_it not in vals_comp:
                                vertices_comp.append(v_it)
                                vals_comp.add(v_it)
                            if len(vertices_comp) == 3:
                                break
                                
                        if len(vertices_comp) == 3:
                            st.write(f"Os três vértices calculados para o triângulo harmônico no Plano de Tesla são: `{vertices_comp}`.")
                            
                            try:
                                comparativo = {nome_simul: vertices_comp}
                                svg_html = gerar_svg_triangulos_harmonicos(comparativo, lider_nome=nome_simul)
                                st.markdown(svg_html, unsafe_allow_html=True)
                            except Exception as ex:
                                st.error(f"Erro ao desenhar o triângulo no SVG: {ex}")
                        else:
                            st.warning("Não foi possível formar um triângulo completo de 3 vértices distintos com os números calculados.")
                    except Exception as e:
                        st.error(f"Erro ao executar cálculos de simulação: {e}")
            
            with sub_estudos_tab4:
                st.markdown("### 🧪 Simulação Dinâmica de Fórmulas Numerológicas")
                st.markdown("Monte uma fórmula personalizada somando e reduzindo campos numéricos do Mapa Salvo de qualquer talento.")
                
                OPCOES_CAMPOS = {
                    "motivacao": "Motivação (Alma)",
                    "impressao": "Impressão (Aparência)",
                    "expressao": "Expressão (Atitude)",
                    "dia_natalicio": "Dia Natalício",
                    "numero_psiquico": "Número Psíquico",
                    "destino": "Destino (Caminho)",
                    "missao": "Missão (Propósito)",
                    "direcionamento": "Direcionamento",
                    "estrutural": "Estrutural",
                    "repeticao_1": "Repetição 1",
                    "repeticao_2": "Repetição 2",
                    "repeticao_mapa": "Repetição Mapa",
                    "repeticao_mapa_2": "Repetição 2 Mapa",
                    "vertice_triangulo_3": "Vértice Triângulo 3",
                    "dividas_carmicas": "Dívidas Cármicas",
                    "licoes_carmicas": "Lições Cármicas",
                    "tendencias_ocultas": "Tendências Ocultas",
                    "resposta_subconsciente": "Resposta Subconsciente"
                }
                
                if "simulacao_campos" not in st.session_state:
                    st.session_state["simulacao_campos"] = ["motivacao", "destino"]
                
                def extrair_valor_numerico_campo(val):
                    if not val:
                        return 0
                    val_str = str(val).strip()
                    if not val_str or val_str.lower() in ("não há", "n/a", "none", "null", ""):
                        return 0
                    if " - " in val_str:
                        val_str = val_str.split(" - ")[0].strip()
                    if "," in val_str:
                        soma = 0
                        parts = val_str.split(",")
                        for part in parts:
                            part_clean = "".join(ch for ch in part if ch.isdigit())
                            if part_clean:
                                soma += int(part_clean)
                        return soma
                    else:
                        dígitos = "".join(ch for ch in val_str if ch.isdigit())
                        if dígitos:
                            return int(dígitos)
                    return 0
                
                def reduzir_cabala(n):
                    while n > 9 and n not in (11, 22):
                        n = sum(int(i) for i in str(n))
                    return n
                
                mapas_valores = []
                try:
                    res_m = supabase_client.table("mapas_salvos_valores").select("*").order("nome").execute()
                    if res_m.data:
                        mapas_valores = res_m.data
                except Exception:
                    pass
                    
                if not mapas_valores:
                    clientes_dict = carregar_todos_clientes()
                    for n_aud, c_info in clientes_dict.items():
                        nasc_dt = c_info.get('data_nascimento')
                        if nasc_dt:
                            try:
                                if isinstance(nasc_dt, (datetime.datetime, datetime.date)):
                                    nascimento_tup = (nasc_dt.day, nasc_dt.month, nasc_dt.year)
                                elif isinstance(nasc_dt, str):
                                    try: dt_obj = datetime.datetime.strptime(nasc_dt, "%d/%m/%Y")
                                    except ValueError: dt_obj = datetime.datetime.strptime(nasc_dt, "%Y-%m-%d")
                                    nascimento_tup = (dt_obj.day, dt_obj.month, dt_obj.year)
                                else:
                                    continue
                                now_dt = datetime.datetime.now()
                                data_atual_tup = (now_dt.day, now_dt.month, now_dt.year)
                                res_calc = realizar_calculos_completos(
                                    n_aud, nascimento_tup, data_atual_tup, 
                                    c_info.get('profissao', c_info.get('cargo', '')), 
                                    c_info.get('grupo')
                                )
                                dados, dados_perfil, kan, estrutural, direcionamento, rep1, rep2, _, _, _, _, _, _ = res_calc
                                
                                def ext_val(label):
                                    for d in dados:
                                        if str(d.get("Campo")).startswith(label):
                                            return str(d.get("Valor"))
                                    return ""
                                    
                                def ext_perfil(label, just_value=False):
                                    for d in dados_perfil:
                                        if str(d.get("Campo")).lower() == label.lower():
                                            if just_value: return str(d.get("Valor", ""))
                                            return str(d.get("Resultado", d.get("Valor", "")))
                                    return ""
                                    
                                num_psiquico = reduzir_cabala(nascimento_tup[0])
                                
                                row_val = {
                                    "nome": n_aud,
                                    "data_nascimento": nasc_dt if isinstance(nasc_dt, str) else nasc_dt.strftime('%Y-%m-%d'),
                                    "perfil": ext_perfil("perfil", just_value=True),
                                    "categoria": ext_perfil("categoria", just_value=True),
                                    "qualidades": ext_perfil("qualidades", just_value=True),
                                    "diferenciais": ext_perfil("diferenciais", just_value=True),
                                    "motivacao": ext_val("Motivação"),
                                    "impressao": ext_val("Impressão"),
                                    "expressao": ext_val("Expressão"),
                                    "dia_natalicio": ext_val("Dia Natalício"),
                                    "numero_psiquico": str(num_psiquico),
                                    "destino": ext_val("Destino"),
                                    "missao": ext_val("Missão"),
                                    "direcionamento": str(direcionamento),
                                    "estrutural": str(estrutural),
                                    "repeticao_1": str(rep1),
                                    "repeticao_2": str(rep2),
                                    "repeticao_mapa": ext_val("Repetição Mapa"),
                                    "repeticao_mapa_2": ext_val("Repetição 2 Mapa"),
                                    "vertice_triangulo_3": ext_val("Triângulo Harmônico"),
                                    "dividas_carmicas": ext_val("Dívidas Cármicas"),
                                    "licoes_carmicas": ext_val("Lições Cármicas"),
                                    "tendencias_ocultas": ext_val("Tendências Ocultas"),
                                    "resposta_subconsciente": ext_val("Resposta Subconsciente"),
                                    "empresa": c_info.get("empresa", ""),
                                    "grupo": c_info.get("grupo", ""),
                                    "profissao": c_info.get("profissao", c_info.get("cargo", ""))
                                }
                                mapas_valores.append(row_val)
                            except Exception:
                                pass

                if mapas_valores:
                    try:
                        clientes_dict = carregar_todos_clientes()
                        for mv in mapas_valores:
                            cli_info = clientes_dict.get(mv["nome"], {})
                            mv["empresa"] = cli_info.get("empresa", "")
                            mv["grupo"] = cli_info.get("grupo", "")
                            mv["profissao"] = cli_info.get("profissao", cli_info.get("cargo", ""))
                    except Exception:
                        pass
                
                st.write("#### 🧱 Construtor de Fórmula")
                
                campos_atuais = st.session_state["simulacao_campos"]
                novos_campos = []
                
                for idx, c_key in enumerate(campos_atuais):
                    col_campo_sel, col_campo_del = st.columns([6, 1])
                    with col_campo_sel:
                        opcoes_lista = list(OPCOES_CAMPOS.keys())
                        try:
                            idx_default = opcoes_lista.index(c_key) if c_key in opcoes_lista else 0
                        except ValueError:
                            idx_default = 0
                        
                        sel_c = st.selectbox(
                            f"Termo {idx+1}:",
                            options=opcoes_lista,
                            format_func=lambda x: OPCOES_CAMPOS[x],
                            index=idx_default,
                            key=f"simul_c_sel_{idx}"
                        )
                        novos_campos.append(sel_c)
                    with col_campo_del:
                        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                        if st.button("🗑️", key=f"simul_c_del_{idx}"):
                            st.session_state["simulacao_campos"].pop(idx)
                            st.rerun()
                            
                st.session_state["simulacao_campos"] = novos_campos
                
                col_btn_add, _ = st.columns([2, 5])
                with col_btn_add:
                    if st.button("➕ Adicionar Campo", use_container_width=True, key="simul_btn_add_term"):
                        st.session_state["simulacao_campos"].append("expressao")
                        st.rerun()
                        
                st.write("---")
                
                if not st.session_state["simulacao_campos"]:
                    st.warning("Adicione pelo menos um campo para formar a fórmula.")
                else:
                    nomes_disponiveis = [m["nome"] for m in mapas_valores]
                    
                    st.write("#### 🔍 Visualização da Fórmula")
                    nome_teste = st.selectbox(
                        "Selecione um talento para visualizar a fórmula aplicada:",
                        options=nomes_disponiveis if nomes_disponiveis else ["Nenhum cadastrado"],
                        key="simul_nome_teste"
                    )
                    
                    if mapas_valores and nome_teste in nomes_disponiveis:
                        reg = [m for m in mapas_valores if m["nome"] == nome_teste][0]
                        termos_valores = []
                        termos_nomes = []
                        soma_total = 0
                        
                        for c_key in st.session_state["simulacao_campos"]:
                            raw_v = reg.get(c_key, "")
                            num_v = extrair_valor_numerico_campo(raw_v)
                            soma_total += num_v
                            termos_valores.append(num_v)
                            termos_nomes.append(f"{OPCOES_CAMPOS[c_key]} ({num_v})")
                            
                        resultado_red = reduzir_cabala(soma_total)
                        formula_str = " + ".join(termos_nomes)
                        st.info(f"**Fórmula:** {formula_str} = `{soma_total}` $\\rightarrow$ **`{resultado_red}`**")
                    else:
                        st.info("Cadastre ou calcule mapas salvos para poder testar com um talento.")
                        
                st.write("---")
                st.write("#### 📐 Seleção de Talentos e Relatório")
                
                if mapas_valores:
                    empresas_unicas = sorted(list(set(str(m.get("empresa", "")).strip() for m in mapas_valores if m.get("empresa"))))
                    grupos_unicos = sorted(list(set(str(m.get("grupo", "")).strip() for m in mapas_valores if m.get("grupo"))))
                    profissoes_unicas = sorted(list(set(str(m.get("profissao", "")).strip() for m in mapas_valores if m.get("profissao"))))
                    nomes_unicos = sorted(list(set(str(m.get("nome", "")).strip() for m in mapas_valores if m.get("nome"))))
                    
                    col_f1, col_f2 = st.columns(2)
                    with col_f1:
                        filtro_nomes = st.multiselect("Filtrar por Nome:", options=nomes_unicos, key="simul_filt_nomes")
                        filtro_empresas = st.multiselect("Filtrar por Empresa:", options=empresas_unicas, key="simul_filt_empresas")
                    with col_f2:
                        filtro_grupos = st.multiselect("Filtrar por Grupo:", options=grupos_unicos, key="simul_filt_grupos")
                        filtro_profissoes = st.multiselect("Filtrar por Profissão:", options=profissoes_unicas, key="simul_filt_profissoes")
                        
                    if st.button("Selecionar talentos e gerar planilha", type="primary", use_container_width=True, key="simul_btn_gerar"):
                        regs_filtrados = mapas_valores
                        
                        if filtro_nomes:
                            regs_filtrados = [r for r in regs_filtrados if r["nome"] in filtro_nomes]
                        if filtro_empresas:
                            regs_filtrados = [r for r in regs_filtrados if r.get("empresa") in filtro_empresas]
                        if filtro_grupos:
                            regs_filtrados = [r for r in regs_filtrados if r.get("grupo") in filtro_grupos]
                        if filtro_profissoes:
                            regs_filtrados = [r for r in regs_filtrados if r.get("profissao") in filtro_profissoes]
                            
                        if not regs_filtrados:
                            st.warning("Nenhum talento corresponde aos filtros selecionados.")
                        elif not st.session_state["simulacao_campos"]:
                            st.warning("A fórmula está vazia. Adicione termos à fórmula acima.")
                        else:
                            rows_df = []
                            for r in regs_filtrados:
                                soma_t = 0
                                valores_termos = []
                                for c_key in st.session_state["simulacao_campos"]:
                                    num_v = extrair_valor_numerico_campo(r.get(c_key, ""))
                                    soma_t += num_v
                                    valores_termos.append(str(num_v))
                                    
                                red_t = reduzir_cabala(soma_t)
                                
                                rows_df.append({
                                    "Nome": r["nome"],
                                    "Empresa": r.get("empresa", ""),
                                    "Grupo": r.get("grupo", ""),
                                    "Profissão/Cargo": r.get("profissao", ""),
                                    "Valores dos Termos": ", ".join(valores_termos),
                                    "Soma": soma_t,
                                    "Resultado Reduzido": red_t
                                })
                                
                            df_res = pd.DataFrame(rows_df)
                            st.success(f"{len(df_res)} talentos processados com sucesso!")
                            st.dataframe(df_res, use_container_width=True)
                            
                            csv_data = df_res.to_csv(index=False, encoding="utf-8-sig")
                            st.download_button(
                                label="📥 Exportar Planilha para CSV",
                                data=csv_data,
                                file_name=f"simulacao_numerologica_{datetime.date.today().strftime('%Y%m%d')}.csv",
                                mime="text/csv",
                                key="simul_btn_download"
                            )
                else:
                    st.info("Nenhum talento ou mapa cadastrado. Vá à aba de 'Auditoria' e calcule os mapas salvos para popular os perfis.")
