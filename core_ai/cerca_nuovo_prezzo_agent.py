import re
import os
import requests
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.ollama import Ollama

# Carichiamo le variabili segrete dal file .env
load_dotenv()

def cerca_prezzi_shopping(query: str) -> str:
    """Usa l'API esterna per cercare i prezzi senza farsi bloccare."""
    print(f"\n[Scraper API] 🔍 Sto chiedendo all'API di cercare: '{query}'...")
    
    # Recuperiamo la chiave segreta
    api_key = os.getenv("SCRAPER_API_KEY")
    if not api_key:
        print("❌ ERRORE: Manca la SCRAPER_API_KEY nel file .env!")
        return "MEDIA: 0.0"

    query_url = query.replace(" ", "+")
    url_ebay = f"https://www.ebay.it/sch/i.html?_nkw={query_url}"
    
    # Chiamiamo ScraperAPI. L'opzione render=true gli dice di aspettare che la pagina si carichi.
    api_url = f"http://api.scraperapi.com?api_key={api_key}&url={url_ebay}&render=true"
    
    try:
        risposta = requests.get(api_url)
        testo_pagina = risposta.text
        
    except Exception as e:
        print(f"[Scraper API] ❌ Errore di connessione: {e}")
        return "MEDIA: 0.0"
        
    # --- Estrazione matematica dei prezzi ---
    valuta = r'(?:[€$£]|EUR|USD|GBP)'
    spazio = r'[\s\xa0\n]*'
    numero = r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?)'
    
    pattern_prezzi = f'{valuta}{spazio}{numero}|{numero}{spazio}{valuta}'
    match_trovati = re.findall(pattern_prezzi, testo_pagina, re.IGNORECASE)
    
    prezzi_puliti = []
    for match in match_trovati:
        prezzo_str = match[0] if match[0] else match[1]
        if prezzo_str:
            prezzo_str = re.sub(r'[^\d.,]', '', prezzo_str)
            if '.' in prezzo_str and ',' in prezzo_str:
                prezzo_str = prezzo_str.replace('.', '').replace(',', '.')
            elif ',' in prezzo_str:
                parti = prezzo_str.split(',')
                if len(parti[-1]) == 2:
                    prezzo_str = prezzo_str.replace(',', '.')
                else:
                    prezzo_str = prezzo_str.replace(',', '') 
            elif '.' in prezzo_str:
                parti = prezzo_str.split('.')
                if len(parti[-1]) != 2:
                    prezzo_str = prezzo_str.replace('.', '') 
            try:
                prezzi_puliti.append(float(prezzo_str))
            except ValueError:
                continue
    
    prezzi_puliti = list(set(prezzi_puliti))
    print(f"[Scraper API DEBUG] Prezzi grezzi trovati: {prezzi_puliti}")
    
    # Manteniamo la soglia bassa a 5 euro per non scartare le magliette!
    prezzi_reali = [p for p in prezzi_puliti if p > 5]
    
    if not prezzi_reali:
        print("[Scraper API] Nessun prezzo valido trovato.")
        return "MEDIA: 0.0"
        
    media_matematica = sum(prezzi_reali) / len(prezzi_reali)
    media_arrotondata = round(media_matematica, 2)
    
    print(f"[Scraper API] ✅ Media calcolata con successo: €{media_arrotondata}")
    return f"MEDIA: {media_arrotondata}"


def crea_agente_prezzi():
    """Resta qui se volessimo usare di nuovo l'IA in futuro per i prezzi"""
    return Agent(
        model=Ollama(id="llama3.2"), 
        tools=[cerca_prezzi_shopping],
        instructions=[
            "Sei un analista esperto nel monitoraggio dei prezzi online.",
            "Usa lo strumento 'cerca_prezzi_shopping' e restituisci SOLO la MEDIA."
        ],
        debug_mode=True
    )