import streamlit as st
import time

def draw_sidebar(nome_azienda="RetailPulse 📈"):
    """Disegna la sidebar. Se passato, usa il nome dell'azienda."""
    
    with st.sidebar:
        st.title(f"{nome_azienda}")
        st.markdown("---")
        
        # --- SEZIONE CHAT AI ---
        st.subheader("🤖 Assistente di Supporto")
        
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Ciao! Sono l'agente di supporto. Chiedimi pure informazioni sul tuo magazzino."}
            ]

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Scrivi qui..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Sto pensando..."):
                    time.sleep(1) 
                    response = "Ancora non sono collegato ad Agno, ma presto lo sarò!"
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})