import streamlit as st

# 1. Configurazione globale della pagina (deve essere la prima chiamata Streamlit)
st.set_page_config(
    page_title="RetailPulse - AI Copilot",
    page_icon="📈",
    layout="wide", # Usa tutto lo spazio in larghezza
    initial_sidebar_state="expanded"
)

# Messaggio temporaneo mentre avviene il reindirizzamento
st.write("Caricamento in corso...")

# 2. Reindirizzamento automatico alla Home Page nella cartella pages/
st.switch_page("pages/HomePage.py")