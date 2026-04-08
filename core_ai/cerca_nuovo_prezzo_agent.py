import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.duckduckgo import DuckDuckGoTools

# Carica le variabili d'ambiente
load_dotenv()

def crea_agente_prezzi():
    # Creiamo l'agente senza i parametri extra di visualizzazione
    agente = Agent(
        model=Ollama(id="llama3.2"), 
        tools=[DuckDuckGoTools()],
        instructions=[
            "Sei un esperto di mercato.",
            "Il tuo compito è trovare il prezzo attuale di un prodotto.",
            "Usa lo strumento di ricerca per trovare fonti affidabili.",
            "Converti sempre il prezzo finale in Euro."
        ]
    )
    return agente