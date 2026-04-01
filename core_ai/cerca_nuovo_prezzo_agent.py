
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.tavily import TavilyTools

# Carica le variabili d'ambiente
load_dotenv()

def crea_agente_prezzi():
    # Creiamo l'agente senza i parametri extra di visualizzazione
    agente = Agent(
        model=Gemini(id="gemini-2.5-flash"), 
        tools=[TavilyTools()],
        instructions=[
            "Sei un esperto di mercato.",
            "Il tuo compito è trovare il prezzo attuale di un prodotto.",
            "Usa lo strumento di ricerca per trovare fonti affidabili.",
            "Converti sempre il prezzo finale in Euro."
        ]
    )
    return agente
