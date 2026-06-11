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
        # Inicializar semente de reset se não existir
        if 'form_reset_id' not in st.session_state:
            st.session_state['form_reset_id'] = 0

        # Adicionar o talento em exibição nos últimos consultados
        cad_nome_atual = st.session_state.get("cad_nome", "")
        if cad_nome_atual and cad_nome_atual.strip():
            if "ultimos_consultados" not in st.session_state:
                st.session_state["ultimos_consultados"] = []
            if cad_nome_atual.strip() not in st.session_state["ultimos_consultados"]:
                st.session_state["ultimos_consultados"].insert(0, cad_nome_atual.strip())
                st.session_state["ultimos_consultados"] = st.session_state["ultimos_consultados"][:6]

        # Garantir que a câmera inicia fechada ao alternar para esta página
        current_menu = st.session_state.get('sidebar_menu', 'Talentos')
        if st.session_state.get('last_sidebar_menu') != current_menu:
            st.session_state['cad_camera_aberta'] = False
            st.session_state['last_sidebar_menu'] = current_menu
            st.session_state['limpar_formulario'] = True

        # Processar a limpeza de inputs antes da criação dos widgets
        if st.session_state.get('limpar_formulario', False):
            st.session_state['cad_nome'] = ""
            st.session_state['cad_data'] = ""
            st.session_state['cad_profissao'] = ""
            st.session_state['cad_grupo'] = ""
            st.session_state['cad_empresa_sel'] = "Nenhuma / Não associada"
            st.session_state['cad_link'] = ""
            st.session_state['cad_exp'] = ""
            st.session_state['ocr_nome'] = ""
            st.session_state['ocr_data_nascimento'] = ""
            st.session_state['cad_data_sincronizado'] = ""
            st.session_state['cad_camera_aberta'] = False
            
            # Limpar chaves antigas de fotos do session_state
            prev_reset_id = st.session_state.get('form_reset_id', 0)
            if f"cad_foto_{prev_reset_id}" in st.session_state:
                del st.session_state[f"cad_foto_{prev_reset_id}"]
            if "cad_foto" in st.session_state:
                del st.session_state["cad_foto"]
                
            # Incrementar o ID para limpar os widgets dinamicamente
            st.session_state['form_reset_id'] = prev_reset_id + 1
            st.session_state['limpar_formulario'] = False

        st.markdown("<h2 style='text-align: left; margin-bottom: 5px;'>Cadastro de Talentos</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.1em; color: rgba(255,255,255,0.7); margin-bottom: 20px;'>Cadastre talentos na base e consulte seus perfis comportamentais.</p>", unsafe_allow_html=True)
        st.write("---")

        supabase_client = get_supabase_admin()
        lista_empresas_salvas = carregar_empresas()
        nomes_empresas = [e["nome_empresa"] for e in lista_empresas_salvas if e.get("nome_empresa")]
        if not nomes_empresas:
            nomes_empresas = ["Mundo Kan", "Empresa Cliente A"]

        clientes = carregar_todos_clientes()

        with st.container(border=True):
            st.subheader("Novo Cadastro")
            cad_nome = st.text_input("Nome Completo (Conforme certidão)*:", value=st.session_state.get('ocr_nome', ''), key="cad_nome")
            
            reset_id = st.session_state.get('form_reset_id', 0)
            col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
            with col_f1:
                ocr_data = st.session_state.get('ocr_data_nascimento', '')
                if ocr_data and st.session_state.get("cad_data_sincronizado") != ocr_data:
                    st.session_state["cad_data"] = ocr_data
                    st.session_state["cad_data_sincronizado"] = ocr_data

                raw_data = st.session_state.get("cad_data", "")
                digitos = "".join(ch for ch in raw_data if ch.isdigit())[:8]
                
                if len(digitos) <= 2:
                    data_formatada = digitos
                elif len(digitos) <= 4:
                    data_formatada = f"{digitos[:2]}/{digitos[2:]}"
                else:
                    data_formatada = f"{digitos[:2]}/{digitos[2:4]}/{digitos[4:]}"
                    
                if raw_data != data_formatada:
                    st.session_state["cad_data"] = data_formatada
                    st.rerun()

                cad_data = st.text_input(
                    "Data de Nascimento*:", 
                    placeholder="dd/mm/aaaa", 
                    key="cad_data"
                )
            with col_f2:
                cad_foto = st.file_uploader("Foto (Opcional)", type=["png", "jpg", "jpeg", "webp"], key=f"cad_foto_{reset_id}")
            with col_f3:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                cam_aberta = st.session_state.get('cad_camera_aberta', False)
                cam_label = "Fechar Câmera" if cam_aberta else "Ativar Câmera"
                if st.button(cam_label, use_container_width=True, key="cad_cam_btn"):
                    st.session_state['cad_camera_aberta'] = not cam_aberta
                    st.rerun()
                st.caption("Leitura de Documento via IA")
            
            if st.session_state.get('cad_camera_aberta', False):
                foto_doc = st.camera_input("Tire uma foto legível do seu documento", key=f"cad_cam_in_{reset_id}")
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
                cad_emp = st.text_input("Grupo (opcional):", key="cad_grupo")
            with col_f6:
                opcoes_empresa = ["Nenhuma / Não associada"] + nomes_empresas
                cad_empresa_sel = st.selectbox("Empresa (opcional):", options=opcoes_empresa, key="cad_empresa_sel")
            with col_f7:
                cad_link = st.text_input("LinkedIn (URL):", key="cad_link")
                
            cad_exp = st.text_area("Experiências Profissionais / Bio", placeholder="Resumo profissional para a IA...", height=80, key="cad_exp")
            
            if st.session_state.get("cad_nome"):
                nome_consultado = st.session_state.get("cad_nome")
                from models.database import carregar_equipes
                eq_pertence = []
                for eq in carregar_equipes():
                    lista_m_raw = eq.get("membros", [])
                    if isinstance(lista_m_raw, str):
                        try:
                            lista_m_raw = json.loads(lista_m_raw)
                        except Exception:
                            lista_m_raw = []
                    m_nomes = []
                    for m in lista_m_raw:
                        if isinstance(m, dict):
                            m_nomes.append(m.get("nome"))
                        else:
                            m_nomes.append(m)
                    if nome_consultado in m_nomes:
                        eq_pertence.append(eq["nome"])
                
                if eq_pertence:
                    st.write("")
                    st.markdown("**Equipes das quais este talento faz parte:**")
                    st.markdown('<div class="talent-link-container" style="display: block; font-size: 0.95em; margin-bottom: 10px;">', unsafe_allow_html=True)
                    cols_eq = st.columns(len(eq_pertence) if len(eq_pertence) < 6 else 6)
                    for eq_idx, eq_nome in enumerate(eq_pertence):
                        col_eq = cols_eq[eq_idx % len(cols_eq)]
                        with col_eq:
                            st.button(eq_nome, key=f"lnk_eq_form_{nome_consultado}_{eq_nome}_{eq_idx}", use_container_width=True, on_click=self.app.ver_equipe, args=(eq_nome,))
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.write("")
                    st.caption("Este talento não pertence a nenhuma equipe cadastrada.")
            
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
                            "profissao": cad_profissao.strip() if cad_profissao else None,
                            "grupo": cad_emp.strip() if cad_emp else None,
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
                                st.session_state['limpar_formulario'] = True
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Erro ao salvar no banco de dados: {ex}")
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
                            st.session_state['limpar_formulario'] = True
                            st.rerun()
            with col_b2:
                if st.button("Novo", use_container_width=True, key="cad_novo_btn"):
                    st.session_state['limpar_formulario'] = True
                    st.rerun()

        st.write("---")
        st.subheader("Consultar Talentos Cadastrados")
        
        if clientes:
            busca = st.text_input("Buscar por Nome, Profissão ou Grupo:", placeholder="Digite o termo de busca...", key="busca_talentos_input")
            
            dados_filtrados = []
            ultimos_consultados = st.session_state.get("ultimos_consultados", [])
            usar_ultimos = not busca.strip()
            
            for nome, info in clientes.items():
                if usar_ultimos and nome not in ultimos_consultados:
                    continue
                    
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
                from models.database import fetch_fotos_clientes
                nomes_filtrados = [t["Nome"] for t in dados_filtrados]
                fotos_dict = fetch_fotos_clientes(nomes_filtrados)
                for t in dados_filtrados:
                    t["foto_base64"] = fotos_dict.get(t["Nome"], "")

                # Monta a grade de cards nativa
                cols = st.columns(3)
                for idx, t in enumerate(dados_filtrados):
                    col = cols[idx % 3]
                    with col:
                        with st.container(border=True):
                            # Avatar/Foto
                            foto_b64 = t["foto_base64"]
                            if foto_b64:
                                avatar_html = f'<div style="display: flex; align-items: center; height: 100%;"><img src="data:image/png;base64,{foto_b64}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 2px solid var(--accent); display: block;" /></div>'
                            else:
                                avatar_html = '<div style="display: flex; align-items: center; height: 100%;"><div style="width: 50px; height: 50px; border-radius: 50%; background: var(--sidebar-item-active-bg); border: 2px solid var(--accent); display: flex; align-items: center; justify-content: center; font-size: 1.5em;"><i class="icon-user" style="font-size:24px; color:var(--accent);"></i></div></div>'
                            
                            col_c_avatar, col_c_info = st.columns([1, 3.2])
                            with col_c_avatar:
                                st.markdown(avatar_html, unsafe_allow_html=True)
                            with col_c_info:
                                st.markdown('<div class="talent-link-container" style="display: block; font-size: 0.9em; margin-bottom: 2px;">', unsafe_allow_html=True)
                                st.button(t["Nome"], key=f"lnk_tal_list_{idx}_{t['Nome']}", on_click=self.app.ver_cadastro_talento, args=(t["Nome"],))
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                role_lbl = t["Profissão"] or "Sem Profissão"
                                st.markdown(f"<span style='font-size: 0.78em; opacity: 0.7; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;' title='{role_lbl}'><i class='icon-briefcase' style='font-size:12px; color: var(--accent); margin-right:4px;'></i>{role_lbl}</span>", unsafe_allow_html=True)
                                
                                if t["Grupo"]:
                                    st.markdown(f"<span style='font-size: 0.78em; opacity: 0.7; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;' title='{t['Grupo']}'><i class='icon-tag' style='font-size: 12px; color: var(--accent); margin-right:4px;'></i>{t['Grupo']}</span>", unsafe_allow_html=True)
                                else:
                                    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

                                # Adicionar Equipes no card
                                from models.database import carregar_equipes
                                todas_equipes = carregar_equipes()
                                membro_de = []
                                for eq in todas_equipes:
                                    lista_m_raw = eq.get("membros", [])
                                    if isinstance(lista_m_raw, str):
                                        try: lista_m_raw = json.loads(lista_m_raw)
                                        except: lista_m_raw = []
                                    m_nomes = []
                                    for m in lista_m_raw:
                                        if isinstance(m, dict): m_nomes.append(m.get("nome"))
                                        else: m_nomes.append(m)
                                    if t["Nome"] in m_nomes:
                                        membro_de.append(eq["nome"])

                                if membro_de:
                                    st.markdown("<span style='font-size: 0.78em; opacity: 0.7; display: block; margin-top: 4px;'><i class='icon-users' style='font-size:12px; color: var(--accent); margin-right:4px;'></i>Equipes:</span>", unsafe_allow_html=True)
                                    st.markdown('<div class="talent-link-container" style="display: block; font-size: 0.75em; margin-bottom: 4px;">', unsafe_allow_html=True)
                                    for eq_idx, eq_nome in enumerate(membro_de):
                                        st.button(eq_nome, key=f"lnk_eq_card_{t['Nome']}_{eq_nome}_{eq_idx}", on_click=self.app.ver_equipe, args=(eq_nome,))
                                    st.markdown('</div>', unsafe_allow_html=True)
                                else:
                                    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
                                    
                                if t["LinkedIn"]:
                                    st.markdown(f"<a href='{t['LinkedIn']}' target='_blank' style='font-size: 0.75em; color: var(--accent); font-weight: bold; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;'><i class='icon-linkedin' style='font-size:12px;'></i>LinkedIn</a>", unsafe_allow_html=True)
                                else:
                                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                
                st.write("")
                st.caption(f"Total de talentos encontrados: {len(dados_filtrados)}")
            else:
                if usar_ultimos:
                    st.info("Use o campo de busca acima para pesquisar talentos cadastrados. Seus talentos consultados recentemente aparecerão aqui para acesso rápido.")
                else:
                    st.info("Nenhum talento correspondente encontrado para a busca.")
        else:
            st.info("Nenhum talento cadastrado no sistema ainda.")
