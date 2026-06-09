import streamlit as st
from contextlib import contextmanager

class PremiumCard:
    @staticmethod
    def render(title, content_html, badges_html="", action_html="", variant="default", key=None):
        """
        Renders a static HTML-based Premium Card with a consistent structure and design tokens.
        
        Args:
            title (str): Title of the card.
            content_html (str): Raw HTML content for the card body (e.g. details, text description).
            badges_html (str, optional): HTML badges shown next to the status. Defaults to "".
            action_html (str, optional): HTML action element (e.g. 'Analisar' button). Defaults to "".
            variant (str, optional): Visual modifier ('default', 'compact', 'interactive', 'selected'). Defaults to "default".
            key (str, optional): Optional identifier for elements inside.
        """
        # Map variant to CSS class
        class_map = {
            "default": "premium-card",
            "compact": "premium-card variant-compact",
            "interactive": "premium-card variant-interactive",
            "selected": "premium-card variant-selected"
        }
        card_class = class_map.get(variant, "premium-card")
        
        # Build header section
        header_part = ""
        if title or badges_html or action_html:
            header_part = (
                f'<div class="premium-card__header">'
                f'<h1 class="premium-card__title">{title}</h1>'
                f'<div style="display: flex; gap: 10px; align-items: center;">'
                f'{badges_html}'
                f'{action_html}'
                f'</div>'
                f'</div>'
            )
            
        # Build divider & body section
        body_part = ""
        if content_html:
            body_part = (
                f'<div class="premium-card__divider">'
                f'<div class="premium-card__reqs">{content_html}</div>'
                f'</div>'
            )
            
        card_html = f'<div class="{card_class}">{header_part}{body_part}</div>'
        st.markdown(card_html, unsafe_allow_html=True)



@contextmanager
def premium_card_container(variant="default", key=None):
    """
    A context manager to wrap native Streamlit widgets inside a styled Premium Card container.
    
    Usage:
        with premium_card_container(variant="interactive"):
            st.write("Form widgets or custom layouts")
            st.selectbox("Select option", ["A", "B"])
            
    Args:
        variant (str): Visual modifier ('default', 'compact', 'interactive', 'selected').
        key (str): Optional unique key.
    """
    st.markdown(f'<div class="premium-card-trigger" data-variant="{variant}"></div>', unsafe_allow_html=True)
    with st.container(border=True):
        yield
