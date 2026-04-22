
# 📦 RetailPulse AI

**RetailPulse AI** è un'applicazione web innovativa per la gestione intelligente del magazzino e l'analisi di mercato. Sfrutta modelli di Intelligenza Artificiale (LLM) eseguiti localmente e tecniche di web scraping avanzate per ottimizzare margini, vendite e strategie di acquisto aziendali.

### 👥 Autori del Progetto
* **Francesco Dappiano** - Matricola: 20055270
* **Riccardo Accatino** - Matricola: 20054233

---

## 📑 Indice
1. [Panoramica del Progetto](#1-panoramica-del-progetto)
2. [Scelte Architetturali](#2-scelte-architetturali)
3. [Funzionamento del Sistema](#3-funzionamento-del-sistema)
4. [Struttura del Progetto](#4-struttura-del-progetto)
5. [Vincoli del Sistema](#5-vincoli-del-sistema)
6. [Guida all'Installazione](#6-guida-allinstallazione)
7. [Guida all'Utilizzo](#7-guida-allutilizzo)

---

## 1. Panoramica del Progetto
RetailPulse AI semplifica e automatizza le decisioni strategiche di un'azienda retail. L'applicazione supera il concetto di semplice tracciamento dell'inventario, integrando **agenti IA intelligenti** capaci di analizzare i dati aziendali, identificare inefficienze strutturali, analizzare i trend di mercato e suggerire azioni mirate (Vendere, Acquistare, Attendere) recuperando prezzi aggiornati in tempo reale dal web.

---

## 2. Scelte Architetturali

Il sistema è stato progettato puntando a modularità, facilità di deployment locale e privacy dei dati aziendali.

* **Frontend & Interfaccia Utente (UI):** [Streamlit](https://streamlit.io/)
  * *Motivazione:* Permette lo sviluppo rapido di interfacce web reattive e data-driven direttamente in Python, facilitando l'integrazione immediata con librerie di data science (Pandas) e script di backend.
* **Backend & Core Logic:** Python 3
* **Database:** SQLite3 (`data/retailpulse.db`)
  * *Motivazione:* Database relazionale leggero, zero-configuration e serverless. Ideale per un prototipo dimostrativo e per l'esecuzione locale senza necessità di configurare servizi esterni (es. PostgreSQL/MySQL).
* **Motore Intelligenza Artificiale:** [Agno Framework](https://github.com/agno-ai/agno) + [Ollama](https://ollama.com/) (Modello LLM: `llama3.2`)
  * *Motivazione:* L'utilizzo di Ollama permette di eseguire LLM (Large Language Models) **in locale**. Questa è una scelta architetturale cruciale per garantire la *privacy totale* dei dati sensibili del magazzino aziendale e per abbattere i costi delle API cloud (es. OpenAI). Il framework Agno facilita l'orchestrazione degli agenti IA (Tools, Context, Instructions).
* **Web Scraping & Automazione:** [Playwright](https://playwright.dev/) + Regular Expressions
  * *Motivazione:* Utilizzato all'interno dell'agente IA per recuperare i prezzi in tempo reale (es. da eBay). Playwright, con la gestione di User-Agent dinamici, permette di aggirare blocchi anti-bot di base e banner dei cookie, estraendo l'HTML per il parsing dei prezzi in modo affidabile.
* **Manipolazione Dati:** [Pandas](https://pandas.pydata.org/)
  * *Motivazione:* Essenziale per manipolare i dati estratti da SQLite, calcolare metriche finanziarie (margini, giacenze) e formattare i dati (Markdown) da fornire in pasto agli agenti IA per l'analisi.

---

## 3. Funzionamento del Sistema

Il sistema si articola in 3 moduli principali interagenti:

1. **Dashboard (HomePage):** Aggrega i dati grezzi dal database, calcola i KPI tramite Pandas (Valore totale, Margine latente, Articoli in perdita) e interroga lo `strategic_advisor_agent` per generare un report discorsivo di alto livello sullo stato dell'azienda.
2. **Modulo Magazzino:** Permette il CRUD (Create, Read, Update, Delete) dei prodotti. Utilizza il `cerca_nuovo_prezzo_agent` per eseguire scraping su richiesta, aggiornando dinamicamente il prezzo attuale dell'oggetto nel database.
3. **Modulo Mercato:** Un ambiente di simulazione e ricerca dove il `market_explorer` valuta le opportunità di acquisto esterne, genera trend di categoria e compila report macroeconomici incrociando i dati del DB con la base di conoscenza del LLM.
4. **Assistente Globale (Sidebar):** Il `support_agent` è sempre attivo. Utilizza il contesto dinamico del database aziendale (`get_prodotti_raw`) per rispondere a domande in linguaggio naturale sull'inventario in tempo reale.

---

## 4. Struttura del Progetto

```text
RetailPulse/
│
├── app.py                     # Punto di ingresso dell'app (Login/Registrazione)
├── populate_db.py             # Script per la generazione di dati fittizi
├── requirements.txt           # Dipendenze di progetto
│
├── core_ai/                   # CORE DEL PROGETTO: Logica e Agenti IA
│   ├── cerca_nuovo_prezzo_agent.py # Scraping con Playwright e parsing prezzi
│   ├── inventory_analyst.py        # Analisi punti deboli e giacenze
│   ├── market_explorer.py          # Analisi trend e macroeconomia
│   ├── strategic_advisor_agent.py  # Sintesi rapida aziendale
│   └── support_agent.py            # Chatbot contestualizzato al DB
│
├── pages/                     # Pagine dell'interfaccia Streamlit
│   ├── HomePage.py                 # Dashboard principale
│   ├── Magazzino.py                # Gestione inventario
│   └── Mercato.py                  # Analisi di mercato globale
│
├── components/                # Componenti UI riutilizzabili
│   └── sidebar.py                  # Menu di navigazione e Chatbot UI
│
├── utils/                     # Moduli helper
│   └── db_manager.py               # Logica di astrazione del database SQLite
│
└── data/                      # Persistenza
    └── retailpulse.db              # File del database relazionale
```

---

## 5. Vincoli del Sistema

Per garantire il corretto funzionamento, il sistema presenta i seguenti vincoli operativi:

* **Esecuzione LLM Locale (Ollama):** Il sistema *richiede* che l'applicativo [Ollama](https://ollama.com/) sia installato sulla macchina host e che il modello `llama3.2` sia stato preventivamente scaricato ed eseguito in background. Se Ollama non è in esecuzione, le funzioni di IA crasheranno o restituiranno timeout.
* **Connettività per lo Scraping:** L'agente di ricerca prezzi necessita di una connessione internet attiva per istanziare i browser Chromium (tramite Playwright) e navigare sui marketplace.
* **Compatibilità Browser Playwright:** Al primo avvio, Playwright richiede l'installazione dei binari del browser (gestita solitamente in automatico o tramite il comando `playwright install`).
* **Session State:** L'autenticazione è basata sullo stato di sessione di Streamlit in RAM. Aggiornare brutalmente la pagina (F5) sul browser potrebbe causare un logout imprevisto se il server locale viene riavviato.

---

## 6. Guida all'Installazione

### Prerequisiti
1. **Python 3.10 o superiore** installato.
2. **Ollama** installato sul proprio sistema operativo ([Download qui](https://ollama.com/download)).
3. Scaricare il modello IA aprendo un terminale e digitando:
   ```bash
   ollama run llama3.2
   ```

### Setup Rapido (Script Automatizzati)
Il repository include script per configurare automaticamente l'ambiente.
* **Su Windows:** Fai doppio clic su `setup_windows.bat`
* **Su Mac/Linux:** Apri il terminale, rendi lo script eseguibile con `chmod +x setup_mac_linux.command` e avvialo: `./setup_mac_linux.command`

*(In alternativa, setup manuale)*:
```bash
# 1. Clona il repository e posizionati nella cartella
cd RetailPulse

# 2. Crea l'ambiente virtuale
python -m venv venv

# 3. Attiva l'ambiente virtuale
# Su Windows:
venv\Scripts\activate
# Su Mac/Linux:
source venv/bin/activate

# 4. Installa le librerie richieste
pip install -r requirements.txt

# 5. Installa i browser per Playwright (fondamentale per lo scraping)
playwright install chromium
```

---

## 7. Guida all'Utilizzo

### 7.1. Inizializzazione del Database
Prima del primissimo avvio, è consigliato popolare il database con dati dimostrativi per poter testare le funzionalità analitiche dell'IA:
```bash
python populate_db.py
```
Questo comando creerà l'utente di test e inserirà prodotti fittizi (es. Smartphone, Sneakers) con i relativi storici dei prezzi.

### 7.2. Avvio dell'Applicazione
Assicurati di avere Ollama in esecuzione in background. Successivamente avvia l'app tramite gli script forniti:
* **Su Windows:** Esegui `avvia_windows.bat`
* **Su Mac/Linux:** Esegui `./avvia_mac_linux.command`

*(Avvio manuale dal terminale con ambiente virtuale attivo)*:
```bash
streamlit run app.py
```
L'applicazione si aprirà automaticamente nel tuo browser predefinito (tipicamente all'indirizzo `http://localhost:8501`).

### 7.3. Navigazione
1. **Login:** Utilizza le credenziali predefinite se hai lanciato il popolamento del DB:
   * **Email:** `admin` (oppure l'email configurata in populate_db.py)
   * **Password:** `admin`
2. **Dashboard (Home):** Visualizza i KPI, avvia la "Scansione Punti Deboli" per trovare gli articoli che stanno danneggiando i tuoi margini.
3. **Magazzino:** Visualizza la tabella dei prodotti. Usa il pulsante **"Aggiorna Prezzo ⚡"** per innescare Playwright: vedrai il sistema aprire un browser in modalità headless, cercare il prodotto sul web, parsare i prezzi e aggiornare il database.
4. **Assistente:** Apri la barra laterale (Sidebar) a sinistra e digita una domanda, ad esempio: *"Qual è il prodotto che mi sta facendo perdere più soldi?"*. L'agente leggerà il tuo DB e ti risponderà in tempo reale.

