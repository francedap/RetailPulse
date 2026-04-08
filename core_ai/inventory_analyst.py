# File: core_ai/inventory_analyst.py

from agno.agent import Agent
from agno.models.ollama import Ollama

def analizza_punti_deboli(df_magazzino):
    """
    Legge la tabella del magazzino e trova il prodotto con le performance peggiori
    in base a giacenza e margine.
    """
    
    # Se il magazzino è vuoto, non c'è nulla da analizzare
    if df_magazzino.empty:
        return "Il tuo magazzino è vuoto. Aggiungi qualche prodotto per iniziare l'analisi!"

    # 1. Configuriamo l'agente analista
    agente_inventario = Agent(
        model=Ollama(id="llama3.2"),
        description="Sei un analista esperto di inventario e margini di profitto.",
        instructions=[
            "Analizza attentamente la tabella dati che riceverai.",
            "Individua il prodotto con il problema più critico (es. in perdita economica, oppure fermo in magazzino da troppi giorni senza vendere).",
            "Nomina chiaramente il prodotto e spiega all'utente perché rappresenta un problema (es. 'capitale immobilizzato').",
            "Dai un consiglio pratico e diretto per risolvere la situazione (es. 'Consiglio uno sconto del 10%').",
            "Sii conciso, professionale e usa le emoji per rendere il testo piacevole."
        ]
    )
    
    # 2. Trasformiamo la tabella (DataFrame) in un testo leggibile per l'IA
    dati_testo = df_magazzino.to_markdown(index=False)
    
    prompt = f"""
    Ecco i dati attuali del magazzino:
    {dati_testo}
    
    Per favore, trova il punto debole più critico e dammi il tuo suggerimento.
    """
    
    # 3. Inviamo tutto all'agente
    risposta = agente_inventario.run(prompt)
    
    return risposta.content