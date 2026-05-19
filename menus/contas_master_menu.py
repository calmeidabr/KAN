import streamlit as st
from menus.base_menu import BaseMenu

class ContasMasterMenu(BaseMenu):
    def render(self):
        st.title("Contas Master")
        st.info("Gerencie os acessos administrativos e permissões do sistema.")
        
        if "contas_master_data" not in st.session_state:
            st.session_state.contas_master_data = [
                {"usuario": "adminkan", "senha": "K@nAdmin#2026*", "tipo": "Administrador Master", "status": "Ativo"},
                {"usuario": "cristiano", "senha": "password123", "tipo": "Administrador Empresa", "status": "Ativo"},
                {"usuario": "maria", "senha": "password456", "tipo": "Usuário", "status": "Ativo"}
            ]
        
        for i, conta in enumerate(st.session_state.contas_master_data):
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                
                with col1:
                    st.write(f"**Usuário:** {conta['usuario']}")
                    st.write(f"**Tipo:** {conta['tipo']}")
                
                with col2:
                    ver_senha = st.checkbox("Ver Senha", key=f"ver_{i}")
                    if ver_senha:
                        st.text_input("Senha", value=conta['senha'], key=f"senha_{i}", disabled=(conta['usuario'] == "adminkan"))
                    else:
                        st.text_input("Senha", value="********", key=f"senha_hide_{i}", disabled=True)
                
                with col3:
                    n_tipo = st.selectbox("Direitos", ["Administrador Master", "Administrador Empresa", "Usuário"], 
                                         index=["Administrador Master", "Administrador Empresa", "Usuário"].index(conta['tipo']),
                                         key=f"tipo_{i}", disabled=(conta['usuario'] == "adminkan"))
                
                with col4:
                    status_opt = ["Ativo", "Desabilitado"]
                    n_status = st.selectbox("Status", status_opt, index=status_opt.index(conta['status']), 
                                           key=f"status_{i}", disabled=(conta['usuario'] == "adminkan"))
                    if st.button("Ver Logs", key=f"log_{i}"):
                        st.toast(f"Gerando logs para {conta['usuario']}...")
                
                if conta['usuario'] != "adminkan":
                    if st.button("Salvar Alterações", key=f"save_{i}"):
                        st.session_state.contas_master_data[i]['tipo'] = n_tipo
                        st.session_state.contas_master_data[i]['status'] = n_status
                        st.success(f"Alterações para {conta['usuario']} salvas!")
