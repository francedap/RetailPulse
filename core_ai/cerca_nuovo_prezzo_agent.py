import os
import re
import random
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.ollama import Ollama
from playwright.sync_api import sync_playwright

load_dotenv()
# 1. DEFINIAMO IL NOSTRO TOOL CON ISTRUZIONI PIÙ RIGIDE
def cerca_prezzi_shopping(query: str) -> str:
    """
    Usa SEMPRE questo strumento per cercare il prezzo di un prodotto online.
    
    Args:
        query (str): Il nome del prodotto da cercare. DEVE essere una stringa di testo semplice (es. "Nike Air Force 1"). NON passare mai oggetti JSON o dizionari.
    
    Returns:
        str: Una lista di prezzi trovati.
    """
    print(f"\n[Scraper] 🔍 Sto aprendo il browser per cercare: '{query}'...")
    
    with sync_playwright() as p:
        # Lista di User-Agent realistici (Windows, Mac, Linux, Chrome, Firefox, Safari)
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

        # Estrai un User-Agent casuale dalla lista
        ua_casuale = random.choice(user_agents)
        
        # Stampa nel log quale sta usando (utile per fare debug)
        print(f"[Scraper] 🕵️‍♂️ Navigo in incognito come: {ua_casuale[:40]}...")

        # Avvia il browser passando l'User-Agent finto
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent=ua_casuale)
        page = context.new_page()
        query_url = query.replace(" ", "+")
        
        page.goto(f"https://duckduckgo.com/?q={query_url}&ia=web&kl=it-it")
        page.wait_for_timeout(3000)
        
        testo_pagina = page.inner_text("body")
        browser.close()
        
    # --- INIZIO NUOVA PARTE INTEGRATA ---
    # 1. Nuova Regex: supporta i punti delle migliaia (es. 2.499,00 €) e prezzi senza decimali
    pattern_prezzi = r'[€$]\s?((?:\d{1,3}[.,])?\d{1,3}[.,]\d{2})|((?:\d{1,3}[.,])?\d{1,3}[.,]\d{2})\s?[€$]'
    
    # IMPORTANTE: qui per comodità mantengo il nome che avevi dato tu (match_trovati)
    match_trovati = re.findall(pattern_prezzi, testo_pagina)
    
    prezzi_puliti = []
    
    for match in match_trovati:
        # Prende il numero trovato (il primo o il secondo gruppo)
        prezzo_str = match[0] if match[0] else match[1]
        
        if prezzo_str:
            # 2. Pulizia per Python: se c'è un punto delle migliaia (es. 2.500,00), lo togliamo
            if '.' in prezzo_str and ',' in prezzo_str:
                prezzo_str = prezzo_str.replace('.', '').replace(',', '.')
            # Se c'è solo la virgola (es. 500,00), la trasformiamo in punto per i calcoli
            elif ',' in prezzo_str:
                prezzo_str = prezzo_str.replace(',', '.')
            
            try:
                prezzi_puliti.append(float(prezzo_str))
            except ValueError:
                continue
    # --- FINE NUOVA PARTE INTEGRATA ---
    
    # Rimuove i duplicati esatti per snellire la lista
    prezzi_puliti = list(set(prezzi_puliti))
    
    prezzi_reali = [p for p in prezzi_puliti if p > 1000]
    
    if not prezzi_reali:
        return "Nessun prezzo valido trovato."
        
    media_matematica = sum(prezzi_reali) / len(prezzi_reali)
    media_arrotondata = round(media_matematica, 2)

    return f"Prezzi trovati: {prezzi_reali}\nMEDIA: {media_arrotondata}"
# 2. AGGIORNIAMO LE ISTRUZIONI DELL'AGENTE
def crea_agente_prezzi():
    return Agent(
        model=Ollama(id="llama3.2"), 
        tools=[cerca_prezzi_shopping],
        instructions=[
            "Sei un analista esperto nel monitoraggio dei prezzi online.",
            "Il tuo obiettivo è trovare il reale prezzo medio di mercato per i prodotti richiesti.",
            "STRATEGIA:",
            "- Estrai la marca e il modello dalla richiesta dell'utente.",
            "- Usa lo strumento 'cerca_prezzi_shopping'. ATTENZIONE: l'argomento 'query' DEVE essere solo testo puro.",
            "- Scarta dalla lista i prezzi palesemente troppo bassi.",
            "FORMATO DI RISPOSTA OBBLIGATORIO:",
            "Non aggiungere MAI discorsi introduttivi o conclusivi. Rispondi ESATTAMENTE con questa riga:",
            "MEDIA: [Scrivi SOLO la media in formato decimale con il punto. Se non hai prezzi, scrivi 0.0]"
        ],
        debug_mode=True
    )
