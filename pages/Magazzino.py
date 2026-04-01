import streamlit as st
import pandas as pd
import time
import core_ai.cerca_nuovo_prezzo_agent as agente_prezzi

from components.sidebar import draw_sidebar
from utils.db_manager import add_prodotto, get_prodotti_raw, update_prezzo_prodotto, delete_prodotto

import re

def estrai_numero(testo):
    # Forziamo la conversione di QUALSIASI cosa arrivi (liste, dizionari, ecc.) in una stringa di testo
    testo_str = str(testo)
    
    # Cerca numeri decimali o interi nella stringa
    numeri = re.findall(r"[-+]?\d*\.\d+|\d+", testo_str.replace(',', '.'))
    return float(numeri[0]) if numeri else None


# --- 0. CONTROLLO SICUREZZA ACCESSI ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

draw_sidebar(st.session_state.get('nome_azienda', 'La Tua Azienda'))

st.title("📦 Gestione Magazzino")
st.write("Visualizza, aggiorna o rimuovi gli articoli dal tuo inventario.")
st.markdown("---")

tab_view, tab_add = st.tabs(["📋 Visualizza Inventario", "➕ Aggiungi Prodotto"])

# --- SCHEDA: AGGIUNGI PRODOTTO ---
with tab_add:
    st.subheader("Inserisci un nuovo articolo")
    with st.form("form_nuovo_prodotto", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Prodotto")
            categoria = st.selectbox("Categoria", ["Sneakers", "Elettronica", "Abbigliamento", "Accessori", "Altro"])
            descrizione = st.text_area("Descrizione o Note (Opzionale)", height=100)
        with col2:
            quantita = st.number_input("Quantità", min_value=1, step=1)
            prezzo_pagato = st.number_input("Prezzo Pagato/Costo (€)", min_value=0.0, step=10.0, format="%.2f")
        
        if st.form_submit_button("💾 Salva nel Database", use_container_width=True):
            if nome.strip() != "" and prezzo_pagato > 0:
                add_prodotto(st.session_state.azienda_id, nome, descrizione, categoria, quantita, prezzo_pagato, prezzo_pagato)
                st.success(f"✅ '{nome}' aggiunto!")
                time.sleep(1)
                st.rerun()

# --- SCHEDA: VISUALIZZA, AGGIORNA E RIMUOVI ---
with tab_view:
    df_prodotti = get_prodotti_raw(st.session_state.azienda_id)
    
    if df_prodotti.empty:
        st.info("Il tuo magazzino è vuoto. Spostati sulla scheda 'Aggiungi Prodotto' per iniziare.")
    else:
        st.subheader("I tuoi Prodotti")
        
        # Visualizzazione Tabella
        df_display = df_prodotti.copy().drop(columns=['id'])
        df_display.columns = ['Nome', 'Descrizione', 'Categoria', 'Quantità', 'Prezzo Pagato (€)', 'Prezzo Attuale (€)', 'Data Inserimento']
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # --- SEZIONE AZIONI SUI PRODOTTI ---
        st.subheader("🛠️ Azioni Rapide")
        
        col_sel, col_upd, col_del = st.columns([2, 1, 1])
        
        opzioni_prodotti = dict(zip(df_prodotti['nome'], df_prodotti['id']))
        
        with col_sel:
            prodotto_scelto_nome = st.selectbox("Seleziona prodotto:", list(opzioni_prodotti.keys()), label_visibility="collapsed")
            prodotto_id = opzioni_prodotti[prodotto_scelto_nome]

        with col_upd:
            if st.button("Aggiorna Prezzo ⚡", use_container_width=True):
                st.info(f"In attesa dell'IA per cercare il prezzo di '{prodotto_scelto_nome}'.")
                
                prompt = f"Cerca sul web il prezzo di mercato di '{prodotto_scelto_nome}'. Rispondi SOLO con il numero del prezzo."
                
                try:
                    # Inizializziamo l'agente di Agno
                    agente = agente_prezzi.crea_agente_prezzi()
                    
                    # .run() esegue la ricerca e restituisce un oggetto RunResponse
                    risposta = agente.run(prompt)
                    
                    # Estraiamo il testo della risposta con .content
                    risposta_raw = risposta.content
                    
                    # Passiamo il testo alla nostra solita funzione di estrazione
                    nuovo_prezzo = estrai_numero(risposta_raw)
                    

                    if nuovo_prezzo is not None:
                        # Salvare nel DB (scommenta quando vuoi testare il salvataggio reale)
                        update_prezzo_prodotto(prodotto_id, nuovo_prezzo)
                        st.success(f"Prezzo aggiornato: €{nuovo_prezzo:.2f}")
                        
                        st.rerun() #questo serve a ricaricare la pagina
                    else:
                        st.error(f"L'IA non ha restituito un prezzo valido. Risposta grezza: {risposta_raw}")
                        
                except Exception as e:
                    st.error(f"Errore durante l'aggiornamento: {e}")

        with col_del:
            with st.popover("Elimina 🗑️", use_container_width=True):
                st.warning(f"Vuoi davvero eliminare '{prodotto_scelto_nome}'?")
                if st.button("Sì, elimina definitivamente", type="primary"):
                    delete_prodotto(prodotto_id)
                    st.success("Prodotto rimosso!")
                    time.sleep(1)
                    st.rerun()