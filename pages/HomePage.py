import streamlit as st
import pandas as pd
import numpy as np
from core_ai.strategic_advisor_agent import genera_sintesi_strategica
from core_ai.inventory_analyst import analizza_punti_deboli
from utils.db_manager import get_all_price_updates
from core_ai.cerca_nuovo_prezzo_agent import crea_agente_prezzi
from utils.db_manager import update_prezzo_prodotto, estrai_prezzo_da_testo, get_prodotti_raw
from core_ai.strategic_advisor_agent import genera_sintesi_strategica, interroga_orchestratore_home
from utils.db_manager import get_all_price_updates, get_prodotti_raw, update_prezzo_prodotto, log_price_update, estrai_prezzo_da_testo
from core_ai.inventory_analyst import analizza_punti_deboli
from core_ai.cerca_nuovo_prezzo_agent import crea_agente_prezzi
            
            

# Importiamo la sidebar e le funzioni del DB
from components.sidebar import draw_sidebar
from utils.db_manager import get_dati_magazzino, get_nome_azienda,log_price_update
# --- CONTROLLO SICUREZZA ACCESSI ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

# Variabili di stato perAI
if 'ai_scan_active' not in st.session_state:
    st.session_state.ai_scan_active = False
if 'market_trend_active' not in st.session_state:
    st.session_state.market_trend_active = False

if 'nome_azienda' not in st.session_state:
    st.session_state.nome_azienda = get_nome_azienda(st.session_state.azienda_id)

nome_azienda = st.session_state.nome_azienda
draw_sidebar(nome_azienda)


dati_magazzino = get_dati_magazzino(st.session_state.azienda_id)

if not dati_magazzino.empty:
    dati_magazzino['Valore_Totale_Mercato'] = dati_magazzino['Prezzo_Mercato'] * dati_magazzino['Quantita']
    dati_magazzino['Margine_Unitario'] = dati_magazzino['Prezzo_Mercato'] - dati_magazzino['Prezzo_Acquisto']
    dati_magazzino['Margine_Totale_Latente'] = dati_magazzino['Margine_Unitario'] * dati_magazzino['Quantita']

    total_value = dati_magazzino['Valore_Totale_Mercato'].sum()
    total_margin = dati_magazzino['Margine_Totale_Latente'].sum()
    prodotti_in_perdita = dati_magazzino[dati_magazzino['Margine_Unitario'] < 0].shape[0]
else:
    total_value = 0
    total_margin = 0
    prodotti_in_perdita = 0


st.title(f"Dashboard: {nome_azienda}")
st.write(f"Benvenuto **{st.session_state.nickname}**. Qui hai una panoramica intelligente della tua attività.")
st.markdown("---")


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Valore Totale Magazzino", value=f"€ {total_value:,.2f}", help="Valore attuale se vendessi tutto.")
with col2:
    st.metric(label="Margine Totale Latente", value=f"€ {total_margin:,.2f}")
with col3:
    st.metric(label="Articoli Critici (In Perdita)", value=prodotti_in_perdita, delta_color="inverse")

st.markdown("---")

# --- IMPORT NECESSARI AGGIUNTIVI (Assicurati che siano in cima al file) ---
# from core_ai.strategic_advisor_agent import genera_sintesi_strategica, interroga_orchestratore_home
# from utils.db_manager import get_all_price_updates, get_prodotti_raw, update_prezzo_prodotto, log_price_update, estrai_prezzo_da_testo
# from core_ai.inventory_analyst import analizza_punti_deboli
# from core_ai.cerca_nuovo_prezzo_agent import crea_agente_prezzi

st.subheader("🤖 Il Tuo Orchestratore Aziendale")

# --- 1. INIZIALIZZAZIONE CHAT E BOTTONI BASE ---
if "home_chat" not in st.session_state:
    st.session_state.home_chat = [
        {
            "role": "assistant",
            "content": "Benvenuto nella tua Dashboard! 👋 Sono l'Orchestratore principale. Come posso aiutarti oggi a massimizzare i profitti?",
            "bottoni": ["Sintesi Strategica", "Scansione Punti Deboli", "Trend Prezzi", "Aggiorna Prezzi"]
        }
    ]

# --- 2. RENDERIZZAZIONE DELLA CRONOLOGIA ---
for msg in st.session_state.home_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Se c'è un grafico salvato in questo messaggio, mostralo!
        if "chart_data" in msg:
            st.line_chart(msg["chart_data"])
            st.caption("Grafico: Evoluzione storica dei prezzi.")

ultimo_msg = st.session_state.home_chat[-1]

# --- 3. ESECUZIONE DELLE AZIONI DEI BOTTONI FISSI ---
if st.session_state.get("azione_home_attiva"):
    azione = st.session_state.azione_home_attiva
    st.session_state.azione_home_attiva = "" # Resetta l'azione per non ripeterla all'infinito
    
    with st.chat_message("assistant"):
        
        if azione == "Sintesi Strategica":
            with st.spinner("Analisi dei KPI in corso... 🧠"):
                testo = genera_sintesi_strategica(total_value, total_margin, prodotti_in_perdita)
                st.session_state.home_chat.append({"role": "assistant", "content": testo, "bottoni": []})
                st.rerun()
                
        elif azione == "Scansione Punti Deboli":
            with st.spinner("Ricerca dei colli di bottiglia... 🕵️‍♂️"):
                testo = analizza_punti_deboli(dati_magazzino)
                st.session_state.home_chat.append({"role": "assistant", "content": testo, "bottoni": []})
                st.rerun()
                
        elif azione == "Trend Prezzi":
            with st.spinner("Generazione grafico andamento mercato... 📈"):
                df_trend = get_all_price_updates(st.session_state.azienda_id)
                if df_trend.empty:
                    testo = "Non ci sono aggiornamenti di prezzo registrati. Esegui prima un 'Aggiorna Prezzi'."
                    st.session_state.home_chat.append({"role": "assistant", "content": testo, "bottoni": []})
                else:
                    # Prepariamo i dati per il grafico
                    chart_data = df_trend.pivot_table(index='update_date', columns='Prodotto', values='price', aggfunc='mean').interpolate(method='linear')
                    # Salviamo il grafico NEL messaggio della chat
                    st.session_state.home_chat.append({
                        "role": "assistant", 
                        "content": "Ecco l'andamento del mercato per i tuoi prodotti:",
                        "chart_data": chart_data,
                        "bottoni": []
                    })
                st.rerun()
                
        elif azione == "Aggiorna Prezzi":
            if dati_magazzino.empty:
                st.session_state.home_chat.append({"role": "assistant", "content": "Il magazzino è vuoto!", "bottoni": []})
                st.rerun()
            else:
                st.markdown("Avvio ricerca prezzi sul web... 🌐")
                prodotti = get_prodotti_raw(st.session_state.azienda_id)
                totale = len(prodotti)
                
                # Barra di caricamento e testo scorrono DENTRO il fumetto chat dell'AI
                status_text = st.empty()
                progress_bar = st.progress(0)
                agente = crea_agente_prezzi()
                
                for i, riga in prodotti.iterrows():
                    nome_p, id_p = riga['nome'], riga['id']
                    status_text.text(f"Aggiornamento ({i+1}/{totale}): {nome_p}...")
                    try:
                        risposta = agente.run(f"Cerca il prezzo attuale di {nome_p} e scrivi solo il valore medio.")
                        nuovo_prezzo = estrai_prezzo_da_testo(risposta.content)
                        if nuovo_prezzo:
                            update_prezzo_prodotto(id_p, nuovo_prezzo)
                            log_price_update(id_p, nuovo_prezzo)
                    except Exception as e:
                        st.error(f"Errore su {nome_p}: {e}")
                    
                    progress_bar.progress((i + 1) / totale)
                
                status_text.success("✅ Completato!")
                
                # Salvo l'esito nella chat
                st.session_state.home_chat.append({"role": "assistant", "content": "Ho terminato l'aggiornamento. I tuoi prezzi ora sono allineati al mercato reale! Come procediamo?", "bottoni": ["Sintesi Strategica", "Trend Prezzi"]})
                st.rerun()

# --- 4. RENDERIZZAZIONE BOTTONI DINAMICI ---
# Vengono mostrati solo se l'ultimo messaggio è dell'IA e non c'è già un'azione in corso
if not st.session_state.get("azione_home_attiva") and ultimo_msg["role"] == "assistant" and ultimo_msg.get("bottoni"):
    bottoni_disponibili = ultimo_msg["bottoni"]
    cols = st.columns(len(bottoni_disponibili))
    
    for i, btn_text in enumerate(bottoni_disponibili):
        if cols[i].button(btn_text, use_container_width=True):
            # L'utente "scrive" il testo del bottone nella chat
            st.session_state.home_chat.append({"role": "user", "content": btn_text})
            
            # Se è uno dei comandi di sistema, lo attiviamo
            if btn_text in ["Sintesi Strategica", "Scansione Punti Deboli", "Trend Prezzi", "Aggiorna Prezzi"]:
                st.session_state.azione_home_attiva = btn_text
            else:
                # Altrimenti, lo passiamo all'LLM Orchestratore
                st.session_state.elabora_prompt_home = btn_text
            st.rerun()

# --- 5. INPUT TESTUALE LIBERO ---
if prompt := st.chat_input("Fai una domanda all'Orchestratore sui tuoi KPI..."):
    st.session_state.home_chat.append({"role": "user", "content": prompt})
    st.session_state.elabora_prompt_home = prompt
    st.rerun()

# --- 6. ELABORAZIONE DOMANDE O BOTTONI CUSTOM TRAMITE L'ORCHESTRATORE ---
if st.session_state.get("elabora_prompt_home"):
    prompt_da_elaborare = st.session_state.elabora_prompt_home
    st.session_state.elabora_prompt_home = "" 
    
    with st.chat_message("assistant"):
        with st.spinner("Sto valutando la situazione... 🧠"):
            kpi_data = {
                "valore_totale": total_value,
                "margine_totale": total_margin,
                "prodotti_in_perdita": prodotti_in_perdita
            }
            
            risposta_json = interroga_orchestratore_home(prompt_da_elaborare, dati_magazzino, kpi_data)
            
            st.session_state.home_chat.append({
                "role": "assistant",
                "content": risposta_json.get("messaggio", "Ecco alcune opzioni:"),
                "bottoni": risposta_json.get("bottoni", [])
            })
            st.rerun()