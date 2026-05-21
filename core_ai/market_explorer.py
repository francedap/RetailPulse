from agno.agent import Agent
from agno.models.ollama import Ollama
import pandas as pd
import json
import re
from typing import Optional

def crea_agente_analista_prodotto() -> Agent:
    """
    Sotto-Agente: Analizza singoli prodotti da prospettiva B2B/Wholesale.
    Focus su: volumi, margini, redditività, trend commerciali.
    """
    return Agent(
        name="Analista_Prodotto",
        model=Ollama(id="gpt-oss:120b-cloud", host="https://ollama.com"),
        description="Esperto analista di mercato specializzato in strategie wholesale e retail B2B.",
        instructions=[
            "CONTESTO: Sei un consulente finanziario specializzato in COMMERCE B2B/WHOLESALE.",
            "FOCUS: Analizza prodotti dal punto di vista di una AZIENDA COMMERCIALE che compra e rivende.",
            "🚫 IMPORTANTE: NON dare mai consigli su uso personale o acquisti privati.",
            "",
            "Quando analizzi un prodotto, valuta:",
            "  • Margine di profitto lordo: Prezzo di acquisto wholesale vs prezzo di vendita retail",
            "  • Velocità di rotazione: Quanto velocemente si vende il prodotto?",
            "  • Domanda commerciale: Quale volume di aziende lo richiede?",
            "  • Trend di mercato: È in ascesa o in declino come prodotto commerciale?",
            "  • Competizione wholesale: Quanti grossisti offrono lo stesso prodotto?",
            "  • Stoccaggio e logistica: Costi di immagazzinamento per questo tipo di prodotto?",
            "",
            "Fornisci consigli tipo:",
            "  ✅ 'Acquistare 10 paia a €X è redditizio: margine lordo del Y%, ROI stimato in Z mesi'",
            "  ✅ 'Consiglio di comprare in lotto da 25-50 paia per negoziare miglior prezzo'",
            "  ✅ 'Domanda stagnante: aspetta 2-3 mesi prima di fare scorte'",
            "  ✅ 'Nuova collezione lanciata: buona opportunità per entrare early'",
            "",
            "Usa formattazione chiara, emoji commerciali (💰, 📈, ⚠️), sii conciso (max 150 parole)."
        ]
    )


def crea_agente_analista_trend() -> Agent:
    """
    Sotto-Agente: Analizza trend di categorie dal punto di vista B2B.
    """
    return Agent(
        name="Analista_Trend",
        model=Ollama(id="gpt-oss:120b-cloud", host="https://ollama.com"),
        description="Esperto di analisi di trend di mercato per buyer commerciali e rivenditori.",
        instructions=[
            "CONTESTO: Sei un analista di trend specializzato in MARKET INTELLIGENCE B2B.",
            "FOCUS: Analizza categorie di prodotto da prospettiva commerciale wholesale.",
            "🚫 IMPORTANTE: Niente consigli su moda personale o use cases privati.",
            "",
            "Quando analizzi una categoria, scrivi un report che includa:",
            "  • 📈 CRESCITA: Quali sottocategorie crescono? Volumi wholesale in aumento?",
            "  • 📉 DECLINO: Quali stanno perdendo appeal tra i buyer B2B?",
            "  • 💰 MARGINI: Come stanno i margini in questa categoria?",
            "  • 🎯 TARGET: Chi compra all'ingrosso? (boutique, catene, e-commerce?)",
            "  • ⚠️ RISCHI: Oversupply? Prodotti contraffatti? Saturazione mercato?",
            "  • 🔮 PREVISIONI: Cosa succederà nei prossimi 6-12 mesi?",
            "",
            "Usa emoji commerciali, sezioni chiare, linguaggio da buyer B2B.",
            "Max 200 parole, conciso ma completo."
        ]
    )


def crea_agente_cso_strategico() -> Agent:
    """
    Sotto-Agente: CSO - Chief Strategy Officer per azienda commerciale.
    """
    return Agent(
        name="CSO_Strategico",
        model=Ollama(id="gpt-oss:120b-cloud", host="https://ollama.com"),
        description="Chief Strategy Officer specializzato in strategie di portfolio per rivenditori.",
        instructions=[
            "RUOLO: Sei il Chief Strategy Officer di un'azienda retail/wholesale.",
            "CONTESTO: Analizzi il portfolio prodotti dal punto di vista commerciale strategico.",
            "🚫 IMPORTANTE: Focus ESCLUSIVO su decisioni commerciali B2B. Niente consigli personali.",
            "",
            "Quando generi un report strategico, analizza:",
            "  • 🎯 PORTFOLIO RISK: Quali categorie sono a rischio? Troppa concentrazione?",
            "  • 💰 CASH FLOW: Quali prodotti generano cash velocemente? Quali sono 'stuck inventory'?",
            "  • 📊 MIX PRODUTTIVO: Quale dovrebbe essere il rapporto ideale tra categorie?",
            "  • 🔥 HOT OPPORTUNITIES: Trend emergenti da cui entrare early?",
            "  • ⚠️ RED FLAGS: Categorie da evitare o da ridurre?",
            "  • 🎯 ACTION PLAN: Specifiche azioni sulla composizione del magazzino",
            "",
            "Dividi la risposta in: '🔥 Opportunità Commerciali', '⚠️ Rischi di Portfolio', '🎯 Piano d'Azione'",
            "Max 250 parole, linguaggio da executive commerciale."
        ]
    )

def crea_agente_orchestratore() -> Agent:
    """
    Agente Principale: Valuta richieste da prospettiva B2B commerciale.
    VERSIONE LIBERA: Suggerisce anche NUOVE opportunità fuori dal magazzino.
    """
    return Agent(
        name="Orchestratore_Mercato",
        model=Ollama(id="gpt-oss:120b-cloud", host="https://ollama.com"),
        description="Direttore Commerciale e Orchestratore di Mercato B2B.",
        instructions=[
            "RUOLO: Sei il DIRETTORE COMMERCIALE di un'azienda che COMPRA E RIVENDE prodotti.",
            "CONTESTO: Rispondi ESCLUSIVAMENTE da prospettiva B2B/Wholesale commerciale.",
            "🚫 VINCOLO CRITICO: MAI suggerire usi personali, no lifestyle advice, no private buying.",
            "",
            "MAGAZZINO ATTUALE: L'informazione sul magazzino è fornita COME CONTESTO INFORMATIVO.",
            "⭐ IMPORTANTE: NON limitare i tuoi consigli a ciò che è già nel magazzino!",
            "🔍 MISSION: Identifica NUOVE OPPORTUNITÀ e categorie interessanti per l'azienda.",
            "💡 Esempio: Se il magazzino ha solo sneaker Nike, puoi consigliare di esplorare:",
            "   • Sneaker di altri brand (Adidas, Puma, New Balance)",
            "   • Nuove categorie (abbigliamento, accessori, streetwear)",
            "   • Trend emergenti nel market",
            "",
            "ROUTING INTELLIGENTE:",
            "• PRODOTTO SPECIFICO → intenzione: 'prodotto'",
            "• CATEGORIA  → intenzione: 'categoria'",
            "• VISIONE STRATEGICA GLOBALE  → intenzione: 'strategico'",
            "• ALTRI CONSIGLI COMMERCIALI → intenzione: 'generico'",
            "",
            "REGOLE RISPOSTA:",
            "✓ SEMPRE JSON valido, NIENTE testo fuori",
            "✓ Messaggio: 3-4 frasi SPECIFICHE sul B2B (margini, volumi, ROI, commercio)",
            "✓ Tono: Executive/Manager commerciale (professional, data-driven)",
            "✓ Riferisciti al magazzino: 'Visto che vendete sneaker Nike, potrei consigliarvi di esplorare...'",
            "✓ Genera 3 bottoni suggeriti per PROSSIME DOMANDE COMMERCIALI rilevanti",
            "",
            "ESEMPIO RISPOSTA (Magazzino con solo Nike, ma suggerimenti ampi):",
            '{',
            '  "intenzione": "strategico",',
            '  "messaggio": "testo del messaggio ",',
            '  "azioni_suggerite": [',
            '    {"tipo": "button", "label": "testoBottone", "azione": "testoazione"},',
            '    {"tipo": "button", "label": "testoBottone", "azione": "testoazione"},',
            '    {"tipo": "button", "label": "testoBottone", "azione": "testoazione"}',
            '  ]',
            '}',
            "",
            "⚠️ ATTENZIONE: RESTITUISCI SOLO JSON, niente markdown, niente spiegazioni."
        ]
    )


class TeamMarketExplorer:
    """Team multi-agente B2B-focused."""
    
    def __init__(self):
        """Inizializza il team."""
        self.orchestratore = crea_agente_orchestratore()
        self.analista_prodotto = crea_agente_analista_prodotto()
        self.analista_trend = crea_agente_analista_trend()
        self.cso = crea_agente_cso_strategico()
        
    def elabora_messaggio(
        self, 
        messaggio_utente: str,
        df_magazzino: Optional[pd.DataFrame] = None,
        inventario_contesto: Optional[str] = None
    ) -> dict:
        """Elabora messaggio tramite il team B2B."""
    
        if inventario_contesto is None:
            if df_magazzino is not None and not df_magazzino.empty:
                inventario_contesto = df_magazzino.to_markdown(index=False)
            else:
                inventario_contesto = "Il magazzino è attualmente vuoto."
        
        print(f"\n📋 Orchestratore B2B valuta: {messaggio_utente[:100]}...")
        
        prompt_orchestratore = f"""
MAGAZZINO ATTUALE DELL'AZIENDA (Per riferimento e contesto):
{inventario_contesto[:500]}

⭐ NOTA: Il magazzino è fornito per capire il vostro posizionamento attuale, 
ma NON è un vincolo! Analizza ANCHE opportunità NUOVE e CATEGORIE DIVERSE.

RICHIESTA COMMERCIALE:
{messaggio_utente}

Valuta l'intento e rispondi SOLO con un JSON valido strutturato come negli esempi.
Ricorda: ESCLUSIVAMENTE prospettiva B2B commerciale. Suggerisci anche NUOVE OPPORTUNITÀ fuori dal magazzino attuale.
"""
        
        try:
            risposta_orchestratore = self.orchestratore.run(prompt_orchestratore)
            risultato_orchestratore = self._parse_json_response(risposta_orchestratore.content)
            print(f"✅ Orchestratore: intenzione={risultato_orchestratore.get('intenzione')}")
        except Exception as e:
            print(f"❌ Errore Orchestratore: {e}")
            return self._fallback_response(
                "Errore nel processare la richiesta. Riformula con termini commerciali più specifici.",
                []
            )
        
        intenzione = risultato_orchestratore.get("intenzione", "generico")
        
        if intenzione == "prodotto":
            print("→ Delegando a: Analista_Prodotto (B2B)")
            risposta_worker = self._chiama_analista_prodotto(messaggio_utente)
            risultato_orchestratore["messaggio"] = risposta_worker
            risultato_orchestratore["azioni_suggerite"] = [
                {"tipo": "button", "label": "📊 Trend della categoria", "azione": "trend_categoria"},
                {"tipo": "button", "label": "💹 Confronta con competitors", "azione": "margini_competitors"},
                {"tipo": "button", "label": "🎯 Strategia di portfolio", "azione": "strategia_portfolio"}
            ]
            
        elif intenzione == "categoria":
            print("→ Delegando a: Analista_Trend (B2B)")
            risposta_worker = self._chiama_analista_trend(messaggio_utente)
            risultato_orchestratore["messaggio"] = risposta_worker
            risultato_orchestratore["azioni_suggerite"] = [
                {"tipo": "button", "label": "🔍 Analizza prodotto specifico", "azione": "prodotto_specifico"},
                {"tipo": "button", "label": "💰 Margini e redditività", "azione": "margini_redditività"},
                {"tipo": "button", "label": "🎯 Report strategico", "azione": "strategico"}
            ]
            
        elif intenzione == "strategico":
            print("→ Delegando a: CSO_Strategico (B2B)")
            risposta_worker = self._chiama_cso(df_magazzino, messaggio_utente)
            risultato_orchestratore["messaggio"] = risposta_worker
            risultato_orchestratore["azioni_suggerite"] = [
                {"tipo": "button", "label": "📈 Nuove categorie da esplorare", "azione": "nuove_categorie"},
                {"tipo": "button", "label": "🔍 Analizza prodotto", "azione": "prodotto_deepdive"},
                {"tipo": "button", "label": "💼 Diversificazione portfolio", "azione": "diversificazione"}
            ]
        else:
            if not risultato_orchestratore.get("azioni_suggerite"):
                risultato_orchestratore["azioni_suggerite"] = [
                    {"tipo": "button", "label": "🔍 Analizza un prodotto", "azione": "prodotto"},
                    {"tipo": "button", "label": "📊 Esplora nuova categoria", "azione": "nuova_categoria"},
                    {"tipo": "button", "label": "🎯 Strategia di espansione", "azione": "espansione"}
                ]
        
        return {
            "intenzione": risultato_orchestratore.get("intenzione", "generico"),
            "messaggio": risultato_orchestratore.get("messaggio", ""),
            "azioni_suggerite": risultato_orchestratore.get("azioni_suggerite", [])
        }
    
    
    def _chiama_analista_prodotto(self, nome_prodotto: str) -> str:
        """Chiama Analista Prodotto (B2B)."""
        prompt = f"Analizza il potenziale commerciale di: '{nome_prodotto}' dal punto di vista di un'azienda wholesale/retail che lo compra e rivende. Quali sono i margini? Vale la pena comprarne in volume?"
        risposta = self.analista_prodotto.run(prompt)
        return risposta.content
    
    def _chiama_analista_trend(self, categoria: str) -> str:
        """Chiama Analista Trend (B2B)."""
        prompt = f"Genera un report di market intelligence per la categoria: '{categoria}' dal punto di vista di un buyer commerciale B2B. Quali sotto-categorie crescono? Quali margini sono buoni?"
        risposta = self.analista_trend.run(prompt)
        return risposta.content
    
    def _chiama_cso(self, df_magazzino: Optional[pd.DataFrame], contesto: str) -> str:
        """Chiama CSO (B2B)."""
        if df_magazzino is not None and not df_magazzino.empty:
            dati_testo = df_magazzino.to_markdown(index=False)
        else:
            dati_testo = "Il magazzino è attualmente vuoto."
        
        prompt = f"""
Sei il CSO di questa azienda commerciale. Analizza il portfolio attuale:

{dati_testo}

Richiesta: {contesto}

Genera un report strategico dal punto di vista del cash flow, rischio portfolio, opportunità commerciali. 
FOCUS: Decisioni di buying/selling, allocazione capitale, gestione inventario.
"""
        risposta = self.cso.run(prompt)
        return risposta.content
    
    def _parse_json_response(self, testo: str) -> dict:
        """Parse robusto JSON (vedi versione precedente)."""
        testo = testo.strip()
        testo = re.sub(r'```json\n?', '', testo)
        testo = re.sub(r'```\n?', '', testo)
        testo = testo.strip()
        
        try:
            return json.loads(testo, strict=False)
        except json.JSONDecodeError:
            pass
        
        try:
            match = re.search(r'\{.*\}', testo, re.DOTALL)
            if match:
                json_str = match.group(0)
                return json.loads(json_str, strict=False)
        except json.JSONDecodeError:
            pass
        
        print("⚠️ Fallback JSON parsing")
        
        match_intenzione = re.search(r'"intenzione"\s*:\s*"([^"]*)"', testo, re.IGNORECASE)
        intenzione = match_intenzione.group(1) if match_intenzione else "generico"
        
        match_messaggio = re.search(
            r'"messaggio"\s*:\s*"(.*?)"(?:\s*,|\s*\})',
            testo,
            re.IGNORECASE | re.DOTALL
        )
        messaggio = match_messaggio.group(1).strip() if match_messaggio else testo[:200]
        
        azioni = []
        match_azioni = re.search(r'"azioni_suggerite"\s*:\s*\[(.*?)\]', testo, re.IGNORECASE | re.DOTALL)
        if match_azioni:
            azioni_testo = match_azioni.group(1)
            buttons = re.findall(
                r'\{\s*"tipo"\s*:\s*"button"\s*,\s*"label"\s*:\s*"([^"]*)"\s*,\s*"azione"\s*:\s*"([^"]*)"\s*\}',
                azioni_testo,
                re.IGNORECASE
            )
            for label, azione in buttons:
                azioni.append({"tipo": "button", "label": label, "azione": azione})
        
        return {
            "intenzione": intenzione,
            "messaggio": messaggio,
            "azioni_suggerite": azioni if azioni else []
        }
    
    def _fallback_response(self, messaggio: str, azioni: list) -> dict:
        """Fallback B2B."""
        return {
            "intenzione": "errore",
            "messaggio": messaggio or "Errore nel processare la richiesta commerciale.",
            "azioni_suggerite": azioni if azioni else [
                {"tipo": "button", "label": "🔄 Riprova", "azione": "retry"},
                {"tipo": "button", "label": "📊 Vedi report", "azione": "report"},
                {"tipo": "button", "label": "💼 Strategia", "azione": "strategia"}
            ]
        }


_team_instance = None

def get_team() -> TeamMarketExplorer:
    """Singleton team B2B."""
    global _team_instance
    if _team_instance is None:
        _team_instance = TeamMarketExplorer()
    return _team_instance


def interroga_orchestratore(
    messaggio_utente: str,
    df_magazzino: Optional[pd.DataFrame] = None,
    contesto_completo: Optional[str] = None  
) -> dict:
    """
    Funzione principale: interfaccia pubblica per Streamlit.
    Ora accetta il contesto della conversazione precedente.
    """
    team = get_team()
    if contesto_completo:
        messaggio_con_contesto = f"""
            CONTESTO COMPLETO:
                {contesto_completo}

            ---

            NUOVA RICHIESTA DELL'UTENTE:
                {messaggio_utente}
         """
    else:
        messaggio_con_contesto = messaggio_utente
    
    return team.elabora_messaggio(messaggio_con_contesto, df_magazzino)


def analizza_opportunita_prodotto(nome_prodotto: str) -> str:
    team = get_team()
    return team._chiama_analista_prodotto(nome_prodotto)

def analizza_trend_categoria(categoria: str) -> str:
    team = get_team()
    return team._chiama_analista_trend(categoria)

def genera_report_strategico_mercato(df_magazzino: pd.DataFrame) -> str:
    team = get_team()
    return team._chiama_cso(df_magazzino, "Genera un report strategico completo dal punto di vista B2B")