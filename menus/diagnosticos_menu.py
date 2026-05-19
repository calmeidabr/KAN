import streamlit as st
import pandas as pd
import datetime
import json
import os
from PIL import Image
import google.generativeai as genai

from menus.base_menu import BaseMenu
from models.database import carregar_todos_clientes, get_supabase, salvar_na_base_dados
from services.perfil import realizar_calculos_completos
from services.pdf_generator import gerar_pdf
from utils.helpers import remover_acentos

class DiagnosticosMenu(BaseMenu):
    def render(self, mode="diagnostico"):
        if mode == "diagnostico":
            st.markdown("<h2 style='text-align: left; margin-bottom: 5px;'>Diagnóstico Comportamental</h2>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 1.1em; color: rgba(255,255,255,0.7); margin-bottom: 20px;'>Diagnóstico comportamental instantâneo. Sem testes. Sem manipulação.</p>", unsafe_allow_html=True)
            st.session_state['show_mapa'] = False
            st.session_state['show_perfil'] = True
        else:
            st.markdown("<h2 style='text-align: left; margin-bottom: 5px;'>Mapas Detalhados</h2>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 1.1em; color: rgba(255,255,255,0.7); margin-bottom: 20px;'>Visualização completa de dados numerológicos e arquétipos.</p>", unsafe_allow_html=True)
            st.session_state['show_mapa'] = True
            st.session_state['show_perfil'] = False

        supabase_client = get_supabase()
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
        cargo = info_cliente.get('cargo', '')
        empresa = info_cliente.get('empresa', '')
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
            foto_upload_existente = st.file_uploader("Carregar Foto (Opcional)", type=["png", "jpg", "jpeg"], key=f"foto_existente_{nome}")
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

        with st.expander("📝 Editar dados do perfil", expanded=False):
            col_edit1, col_edit2 = st.columns(2)
            with col_edit1:
                new_nome = st.text_input("Nome", value=nome, key=f"edit_nome_{nome}")
                new_data = st.text_input("Data de Nascimento (dd/mm/yyyy)", value=data_str, key=f"edit_data_{nome}")
                new_cargo = st.text_input("Cargo/Profissão", value=cargo if pd.notna(cargo) and str(cargo) != 'nan' else "", key=f"edit_cargo_{nome}")
            with col_edit2:
                new_empresa = st.text_input("Empresa/Grupo", value=empresa if pd.notna(empresa) and str(empresa) != 'nan' else "", key=f"edit_emp_{nome}")
                new_linkedin = st.text_input("LinkedIn (URL)", value=linkedin if pd.notna(linkedin) and str(linkedin) != 'nan' else "", key=f"edit_link_{nome}")
                new_experiencias = st.text_area("Experiências Profissionais / Bio", value=experiencias if pd.notna(experiencias) and str(experiencias) != 'nan' else "", key=f"edit_exp_{nome}", height=68)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Salvar Alterações", key=f"btn_save_edit_{nome}"):
                if supabase_client:
                    try:
                        supabase_client.table("mapas_salvos").update({
                            "nome": new_nome,
                            "data_nascimento": new_data,
                            "cargo": new_cargo,
                            "empresa": new_empresa,
                            "linkedin_url": new_linkedin,
                            "experiencias": new_experiencias
                        }).eq("nome", nome).execute()
                        st.toast("✅ Informações atualizadas!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao atualizar: {e}")

        st.markdown("---")
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            show_p_chk = st.checkbox("Exibir Perfil Comportamental", value=st.session_state['show_perfil'], key=f"chk_p_{nome}")
            st.session_state['show_perfil'] = show_p_chk
        with col_t2:
            show_m_chk = st.checkbox("Exibir Tabela Completa do Mapa", value=st.session_state['show_mapa'], key=f"chk_m_{nome}")
            st.session_state['show_mapa'] = show_m_chk

        res_calc = realizar_calculos_completos(nome, nascimento_tup, data_atual_tup, cargo, empresa)
        dados, dados_perfil, kan, estrutural, direcionamento, rep1, rep2, rep3, rep4, score_df_calc, score_cat_df, score_qual_df, auditoria_qual_df = res_calc
        st.session_state['last_calc_results'] = res_calc

        if not info_cliente.get('has_json') and supabase_client:
            try:
                dados_para_salvar = list(dados_perfil)
                for label, val in [("Estrutural", estrutural), ("Direcionamento", direcionamento), 
                                   ("REPETIÇÃO 1", rep1), ("REPETIÇÃO 2", rep2)]:
                    dados_para_salvar.append({
                        "Campo": label, "Valor": str(val), "Descricao": "", "Resultado": str(val)
                    })
                for item in dados:
                    campo_full = item.get('Campo', '')
                    if ' - ' in campo_full:
                        partes = campo_full.split(' - ')
                        campo_simples = partes[0]
                        valor_simples = partes[1]
                    else:
                        campo_simples = campo_full
                        valor_simples = item.get('Resultado', '')
                        if len(str(valor_simples)) > 50: valor_simples = "Ver Mapa"
                    
                    dados_para_salvar.append({
                        "Campo": f"Mapa: {campo_simples}", "Valor": valor_simples, "Descricao": "", "Resultado": valor_simples
                    })
                perfil_json_str = json.dumps(dados_para_salvar, ensure_ascii=False)
                mapa_json_str = json.dumps(dados, ensure_ascii=False)
                supabase_client.table("mapas_salvos").update({
                    "mapa_json": mapa_json_str,
                    "perfil_json": perfil_json_str
                }).eq("nome", nome).execute()
                info_cliente['has_json'] = True
            except Exception:
                pass

        col_res1, col_res2, col_res3 = st.columns([1, 10, 1])
        with col_res2:
            info_parts = [nome, data_str]
            for p in [cargo, empresa]:
                if p and str(p).lower() != "nan" and str(p).strip() != "":
                    info_parts.append(str(p))
            info_text = " | ".join(info_parts)
            
            foto_b64 = None
            if nome in st.session_state['fotos']:
                import base64
                foto_b64 = base64.b64encode(st.session_state['fotos'][nome]).decode()
            elif clientes_salvos.get(nome) and clientes_salvos[nome].get('foto_base64'):
                foto_b64 = clientes_salvos[nome]['foto_base64']
            
            if foto_b64:
                html = f'''
                <div style="display: flex; align-items: center; margin-bottom: 25px;">
                    <div style="width: 120px; height: 120px; min-width: 120px; min-height: 120px; border-radius: 50%; overflow: hidden; border: 3px solid #F18617; box-shadow: 0px 4px 10px rgba(0,0,0,0.3); margin-right: 25px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; background-color: #1b0520;">
                        <img src="data:image/png;base64,{foto_b64}" style="width: 100%; height: 100%; object-fit: cover; display: block;">
                    </div>
                    <h3 style="margin: 0; color: #FFFFFF; font-weight: bold;">{info_text}</h3>
                </div>
                '''
                st.markdown(html, unsafe_allow_html=True)
            else:
                html = f'''
                <div style="display: flex; align-items: center; margin-bottom: 25px;">
                    <h3 style="margin: 0; color: #FFFFFF; font-weight: bold;">{info_text}</h3>
                </div>
                '''
                st.markdown(html, unsafe_allow_html=True)

            if st.session_state.get('show_perfil'):
                st.markdown("---")
                st.subheader("Perfil Comportamental")
                
                st.markdown("""<style>
                .perfil-custom-table { width: 100%; border-collapse: collapse; margin-top: 10px; background: rgba(255,255,255,0.05); }
                .perfil-custom-table th { background-color: #F18617; color: #401041; padding: 12px; text-align: left; }
                .perfil-custom-table td { border: 1px solid rgba(255,255,255,0.1); vertical-align: top; padding: 0; }
                .p-label { color: #F18617; font-weight: bold; padding: 12px; }
                .p-value { background-color: #F18617; color: #401041; padding: 6px; font-weight: bold; text-align: center; }
                .p-desc { padding: 12px; color: #FFFFFF; font-size: 0.95em; line-height: 1.5; }
                </style>""", unsafe_allow_html=True)
                
                html_table = '<table class="perfil-custom-table"><thead><tr><th>Campo</th><th>Resultado</th></tr></thead><tbody>'
                for item in dados_perfil:
                    html_table += f"<tr><td style='width: 25%;'><div class='p-label'>{item['Campo']}</div></td>"
                    html_table += f"<td><div class='p-value'>{item['Valor']}</div><div class='p-desc'>{item['Descricao']}</div></td></tr>"
                html_table += "</tbody></table>"
                
                st.markdown(html_table, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🪄 Gerar Diagnóstico Profissional com IA", key=f"btn_ia_{nome}"):
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
                    st.download_button("📥 Baixar Perfil como CSV", data=csv_p, file_name=f"perfil_{nome_limpo_p}.csv", mime="text/csv", key=f"dl_p_csv_{nome}")
                with col_p2:
                    data_str_pdf = data_input.strftime('%d/%m/%Y')
                    pdf_p = gerar_pdf(nome, data_str_pdf, dados_perfil, titulo="Perfil Comportamental KAN")
                    st.download_button("📄 Baixar Perfil como PDF", data=pdf_p, file_name=f"perfil_{nome_limpo_p}.pdf", mime="application/pdf", key=f"dl_p_pdf_{nome}")
                with col_p3:
                    if st.button("💾 Salvar na Base de Dados", key=f"save_bottom_{nome}", use_container_width=True):
                        salvar_na_base_dados(nome, dados_perfil, dados, estrutural, direcionamento, rep1, rep2)

            if st.session_state.get('show_mapa'):
                st.markdown("---")
                st.subheader("Mapa Numerológico Cabalístico")
                st.markdown("""
                <style>
                .mapa-table { width: 100%; border-collapse: collapse; margin-top: 10px; background: rgba(255,255,255,0.05); }
                .mapa-table th { background-color: #F18617; color: #401041; padding: 10px 14px; text-align: left; font-size: 0.95em; }
                .mapa-table td { border: 1px solid rgba(255,255,255,0.1); vertical-align: top; padding: 0; }
                .mapa-campo { color: #F18617; font-weight: bold; padding: 10px 14px; white-space: nowrap; font-size: 0.9em; }
                .mapa-numero { display: inline-block; background: #F18617; color: #401041;
                               font-weight: bold; font-size: 1.1em; padding: 1px 8px;
                               border-radius: 4px; margin-left: 6px; }
                .mapa-desc { padding: 10px 14px; color: #FFFFFF; font-size: 0.88em;
                             line-height: 1.45; text-align: justify; }
                .mapa-valor { padding: 10px 14px; color: #FFFFFF; font-size: 0.95em; }
                </style>
                """, unsafe_allow_html=True)

                html_mapa = '<table class="mapa-table"><thead><tr><th style="width:18%">Campo</th><th>Resultado</th></tr></thead><tbody>'
                for item in dados:
                    campo_raw = item['Campo']
                    resultado_raw = item['Resultado']

                    if ' - ' in campo_raw:
                        partes_campo = campo_raw.rsplit(' - ', 1)
                        label_campo = partes_campo[0]
                        numero_badge = f"<span class='mapa-numero'>{partes_campo[1]}</span>"
                    else:
                        label_campo = campo_raw
                        numero_badge = ""

                    if resultado_raw:
                        cel_resultado = f"<div class='mapa-desc'>{resultado_raw}</div>"
                    else:
                        cel_resultado = "<div class='mapa-valor'></div>"

                    explicacao_html = ""
                    if item.get("Explicacao"):
                        explicacao_html = f"<div style='font-size: 0.78em; color: rgba(255,255,255,0.6); padding: 0 14px 10px 14px; font-style: italic;'>{item['Explicacao']}</div>"

                    html_mapa += (
                        f"<tr>"
                        f"<td><div class='mapa-campo'>{label_campo}{numero_badge}</div>{explicacao_html}</td>"
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
                    st.download_button("📥 Baixar Mapa como CSV", data=csv, file_name=f"mapa_{nome_limpo}.csv", mime="text/csv", key=f"dl_mapa_csv_{nome}")
                with col2:
                    data_str_pdf = data_input.strftime('%d/%m/%Y')
                    pdf_bytes = gerar_pdf(nome, data_str_pdf, dados, titulo="Mapa Numerologico Cabalistico")
                    st.download_button("📄 Baixar Mapa como PDF", data=pdf_bytes, file_name=f"mapa_{nome_limpo}.pdf", mime="application/pdf", key=f"dl_mapa_pdf_{nome}")
