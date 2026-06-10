import streamlit as st
import pandas as pd
import datetime
import json
import os
from PIL import Image
import google.generativeai as genai

from menus.base_menu import BaseMenu
from models.database import carregar_todos_clientes, get_supabase_admin, salvar_na_base_dados
from services.perfil import realizar_calculos_completos
from services.pdf_generator import gerar_pdf
from utils.helpers import remover_acentos

class DiagnosticosMenu(BaseMenu):
    def render(self, mode="diagnostico"):
        st.markdown("<h2 style='text-align: left; margin-bottom: 5px;'>Diagnóstico Comportamental</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.1em; color: rgba(255,255,255,0.7); margin-bottom: 20px;'>Diagnóstico comportamental instantâneo. Sem testes. Sem manipulação.</p>", unsafe_allow_html=True)
        st.session_state['show_mapa'] = False
        st.session_state['show_perfil'] = True

        supabase_client = get_supabase_admin()
        clientes_salvos = carregar_todos_clientes()

        opcoes_clientes = sorted(list(clientes_salvos.keys()))
        if not opcoes_clientes:
            opcoes_clientes = ["Nenhum perfil cadastrado"]

        col_top1, col_top2_area = st.columns([3, 1])
        with col_top1:
            cliente_selecionado = st.selectbox("Selecione um perfil cadastrado:", opcoes_clientes)
        col_top2 = col_top2_area.empty()

        if cliente_selecionado == "Nenhum perfil cadastrado":
            st.info("Nenhum perfil cadastrado ainda. Acesse o menu 'Cadastro' na barra lateral para adicionar o primeiro perfil.")
            return

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

        if 'fotos' not in st.session_state:
            st.session_state['fotos'] = {}

        tem_foto = bool(info_cliente.get('foto_base64')) or (nome in st.session_state['fotos'])
        if not tem_foto:
            foto_upload_existente = st.file_uploader("Carregar Foto (Opcional)", type=["png", "jpg", "jpeg", "webp"], key=f"foto_existente_{nome}")
            if foto_upload_existente:
                foto_bytes = foto_upload_existente.getvalue()
                st.session_state['fotos'][nome] = foto_bytes
                import base64
                encoded = base64.b64encode(foto_bytes).decode()
                if supabase_client:
                    try:
                        supabase_client.table("mapas_salvos").update({"foto_base64": encoded}).eq("nome", nome).execute()
                        info_cliente['foto_base64'] = encoded
                        st.rerun()
                    except Exception:
                        pass

        with st.expander("Editar dados do perfil", expanded=False):
            col_edit1, col_edit2 = st.columns(2)
            with col_edit1:
                new_nome = st.text_input("Nome", value=nome, key=f"edit_nome_{nome}")
                new_data = st.text_input("Data de Nascimento (dd/mm/yyyy)", value=data_str, key=f"edit_data_{nome}")
                new_profissao = st.text_input("Profissão", value=profissao if pd.notna(profissao) and str(profissao) != 'nan' else "", key=f"edit_profissao_{nome}")
            with col_edit2:
                new_grupo = st.text_input("Grupo", value=grupo if pd.notna(grupo) and str(grupo) != 'nan' else "", key=f"edit_emp_{nome}")
                new_linkedin = st.text_input("LinkedIn (URL)", value=linkedin if pd.notna(linkedin) and str(linkedin) != 'nan' else "", key=f"edit_link_{nome}")
                new_experiencias = st.text_area("Experiências Profissionais / Bio", value=experiencias if pd.notna(experiencias) and str(experiencias) != 'nan' else "", key=f"edit_exp_{nome}", height=68)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Salvar Alterações", key=f"btn_save_edit_{nome}"):
                sucesso_edit = False
                if supabase_client:
                    try:
                        supabase_client.table("mapas_salvos").update({
                            "nome": new_nome,
                            "data_nascimento": new_data,
                            "profissao": new_profissao,
                            "grupo": new_grupo,
                            "linkedin_url": new_linkedin,
                            "experiencias": new_experiencias
                        }).eq("nome", nome).execute()
                        sucesso_edit = True
                    except Exception as e:
                        st.error(f"Erro ao atualizar: {e}")
                else:
                    if "clientes_local_data" in st.session_state and nome in st.session_state["clientes_local_data"]:
                        st.session_state["clientes_local_data"][nome]["data_nascimento"] = new_data
                        st.session_state["clientes_local_data"][nome]["profissao"] = new_profissao
                        st.session_state["clientes_local_data"][nome]["grupo"] = new_grupo
                        st.session_state["clientes_local_data"][nome]["linkedin_url"] = new_linkedin
                        st.session_state["clientes_local_data"][nome]["experiencias"] = new_experiencias
                        sucesso_edit = True
                
                if sucesso_edit:
                    st.toast("Informações atualizadas!")
                    st.cache_data.clear()
                    st.rerun()

        st.markdown("---")
        
        # O perfil comportamental abre diretamente de forma fixa e a tabela do mapa fica restrita ao painel de controle
        st.session_state['show_perfil'] = True
        st.session_state['show_mapa'] = False

        empresa = info_cliente.get('empresa', '')
        res_calc = realizar_calculos_completos(nome, nascimento_tup, data_atual_tup, profissao, empresa)
        dados, dados_perfil, kan, estrutural, direcionamento, rep1, rep2, rep3, rep4, score_df_calc, score_cat_df, score_qual_df, auditoria_qual_df = res_calc
        st.session_state['last_calc_results'] = res_calc

        if not info_cliente.get('has_json'):
            salvar_na_base_dados(nome, dados_perfil, dados, estrutural, direcionamento, rep1, rep2)
            info_cliente['has_json'] = True

        col_res1, col_res2, col_res3 = st.columns([1, 10, 1])
        with col_res2:
            foto_b64 = None
            if nome in st.session_state['fotos']:
                import base64
                foto_b64 = base64.b64encode(st.session_state['fotos'][nome]).decode()
            elif clientes_salvos.get(nome) and clientes_salvos[nome].get('foto_base64'):
                foto_b64 = clientes_salvos[nome]['foto_base64']
            
            if foto_b64 and "base64," in foto_b64:
                foto_b64 = foto_b64.split("base64,")[1]
            
            subinfo_parts = [data_str]
            for p in [profissao, cargo, grupo]:
                if p and str(p).lower() != "nan" and str(p).strip() != "":
                    subinfo_parts.append(str(p))
            subinfo_text = " | ".join(subinfo_parts)

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
                    st.button(nome, key="lnk_diag_header_nome_foto", on_click=self.app.ver_cadastro_talento, args=(nome,))
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown(f"<p style='font-size: 1.1em; color: var(--text-soft); font-weight: 500; margin-top: 5px;'>{subinfo_text}</p>", unsafe_allow_html=True)
            else:
                st.markdown('<div class="talent-link-container" style="font-size: 1.6em; font-weight: bold; display: inline-block;">', unsafe_allow_html=True)
                st.button(nome, key="lnk_diag_header_nome_nofoto", on_click=self.app.ver_cadastro_talento, args=(nome,))
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 1.1em; color: var(--text-soft); font-weight: 500; margin-top: 5px;'>{subinfo_text}</p>", unsafe_allow_html=True)

            # Injeção de CSS unificado para os botões de ação do Perfil e do Mapa
            st.markdown("""
            <style>
                /* Forçar alinhamento e dimensões consistentes dos botões de ação */
                div[class*="st-key-dl_p_csv_"] button,
                div[class*="st-key-dl_mapa_csv_"] button,
                div[class*="st-key-dl_p_pdf_"] button,
                div[class*="st-key-dl_mapa_pdf_"] button,
                div[class*="st-key-save_bottom_"] button {
                    display: inline-flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    gap: 8px !important;
                    height: 42px !important;
                    color: #FFFFFF !important;
                    font-family: 'Inter', sans-serif !important;
                    border: 1px solid rgba(255, 255, 255, 0.15) !important;
                    border-radius: 8px !important;
                }

                /* Configuração dos ícones Lucide baseados em SVG Base64 */
                div[class*="st-key-dl_p_csv_"] button::before,
                div[class*="st-key-dl_mapa_csv_"] button::before,
                div[class*="st-key-dl_p_pdf_"] button::before,
                div[class*="st-key-dl_mapa_pdf_"] button::before,
                div[class*="st-key-save_bottom_"] button::before {
                    content: "" !important;
                    display: inline-flex !important;
                    width: 16px !important;
                    height: 16px !important;
                    margin-right: 8px !important;
                    background-size: contain !important;
                    background-repeat: no-repeat !important;
                    background-position: center !important;
                    vertical-align: middle !important;
                }

                /* Ícone de download/arquivo (file-spreadsheet) para CSV */
                div[class*="st-key-dl_p_csv_"] button::before,
                div[class*="st-key-dl_mapa_csv_"] button::before {
                    background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTYgMjJhMiAyIDAgMCAxLTItMlY0YTIgMiAwIDAgMSAyLTJoOGEyLjQgMi40IDAgMCAxIDEuNzA0LjcwNmwzLjU4OCAzLjU4OEEyLjQgMi40IDAgMCAxIDIwIDh2MTJhMiAyIDAgMCAxLTIgMnoiIC8+PHBhdGggZD0iTTE0IDJ2NWExIDEgMCAwIDAgMSAxaDUiIC8+PHBhdGggZD0iTTggMTNoMiIgLz48cGF0aCBkPSJNMTQgMTNoMiIgLz48cGF0aCBkPSJNOCAxN2gyIiAvPjxwYXRoIGQ9Ik0xNCAxN2gyIiAvPjwvc3ZnPg==") !important;
                }

                /* Ícone de download/documento (file-text) para PDF */
                div[class*="st-key-dl_p_pdf_"] button::before,
                div[class*="st-key-dl_mapa_pdf_"] button::before {
                    background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTYgMjJhMiAyIDAgMCAxLTItMlY0YTIgMiAwIDAgMSAyLTJoOGEyLjQgMi40IDAgMCAxIDEuNzA0LjcwNmwzLjU4OCAzLjU4OEEyLjQgMi40IDAgMCAxIDIwIDh2MTJhMiAyIDAgMCAxLTIgMnoiIC8+PHBhdGggZD0iTTE0IDJ2NWExIDEgMCAwIDAgMSAxaDUiIC8+TTEwIDlIOCIgLz48cGF0aCBkPSJNMTYgMTNIOCIgLz48cGF0aCBkPSJNMTYgMTdIOCIgLz48L3N2Zz4=") !important;
                }

                /* Ícone de database/salvar (database) para Salvar na Base de Dados */
                div[class*="st-key-save_bottom_"] button::before {
                    background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PGVsbGlwc2UgY3g9IjEyIiBjeT0iNSIgcng9IjkiIHJ5PSIzIiAvPjxwYXRoIGQ9Ik0zIDVWMTlBOSAzIDAgMCAwIDIxIDE5VjUiIC8+PHBhdGggZD0iTTMgMTJBOSAzIDAgMCAwIDIxIDEyIiAvPjwvc3ZnPg==") !important;
                }
            </style>
            """, unsafe_allow_html=True)

            if st.session_state.get('show_perfil'):
                st.markdown("---")
                st.subheader("Perfil Comportamental")
                
                st.markdown("""<style>
                .perfil-custom-table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin-top: 15px; 
                    background: var(--panel-bg); 
                    border: 1px solid var(--panel-border);
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: var(--card-shadow);
                }
                .perfil-custom-table th { 
                    background-color: var(--accent); 
                    color: var(--button-primary-text); 
                    padding: 14px 20px; 
                    text-align: left; 
                    font-size: 1.05em; 
                    font-weight: 800;
                }
                .perfil-custom-table td { 
                    border-bottom: 1px solid var(--divider); 
                    vertical-align: top; 
                    padding: 16px 20px; 
                }
                .p-label { color: var(--accent); font-weight: 800; font-size: 1.1em; margin-bottom: 8px; }
                .p-badge { 
                    display: inline-block; 
                    background: linear-gradient(135deg, var(--accent) 0%, #D97706 100%); 
                    color: var(--button-primary-text); 
                    font-weight: 900; 
                    font-size: 1.2em; 
                    padding: 4px 14px; 
                    border-radius: 8px; 
                    box-shadow: 0 4px 10px rgba(240, 138, 0, 0.3);
                    margin-bottom: 8px; 
                }
                .p-desc { color: var(--text-main); font-size: 0.95em; line-height: 1.6; text-align: justify; }
                </style>""", unsafe_allow_html=True)
                
                html_table = '<table class="perfil-custom-table"><thead><tr><th style="width: 28%;">Indicador KAN / Valor</th><th>Análise e Interpretação</th></tr></thead><tbody>'
                for item in dados_perfil:
                    html_table += f"<tr><td><div class='p-label'>{item['Campo']}</div><div class='p-badge'>{item['Valor']}</div></td>"
                    html_table += f"<td><div class='p-desc'>{item['Descricao']}</div></td></tr>"
                html_table += "</tbody></table>"
                
                st.markdown(html_table, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Gerar Diagnóstico Profissional com IA", key=f"btn_ia_{nome}"):
                    try:
                        api_key = st.secrets["gemini"]["api_key"]
                        genai.configure(api_key=api_key)
                        
                        mapa_texto = "\n".join([f"- {item['Campo']}: {item['Resultado']}" for item in dados])
                        perfil_texto = "\n".join([f"- {item['Campo']}: {item['Resultado']}" for item in dados_perfil if item['Campo'] != "Diagnóstico"])
                        info_prof = f"- LinkedIn: {linkedin}\n- Experiências: {experiencias}" if (linkedin or experiencias) else ""
                        
                        contexto = f"""
                        Você é um Especialista em Recrutamento e Seleção (RH) de alta performance e Consultor de Carreira.
                        Sua tarefa é analisar o perfil completo de {nome} e gerar um Diagnóstico de Performance com foco em contratação corporativa.
                        
                        DADOS BRUTOS DO PERFIL E TENDÊNCIAS COMPORTAMENTAIS:
                        {mapa_texto}
                        
                        DADOS DO PERFIL KAN (Forças, Estilo de Trabalho e Qualidades):
                        {perfil_texto}
                        
                        INFORMAÇÕES PROFISSIONAIS ADICIONAIS:
                        {info_prof}
                        
                        DIRETRIZES ESTRITAS PARA A REDAÇÃO:
                        1. Use puramente linguagem corporativa, psicológica e de RH (Foco em soft skills, competências, fit cultural e desafios de gestão).
                        2. PROIBIDO MENCIONAR TERMOS NUMEROLÓGICOS: NUNCA escreva palavras como "Mapa", "Numerologia", "Expressão 1", "Destino 8", "Motivação", "Dívidas Cármicas", etc. Você deve APENAS absorver o significado psicológico desses itens e transformá-los em análise de competência profissional.
                        3. NUNCA use a expressão "tendências numerológicas". Se precisar, use "tendências comportamentais", "análise de perfil" ou "mapeamento".
                        4. O texto não pode, em hipótese alguma, parecer uma consulta esotérica. Deve soar como uma avaliação técnica, profunda e baseada em dados analíticos de RH.
                        5. O texto deve ser formatado em exatamente 3 parágrafos curtos, diretos e objetivos.
                        """
                        
                        with st.spinner("IA analisando perfil com visão de RH (Alta Performance)..."):
                            texto_ia = ""
                            try:
                                model = genai.GenerativeModel('models/gemini-2.5-flash')
                                response = model.generate_content(contexto)
                                texto_ia = response.text.replace("\n", "<br>")
                            except Exception as e1:
                                try:
                                    model = genai.GenerativeModel('models/gemini-3.1-pro-preview')
                                    response = model.generate_content(contexto)
                                    texto_ia = response.text.replace("\n", "<br>")
                                except Exception as e2:
                                    texto_ia = f"<b>Aviso de Sistema:</b> Erro na geração com IA: {e1}"
                            
                            user_name_key = f"diag_{nome}"
                            if "ai_diagnosis" not in st.session_state:
                                st.session_state["ai_diagnosis"] = {}
                            st.session_state["ai_diagnosis"][user_name_key] = texto_ia
                            
                            if supabase_client:
                                try:
                                    supabase_client.table("mapas_salvos").update({"ai_diagnosis": texto_ia}).eq("nome", nome).execute()
                                except Exception: pass
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erro na IA: {e}")

                st.markdown("---")

                st.subheader("Salvar Perfil Comportamental")
                col_p1, col_p2, col_p3 = st.columns(3)
                df_perfil = pd.DataFrame(dados_perfil)
                nome_limpo_p = remover_acentos(nome).replace(' ', '_')
                with col_p1:
                    csv_p = df_perfil.to_csv(sep=';', index=False).encode('utf-8')
                    st.download_button("Baixar Perfil como CSV", data=csv_p, file_name=f"perfil_{nome_limpo_p}.csv", mime="text/csv", key=f"dl_p_csv_{nome}", use_container_width=True)
                with col_p2:
                    data_str_pdf = data_input.strftime('%d/%m/%Y')
                    pdf_p = gerar_pdf(nome, data_str_pdf, dados_perfil, titulo="Perfil Comportamental KAN")
                    st.download_button("Baixar Perfil como PDF", data=pdf_p, file_name=f"perfil_{nome_limpo_p}.pdf", mime="application/pdf", key=f"dl_p_pdf_{nome}", use_container_width=True)
                with col_p3:
                    if st.button("Salvar na Base de Dados", key=f"save_bottom_{nome}", use_container_width=True):
                        salvar_na_base_dados(nome, dados_perfil, dados, estrutural, direcionamento, rep1, rep2)

            if st.session_state.get('show_mapa'):
                st.markdown("---")
                st.subheader("Mapa Numerológico Cabalístico")
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

                st.markdown("---")
                st.subheader("Baixar Resultados do Mapa")
                col1, col2 = st.columns(2)
                nome_limpo = remover_acentos(nome).replace(' ', '_')
                df = pd.DataFrame(dados)
                
                with col1:
                    csv = df.to_csv(sep=';', index=False).encode('utf-8')
                    st.download_button("Baixar Mapa como CSV", data=csv, file_name=f"mapa_{nome_limpo}.csv", mime="text/csv", key=f"dl_mapa_csv_{nome}", use_container_width=True)
                with col2:
                    data_str_pdf = data_input.strftime('%d/%m/%Y')
                    pdf_bytes = gerar_pdf(nome, data_str_pdf, dados, titulo="Mapa Numerologico Cabalistico")
                    st.download_button("Baixar Mapa como PDF", data=pdf_bytes, file_name=f"mapa_{nome_limpo}.pdf", mime="application/pdf", key=f"dl_mapa_pdf_{nome}", use_container_width=True)
