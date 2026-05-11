import time
import sqlite3
import re
from core_ai.cerca_nuovo_prezzo_agent import cerca_prezzi_shopping
from utils.db_manager import add_notifica, update_prezzo_prodotto, log_price_update

DB_PATH = "data/retailpulse.db"

def monitoraggio_continuo():
    """L'Agente Silente che gira in background per controllare i prezzi."""
    print("🤖 Avvio Agente Silente (Versione Pura Python, senza IA) per il monitoraggio...")
    
    SOGLIA_VARIAZIONE = 0.10 
    
    while True:
        print("\n🔄 Inizio nuovo ciclo di controllo prezzi...")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, id_azienda, nome, prezzo_attuale FROM prodotti")
        prodotti = cursor.fetchall()
        conn.close()
        
        for prodotto in prodotti:
            id_prodotto, id_azienda, nome, prezzo_salvato = prodotto
            print(f"🔍 Controllo: {nome} (Prezzo salvato: €{prezzo_salvato})")
            
            try:
                # ⚡ SALTIAMO L'IA! Chiamiamo direttamente lo strumento matematico di ricerca ⚡
                risultato_scraping = cerca_prezzi_shopping(nome)
                nuovo_prezzo = None
                
                # Leggiamo il risultato esatto restituito dallo scraper
                if isinstance(risultato_scraping, str) and "MEDIA:" in risultato_scraping:
                    match = re.search(r'MEDIA:\s*([0-9.,]+)', risultato_scraping)
                    if match:
                        nuovo_prezzo = float(match.group(1))
                        
                # Se abbiamo trovato un prezzo reale e sensato
                if nuovo_prezzo and nuovo_prezzo > 0:
                    variazione = abs(nuovo_prezzo - prezzo_salvato) / prezzo_salvato
                    
                    if variazione >= SOGLIA_VARIAZIONE:
                        print(f"⚠️ Variazione rilevata per {nome}! Nuovo prezzo: €{nuovo_prezzo}")
                        
                        update_prezzo_prodotto(id_prodotto, nuovo_prezzo)
                        log_price_update(id_prodotto, nuovo_prezzo)
                        
                        tipo_var = "aumentato" if nuovo_prezzo > prezzo_salvato else "diminuito"
                        percentuale_testo = f"{variazione * 100:.1f}%"
                        messaggio = f"Il prezzo di '{nome}' è {tipo_var} a €{nuovo_prezzo:.2f} (variazione del {percentuale_testo})."
                        
                        add_notifica(id_azienda, id_prodotto, messaggio)
                    else:
                        print(f"✅ Prezzo stabile per {nome} (Variazione minima).")
                else:
                    print(f"⚠️ Nessun prezzo valido trovato per '{nome}' (Prezzo ignorato per sicurezza).")
                
            except Exception as e:
                print(f"❌ Errore durante il controllo di {nome}: {e}")
        
        attesa = 60
        print(f"⏳ Ciclo terminato. L'Agente si riposa per {attesa} secondi...")
        time.sleep(attesa)

if __name__ == "__main__":
    monitoraggio_continuo()