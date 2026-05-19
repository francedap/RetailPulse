from agno.agent import Agent
from agno.models.ollama import Ollama
import pandas as pd
import json

def analizza_opportunita_prodotto(nome_prodotto: str) -> str:
    """
    1. Ricerca Opportunità: Valuta un prodotto e fornisce consigli finanziari/di mercato.
    """
    agente = Agent(
        model=Ollama(id="gpt-oss:120b-cloud", host="https://ollama.com"),
        description="Sei un esperto analista di mercato e consulente finanziario per il retail.",
        instructions=[
            "Valuta il prodotto indicato dall'utente.",
            "Spiega brevemente la sua situazione attuale nel mercato globale (è molto richiesto? è passato di moda?).",
            "Fornisci un consiglio tecnico chiaro: è il momento di ACQUISTARE, VENDERE o ATTENDERE?",
            "Spiega il perché del tuo consiglio in modo semplice ma professionale.",
            "Usa formattazione chiara (grassetti, elenchi) e qualche emoji per rendere la lettura piacevole."
            "Sii breve, conciso ma molto informativo."
        ]
    )
    
    prompt = f"Analizza il potenziale di mercato di questo prodotto: '{nome_prodotto}'. Cosa mi consigli di fare?"
    risposta = agente.run(prompt)
    return risposta.content

def analizza_trend_categoria(categoria: str) -> str:
    """
    2. Trend delle Categorie: Genera un report sull'andamento di una specifica categoria.
    """
    agente = Agent(
        model=Ollama(id="gpt-oss:120b-cloud", host="https://ollama.com"),
        description="Sei un analista di tendenze specializzato nei settori retail ed e-commerce.",
        instructions=[
            "Scrivi un breve report sulle tendenze di mercato attuali per la categoria indicata.",
            "Indica quali tipi di prodotti stanno crescendo e quali stanno perdendo interesse in questa categoria.",
            "Fornisci una previsione a breve/medio termine per il settore.",
            "Sii breve, conciso ma molto informativo."
        ]
    )
    
    prompt = f"Genera un report di mercato per la categoria: '{categoria}'."
    risposta = agente.run(prompt)
    return risposta.content

def genera_report_strategico_mercato(df_magazzino: pd.DataFrame) -> str:
    """
    3. Report Strategico: Confronta il magazzino con i rischi/opportunità globali.
    """
    agente = Agent(
        model=Ollama(id="gpt-oss:120b-cloud", host="https://ollama.com"),
        description="Sei un macro-economista e Chief Strategy Officer (CSO) per un'azienda retail.",
        instructions=[
            "Riceverai i dati del magazzino attuale dell'utente.",
            "Fai un'analisi di livello superiore: non guardare solo i singoli prodotti, ma le categorie e l'esposizione al rischio.",
            "Avverti l'utente di possibili 'bolle' di mercato o crisi imminenti legate ai prodotti che possiede.",
            "Suggerisci 'buchi di mercato' o opportunità globali che attualmente mancano nel suo magazzino.",
            "Dividi il report in: '🔥 Opportunità', '⚠️ Rischi e Bolle', e '🎯 Piano d'Azione'."
            "Sii breve, conciso ma molto informativo."
        ]
    )
    
    if df_magazzino.empty:
         dati_testo = "Il magazzino attualmente è vuoto."
    else:
         dati_testo = df_magazzino.to_markdown(index=False)
         
    prompt = f"""
    Basandoti sulla tua conoscenza del mercato globale attuale e guardando questo magazzino:
    {dati_testo}
    
    Genera un resoconto strategico per l'azienda.
    """
    risposta = agente.run(prompt)
    return risposta.content

import json

def interroga_orchestratore(messaggio_utente: str, df_magazzino: pd.DataFrame = None) -> dict:
    """
    Agente Orchestratore: Valuta l'intento dell'utente, guarda il magazzino attuale
    e restituisce un JSON con consigli approfonditi e i bottoni.
    """
    
    # Prepariamo il testo del magazzino da far leggere all'IA
    if df_magazzino is not None and not df_magazzino.empty:
        inventario_testo = df_magazzino.to_markdown(index=False)
    else:
        inventario_testo = "Il magazzino è attualmente vuoto."

    agente_orchestratore = Agent(
        model=Ollama(id="gpt-oss:120b-cloud", host="https://ollama.com"),
        description="Sei il Direttore Strategico (CSO) e Analista Finanziario del Mercato Retail.",
        instructions=[
            "L'utente ti chiederà consigli strategici su cosa acquistare o esplorare.",
            f"DATI DI CONTESTO OBBIGATORI - Questo è il magazzino attuale dell'utente:\n{inventario_testo}",
            "REGOLE DI RISPOSTA:",
            "1. NON ESSERE SBRIGATIVO. Quando ti viene chiesto un consiglio, scrivi una risposta argomentata di almeno 3-4 frasi.",
            "2. Fai riferimento ai prodotti che l'utente ha già nel magazzino per giustificare i tuoi suggerimenti (es. 'Visto che vendi molta elettronica...').",
            "3. Usa un tono da vero esperto finanziario e logistico (usa emoji per rendere la lettura piacevole).",
            "4. I BOTTONI DINAMICI: Puoi suggerire i 3 strumenti base ('Analisi Prodotto', 'Trend Categoria', 'Report Strategico'). INOLTRE, DEVI INVENTARE 1 o 2 bottoni nuovi e dinamici basati su quello di cui state parlando (es. se parlate di elettronica, crea un bottone 'Esplora fornitori Smartphone').",
            "REGOLA FONDAMENTALE: DEVI SEMPRE rispondere SOLO e SOLTANTO con un oggetto JSON valido. Nessun testo fuori dal JSON.",
            "Il JSON deve avere due chiavi:",
            "- 'messaggio': la tua risposta dettagliata e argomentata.",
            "- 'bottoni': una lista di opzioni da cliccare (es. i tuoi bottoni inventati e/o quelli di default)."
        ]
    )
    
    risposta = agente_orchestratore.run(messaggio_utente)
    testo_risposta = risposta.content
    
    testo_risposta = testo_risposta.replace("```json", "").replace("```", "").strip()
    
    try:
        # Aggiungiamo strict=False per permettere all'IA di usare gli "a capo" reali!
        return json.loads(testo_risposta, strict=False)
    
    except json.JSONDecodeError:
        # NUOVO PIANO DI EMERGENZA: Se fallisce, usiamo una Regex per estrarre 
        # solo il testo puro e nascondere le parentesi graffe e i marker JSON.
        import re
        match_msg = re.search(r'"messaggio"\s*:\s*"(.*?)"\s*(?:,|\})', testo_risposta, re.IGNORECASE | re.DOTALL)
        
        if match_msg:
            messaggio_pulito = match_msg.group(1).strip()
        else:
            messaggio_pulito = testo_risposta.replace('{"messaggio":', '').replace('"bottoni":', '').replace('}','').replace('"','').replace('[', '').replace(']', '').strip()
            
        return {
            "messaggio": messaggio_pulito,
            "bottoni": ["Analisi Prodotto", "Trend Categoria", "Report Strategico"]
        }