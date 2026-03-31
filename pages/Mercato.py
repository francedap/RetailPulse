import streamlit as st
import pandas as pd
from components.sidebar import draw_sidebar
from utils.db_manager import get_prodotti_raw

# --- 0. CONTROLLO SICUREZZA ACCESSI ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

draw_sidebar(st.session_state.get('nome_azienda', 'La Tua Azienda'))

st.title("📈 Analisi di Mercato")
st.write("Esplora i trend attuali, valuta nuovi acquisti e ottieni report strategici dall'IA.")
st.markdown("---")


# --- 1. RICERCA PRODOTTO ESTERNO (Market Explorer Agent) ---
st.subheader("🔍 Ricerca Opportunità")
st.write("Cerca un prodotto esterno per vederne il valore di mercato attuale prima di acquistarlo.")

col_search, col_btn = st.columns([3, 1])
with col_search:
    ricerca_prodotto = st.text_input("Nome del prodotto (es. PlayStation 5 Pro)", label_visibility="collapsed")
with col_btn:
    btn_cerca = st.button("Analizza Mercato ⚡", use_container_width=True, type="primary")

if btn_cerca:
    if ricerca_prodotto.strip():
        st.info(f"Area riservata all'IA: In attesa di elaborare '{ricerca_prodotto}'")
        
        # TODO: IMPLEMENTARE AGNO - Market Explorer Agent
        # 1. Inviare la stringa 'ricerca_prodotto' all'agente Agno.
        # 2. L'agente usa i suoi tool (es. Web Search, API StockX/eBay) per trovare i prezzi.
        # 3. Recuperare dall'agente il Prezzo Medio, la Volatilità e un'analisi testuale.
        # 4. Mostrare i risultati qui usando st.metric() per i numeri e st.markdown() per il testo.
        
    else:
        st.warning("Inserisci il nome di un prodotto per iniziare la ricerca.")

st.markdown("---")


# --- 2. TREND DI CATEGORIA ---
st.subheader("📊 Trend delle Categorie")
st.write("Monitora l'andamento generale dei settori in cui operi.")

# Recuperiamo le categorie uniche dal magazzino dell'utente per personalizzare la tendina
df_magazzino = get_prodotti_raw(st.session_state.azienda_id)
if not df_magazzino.empty:
    categorie_utente = df_magazzino['categoria'].unique().tolist()
else:
    categorie_utente = ["Sneakers", "Elettronica", "Abbigliamento", "Accessori"] # Default se vuoto

categoria_scelta = st.selectbox("Seleziona una categoria da analizzare:", categorie_utente)

st.info(f"Area grafico: in attesa dei dati storici per la categoria '{categoria_scelta}'")

# TODO: IMPLEMENTARE CHIAMATA DATI TREND
# 1. Passare 'categoria_scelta' a un Agente o a un'API di trend.
# 2. Ottenere un DataFrame Pandas con due colonne: 'Data' e 'Prezzo Medio' (ultimi 30 giorni).
# 3. Disegnare il grafico usando: st.line_chart(df, x='Data', y='Prezzo Medio')

st.markdown("---")


# --- 3. REPORT STRATEGICO IA (Strategic Advisor Agent) ---
st.subheader("🧠 Report Strategico di Mercato")
st.write("Genera un resoconto completo basato sul confronto tra il tuo magazzino e il mercato globale.")

if st.button("Genera Report AI"):
    st.info("Area riservata all'IA: In attesa dell'Agente Strategico.")
    
    # TODO: IMPLEMENTARE AGNO - Strategic Advisor Agent
    # 1. Leggere l'intero DataFrame df_magazzino dell'utente.
    # 2. Convertire i dati in testo/JSON e passarli all'agente.
    # 3. Chiedere all'agente di: identificare i best seller, suggerire cosa vendere subito e cosa tenere.
    # 4. Stampare l'output dell'agente qui sotto con st.write_stream() per un bell'effetto "macchina da scrivere".