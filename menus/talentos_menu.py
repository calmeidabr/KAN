import streamlit as st
import datetime
import json
from PIL import Image
import google.generativeai as genai

from menus.base_menu import BaseMenu
from models.database import carregar_empresas, get_supabase_admin
from utils.helpers import compress_image_to_b64

class TalentosMenu(BaseMenu):
    def render(self):
        st.title("Cadastro de Talentos")
        st.info("Cadastre novos perfis para análise comportamental e numerológica no sistema.")
        st.write("---")

        supabase_client = get_supabase_admin()
        lista_empresas_salvas = carregar_empresas()
        nomes_empresas = [e["nome_empresa"] for e in lista_empresas_salvas if e.get("nome_empresa")]
        if not nomes_empresas:
            nomes_empresas = ["Mundo KAN", "Empresa Cliente A"]

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

            col_f4, col_f5, col_f6 = st.columns([1, 1, 1])
            with col_f4:
                cad_cargo = st.text_input("Cargo/Profissão:", key="cad_cargo")
            with col_f5:
                cad_emp = st.selectbox("Empresa/Grupo*:", options=nomes_empresas, key="cad_emp")
            with col_f6:
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
                    else:
                        foto_b64 = ""
                        if cad_foto:
                            foto_b64 = compress_image_to_b64(cad_foto, max_width=300) or ""

                        payload = {
                            "nome": cad_nome.strip(),
                            "data_nascimento": cad_data.strip(),
                            "cargo": cad_cargo.strip() if cad_cargo else None,
                            "empresa": cad_emp,
                            "linkedin_url": cad_link.strip() if cad_link else None,
                            "experiencias": cad_exp.strip() if cad_exp else None,
                            "foto_base64": foto_b64,
                            "created_at": datetime.datetime.now().isoformat()
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
                            
                            # Simulando o payload completo que a tabela Supabase forneceria 
                            # (em carregar_todos_clientes)
                            st.session_state["clientes_local_data"][cad_nome.strip()] = {
                                'data_nascimento': cad_data.strip(),
                                'cargo': cad_cargo.strip() if cad_cargo else '',
                                'empresa': cad_emp,
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
