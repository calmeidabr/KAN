import streamlit as st
from PIL import Image
import os

USUARIOS = {
    "admin": "admin123",
    "adminkan": "K@nAdmin#2026*",
    "cristiano": "kan2026",
    "maria": "maria2026"
}

try:
    img_path = os.path.join("images", "kan_logo_lar.png")
    if os.path.exists(img_path):
        header_img = img_path
    else:
        header_img = "◇"
except Exception:
    header_img = "◇"

def get_header_image():
    return header_img

def check_password():
    def password_entered():
        user = st.session_state.get("username", "")
        pwd = st.session_state.get("password", "")
        if user in USUARIOS and USUARIOS[user] == pwd:
            st.session_state["password_correct"] = True
            st.session_state["logged_user"] = user
            if "password" in st.session_state:
                del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    def render_login_header():
        if header_img != "◇":
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.image(header_img, use_container_width=True)
        st.markdown("<h4 style='text-align: center;'>Diagnóstico comportamental instantâneo. Sem testes. Sem manipulação.</h4>", unsafe_allow_html=True)
        st.write("")

    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        render_login_header()
        col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
        with col_l2:
            st.text_input("Usuário", key="username")
            st.text_input("Senha", type="password", key="password")
            st.button("Entrar", on_click=password_entered)
            if st.session_state.get("password_correct") == False:
                st.error("Usuário ou senha incorretos. Tente novamente.")
        return False
    else:
        return True
