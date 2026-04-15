# File: pages/Mercato.py

import streamlit as st
import pandas as pd
from components.sidebar import draw_sidebar
from utils.db_manager import get_prodotti_raw

# IMPORTIAMO LE NOSTRE NUOVE FUNZIONI AI
from core_ai.market_explorer import (
    analizza_opportunita_prodotto, 
    analizza_trend_categoria, 
    genera_report_strategico_mercato
)

# --- 0. CONTROLLO SICUREZZA ACCESSI ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

draw_sidebar(st.session_state.get('nome_azienda', 'La Tua Azienda'))

st.title("📈 Analisi di Mercato")
st.write("Esplora i trend attuali, valuta nuovi acquisti e ottieni report strategici dall'IA.")
st.markdown("---")

# Recuperiamo i dati del magazzino (ci serviranno per le categorie e per il report)
df_magazzino = get_prodotti_raw(st.session_state.azienda_id)


# --- 1. RICERCA PRODOTTO ESTERNO (Market Explorer Agent) ---
st.subheader("🔍 Ricerca Opportunità")
st.write("Cerca un prodotto esterno per vederne il valore di mercato attuale prima di acquistarlo.")

col_search, col_btn = st.columns([3, 1])
with col_search:
    ricerca_prodotto = st.text_input("Nome del prodotto (es. PlayStation 5 Pro)", label_visibility="collapsed")
with col_btn:
    btn_cerca = st.button("Analizza Prodotto ⚡", use_container_width=True, type="primary")

if btn_cerca:
    if ricerca_prodotto.strip():
        # Usiamo st.spinner per mostrare all'utente che l'IA sta pensando
        with st.spinner(f"L'IA sta analizzando il mercato per '{ricerca_prodotto}'... ⏳"):
            # Chiamiamo la nostra nuova funzione
            risultato_prodotto = analizza_opportunita_prodotto(ricerca_prodotto)
            # Mostriamo il risultato in un box colorato
            st.info(risultato_prodotto)
    else:
        st.warning("Inserisci il nome di un prodotto per iniziare la ricerca.")

st.markdown("---")


# --- 2. TREND DI CATEGORIA ---
st.subheader("📊 Trend delle Categorie")
st.write("Monitora l'andamento generale dei settori in cui operi.")

if not df_magazzino.empty:
    categorie_utente = df_magazzino['categoria'].unique().tolist()
else:
    categorie_utente = ["Sneakers", "Elettronica", "Abbigliamento", "Accessori"] # Default se vuoto

col_cat, col_btn_cat = st.columns([3, 1])
with col_cat:
    categoria_scelta = st.selectbox("Seleziona una categoria da analizzare:", categorie_utente, label_visibility="collapsed")
with col_btn_cat:
    btn_trend = st.button("Genera Trend 📈", use_container_width=True)

if btn_trend:
    with st.spinner(f"Sto raccogliendo i dati globali per la categoria '{categoria_scelta}'... ⏳"):
        # Chiamiamo l'IA per il report sulla categoria
        risultato_trend = analizza_trend_categoria(categoria_scelta)
        st.success(risultato_trend)

st.markdown("---")


# --- 3. REPORT STRATEGICO IA (Strategic Advisor Agent) ---
st.subheader("🧠 Report Strategico di Mercato")
st.write("Genera un resoconto completo basato sul confronto tra il tuo magazzino e il mercato globale.")

if st.button("Genera Report Macroecomico AI 🌍", use_container_width=True):
    with st.spinner("Il Chief Strategy Officer virtuale sta incrociando i tuoi dati con il mercato globale... ⏳"):
        # Passiamo l'intero DataFrame all'IA
        risultato_strategico = genera_report_strategico_mercato(df_magazzino)
        
        # Mostriamo il risultato. 
        # Usiamo un container con bordo per farlo sembrare un vero documento ufficiale!
        with st.container(border=True):
            st.markdown(risultato_strategico)