# File: core_ai/strategic_advisor_agent.py

from agno.agent import Agent
from agno.models.ollama import Ollama
from dotenv import load_dotenv

# Carichiamo le variabili d'ambiente (se ne hai bisogno in futuro)
load_dotenv()

def genera_sintesi_strategica(valore_totale, margine_totale, in_perdita):
    """
    Questa funzione prende i dati riassuntivi del magazzino e li passa
    all'Intelligenza Artificiale per generare un breve report testuale.
    """
    
    # 1. Configuriamo il nostro agente
    agente_stratega = Agent(
        model=Ollama(id="llama3.2"), # Usiamo lo stesso modello che hai usato negli altri file
        description="Sei un consulente aziendale esperto di logistica e vendite.",
        instructions=[
            "Il tuo compito è scrivere un brevissimo riassunto (massimo 3 o 4 frasi) sullo stato di salute del magazzino.",
            "Usa un tono professionale, chiaro e incoraggiante.",
            "Se i prodotti in perdita sono tanti, consiglia di fare attenzione.",
            "Se il margine è positivo, fai i complimenti all'utente.",
            "Evita formattazioni troppo complesse, rispondi con un discorso fluido e discorsivo."
        ]
    )
    
    # 2. Creiamo il messaggio che l'agente leggerà (il prompt)
    prompt_dati = f"""
    Ecco i dati attuali del magazzino dell'utente:
    - Valore Totale Stimato: € {valore_totale:.2f}
    - Margine Totale Latente (guadagno potenziale): € {margine_totale:.2f}
    - Numero di prodotti attualmente in perdita: {in_perdita}
    
    Per favore, scrivi la tua sintesi strategica basandoti su questi numeri.
    """
    
    # 3. Facciamo elaborare la risposta all'agente
    risposta = agente_stratega.run(prompt_dati)
    
    # Restituiamo solo il testo della risposta
    return risposta.content