import time
import sqlite3
import re
from core_ai.cerca_nuovo_prezzo_agent import crea_agente_prezzi
from utils.db_manager import add_notifica, update_prezzo_prodotto, log_price_update

DB_PATH = "data/retailpulse.db"

def estrai_prezzo_da_testo(testo):
    """Estrae il valore numerico più alto dal testo restituito dall'IA."""
    numeri = re.findall(r"[-+]?\d*\.\d+|\d+", str(testo).replace(',', '.'))
    if not numeri:
        return None
    return max([float(n) for n in numeri])

def monitoraggio_continuo():
    """L'Agente Silente che gira in background per controllare i prezzi."""
    print("🤖 Avvio Agente Silente per il monitoraggio prezzi in background...")
    agente = crea_agente_prezzi()
    
    # Soglia di sensibilità impostata al 10% come richiesto
    SOGLIA_VARIAZIONE = 0.10 
    
    while True:
        print("\n🔄 Inizio nuovo ciclo di controllo prezzi...")
        
        # Preleviamo tutti i prodotti dal database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, id_azienda, nome, prezzo_attuale FROM prodotti")
        prodotti = cursor.fetchall()
        conn.close()
        
        for prodotto in prodotti:
            id_prodotto, id_azienda, nome, prezzo_salvato = prodotto
            print(f"🔍 Controllo: {nome} (Prezzo salvato: €{prezzo_salvato})")
            
            try:
                # Chiediamo all'IA di cercare il nuovo prezzo
                prompt = f"Cerca {nome} e scrivi solo il prezzo medio."
                risposta = agente.run(prompt)
                nuovo_prezzo = estrai_prezzo_da_testo(risposta.content)
                
                if nuovo_prezzo and nuovo_prezzo > 0:
                    # Calcoliamo la variazione percentuale (valore assoluto)
                    variazione = abs(nuovo_prezzo - prezzo_salvato) / prezzo_salvato
                    
                    if variazione >= SOGLIA_VARIAZIONE:
                        print(f"⚠️ Variazione rilevata per {nome}! Nuovo prezzo: €{nuovo_prezzo}")
                        
                        # Aggiorniamo il prezzo nel DB
                        update_prezzo_prodotto(id_prodotto, nuovo_prezzo)
                        log_price_update(id_prodotto, nuovo_prezzo)
                        
                        # Creiamo il messaggio di alert
                        tipo_var = "aumentato" if nuovo_prezzo > prezzo_salvato else "diminuito"
                        percentuale_testo = f"{variazione * 100:.1f}%"
                        messaggio = f"Il prezzo di '{nome}' è {tipo_var} a €{nuovo_prezzo:.2f} (variazione del {percentuale_testo})."
                        
                        # Salviamo la notifica nel DB affinché Streamlit la legga
                        add_notifica(id_azienda, id_prodotto, messaggio)
                    else:
                        print(f"✅ Prezzo stabile per {nome} (Variazione minima).")
                
            except Exception as e:
                print(f"❌ Errore durante il controllo di {nome}: {e}")
        
        # Facciamo "riposare" lo script prima del prossimo controllo.
        # Per ora impostato a 60 secondi per i test. Poi potrai alzarlo a 3600 (1 ora).
        attesa = 60
        print(f"⏳ Ciclo terminato. L'Agente Silente si riposa per {attesa} secondi...")
        time.sleep(attesa)

if __name__ == "__main__":
    monitoraggio_continuo()