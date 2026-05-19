import json
import pandas as pd
import re
from agno.agent import Agent
from agno.models.ollama import Ollama

def genera_sintesi_strategica(valore_totale, margine_totale, in_perdita):
    """
    Questa funzione prende i dati riassuntivi del magazzino e li passa
    all'Intelligenza Artificiale per generare un breve report testuale.
    """
    
    
    agente_stratega = Agent(
        model=Ollama(id="gpt-oss:120b-cloud", host="https://ollama.com"),
        description="Sei un consulente aziendale esperto di logistica e vendite.",
        instructions=[
            "Il tuo compito è scrivere un brevissimo riassunto (massimo 3 o 4 frasi) sullo stato di salute del magazzino.",
            "Usa un tono professionale, chiaro e incoraggiante.",
            "Se i prodotti in perdita sono tanti, consiglia di fare attenzione.",
            "Se il margine è positivo, fai i complimenti all'utente.",
            "Evita formattazioni troppo complesse, rispondi con un discorso fluido e discorsivo."
        ]
    )
    
    
    prompt_dati = f"""
    Ecco i dati attuali del magazzino dell'utente:
    - Valore Totale Stimato: € {valore_totale:.2f}
    - Margine Totale Latente (guadagno potenziale): € {margine_totale:.2f}
    - Numero di prodotti attualmente in perdita: {in_perdita}
    
    Per favore, scrivi la tua sintesi strategica basandoti su questi numeri.
    """
    
    
    risposta = agente_stratega.run(prompt_dati)
    
    
    return risposta.content

def interroga_orchestratore_home(messaggio_utente: str, df_magazzino: pd.DataFrame, kpi_data: dict) -> dict:
    """
    Agente Orchestratore per la HomePage: analizza la situazione, i KPI 
    e restituisce un JSON con messaggio e nuovi bottoni contestuali.
    """
    if df_magazzino is not None and not df_magazzino.empty:
        inventario_testo = df_magazzino.to_markdown(index=False)
    else:
        inventario_testo = "Il magazzino è attualmente vuoto."

    valore = kpi_data.get('valore_totale', 0)
    margine = kpi_data.get('margine_totale', 0)
    perdite = kpi_data.get('prodotti_in_perdita', 0)

    agente_orchestratore = Agent(
        model=Ollama(id="gpt-oss:120b-cloud", host="https://ollama.com"),
                     
        description="Sei l'Orchestratore della Dashboard Principale di RetailPulse, un brillante Chief Strategy Officer.",
        instructions=[
            f"L'utente sta guardando la dashboard aziendale. Ecco i KPI attuali:\n- Valore Magazzino: €{valore:.2f}\n- Margine Latente: €{margine:.2f}\n- Prodotti in perdita: {perdite}",
            f"Questo è il magazzino attuale:\n{inventario_testo}",
            "REGOLE DI RISPOSTA:",
            "1. RISPONDI IN MODO COMPLETO E DETTAGLIATO. Non essere sbrigativo. Giustifica le tue idee.",
            "2. DEVI INVENTARE 2 o 3 bottoni dinamici che suggeriscano all'utente i prossimi passi (es. 'Strategia di recupero perdite', 'Taglio prezzi', 'Esplora nuovi trend'). Non usare i vecchi bottoni di default se non ha senso.",
            "3. Restituisci la tua risposta SOLO ed ESCLUSIVAMENTE in formato JSON con le chiavi 'messaggio' e 'bottoni' (lista di stringhe)."
        ]
    )
    
    risposta = agente_orchestratore.run(messaggio_utente)
    testo_risposta = str(risposta.content).strip()
    
    # 1. Pulizia: Se l'IA aggiunge testo prima o dopo il JSON, cerchiamo di isolare solo le parentesi graffe
    match_json = re.search(r'\{.*\}', testo_risposta, re.DOTALL)
    if match_json:
        testo_risposta = match_json.group(0)

    try:
        # Tentativo primario: Parsing pulito del JSON
        return json.loads(testo_risposta, strict=False)
        
    except json.JSONDecodeError:
        # 2. PIANO DI EMERGENZA (Regex): L'IA ha sbagliato a scrivere il JSON.
        # Andiamo a caccia del testo e dei bottoni ignorando la sintassi rotta.
        messaggio_pulito = "Ho analizzato i dati, ma ho avuto un piccolo problema a formattare la risposta. Come vuoi procedere?"
        bottoni_puliti = ["Sintesi Strategica", "Trend Prezzi"] # Fallback estremo
        
        # Estrae il contenuto della chiave "messaggio"
        match_msg = re.search(r'"messaggio"\s*:\s*"(.*?)"(?:\s*,|\s*\})', testo_risposta, re.IGNORECASE | re.DOTALL)
        if match_msg:
            # Rimuoviamo eventuali doppi apici interni che hanno rotto il JSON
            messaggio_pulito = match_msg.group(1).replace('"', "'").strip()
            
        # Estrae il contenuto dell'array "bottoni" e cerca le singole stringhe
        match_bottoni = re.search(r'"bottoni"\s*:\s*\[(.*?)\]', testo_risposta, re.IGNORECASE | re.DOTALL)
        if match_bottoni:
            # Trova tutte le parole racchiuse tra virgolette dentro l'array
            items = re.findall(r'"([^"]*)"', match_bottoni.group(1))
            if items:
                bottoni_puliti = items
                
        return {
            "messaggio": messaggio_pulito,
            "bottoni": bottoni_puliti
        }