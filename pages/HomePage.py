import streamlit as st
import pandas as pd
import numpy as np
import time
# Importiamo il componente sidebar che abbiamo appena creato
from components.sidebar import draw_sidebar

# 1. Inietta la sidebar condivisa
draw_sidebar()

# --- DATI MOCK (SIMULATI) ---
# In un'app reale, questi dati verrebbero letti da un DB gestito dagli agenti Agno
dati_magazzino = pd.DataFrame({
    'Prodotto': ['Jordan 1 Tech', 'Sony PS5', 'RTX 4090', 'Yeezy Boost', 'iPhone 15'],
    'Prezzo_Acquisto': [150, 450, 1600, 220, 900],
    'Prezzo_Mercato': [210, 430, 1950, 200, 950], # Nota: PS5 e Yeezy sono in perdita
    'Quantita': [10, 5, 2, 15, 8],
    'Giorno_Giacenza': [30, 15, 5, 65, 10] # Yeezy è ferma da molto
})

# Calcoli matematici di base (non AI)
dati_magazzino['Valore_Totale_Mercato'] = dati_magazzino['Prezzo_Mercato'] * dati_magazzino['Quantita']
dati_magazzino['Margine_Unitario'] = dati_magazzino['Prezzo_Mercato'] - dati_magazzino['Prezzo_Acquisto']
dati_magazzino['Margine_Totale_Latente'] = dati_magazzino['Margine_Unitario'] * dati_magazzino['Quantita']

total_value = dati_magazzino['Valore_Totale_Mercato'].sum()
total_margin = dati_magazzino['Margine_Totale_Latente'].sum()
prodotti_in_perdita = dati_magazzino[dati_magazzino['Margine_Unitario'] < 0].shape[0]


# --- LAYOUT PAGINA PRINCIPALE ---
st.title("Dashboard Principale - Stato Aziendale")
st.write("Benvenuto in RetailPulse. Qui hai una panoramica intelligente della tua attività.")

st.markdown("---")

# 2. SEZIONE METRICHE (KPI) - Richiesto nell'email
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Valore Totale Magazzino", 
        value=f"€ {total_value:,}", 
        delta="+5.2% (vs ieri)",
        help="Valore attuale se vendessi tutto ai prezzi di mercato correnti."
    )

with col2:
    st.metric(
        label="Margine Totale Latente", 
        value=f"€ {total_margin:,}", 
        delta=f"{'⬆️' if total_margin > 0 else '⬇️'} Basato su trend attuali"
    )

with col3:
    st.metric(
        label="Articoli Critici (In Perdita)", 
        value=prodotti_in_perdita, 
        delta="-1 (risolto)",
        delta_color="inverse" # Rosso se aumenta, verde se diminuisce
    )

st.markdown("---")


# 3. SEZIONE SINTESI AI (Strategic Advisor Agent) - Richiesto nell'email
st.subheader("🧠 Sintesi Strategica Generata dall'IA")

# --- QUI ANDRÀ L'INTEGRAZIONE CON AGNO (Strategic Advisor Agent) ---
# Simuliamo l'output dell'agente che analizza i KPI sopra.
with st.container(border=True):
    st.markdown(f"""
    **Analisi dell'Agente Strategico:**
    La situazione generale è **solida**, con un valore di magazzino di €{total_value:,}. Tuttavia, si nota una contrazione dei margini nel settore *Sneakers* (Yeezy Boost in particolare) che sta erodendo il profitto potenziale generato dall'ottima performance del reparto *Hardware* (RTX 4090).
    
    L'esposizione al rischio è moderata, ma richiede attenzione immediata sulla gestione delle giacenze a lento realizzo.
    """)
    st.caption("Generato 1 minuto fa basandosi su dati live.")


st.markdown("---")


# 4. SEZIONE AZIONI E SUGGERIMENTI AI - Richiesto nell'email
st.subheader("⚡ Azioni Intelligenti")

# Creiamo due colonne per i pulsanti richiesti
col_btn1, col_btn2 = st.columns(2)

# Inizializziamo stati nella sessione per mostrare i risultati solo dopo il click
if 'ai_scan_active' not in st.session_state:
    st.session_state.ai_scan_active = False
if 'market_trend_active' not in st.session_state:
    st.session_state.market_trend_active = False

with col_btn1:
    if st.button("🔍 Scansione Punti Deboli (Inventory Agent)", use_container_width=True):
        st.session_state.ai_scan_active = True
        st.session_state.market_trend_active = False # Chiudi l'altro se aperto

with col_btn2:
    if st.button("📊 Mostra Andamento Mercato (Market Agent)", use_container_width=True):
        st.session_state.market_trend_active = True
        st.session_state.ai_scan_active = False # Chiudi l'altro se aperto


# --- LOGICA VISUALIZZAZIONE RISULTATI AI (SIMULATI) ---

if st.session_state.ai_scan_active:
    st.markdown("### Risultati Scansione Inefficienze")
    with st.spinner("L'Inventory Analyst Agent sta scansionando i dati strutturali..."):
        time.sleep(2) # Simula tempo di calcolo LLM
        
        # Identifichiamo i dati per la simulazione
        Yeezy_data = dati_magazzino[dati_magazzino['Prodotto'] == 'Yeezy Boost'].iloc[0]
        
        st.warning(f"**Punto Debole Rilevato: Eccesso di Giacenza e Margine Negativo**")
        
        col_pic1, col_pic2 = st.columns([1, 3])
        with col_pic1:
            # Immagine segnaposto
            st.image("https://via.placeholder.com/150", caption="Yeezy Boost")
        
        with col_pic2:
            st.markdown(f"""
            * **Prodotto:** Yeezy Boost
            * **Quantità:** {Yeezy_data['Quantita']} unità
            * **Giorni in magazzino:** {Yeezy_data['Giorno_Giacenza']} (Media aziendale: 25)
            * **Margine Attuale:** € {Yeezy_data['Margine_Unitario']} per unità.
            
            **💡 Suggerimento IA:** L'hype su questo modello è crollato. Mantenere lo stock sta generando costi di capitale. Si consiglia liquidazione immediata anche a prezzo di pareggio su piattaforme secondarie (Vinted/Subito) per recuperare liquidità (€ {Yeezy_data['Prezzo_Acquisto']*Yeezy_data['Quantita']}) da reinvestire in Hardware.
            """)

if st.session_state.market_trend_active:
    st.markdown("### Analisi Trend di Mercato Generali")
    with st.spinner("Il Market Explorer Agent sta analizzando i marketplace esterni..."):
        time.sleep(1.5)
        
        st.success("**Sentiment di Mercato Generale: Rialzista (Bullish) nel settore Tech**")
        
        # Grafico fittizio di andamento
        chart_data = pd.DataFrame(
            np.random.randn(20, 2),
            columns=['Settore Tech', 'Settore Sneakers']
        ).cumsum()
        st.line_chart(chart_data)
        
        st.markdown("""
        **Spiegazione Breve dell'IA:**
        I dati aggregati da StockX, eBay e Amazon mostrano una forte domanda per GPU Nvidia di fascia alta e smartphone. Il settore Sneakers è in stagnazione a causa di sovrapproduzione di modelli retail.
        
        **💡 Sezione Suggerimenti IA:**
        * Aumentare l'acquisizione di RTX 4080/4090 se trovate a <€100 dal retail.
        * Evitare restock di modelli Jordan 1 Mid per i prossimi 30 giorni.
        """)