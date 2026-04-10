import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.duckduckgo import DuckDuckGoTools
from pydantic import BaseModel, Field

# Carica le variabili d'ambiente
load_dotenv()

def crea_agente_prezzi():
    return Agent(
        model=Ollama(id="llama3.2"), 
        tools=[DuckDuckGoTools()],
        instructions=[
            "Sei un analista di prezzi specializzato in comparatori online.",
            "Oggi è il 2026. Ignora i dati vecchi.",
            "Riceverai risultati da siti come Trovaprezzi o Idealo.",
            "1. Cerca il prezzo del prodotto NUOVO.",
            "2. Se vedi una lista di prezzi, calcola la media dei primi 3 risultati pertinenti.",
            "3. IMPORTANTE: Scarta i prezzi troppo bassi (es. sotto i 100€ per elettronica costosa) perché sono sicuramente errori o accessori.",
            "4. Rispondi SEMPRE e SOLO con il numero decimale (punto per i decimali, niente virgole delle migliaia).",
            "5. Se non trovi nulla, rispondi 0.0"
        ],
    )
    