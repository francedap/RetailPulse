from agno.agent import Agent
from agno.models.ollama import Ollama

def analizza_punti_deboli(df_magazzino):
    """
    Legge la tabella del magazzino e trova il prodotto con le performance peggiori
    in base a giacenza, margine e andamento dei prezzi.
    """
    
    
    if df_magazzino.empty:
        return "Il tuo magazzino è vuoto. Aggiungi qualche prodotto per iniziare l'analisi!"

    
    agente_inventario = Agent(
        model=Ollama(id="gpt-oss:120b-cloud", host="https://ollama.com"),
        description="Sei un analista esperto di inventario e margini di profitto.",
        instructions=[
            "Analizza attentamente le tabelle di dati che riceverai.",
            "Individua il prodotto con il problema più critico.",
            "Nomina chiaramente il prodotto e spiega all'utente perché rappresenta un problema.",
            "Dai un consiglio pratico e diretto per risolvere la situazione.",
            "Sii conciso e breve, professionale e usa le emoji per rendere il testo piacevole."
        ]
    )
    
    
    dati_testo = df_magazzino.to_markdown(index=False)
    
    prompt = f"""
    Ecco i dati attuali del magazzino:
    {dati_testo}
    
    Per favore, trova il punto debole più critico e dammi il tuo suggerimento.
    """
    
 
    
    risposta = agente_inventario.run(prompt)
    
    return risposta.content