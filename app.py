import streamlit as st
from utils.db_manager import init_db, register_user, verify_login

# 1. Configurazione globale (DEVE essere la prima istruzione)
st.set_page_config(page_title="RetailPulse Accesso", page_icon="🔒", layout="centered")

# Inizializza le tabelle del database se non esistono
init_db()

# --- GESTIONE DELLO STATO DELLA SESSIONE ---
# Queste variabili ricorderanno chi è l'utente mentre naviga tra le pagine
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'azienda_id' not in st.session_state:
    st.session_state.azienda_id = None
if 'nickname' not in st.session_state:
    st.session_state.nickname = None


def show_auth_page():
    """Mostra l'interfaccia con le tab per Login e Registrazione."""
    st.title("Benvenuto in RetailPulse 📈")
    st.write("Il tuo co-pilota IA per l'analisi del magazzino e del mercato.")
    st.markdown("---")
    
    # Crea due schede navigabili
    tab_login, tab_register = st.tabs(["🔑 Accedi", "📝 Crea Account"])
    
    # --- SCHEDA LOGIN ---
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Entra", width='stretch')
            
            if submit_login:
                user_data = verify_login(email, password)
                if user_data:
                    # Salva i dati nella sessione
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_data[0]
                    st.session_state.azienda_id = user_data[1]
                    st.session_state.nickname = user_data[2]
                    
                    st.success(f"Accesso eseguito! Bentornato, {user_data[2]}.")
                    st.rerun() # Ricarica l'app per far scattare il reindirizzamento
                else:
                    st.error("Email o password non corretti.")

    # --- SCHEDA REGISTRAZIONE ---
    with tab_register:
        with st.form("register_form"):
            new_nick = st.text_input("Nickname (es. Mario Rossi)")
            new_email = st.text_input("Email aziendale")
            new_password = st.text_input("Password", type="password")
            new_azienda = st.text_input("Nome della tua Azienda (es. Mario Sneakers Srl)")
            
            submit_register = st.form_submit_button("Registrati", width='stretch')
            
            if submit_register:
                if new_nick and new_email and new_password and new_azienda:
                    success = register_user(new_nick, new_email, new_password, new_azienda)
                    if success:
                        st.success("Account e Azienda creati con successo! Ora puoi accedere dalla scheda 'Accedi'.")
                    else:
                        st.error("Attenzione: Questa email è già in uso.")
                else:
                    st.warning("Per favore, compila tutti i campi richiesti.")


# --- CONTROLLORE DI ACCESSO ---
if not st.session_state.logged_in:
    show_auth_page()
else:
    # Se l'utente è loggato, lo reindirizziamo istantaneamente alla Home Page
    st.switch_page("pages/HomePage.py")
