import streamlit as st
import os
import hmac
import hashlib
import urllib.parse

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

def generate_auth_token(username):
    try:
        secret_key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
    except Exception:
        secret_key = "kan_secret_fallback_key_2026"
    signature = hmac.new(secret_key.encode(), username.encode(), hashlib.sha256).hexdigest()
    return f"{username}:{signature}"

def verify_auth_token(token):
    if not token or ":" not in token:
        return None
    try:
        token = urllib.parse.unquote(token)
        username, signature = token.split(":", 1)
        expected_token = generate_auth_token(username)
        if hmac.compare_digest(f"{username}:{signature}", expected_token):
            return username
    except Exception:
        pass
    return None

def check_password():
    # 1. Verificar se há pedido de auto-login seguro via query params
    if "auto_login" in st.query_params:
        token = st.query_params["auto_login"]
        username = verify_auth_token(token)
        if username and username in USUARIOS:
            st.session_state["password_correct"] = True
            st.session_state["logged_user"] = username
            # Limpa o query param e recarrega
            del st.query_params["auto_login"]
            st.rerun()
        else:
            # Token inválido ou expirado, marca falha para evitar loop e recarrega limpo
            st.session_state["auto_login_failed"] = True
            if "auto_login" in st.query_params:
                del st.query_params["auto_login"]
            st.rerun()

    def password_entered():
        user = st.session_state.get("username", "")
        pwd = st.session_state.get("password", "")
        if user in USUARIOS and USUARIOS[user] == pwd:
            st.session_state["password_correct"] = True
            st.session_state["logged_user"] = user
            st.session_state["write_auth_cookie"] = generate_auth_token(user)
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
        # Se houve logout, limpa o cookie e o localStorage
        if st.session_state.get("clear_auth_cookie"):
            st.markdown("""
            <div style="display:none;">
            <script>
                (function() {
                    try {
                        localStorage.removeItem("kan_auth_token");
                    } catch(e) {}
                    const name = "kan_auth_token";
                    const expires = "; expires=Thu, 01 Jan 1970 00:00:00 UTC";
                    const cookieStr = name + "=" + expires + "; path=/; SameSite=Lax";
                    document.cookie = cookieStr;
                    try {
                        if (window.parent && window.parent.document) {
                            window.parent.document.cookie = cookieStr;
                        }
                    } catch(e) {}
                })();
            </script>
            </div>
            """, unsafe_allow_html=True)
            del st.session_state["clear_auth_cookie"]

        # Tenta auto-login via localStorage ou cookie se ainda não tentou/falhou nesta sessão
        if not st.session_state.get("auto_login_failed") and "auto_login" not in st.query_params:
            st.markdown("""
            <div style="display:none;">
            <script>
                (function() {
                    let token = "";
                    try {
                        token = localStorage.getItem("kan_auth_token") || "";
                    } catch(e) {}
                    
                    if (!token) {
                        const name = "kan_auth_token=";
                        try {
                            if (window.parent && window.parent.document) {
                                const decodedCookie = decodeURIComponent(window.parent.document.cookie);
                                const ca = decodedCookie.split(';');
                                for(let i = 0; i < ca.length; i++) {
                                    let c = ca[i].trim();
                                    if (c.indexOf(name) === 0) {
                                        token = c.substring(name.length, c.length);
                                        break;
                                    }
                                }
                            }
                        } catch(e) {}
                        if (!token) {
                            try {
                                const decodedCookie = decodeURIComponent(document.cookie);
                                const ca = decodedCookie.split(';');
                                for(let i = 0; i < ca.length; i++) {
                                    let c = ca[i].trim();
                                    if (c.indexOf(name) === 0) {
                                        token = c.substring(name.length, c.length);
                                        break;
                                    }
                                }
                            } catch(e) {}
                        }
                    }
                    if (token) {
                        const urlParams = new URLSearchParams(window.location.search);
                        if (!urlParams.has('auto_login')) {
                            urlParams.set('auto_login', token);
                            window.location.search = urlParams.toString();
                        }
                    }
                })();
            </script>
            </div>
            """, unsafe_allow_html=True)

        render_login_header()
        col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
        with col_l2:
            with st.form("login_form", border=False):
                st.text_input("Usuário", key="username")
                st.text_input("Senha", type="password", key="password")
                st.form_submit_button("Entrar", on_click=password_entered)
            if st.session_state.get("password_correct") == False:
                st.error("Usuário ou senha incorretos. Tente novamente.")
        return False
    else:
        # Se logado com sucesso e precisa persistir a sessão
        if "write_auth_cookie" in st.session_state:
            token = st.session_state["write_auth_cookie"]
            st.markdown(f"""
            <div style="display:none;">
            <script>
                (function() {{
                    const name = "kan_auth_token";
                    const value = "{token}";
                    try {{
                        localStorage.setItem(name, value);
                    }} catch(e) {{}}
                    
                    const days = 7;
                    const date = new Date();
                    date.setTime(date.getTime() + (days*24*60*60*1000));
                    const expires = "; expires=" + date.toUTCString();
                    const isHttps = window.location.protocol === "https:";
                    const secureFlag = isHttps ? "; Secure" : "";
                    
                    const cookieStr = name + "=" + value + expires + "; path=/; SameSite=Lax" + secureFlag;
                    document.cookie = cookieStr;
                    try {{
                        if (window.parent && window.parent.document) {{
                            window.parent.document.cookie = cookieStr;
                        }}
                    }} catch(e) {{}}
                }})();
            </script>
            </div>
            """, unsafe_allow_html=True)
            del st.session_state["write_auth_cookie"]
        return True
