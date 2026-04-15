import os
import re
import random
import sys          
import asyncio
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.ollama import Ollama
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

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
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=ua_casuale)
        page = context.new_page()

        query_url = query.replace(" ", "+")
        
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        # Puntiamo dritti a Trovaprezzi invece che a DuckDuckGo
        url_ricerca = f"https://www.ebay.it/sch/i.html?_nkw={query_url}"
        print(f"[Scraper] 🌐 Navigo su: {url_ricerca}")
        
        page.goto(url_ricerca)
        
        page.wait_for_timeout(5000)
        try:
            # Cerca un qualsiasi pulsante con parole chiave di accettazione
            pulsante_accetta = page.get_by_role("button", name=re.compile("accett|accept|concord|ok", re.IGNORECASE))
            if pulsante_accetta.count() > 0:
                pulsante_accetta.first.click(timeout=3000)
                print("[Scraper] 🍪 Banner dei cookie distrutto!")
                page.wait_for_timeout(1500) # Aspettiamo che l'animazione del banner sparisca
        except Exception:
            # Se non c'è il banner o fallisce, pazienza, continuiamo
            pass
      
        testo_pagina = page.inner_text("body")
        
        browser.close()
        
    # --- INIZIO NUOVA PARTE INTEGRATA ---
   # 1. LA REGEX UNIVERSALE DEFINITIVA
    # Cattura valute (€, $, £, EUR, USD, GBP)
    # Gestisce qualsiasi spazio o ritorno a capo in mezzo [\s\xa0\n]*
    # Accetta numeri con o senza decimali, e con qualsiasi punto/virgola
    valuta = r'(?:[€$£]|EUR|USD|GBP)'
    spazio = r'[\s\xa0\n]*'
    numero = r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?)'
    
    # Cerchiamo: "Valuta + Numero" OPPURE "Numero + Valuta"
    pattern_prezzi = f'{valuta}{spazio}{numero}|{numero}{spazio}{valuta}'
    
    match_trovati = re.findall(pattern_prezzi, testo_pagina, re.IGNORECASE)
    
    prezzi_puliti = []
    
    for match in match_trovati:
        # Prende il numero (è nel primo gruppo se la valuta è prima, nel secondo se è dopo)
        prezzo_str = match[0] if match[0] else match[1]
        
        if prezzo_str:
            # Tolgo eventuali lettere o spazi estranei finiti nel mezzo
            prezzo_str = re.sub(r'[^\d.,]', '', prezzo_str)
            
            # 2. PULIZIA INTELLIGENTE DEL TESTO
            if '.' in prezzo_str and ',' in prezzo_str:
                # Formato IT standard: 1.250,00 -> diventa 1250.00
                prezzo_str = prezzo_str.replace('.', '').replace(',', '.')
                
            elif ',' in prezzo_str:
                # Capisce se è 1,250 (migliaia inglesi) o 150,50 (decimali)
                # Se dopo la virgola ci sono esattamente 2 cifre, sono decimali.
                parti = prezzo_str.split(',')
                if len(parti[-1]) == 2:
                    prezzo_str = prezzo_str.replace(',', '.')
                else:
                    prezzo_str = prezzo_str.replace(',', '') 
                    
            elif '.' in prezzo_str:
                # Capisce se è 1.250 (migliaia italiane) o 150.50 (decimali inglesi)
                parti = prezzo_str.split('.')
                if len(parti[-1]) != 2:
                    prezzo_str = prezzo_str.replace('.', '') 

            try:
                prezzi_puliti.append(float(prezzo_str))
            except ValueError:
                continue
    
    # --- FINE PARTE INTEGRATA ---
    
    # Rimuove i duplicati esatti per snellire la lista
    prezzi_puliti = list(set(prezzi_puliti))
    
    # 3. FILTRO CORRETTO (Evitiamo gli accessori troppo economici, ma includiamo il prodotto)
    prezzi_reali = [p for p in prezzi_puliti if p > 50]
    
    if not prezzi_reali:
        print("[Scraper] Nessun prezzo valido trovato nella pagina.")
        return 0.0
        
    media_matematica = sum(prezzi_reali) / len(prezzi_reali)
    media_arrotondata = round(media_matematica, 2)
    
    print(f"[Scraper] Trovati i seguenti prezzi validi: {prezzi_reali}")
    
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
            "- Estrai la marca e il modello preciso e le caratteristiche dalla richiesta dell'utente.",
            "- Usa lo strumento 'cerca_prezzi_shopping'. ATTENZIONE: l'argomento 'query' DEVE essere solo testo puro.",
            "- Scarta dalla lista i prezzi palesemente troppo bassi.",
            "FORMATO DI RISPOSTA OBBLIGATORIO:",
            "Non aggiungere MAI discorsi introduttivi o conclusivi. Rispondi ESATTAMENTE con questa riga:",
            "MEDIA: [Scrivi SOLO la media in formato decimale con il punto. Se non hai prezzi, scrivi 0.0]"
        ],
        debug_mode=True
    )
