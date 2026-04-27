import streamlit as st
import time
from core_ai.support_agent import chiedi_all_assistente

def draw_sidebar(nome_azienda="RetailPulse 📈"):
    """Disegna la sidebar. Se passato, usa il nome dell'azienda."""
    
    with st.sidebar:
        st.title(f"{nome_azienda}")
        st.markdown("---")
        
    
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
                with st.spinner("Sto guardando nel magazzino... 📦"):
                    
                    mio_id_azienda = st.session_state.azienda_id
                    
                    response = chiedi_all_assistente(prompt, mio_id_azienda)
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})