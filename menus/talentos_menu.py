import streamlit as st
import datetime
import json
from PIL import Image
import google.generativeai as genai

import pandas as pd
from menus.base_menu import BaseMenu
from models.database import carregar_empresas, get_supabase_admin, carregar_todos_clientes
from utils.helpers import compress_image_to_b64

class TalentosMenu(BaseMenu):
    def render(self):
        st.title("Cadastro de Talentos")
        st.write("---")

        supabase_client = get_supabase_admin()
        lista_empresas_salvas = carregar_empresas()
        nomes_empresas = [e["nome_empresa"] for e in lista_empresas_salvas if e.get("nome_empresa")]
        if not nomes_empresas:
            nomes_empresas = ["Mundo KAN", "Empresa Cliente A"]

        clientes = carregar_todos_clientes()

        with st.container(border=True):
            st.subheader("Novo Cadastro")
            cad_nome = st.text_input("Nome Completo (Conforme certidão)*:", value=st.session_state.get('ocr_nome', ''), key="cad_nome")
            
            col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
            with col_f1:
                cad_data = st.text_input("Data de Nascimento*:", placeholder="dd/mm/yyyy", value=st.session_state.get('ocr_data_nascimento', ''), key="cad_data")
            with col_f2:
                cad_foto = st.file_uploader("Foto (Opcional)", type=["png", "jpg", "jpeg"], key="cad_foto")
            with col_f3:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("Ativar Câmera", use_container_width=True, key="cad_cam_btn"):
                    st.session_state['cad_camera_aberta'] = True
                st.caption("Leitura de Documento via IA")
            
            if st.session_state.get('cad_camera_aberta', False):
                foto_doc = st.camera_input("Tire uma foto legível do seu documento", key="cad_cam_in")
                if foto_doc:
                    with st.spinner("Extraindo dados do documento..."):
                        try:
                            api_key = st.secrets["gemini"]["api_key"]
                            genai.configure(api_key=api_key)
                            imagem_pil = Image.open(foto_doc)
                            model = genai.GenerativeModel('models/gemini-2.5-flash')
                            prompt = """
                            Você é um especialista em OCR. Extraia as seguintes informações deste documento de identidade brasileiro:
                            1. Nome completo (campo Nome).
                            2. Data de nascimento (campo Data de Nascimento).
                            Retorne EXCLUSIVAMENTE um objeto JSON válido no padrão a seguir:
                            {"nome": "NOME COMPLETO", "data_nascimento": "DD/MM/AAAA"}
                            """
                            resposta_ia = model.generate_content([prompt, imagem_pil])
                            texto_ia = resposta_ia.text.strip().replace("```json", "").replace("```", "")
                            dados_json = json.loads(texto_ia)
                            if "nome" in dados_json:
                                st.session_state['ocr_nome'] = str(dados_json['nome']).upper().strip()
                            if "data_nascimento" in dados_json:
                                st.session_state['ocr_data_nascimento'] = str(dados_json['data_nascimento']).strip()
                            st.session_state['cad_camera_aberta'] = False
                            st.success("Dados preenchidos!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro na leitura: {e}")

            col_f4, col_f5, col_f6, col_f7 = st.columns([1, 1, 1, 1])
            with col_f4:
                cad_profissao = st.text_input("Profissão:", key="cad_profissao")
            with col_f5:
                import pandas as pd
                grupos_existentes = set()
                for c_nome, info in clientes.items():
                    g = info.get("grupo")
                    if g and not pd.isna(g) and str(g).strip():
                        grupos_existentes.add(str(g).strip())
                grupos_opcoes = sorted(list(grupos_existentes))
                if not grupos_opcoes:
                    grupos_opcoes = ["Mundo KAN"]
                
                opcoes_grupo = grupos_opcoes + ["Outro (Digitar Novo)..."]
                grupo_sel = st.selectbox("Grupo*:", options=opcoes_grupo, key="cad_grupo_select")
                if grupo_sel == "Outro (Digitar Novo)...":
                    cad_emp = st.text_input("Digite o nome do Grupo*:", key="cad_grupo_manual")
                else:
                    cad_emp = grupo_sel
            with col_f6:
                opcoes_empresa = ["Nenhuma / Não associada"] + nomes_empresas
                cad_empresa_sel = st.selectbox("Empresa (opcional):", options=opcoes_empresa, key="cad_empresa_sel")
            with col_f7:
                cad_link = st.text_input("LinkedIn (URL):", key="cad_link")
                
            cad_exp = st.text_area("Experiências Profissionais / Bio", placeholder="Resumo profissional para a IA...", height=80, key="cad_exp")
            
            st.write("---")
            col_b1, col_b2, col_b3 = st.columns([2, 2, 4])
            with col_b1:
                if st.button("Salvar", type="primary", use_container_width=True, key="cad_salvar_btn"):
                    if not cad_nome or not cad_nome.strip():
                        st.error("O campo 'Nome Completo' é obrigatório.")
                    elif not cad_data or not cad_data.strip() or len(cad_data.split('/')) != 3:
                        st.error("Formato de data inválido. Use dd/mm/yyyy (ex: 25/12/1980).")
                    elif not cad_emp or not cad_emp.strip():
                        st.error("O campo 'Grupo' é obrigatório.")
                    else:
                        foto_b64 = ""
                        if cad_foto:
                            foto_b64 = compress_image_to_b64(cad_foto, max_width=300) or ""

                        payload = {
                            "nome": cad_nome.strip(),
                            "data_nascimento": cad_data.strip(),
                            "profissao": cad_profissao.strip() if cad_profissao else None,
                            "grupo": cad_emp,
                            "empresa": cad_empresa_sel if cad_empresa_sel != "Nenhuma / Não associada" else None,
                            "linkedin_url": cad_link.strip() if cad_link else None,
                            "experiencias": cad_exp.strip() if cad_exp else None,
                            "foto_base64": foto_b64
                        }
                        if cad_foto:
                            if 'fotos' not in st.session_state: st.session_state['fotos'] = {}
                            st.session_state['fotos'][cad_nome.strip()] = cad_foto.getvalue()

                        if supabase_client:
                            try:
                                res_exist = supabase_client.table("mapas_salvos").select("id").eq("nome", cad_nome.strip()).execute()
                                if res_exist.data:
                                    supabase_client.table("mapas_salvos").update(payload).eq("nome", cad_nome.strip()).execute()
                                else:
                                    supabase_client.table("mapas_salvos").insert(payload).execute()
                                st.success("cadastro salvo com sucesso.")
                                st.session_state['ocr_nome'] = ''
                                st.session_state['ocr_data_nascimento'] = ''
                                st.cache_data.clear()
                            except Exception as ex:
                                st.error(f"Erro ao salvar no Supabase: {ex}")
                        else:
                            if "clientes_local_data" not in st.session_state:
                                st.session_state["clientes_local_data"] = {}
                            
                            existing_client = st.session_state.get("clientes_local_data", {}).get(cad_nome.strip(), {})
                            st.session_state["clientes_local_data"][cad_nome.strip()] = {
                                'data_nascimento': cad_data.strip(),
                                'profissao': cad_profissao.strip() if cad_profissao else '',
                                'cargo': existing_client.get('cargo', ''),
                                'grupo': cad_emp,
                                'empresa': cad_empresa_sel if cad_empresa_sel != "Nenhuma / Não associada" else '',
                                'linkedin_url': cad_link.strip() if cad_link else '',
                                'experiencias': cad_exp.strip() if cad_exp else '',
                                'foto_base64': foto_b64,
                                'ai_diagnosis': '',
                                'kan': None,
                                'perfil': '',
                                'categoria': '',
                                'qualidades': '',
                                'fortaleza': '',
                                'desafio': '',
                                'estrutural': '',
                                'direcionamento': '',
                                'repeticao_1': '',
                                'repeticao_2': '',
                                'mapa_detalhado': {},
                                'has_json': False
                            }
                            st.success("cadastro salvo com sucesso (armazenamento local ativo).")
                            st.session_state['ocr_nome'] = ''
                            st.session_state['ocr_data_nascimento'] = ''

        st.write("---")
        st.subheader("Consultar Talentos Cadastrados")
        
        if clientes:
            busca = st.text_input("Buscar por Nome, Profissão ou Grupo:", placeholder="Digite o termo de busca...", key="busca_talentos_input")
            
            dados_filtrados = []
            for nome, info in clientes.items():
                profissao = info.get("profissao") or info.get("cargo") or ""
                grupo = info.get("grupo") or info.get("empresa") or ""
                
                # Normaliza nans e None para string vazia
                if pd.isna(profissao) or str(profissao).lower() == 'nan': profissao = ""
                if pd.isna(grupo) or str(grupo).lower() == 'nan': grupo = ""
                
                if busca.strip():
                    termo = busca.lower().strip()
                    if termo not in nome.lower() and termo not in str(profissao).lower() and termo not in str(grupo).lower():
                        continue
                
                dados_filtrados.append({
                    "Nome": nome,
                    "Data de Nascimento": info.get("data_nascimento", ""),
                    "Profissão": profissao,
                    "Grupo": grupo,
                    "LinkedIn": info.get("linkedin_url", "") or "",
                    "foto_base64": info.get("foto_base64", "")
                })
                
            if dados_filtrados:
                # Monta a grade de cards nativa
                cols = st.columns(3)
                for idx, t in enumerate(dados_filtrados):
                    col = cols[idx % 3]
                    with col:
                        with st.container(border=True):
                            # Avatar/Foto
                            foto_b64 = t["foto_base64"]
                            if foto_b64:
                                avatar_html = f'<div style="display: flex; align-items: center; height: 100%;"><img src="data:image/png;base64,{foto_b64}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 2px solid #F18617; display: block;" /></div>'
                            else:
                                avatar_html = '<div style="display: flex; align-items: center; height: 100%;"><div style="width: 50px; height: 50px; border-radius: 50%; background: rgba(241,134,23,0.2); border: 2px solid #F18617; display: flex; align-items: center; justify-content: center; font-size: 1.5em;"><i class="icon-user" style="font-size:24px; color:#F18617;"></i></div></div>'
                            
                            col_c_avatar, col_c_info = st.columns([1, 3.2])
                            with col_c_avatar:
                                st.markdown(avatar_html, unsafe_allow_html=True)
                            with col_c_info:
                                st.markdown('<div class="talent-link-container" style="display: block; font-size: 0.9em; margin-bottom: 2px;">', unsafe_allow_html=True)
                                if st.button(t["Nome"], key=f"lnk_tal_list_{idx}_{t['Nome']}"):
                                    self.app.ver_cadastro_talento(t["Nome"])
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                role_lbl = t["Profissão"] or "Sem Profissão"
                                st.markdown(f"<span style='font-size: 0.78em; opacity: 0.7; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;' title='{role_lbl}'><i class='icon-briefcase' style='font-size:12px; color: #F18617; margin-right:4px;'></i>{role_lbl}</span>", unsafe_allow_html=True)
                                
                                if t["Grupo"]:
                                    st.markdown(f"<span style='font-size: 0.78em; opacity: 0.7; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;' title='{t['Grupo']}'><i class='icon-tag' style='font-size: 12px; color: #F18617; margin-right:4px;'></i>{t['Grupo']}</span>", unsafe_allow_html=True)
                                else:
                                    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
                                    
                                if t["LinkedIn"]:
                                    st.markdown(f"<a href='{t['LinkedIn']}' target='_blank' style='font-size: 0.75em; color: #F18617; font-weight: bold; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;'><i class='icon-linkedin' style='font-size:12px;'></i>LinkedIn</a>", unsafe_allow_html=True)
                                else:
                                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                
                st.write("")
                st.caption(f"Total de talentos encontrados: {len(dados_filtrados)}")
            else:
                st.info("Nenhum talento correspondente encontrado para a busca.")
        else:
            st.info("Nenhum talento cadastrado no sistema ainda.")
