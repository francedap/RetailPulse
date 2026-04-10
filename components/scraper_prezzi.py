from playwright.sync_api import sync_playwright
import re

def trova_prezzi_carosello(query):
    print(f"🔍 Avvio la ricerca per: '{query}'...")
    
    with sync_playwright() as p:
        # headless=True fa girare il browser in background. 
        # Mettilo a False se vuoi vedere la pagina che si apre sul tuo schermo!
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Formattiamo la query per l'URL (sostituisce gli spazi con i +)
        query_url = query.replace(" ", "+")
        
        # Andiamo su DuckDuckGo
        page.goto(f"https://duckduckgo.com/?q={query_url}&ia=web")
        
        # ATTESA FONDAMENTALE: Aspettiamo 3 secondi per permettere a DuckDuckGo 
        # di caricare il carosello Shopping in JavaScript
        page.wait_for_timeout(3000)
        
        # Estraiamo TUTTO il testo attualmente visibile sulla pagina
        testo_pagina = page.inner_text("body")
        
        browser.close()
        
    # --- FASE 2: ESTREZIONE DEI PREZZI CON REGEX ---
    # Questa espressione regolare cerca il simbolo € seguito o preceduto da numeri
    # Cerca formati come: €100,00 oppure 119.99€
    pattern_prezzi = r'€\s?(\d{1,4}[,.]\d{2})|(\d{1,4}[,.]\d{2})\s?€'
    
    match_trovati = re.findall(pattern_prezzi, testo_pagina)
    
    prezzi_puliti = []
    for match in match_trovati:
        # re.findall restituisce tuple a causa dei due gruppi nella regex, prendiamo quello pieno
        prezzo_str = match[0] if match[0] else match[1]
        
        # Convertiamo il formato italiano (virgola) nel formato Python (punto) e lo facciamo diventare un numero decimale
        prezzo_str = prezzo_str.replace('.', '').replace(',', '.')
        prezzi_puliti.append(float(prezzo_str))
    
    # Rimuoviamo eventuali duplicati esatti
    prezzi_puliti = list(set(prezzi_puliti))
    
    return prezzi_puliti

# --- TESTIAMO LO SCRIPT ---
if __name__ == "__main__":
    oggetto_da_cercare = "Nike Air Force 1"
    lista_prezzi = trova_prezzi_carosello(oggetto_da_cercare)
    
    print("\n✅ Risultati estratti dalla pagina:")
    if lista_prezzi:
        print(f"Prezzi trovati: {lista_prezzi}")
        media = sum(lista_prezzi) / len(lista_prezzi)
        print(f"MEDIA CALCOLATA: {media:.2f} €")
    else:
        print("Nessun prezzo trovato (forse non c'era il carosello shopping).")