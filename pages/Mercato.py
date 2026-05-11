import streamlit as st
import pandas as pd
from components.sidebar import draw_sidebar
from utils.db_manager import get_prodotti_raw

# Importiamo la nostra nuova funzione Orchestratore e i Sotto-Agenti storici
from core_ai.market_explorer import (
    analizza_opportunita_prodotto, 
    analizza_trend_categoria, 
    genera_report_strategico_mercato,
    interroga_orchestratore
)

# --- CONTROLLO SICUREZZA ACCESSI ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

draw_sidebar(st.session_state.get('nome_azienda', 'La Tua Azienda'))

st.title("📈 Analisi di Mercato (Orchestratore IA)")
st.write("Parla in chat con il tuo Direttore Strategico. Ti guiderà nelle scelte e chiamerà gli analisti specializzati solo al momento del bisogno.")
st.markdown("---")

df_magazzino = get_prodotti_raw(st.session_state.azienda_id)

# --- INIZIALIZZAZIONE CRONOLOGIA CHAT ---
if "mercato_chat" not in st.session_state:
    st.session_state.mercato_chat = [
        {
            "role": "assistant", 
            "content": "Benvenuto! 👋 Sono il tuo Orchestratore di Mercato. Posso aiutarti a esplorare un nuovo prodotto, analizzare i trend di una categoria o generare un report strategico globale. Come procediamo?", 
            "bottoni": ["Analisi Prodotto", "Trend Categoria", "Report Strategico"]
        }
    ]

# 1. MOSTRA TUTTI I MESSAGGI PRECEDENTI
for msg in st.session_state.mercato_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # (Non mostriamo i bottoni vecchi per non creare confusione visiva)

ultimo_msg = st.session_state.mercato_chat[-1]

# 2. GESTIONE SOTTO-AGENTI (Interfacce Dinamiche)
# Se abbiamo attivato un Sotto-Agente specifico, mostriamo l'input direttamente nella chat!
if st.session_state.get("azione_attiva") == "Analisi Prodotto":
    with st.chat_message("assistant"):
        st.info("🛠️ **Sotto-Agente Attivato: Analista Singoli Prodotti**")
        prodotto_da_cercare = st.text_input("Digita il nome del prodotto da analizzare:")
        
        if st.button("Avvia Analisi ⚡", type="primary"):
            with st.spinner(f"Analizzando '{prodotto_da_cercare}' sul mercato..."):
                risultato = analizza_opportunita_prodotto(prodotto_da_cercare)
                # Salviamo il risultato nella chat e chiudiamo l'input
                st.session_state.mercato_chat.append({"role": "assistant", "content": risultato, "bottoni": []})
                st.session_state.azione_attiva = ""
                st.rerun()

elif st.session_state.get("azione_attiva") == "Trend Categoria":
    with st.chat_message("assistant"):
        st.info("🛠️ **Sotto-Agente Attivato: Analista Trend Globali**")
        categorie = df_magazzino['categoria'].unique().tolist() if not df_magazzino.empty else ["Elettronica", "Abbigliamento", "Sneakers"]
        cat_scelta = st.selectbox("Seleziona la categoria da analizzare:", categorie)
        
        if st.button("Analizza Trend 📊", type="primary"):
            with st.spinner(f"Raccogliendo dati per il settore '{cat_scelta}'..."):
                risultato = analizza_trend_categoria(cat_scelta)
                st.session_state.mercato_chat.append({"role": "assistant", "content": risultato, "bottoni": []})
                st.session_state.azione_attiva = ""
                st.rerun()

# 3. MOSTRA BOTTONI DINAMICI (Solo per l'ultimo messaggio dell'Orchestratore)
elif ultimo_msg["role"] == "assistant" and ultimo_msg.get("bottoni"):
    st.write("🎯 **Scegli un'azione suggerita o scrivimi qui sotto:**")
    
    # Crea tante colonne quanti sono i bottoni restituiti dal JSON
    cols = st.columns(len(ultimo_msg["bottoni"]))
    
    for i, btn_text in enumerate(ultimo_msg["bottoni"]):
        if cols[i].button(btn_text, use_container_width=True):
            # Aggiungiamo la scelta alla chat come se l'avesse scritta l'utente
            st.session_state.mercato_chat.append({"role": "user", "content": btn_text})
            
            # --- ROUTER SOTTO-AGENTI ---
            if "Report Strategico" in btn_text:
                with st.spinner("Il Sotto-Agente CSO sta incrociando i dati... ⏳"):
                    risultato = genera_report_strategico_mercato(df_magazzino)
                    st.session_state.mercato_chat.append({"role": "assistant", "content": risultato, "bottoni": []})
            elif "Analisi Prodotto" in btn_text:
                st.session_state.azione_attiva = "Analisi Prodotto"
            elif "Trend Categoria" in btn_text:
                st.session_state.azione_attiva = "Trend Categoria"
            else:
                # Se clicca un bottone generico, lo passiamo all'Orchestratore
                st.session_state.elabora_prompt = btn_text
            
            st.rerun()

# 4. GESTIONE INPUT TESTUALE LIBERO (La Chat vera e propria)
if prompt := st.chat_input("Chiedi consiglio al tuo Orchestratore..."):
    st.session_state.mercato_chat.append({"role": "user", "content": prompt})
    st.session_state.elabora_prompt = prompt
    st.rerun()

# 5. ELABORAZIONE INTELLIGENZA DELL'ORCHESTRATORE
if st.session_state.get("elabora_prompt"):
    prompt_da_elaborare = st.session_state.elabora_prompt
    st.session_state.elabora_prompt = "" # Resettiamo la variabile
    
    with st.chat_message("assistant"):
        with st.spinner("L'Orchestratore sta elaborando la tua richiesta... 🧠"):
            # Chiamiamo la funzione che restituisce il JSON
            risposta_json = interroga_orchestratore(prompt_da_elaborare, df_magazzino)
            
            # Estraiamo i dati in modo sicuro
            messaggio = risposta_json.get("messaggio", "Ecco alcune opzioni per te:")
            bottoni_dinamici = risposta_json.get("bottoni", [])
            
            # Salviamo tutto in cronologia
            st.session_state.mercato_chat.append({
                "role": "assistant", 
                "content": messaggio, 
                "bottoni": bottoni_dinamici
            })
            st.rerun()