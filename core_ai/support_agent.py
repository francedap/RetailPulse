from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import pandas as pd
from utils.db_manager import get_prodotti_raw # Importiamo la funzione per leggere il DB

load_dotenv() 

assistente_magazzino = Agent(
    model=Gemini(id="gemini-2.5-flash"),
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

# Aggiungiamo l'ID dell'azienda come parametro obbligatorio
def chiedi_all_assistente(messaggio_utente: str, azienda_id: int) -> str:
    """Recupera i dati, crea un prompt arricchito e lo invia all'agente."""
    
    # 1. Recuperiamo i dati grezzi dal database
    df_prodotti = get_prodotti_raw(azienda_id)
    
    # 2. Trasformiamo la tabella in testo per farla leggere all'IA
    if df_prodotti.empty:
        contesto_dati = "Il magazzino attualmente è VUOTO. Non ci sono prodotti."
    else:
        # Trasforma il DataFrame in una stringa leggibile (formato Markdown)
        contesto_dati = f"Ecco l'attuale inventario del magazzino:\n{df_prodotti.to_markdown(index=False)}"
        
    # 3. Creiamo il super-messaggio segreto da inviare a Gemini
    prompt_arricchito = f"""
    INFORMAZIONI DI CONTESTO (Non dirlo all'utente, usale solo per rispondere):
    {contesto_dati}
    
    DOMANDA DELL'UTENTE:
    {messaggio_utente}
    """
    
    # 4. Inviamo tutto a Gemini
    risposta = assistente_magazzino.run(prompt_arricchito)
    return risposta.content