from agno.agent import Agent
from agno.models.ollama import Ollama
import json
import re

def estrai_prodotto_da_testo(messaggio_utente: str) -> dict:
    agente = Agent(
        model=Ollama(id="gpt-oss:120b-cloud", host="https://ollama.com"),
        description="Agente che estrae i dati di un prodotto da una richiesta in linguaggio naturale.",
        instructions=[
            "Estrai i dati del prodotto e rispondi SOLO in JSON.",
            "Chiavi obbligatorie: nome, categoria, quantita, prezzo_pagato, descrizione.",
            "Se un valore manca, usa null.",
            "Esempio output: {\"nome\":\"Air Max 90\",\"categoria\":\"Sneakers\",\"quantita\":5,\"prezzo_pagato\":79.99,\"descrizione\":\"Sneaker uomo\"}"
        ]
    )
    risposta = agente.run(messaggio_utente)
    testo = str(risposta.content).strip()

    match = re.search(r'\{.*\}', testo, re.DOTALL)
    if match:
        testo = match.group(0)

    try:
        return json.loads(testo, strict=False)
    except:
        return {"nome": None, "categoria": None, "quantita": None, "prezzo_pagato": None, "descrizione": None}