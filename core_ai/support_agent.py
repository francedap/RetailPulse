from agno.agent import Agent
from agno.models.ollama import Ollama 
from dotenv import load_dotenv
import pandas as pd
from utils.db_manager import get_prodotti_raw # Importiamo la funzione per leggere il DB

assistente_magazzino = Agent(
    model=Ollama(id="llama3.2"),
    description="Sei un assistente virtuale per l'app RetailPulse, esperto di gestione magazzino e vendite.",
    instructions=[
        "Rispondi sempre in modo cortese, conciso e incoraggiante.",
        "Sei un esperto di logistica, margine di profitto e trend di mercato.",
        "Il tuo scopo è aiutare l'utente a prendere decisioni basandoti SUI DATI DEL SUO MAGAZZINO che ti verranno forniti.",
        "Se ti chiedono dati specifici (es. quante scarpe ci sono), cerca nella tabella che ti viene passata nel contesto.",
        "Usa emoji per rendere il testo più leggibile."
    ],
    markdown=True
)


def chiedi_all_assistente(messaggio_utente: str, azienda_id: int) -> str:
    """Recupera i dati, crea un prompt arricchito e lo invia all'agente."""
    
    df_prodotti = get_prodotti_raw(azienda_id)
    
    if df_prodotti.empty:
        contesto_dati = "Il magazzino attualmente è VUOTO. Non ci sono prodotti."
    else:
        
        contesto_dati = f"Ecco l'attuale inventario del magazzino:\n{df_prodotti.to_markdown(index=False)}"
        
    prompt_arricchito = f"""
    INFORMAZIONI DI CONTESTO (Non dirlo all'utente, usale solo per rispondere):
    {contesto_dati}
    
    DOMANDA DELL'UTENTE:
    {messaggio_utente}
    """
    
    risposta = assistente_magazzino.run(prompt_arricchito)
    return risposta.content