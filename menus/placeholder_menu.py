import streamlit as st
from menus.base_menu import BaseMenu

class PlaceholderMenu(BaseMenu):
    def render(self, title="Em Desenvolvimento", message="Módulo em desenvolvimento."):
        st.title(title)
        st.info(message)
