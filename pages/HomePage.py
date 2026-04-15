import streamlit as st
import pandas as pd
import numpy as np
from core_ai.strategic_advisor_agent import genera_sintesi_strategica
from core_ai.inventory_analyst import analizza_punti_deboli

# Importiamo la sidebar e le funzioni del DB
from components.sidebar import draw_sidebar
from utils.db_manager import get_dati_magazzino, get_nome_azienda

# --- 0. CONTROLLO SICUREZZA ACCESSI ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

# Inizializziamo le variabili di stato se non esistono
if 'ai_scan_active' not in st.session_state:
    st.session_state.ai_scan_active = False
if 'market_trend_active' not in st.session_state:
    st.session_state.market_trend_active = False

# --- 1. RECUPERO DATI UTENTE E AZIENDA ---
if 'nome_azienda' not in st.session_state:
    st.session_state.nome_azienda = get_nome_azienda(st.session_state.azienda_id)

nome_azienda = st.session_state.nome_azienda
draw_sidebar(nome_azienda)

# --- 2. COLLEGAMENTO AL DATABASE REALE ---
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

# --- 3. LAYOUT PAGINA PRINCIPALE ---
st.title(f"Dashboard: {nome_azienda}")
st.write(f"Benvenuto **{st.session_state.nickname}**. Qui hai una panoramica intelligente della tua attività.")
st.markdown("---")

# 4. SEZIONE METRICHE (KPI)
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Valore Totale Magazzino", value=f"€ {total_value:,.2f}", help="Valore attuale se vendessi tutto.")
with col2:
    st.metric(label="Margine Totale Latente", value=f"€ {total_margin:,.2f}")
with col3:
    st.metric(label="Articoli Critici (In Perdita)", value=prodotti_in_perdita, delta_color="inverse")

st.markdown("---")

# 5. SEZIONE SINTESI AI (Strategic Advisor Agent)
st.subheader("🧠 Sintesi Strategica Generata dall'IA")

with st.container(border=True):
    # 1. Creiamo il pulsante
    if st.button("Genera Sintesi 🤖", use_container_width=True):
        
        # 2. Se l'utente clicca, mostriamo il caricamento
        with st.spinner("L'Intelligenza Artificiale sta analizzando i dati del tuo magazzino... ⏳"):
            
            # Chiamiamo l'agente e salviamo il risultato in memoria
            testo_generato = genera_sintesi_strategica(total_value, total_margin, prodotti_in_perdita)
            st.session_state.sintesi_ai_home = testo_generato

    # 3. Controlliamo se abbiamo una sintesi in memoria da mostrare
    if 'sintesi_ai_home' in st.session_state:
        st.info(st.session_state.sintesi_ai_home)
        
    else:
        # Messaggio di default quando non è ancora stata generata
        st.info("Clicca il pulsante qui sopra per ottenere un'analisi intelligente del tuo magazzino.")

st.markdown("---")

# --- 6. SEZIONE AZIONI E SUGGERIMENTI AI ---
st.subheader("⚡ Azioni Intelligenti")

col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    if st.button("🔍 Scansione Punti Deboli", use_container_width=True):
        st.session_state.ai_scan_active = True
        st.session_state.market_trend_active = False
        if 'risultato_scansione' in st.session_state:
            del st.session_state['risultato_scansione']

with col_btn2:
    if st.button("📊 Mostra Andamento Mercato", use_container_width=True):
        st.session_state.market_trend_active = True
        st.session_state.ai_scan_active = False 

with col_btn3:
    # --- NUOVO TASTO: AGGIORNAMENTO GLOBALE ---
    if st.button("🔄 Aggiorna Prezzi Mercato", use_container_width=True, help="Scarica i prezzi reali per tutti i prodotti"):
        if dati_magazzino.empty:
            st.warning("Il magazzino è vuoto!")
        else:
            from core_ai.cerca_nuovo_prezzo_agent import crea_agente_prezzi
            from utils.db_manager import update_prezzo_prodotto, estrai_prezzo_da_testo, get_prodotti_raw
            
            # Recuperiamo i dati grezzi per avere gli ID
            prodotti = get_prodotti_raw(st.session_state.azienda_id)
            totale = len(prodotti)
            
            # Interfaccia di caricamento
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            agente = crea_agente_prezzi()
            
            for i, riga in prodotti.iterrows():
                nome_p = riga['nome']
                id_p = riga['id']
                
                status_text.text(f"Aggiornamento ({i+1}/{totale}): {nome_p}...")
                
                try:
                    # Chiamata all'IA
                    risposta = agente.run(f"Cerca il prezzo attuale di {nome_p} e scrivi solo il valore medio.")
                    nuovo_prezzo = estrai_prezzo_da_testo(risposta.content)
                    
                    if nuovo_prezzo:
                        update_prezzo_prodotto(id_p, nuovo_prezzo)
                except Exception as e:
                    st.error(f"Errore su {nome_p}: {e}")
                
                progress_bar.progress((i + 1) / totale)
            
            status_text.success("✅ Tutti i prezzi sono stati aggiornati!")
            st.rerun()

st.markdown("---")

# --- 7. LOGICA VISUALIZZAZIONE RISULTATI ---

# Sezione: Scansione Punti Deboli
if st.session_state.ai_scan_active:
    st.markdown("### 🔍 Risultati Scansione Inefficienze")
    
    if 'risultato_scansione' not in st.session_state:
        with st.spinner("Analisi in corso... L'IA sta cercando i colli di bottiglia 🕵️‍♂️"):
            testo_scansione = analizza_punti_deboli(dati_magazzino)
            st.session_state.risultato_scansione = testo_scansione

    st.info(st.session_state.risultato_scansione)

# Sezione: Andamento di Mercato (Grafico)
if st.session_state.market_trend_active:
    st.markdown("### 📊 Andamento Storico del Mercato")
    
    with st.spinner("Generando il grafico dei trend... 📈"):
        from utils.db_manager import get_dati_trend_temporale
        
        df_trend = get_dati_trend_temporale(st.session_state.azienda_id)
        
        if df_trend.empty:
            st.warning("Non ci sono abbastanza dati nel magazzino per generare un trend.")
        else:
            # Trasformiamo i dati per Streamlit usando pivot_table
            chart_data = df_trend.pivot_table(index='Data', columns='Prodotto', values='Prezzo (€)', aggfunc='mean')
            
            # --- IL TRUCCO ---
            # .interpolate(method='linear') unisce i puntini vuoti, 
            # così se due prodotti hanno date diverse, le linee non si spezzano mai!
            chart_data = chart_data.interpolate(method='linear')
            
            # Mostriamo il grafico a linee
            st.line_chart(chart_data)
            
            st.caption("Il grafico mostra l'evoluzione del prezzo dal momento del tuo acquisto (Prezzo Pagato) fino al valore di mercato attuale.")