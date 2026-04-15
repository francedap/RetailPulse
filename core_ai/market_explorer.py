# File: core_ai/market_explorer.py

from agno.agent import Agent
from agno.models.ollama import Ollama
import pandas as pd

def analizza_opportunita_prodotto(nome_prodotto: str) -> str:
    """
    1. Ricerca Opportunità: Valuta un prodotto e fornisce consigli finanziari/di mercato.
    """
    agente = Agent(
        model=Ollama(id="llama3.2"),
        description="Sei un esperto analista di mercato e consulente finanziario per il retail.",
        instructions=[
            "Valuta il prodotto indicato dall'utente.",
            "Spiega brevemente la sua situazione attuale nel mercato globale (è molto richiesto? è passato di moda?).",
            "Fornisci un consiglio tecnico chiaro: è il momento di ACQUISTARE, VENDERE o ATTENDERE?",
            "Spiega il perché del tuo consiglio in modo semplice ma professionale.",
            "Usa formattazione chiara (grassetti, elenchi) e qualche emoji per rendere la lettura piacevole."
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
        model=Ollama(id="llama3.2"),
        description="Sei un analista di tendenze specializzato nei settori retail ed e-commerce.",
        instructions=[
            "Scrivi un breve report sulle tendenze di mercato attuali per la categoria indicata.",
            "Indica quali tipi di prodotti stanno crescendo e quali stanno perdendo interesse in questa categoria.",
            "Fornisci una previsione a breve/medio termine per il settore.",
            "Sii conciso ma molto informativo."
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
        model=Ollama(id="llama3.2"),
        description="Sei un macro-economista e Chief Strategy Officer (CSO) per un'azienda retail.",
        instructions=[
            "Riceverai i dati del magazzino attuale dell'utente.",
            "Fai un'analisi di livello superiore: non guardare solo i singoli prodotti, ma le categorie e l'esposizione al rischio.",
            "Avverti l'utente di possibili 'bolle' di mercato o crisi imminenti legate ai prodotti che possiede.",
            "Suggerisci 'buchi di mercato' o opportunità globali che attualmente mancano nel suo magazzino.",
            "Dividi il report in: '🔥 Opportunità', '⚠️ Rischi e Bolle', e '🎯 Piano d'Azione'."
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