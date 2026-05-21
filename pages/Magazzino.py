import streamlit as st
import pandas as pd
import time
import core_ai.cerca_nuovo_prezzo_agent as agente_prezzi

from components.sidebar import draw_sidebar
from utils.db_manager import add_prodotto, get_prodotti_raw, update_prezzo_prodotto, delete_prodotto, log_price_update

import re

def estrai_numero(testo):
    testo_str = str(testo)
    numeri = re.findall(r"[-+]?\d*\.\d+|\d+", testo_str.replace(',', '.'))
    if not numeri:
        return None       
    numeri_float = [float(n) for n in numeri]
    prezzo_reale = max(numeri_float)
    
    return prezzo_reale


if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

draw_sidebar(st.session_state.get('nome_azienda', 'La Tua Azienda'))

st.title("📦 Gestione Magazzino")
st.write("Visualizza, aggiorna o rimuovi gli articoli dal tuo inventario.")
st.markdown("---")

tab_view, tab_add = st.tabs(["📋 Visualizza Inventario", " ➕ Aggiungi Prodotto"])


df_prodotti = get_prodotti_raw(st.session_state.azienda_id)

categorie_disponibili = ["Sneakers", "Elettronica", "Abbigliamento", "Accessori", "Altro"]
if not df_prodotti.empty:
    categorie_dal_db = df_prodotti['categoria'].dropna().unique().tolist()
    for cat in categorie_dal_db:
        if cat not in categorie_disponibili:
            categorie_disponibili.append(cat)


with tab_add:
    st.subheader("Inserisci un nuovo articolo")
    with st.form("form_nuovo_prodotto", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Prodotto")
            categoria_selezionata = st.selectbox("Scegli una Categoria", categorie_disponibili)
            
            nuova_categoria = st.text_input("OPPURE scrivi una Nuova Categoria", placeholder="Es. Videogiochi, Arredamento...")
            
            descrizione = st.text_area("Descrizione o Note (Opzionale)", height=100)
            
        with col2:
            quantita = st.number_input("Quantità", min_value=1, step=1)
            prezzo_pagato = st.number_input("Prezzo Pagato/Costo (€)", min_value=0.0, step=10.0, format="%.2f")
        
        if st.form_submit_button("💾 Aggiungi Prodotto", width='stretch'):
            categoria_finale = nuova_categoria.strip() if nuova_categoria.strip() != "" else categoria_selezionata

            if nome.strip() != "" and prezzo_pagato > 0:
                add_prodotto(st.session_state.azienda_id, nome, descrizione, categoria_finale, quantita, prezzo_pagato, prezzo_pagato)
                st.success(f"✅ '{nome}' aggiunto nella categoria '{categoria_finale}'!")
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("Assicurati di inserire il Nome e un Prezzo maggiore di 0.")

with tab_view:
    if df_prodotti.empty:
        st.info("Il tuo magazzino è vuoto. Spostati sulla scheda 'Aggiungi Prodotto' per iniziare.")
    else:
        st.subheader("I tuoi Prodotti")
        
        df_display = df_prodotti.copy().drop(columns=['id'])
        df_display.columns = ['Nome', 'Descrizione', 'Categoria', 'Quantità', 'Prezzo Pagato (€)', 'Prezzo Attuale (€)', 'Data Inserimento']
        st.dataframe(df_display, width='stretch', hide_index=True)
        
        st.markdown("---")
        
        st.subheader("🛠️ Azioni Rapide")
        
        col_sel, col_upd, col_del = st.columns([2, 1, 1])
        
        opzioni_prodotti = dict(zip(df_prodotti['nome'], df_prodotti['id']))
        
        with col_sel:
            prodotto_scelto_nome = st.selectbox("Seleziona prodotto:", list(opzioni_prodotti.keys()), label_visibility="collapsed")
            prodotto_id = opzioni_prodotti[prodotto_scelto_nome]

        with col_upd:
            if st.button("Aggiorna Prezzo ⚡", width='stretch'):
                st.info(f"In attesa dell'IA per cercare il prezzo di '{prodotto_scelto_nome}'.")
            
                prompt = f"Cerca {prodotto_scelto_nome} e scrivi solo il prezzo medio."
                try:
                    agente = agente_prezzi.crea_agente_prezzi()
                    
                    risposta = agente.run(prompt)
                    
                    risposta_raw = risposta.content
                    
                    nuovo_prezzo = estrai_numero(risposta_raw)
                    

                    if nuovo_prezzo is not None:
                        update_prezzo_prodotto(prodotto_id, nuovo_prezzo)
                        log_price_update(prodotto_id, nuovo_prezzo)
                        st.success(f"Prezzo aggiornato: €{nuovo_prezzo:.2f}")
                        
                        time.sleep(1.5)
                        st.rerun() 
                    else:
                        st.error(f"L'IA non ha restituito un prezzo valido. Risposta grezza: {risposta_raw}")
                        
                except Exception as e:
                    st.error(f"Errore durante l'aggiornamento: {e}")

        with col_del:
            with st.popover("Elimina 🗑️", width='stretch'):
                st.warning(f"Vuoi davvero eliminarlo '{prodotto_scelto_nome}'?")
                if st.button("Conferma Eliminazione", type="primary"):
                    delete_prodotto(prodotto_id)
                    st.success("Prodotto rimosso!")
                    time.sleep(1)
                    st.rerun()