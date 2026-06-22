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
    """Retorna o refresh_token do Supabase para ser persistido nos cookies."""
    if "supabase_session" in st.session_state:
        return st.session_state["supabase_session"].refresh_token
    return ""

def verify_auth_token(token):
    """Verifica se o token de sessão do cookie pode ser restaurado no Supabase Auth."""
    if not token or ":" in token:
        # Se for formato antigo com ":", invalida para forçar login correto com JWT
        return None
    from services.db_client import get_public_client
    client = get_public_client()
    try:
        res = client.auth.set_session("", token)
        if res.session:
            return res.session.user.email.split("@")[0]
    except Exception:
        pass
    return None

def lookup_email_by_username(username):
    """Busca o e-mail associado a um nome de usuário na tabela public.usuarios."""
    from services.db_client import get_supabase_admin
    try:
        admin_client = get_supabase_admin()
        res = admin_client.table("usuarios").select("email").eq("usuario", username).execute()
        if res.data:
            return res.data[0]["email"]
    except Exception:
        pass
    return None

def handle_login_success(res):
    """Processa o sucesso do login e configura as chaves de tenant no session_state."""
    from services.db_client import get_supabase_client
    st.session_state["supabase_session"] = res.session
    st.session_state["password_correct"] = True
    
    client = get_supabase_client()
    try:
        user_res = client.table("usuarios").select("tenant_id, direitos, usuario, empresa").eq("id", res.user.id).execute()
        if user_res.data:
            user_info = user_res.data[0]
            st.session_state["tenant_id"] = user_info["tenant_id"]
            st.session_state["user_rights"] = user_info["direitos"]
            st.session_state["logged_user"] = user_info["usuario"]
            
            # Carrega o plano do tenant correspondente
            tenant_res = client.table("tenants").select("tier, name").eq("id", user_info["tenant_id"]).execute()
            if tenant_res.data:
                st.session_state["tenant_tier"] = tenant_res.data[0]["tier"]
                st.session_state["user_company"] = user_info.get("empresa") or tenant_res.data[0].get("name") or "Mundo Kan"
            else:
                st.session_state["tenant_tier"] = "basic"
                st.session_state["user_company"] = user_info.get("empresa") or "Mundo Kan"
        else:
            # Fallback em caso do trigger não ter terminado de popular a tabela
            username = res.user.email.split("@")[0]
            st.session_state["logged_user"] = username
            st.session_state["tenant_id"] = "00000000-0000-0000-0000-000000000000" if res.user.email.endswith("@mundokan.com.br") else None
            st.session_state["tenant_tier"] = "premium" if res.user.email.endswith("@mundokan.com.br") else "basic"
            st.session_state["user_rights"] = "admin master" if username == "adminkan" else "Comum"
            st.session_state["user_company"] = "Mundo Kan" if res.user.email.endswith("@mundokan.com.br") else f"{username.capitalize()} Workspace"
    except Exception:
        username = res.user.email.split("@")[0]
        st.session_state["logged_user"] = username
        st.session_state["tenant_id"] = "00000000-0000-0000-0000-000000000000" if res.user.email.endswith("@mundokan.com.br") else None
        st.session_state["tenant_tier"] = "premium" if res.user.email.endswith("@mundokan.com.br") else "basic"
        st.session_state["user_rights"] = "admin master" if username == "adminkan" else "Comum"
        st.session_state["user_company"] = "Mundo Kan" if res.user.email.endswith("@mundokan.com.br") else f"{username.capitalize()} Workspace"
        
    st.session_state["write_auth_cookie"] = res.session.refresh_token
    return True, "Sucesso"

def login_user_auth(email, password):
    """Efetua o login direto no Supabase Auth."""
    from services.db_client import get_public_client
    client = get_public_client()
    try:
        res = client.auth.sign_in_with_password({"email": email, "password": password})
        if res.session:
            return handle_login_success(res)
    except Exception as e:
        return False, str(e)
    return False, "Usuário ou senha incorretos."

def run_login_with_onboarding(email, password, username):
    """Efetua o login e, caso o usuário não exista no Supabase Auth, cria-o automaticamente (Migração)."""
    from services.db_client import get_public_client, get_supabase_admin
    client = get_public_client()
    try:
        # Tenta login direto
        res = client.auth.sign_in_with_password({"email": email, "password": password})
        return handle_login_success(res)
    except Exception as e:
        err_msg = str(e).lower()
        # Se o erro indicar credenciais inválidas ou usuário inexistente, tenta criar no Supabase Auth
        if any(keyword in err_msg for keyword in ["invalid login credentials", "user not found", "cannot find", "400"]):
            try:
                admin_client = get_supabase_admin()
                # Cria usuário no Supabase Auth ignorando confirmação por e-mail
                admin_client.auth.admin.create_user({
                    "email": email,
                    "password": password,
                    "email_confirm": True,
                    "user_metadata": {
                        "full_name": username.capitalize()
                    }
                })
                # Tenta o login novamente agora que o usuário foi migrado
                res = client.auth.sign_in_with_password({"email": email, "password": password})
                if res.session:
                    return handle_login_success(res)
            except Exception as ex:
                return False, f"Falha na migração automática do usuário: {ex}"
        return False, str(e)

def restore_session(token):
    """Restaura a sessão Supabase usando o refresh token persistido."""
    from services.db_client import get_public_client
    if not token or ":" in token:
        return False
    client = get_public_client()
    try:
        res = client.auth.set_session("", token)
        if res.session:
            success, _ = handle_login_success(res)
            return success
    except Exception:
        pass
    return False

def check_password():
    # 1. Verificar auto-login via query params
    if "auto_login" in st.query_params:
        token = st.query_params["auto_login"]
        # Limpa o query param para evitar loops
        del st.query_params["auto_login"]
        
        if restore_session(token):
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.session_state["auto_login_failed"] = True
            st.rerun()

    def password_entered():
        user = st.session_state.get("username", "").strip()
        pwd = st.session_state.get("password", "")
        
        success = False
        # Caso seja login legado
        if user in USUARIOS and USUARIOS[user] == pwd:
            email = f"{user}@mundokan.com.br"
            success, msg = run_login_with_onboarding(email, pwd, user)
        else:
            email = user
            if "@" not in email:
                email = lookup_email_by_username(user) or f"{user}@mundokan.com.br"
            success, msg = login_user_auth(email, pwd)
            
        if success:
            st.session_state["password_correct"] = True
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
        # Se houve logout, limpa os cookies
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

        # Tenta auto-login via localStorage ou cookie
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
                st.text_input("Usuário ou E-mail", key="username")
                st.text_input("Senha", type="password", key="password")
                st.form_submit_button("Entrar", on_click=password_entered)
            if st.session_state.get("password_correct") == False:
                st.error("Usuário/E-mail ou senha incorretos. Tente novamente.")
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
