import streamlit as st
from menus.base_menu import BaseMenu
from models.database import fetch_banners, fetch_asset_b64, carregar_todos_clientes, carregar_empresas
from utils.helpers import get_base64_of_bin_file
from services.auth import header_img

class HomeMenu(BaseMenu):
    def render(self):
        if 'carousel_index' not in st.session_state:
            st.session_state.carousel_index = 0
        
        db_banners = fetch_banners()
        clientes = carregar_todos_clientes()
        empresas = carregar_empresas()
        
        total_clientes = len(clientes) if clientes else 0
        total_empresas = len(empresas) if empresas else 1

        st.markdown("""
        <style>
        .kpi-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }
        .kpi-card {
            background: rgba(255,255,255,0.04);
            border-left: 4px solid #F18617;
            border-radius: 12px;
            padding: 18px 22px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            background: rgba(255,255,255,0.07);
        }
        .kpi-title {
            font-size: 0.85em;
            text-transform: uppercase;
            color: rgba(255,255,255,0.6);
            margin-bottom: 5px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }
        .kpi-value {
            font-size: 2.2em;
            font-weight: 900;
            color: #FFFFFF;
            line-height: 1.1;
        }
        .kpi-sub {
            font-size: 0.75em;
            color: #39ff14;
            margin-top: 5px;
            font-weight: 600;
        }
        </style>
        
        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-title">Perfis Cadastrados</div>
                <div class="kpi-value">""" + str(total_clientes) + """</div>
                <div class="kpi-sub">● Banco Sincronizado</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Empresas / Grupos</div>
                <div class="kpi-value">""" + str(total_empresas) + """</div>
                <div class="kpi-sub">● Ativas no Sistema</div>
            </div>
            <div class="kpi-card" style="border-left-color: #00d2ff;">
                <div class="kpi-title">Status do Banco</div>
                <div class="kpi-value" style="font-size: 1.6em; padding-top: 5px;">Online</div>
                <div class="kpi-sub" style="color: #00d2ff;">● Supabase Conectado</div>
            </div>
            <div class="kpi-card" style="border-left-color: #39ff14;">
                <div class="kpi-title">Motor IA</div>
                <div class="kpi-value" style="font-size: 1.6em; padding-top: 5px;">Gemini 2.5</div>
                <div class="kpi-sub">● Flash Ativo</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if db_banners:
            banners_list = db_banners
            current_b = banners_list[st.session_state.carousel_index % len(banners_list)]
            
            img_b64 = ""
            asset_id = current_b.get('asset_id')
            if asset_id:
                img_b64 = fetch_asset_b64(asset_id)
            
            if not img_b64:
                local_map = {1: "banner1.png", 2: "banner2.png", 3: "banner3.png"}
                img_b64 = get_base64_of_bin_file(local_map.get(current_b['id'], "banner1.png"))
            
            title = current_b.get('title', '')
            subtitle = current_b.get('subtitle', '')
            accent = current_b.get('accent_color', '#F18617')
        else:
            banner1_path = "banner1.png"
            banner2_path = "banner2.png"
            banner3_path = "banner3.png"
            
            if 'banners_data' not in st.session_state:
                st.session_state.banners_data = [
                    {"id": 1, "title": "Diagnóstico Inteligente", "subtitle": "Análise comportamental profunda e instantânea.", "accent": "#F18617", "img_path": banner1_path},
                    {"id": 2, "title": "Gestão de Talentos", "subtitle": "Dados precisos para equipes de alta performance.", "accent": "#00d2ff", "img_path": banner2_path},
                    {"id": 3, "title": "Inovação Humana", "subtitle": "A inteligência por trás do comportamento.", "accent": "#39ff14", "img_path": banner3_path}
                ]
            
            current_b = st.session_state.banners_data[st.session_state.carousel_index % len(st.session_state.banners_data)]
            if current_b.get('b64_custom'):
                img_b64 = current_b['b64_custom']
            else:
                img_b64 = get_base64_of_bin_file(current_b.get('img_path', ""))
                
            title = current_b['title']
            subtitle = current_b['subtitle']
            accent = current_b['accent']

        st.markdown(f"""
        <style>
        .main-hero {{
            position: relative;
            width: 100%;
            height: 400px;
            background-image: linear-gradient(90deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.4) 50%, rgba(0,0,0,0) 100%), url('data:image/png;base64,{img_b64}');
            background-size: cover;
            background-position: center;
            border-radius: 30px;
            overflow: hidden;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            padding: 60px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.4);
            transition: all 0.8s ease;
        }}
        .hero-content {{
            position: relative;
            z-index: 10;
            max-width: 650px;
        }}
        .hero-label {{
            background-color: {accent};
            color: black;
            padding: 6px 18px;
            border-radius: 20px;
            font-weight: 800;
            font-size: 0.85em;
            text-transform: uppercase;
            display: inline-block;
            margin-bottom: 18px;
            box-shadow: 0 4px 15px rgba(241,134,23,0.4);
        }}
        .hero-title {{
            font-size: 3.8em;
            font-weight: 900;
            color: white;
            line-height: 1.1;
            letter-spacing: -1px;
            margin-bottom: 12px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.8);
        }}
        .hero-subtitle {{
            font-size: 1.35em;
            color: rgba(255,255,255,0.85);
            line-height: 1.4;
            text-shadow: 0 2px 10px rgba(0,0,0,0.6);
        }}
        </style>
        
        <div class='main-hero'>
            <div class='hero-content'>
                <div class='hero-label'>Mundo KAN</div>
                <div class='hero-title'>{title}</div>
                <div class='hero-subtitle'>{subtitle}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])
        with col_nav1:
            if header_img != "◇":
                st.image(header_img, width=80)
            else:
                st.markdown("<h4 style='margin:10px 0 0 0; color: #F18617;'>◇ KAN</h4>", unsafe_allow_html=True)
                
        with col_nav2:
            c1, c2, c3 = st.columns([1, 1, 1])
            num_banners = len(db_banners) if db_banners else len(st.session_state.banners_data)
            with c1:
                if st.button("❮", key="prev_home"):
                    st.session_state.carousel_index = (st.session_state.carousel_index - 1) % num_banners
                    st.rerun()
            with c2:
                st.markdown(f"<p style='text-align: center; margin-top: 10px; font-weight: bold; opacity: 0.6;'>{st.session_state.carousel_index + 1} / {num_banners}</p>", unsafe_allow_html=True)
            with c3:
                if st.button("❯", key="next_home"):
                    st.session_state.carousel_index = (st.session_state.carousel_index + 1) % num_banners
                    st.rerun()

        st.markdown("<br><hr style='border-color: rgba(255,255,255,0.1); margin: 30px 0;'><br>", unsafe_allow_html=True)
        st.markdown("<h3>Acesso Rápido</h3><p style='color: rgba(255,255,255,0.6); margin-bottom: 25px;'>Navegue diretamente pelos módulos principais do sistema</p>", unsafe_allow_html=True)

        col_q1, col_q2 = st.columns(2)
        with col_q1:
            with st.container(border=True):
                st.markdown("<h3 style='margin-bottom:10px;'>⎔ Diagnósticos</h3><p style='color: rgba(255,255,255,0.7); font-size: 0.95em; min-height: 50px;'>Avaliação comportamental corporativa instantânea para tomada de decisão.</p>", unsafe_allow_html=True)
                if st.button("Acessar Diagnósticos ➔", key="btn_qa_diag", use_container_width=True, type="primary"):
                    self.app.navigate("Diagnósticos")
        with col_q2:
            with st.container(border=True):
                st.markdown("<h3 style='margin-bottom:10px;'>○ Talentos & OCR</h3><p style='color: rgba(255,255,255,0.7); font-size: 0.95em; min-height: 50px;'>Cadastre novos membros manualmente ou via leitura de documento por IA.</p>", unsafe_allow_html=True)
                if st.button("Cadastrar Talentos ➔", key="btn_qa_tal", use_container_width=True, type="primary"):
                    self.app.navigate("Talentos")
