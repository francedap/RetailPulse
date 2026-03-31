import streamlit as st
import time

def draw_sidebar():
    """Disegna la sidebar condivisa con la navigazione e la chat AI."""
    
    with st.sidebar:
        st.title("RetailPulse 📈")
        st.caption("Il tuo assistente AI per il Reselling")
        st.markdown("---")
        
        # --- SEZIONE CHAT AI (Suggerimento Professore) ---
        st.subheader("🤖 Assistente di Supporto")
        
        # Inizializza lo stato della chat se non esiste
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Ciao! Sono l'agente di supporto. Chiedimi pure informazioni sul tuo magazzino o strategie di mercato."}
            ]

        # Visualizza i messaggi precedenti
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accetta l'input dell'utente
        if prompt := st.chat_input("Scrivi qui..."):
            # Aggiungi messaggio utente allo stato
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # --- QUI ANDRÀ L'INTEGRAZIONE CON AGNO (Support Agent) ---
            # Per ora simuliamo la risposta
            with st.chat_message("assistant"):
                with st.spinner("Sto pensando..."):
                    time.sleep(1) # Simula elaborazione agente
                    
                    # Risposta simulata basata su parole chiave
                    response = "Ancora non sono collegato al mio cervello Agno, ma quando lo sarò, analizzerò i tuoi dati per risponderti!"
                    if "scarpe" in prompt.lower():
                        response = "Il mercato delle scarpe è volatile oggi. L'agente Mercato suggerisce cautela sulle Jordan."
                    
                    st.markdown(response)
                    # Aggiungi risposta assistente allo stato
                    st.session_state.messages.append({"role": "assistant", "content": response})