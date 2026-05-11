import re
import random
import sys          
import asyncio
from agno.agent import Agent
from agno.models.ollama import Ollama
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

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
        # Lista di User-Agent realistici per evitare blocchi e sembrare un utente reale
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

        ua_casuale = random.choice(user_agents)
        
        print(f"[Scraper] 🕵️‍♂️ Navigo in incognito come: {ua_casuale[:40]}...")

        # Usiamo Firefox e lo teniamo invisibile (headless=True)
        browser = p.firefox.launch(headless=False) 
        
        # Aggiungiamo dettagli realistici per ingannare Akamai
        context = browser.new_context(
            user_agent=ua_casuale,
            viewport={'width': 1920, 'height': 1080},
            extra_http_headers={
                "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1"
            }
        )
        page = context.new_page()

        query_url = query.replace(" ", "+")
        
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        url_ricerca = f"https://www.ebay.it/sch/i.html?_nkw={query_url}"
        print(f"[Scraper] 🌐 Navigo su: {url_ricerca}")
        
        page.goto(url_ricerca)
        
        page.wait_for_timeout(5000)

        #per banner cookie di ebay
        try:
            pulsante_accetta = page.get_by_role("button", name=re.compile("accett|accept|concord|ok", re.IGNORECASE))
            if pulsante_accetta.count() > 0:
                pulsante_accetta.first.click(timeout=3000)
                print("[Scraper] 🍪 Banner dei cookie distrutto!")
                page.wait_for_timeout(1500) 
        except Exception:
            pass
      
        testo_pagina = page.inner_text("body")
        
        browser.close()
        
#--- per estrarre i prezz dal testo ---

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
    
    prezzi_reali = [p for p in prezzi_puliti if p > 5]
    
    #debug 
    if not prezzi_reali:
        print("[Scraper] Nessun prezzo valido trovato nella pagina.")
        return 0.0
        
    media_matematica = sum(prezzi_reali) / len(prezzi_reali)
    media_arrotondata = round(media_matematica, 2)
    
    print(f"[Scraper] Trovati i seguenti prezzi validi: {prezzi_reali}")
    
    return f"Prezzi trovati: {prezzi_reali}\nMEDIA: {media_arrotondata}"


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
