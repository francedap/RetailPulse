


# 📦 RetailPulse AI

**RetailPulse AI** è un'applicazione web per la gestione intelligente del magazzino e l'analisi di mercato. Sfrutta modelli di Intelligenza Artificiale e web scraping per ottimizzare margini, vendite e strategie di acquisto aziendali.

### 👥 Autori del Progetto
* **Francesco Dappiano** - Matricola: 20055270
* **Riccardo Accatino** - Matricola: 20054233

---

## 📑 Indice
1. [Panoramica del Progetto](#1-panoramica-del-progetto)
2. [Scelte Architetturali](#2-scelte-architetturali)
3. [Funzionamento del Sistema](#3-funzionamento-del-sistema)
4. [Struttura del Progetto](#4-struttura-del-progetto)
5. [Guida all'Installazione](#5-guida-allinstallazione)
6. [Guida all'Utilizzo](#6-guida-allutilizzo)
7. [Utilizzo di Strumenti di Intelligenza Artificiale nello Sviluppo](#7-utilizzo-di-strumenti-di-intelligenza-artificiale-nello-sviluppo)

---

## 1. Panoramica del Progetto
RetailPulse semplifica e automatizza le decisioni strategiche di un'azienda retail. L'applicazione usa **agenti AI** capaci di analizzare i dati aziendali, identificare inefficienze strutturali, analizzare i trend di mercato e suggerire azioni mirate (Vendere, Acquistare, Attendere) recuperando prezzi aggiornati in tempo reale dal web tramite scarping web.

---

## 2. Scelte Architetturali

* **Frontend & Interfaccia Utente (UI):** [Streamlit](https://streamlit.io/)
  * *Motivazione:* Permette lo sviluppo rapido di interfacce web reattive in Python, facilitando l'integrazione immediata con librerie di data science (Pandas) e script di backend.
* **Backend & Core Logic:** Python 3.10+
* **Database:** SQLite3 (`data/retailpulse.db`)
  * *Motivazione:* Database relazionale leggero, zero-configuration e serverless. Ideale per un prototipo e per l'esecuzione locale senza necessità di configurare servizi esterni (es. PostgreSQL/MySQL).
* **Motore Intelligenza Artificiale:** [Agno Framework](https://github.com/agno-ai/agno) + [Ollama](https://ollama.com/) (Modello LLM: `gpt-oss:120b-cloud`)
  * *Motivazione:* avevamo inizialmente pensato ad un modello in locale per garantire sicurezza e per non avere limiti nelle richieste possibili, ma per assicurare risposte più precise e tempi di risposta più rapidi siamo stati costretti a passare al modello in cloud  di ollama.
  * Il framework Agno ci facilita l'organizzazione e l'istruzione degli agenti.
* **Web Scraping & Automazione:** [Playwright](https://playwright.dev/) / ScraperAPI + Regular Expressions
  * *Motivazione:* Utilizzato all'interno dell'agente di tracciamento per recuperare i prezzi in tempo reale senza subire blocchi dai marketplace. L'HTML ottenuto viene poi analizzato tramite espressioni regolari matematiche per calcolare la media esatta dei prezzi di mercato.
    
---

## 3. Funzionamento del Sistema
Il sistema si articola in 4 moduli principali strettamente interconnessi:

1. **HomePage:** Aggrega i dati grezzi dal database e calcola i KPI aziendali (Valore totale magazzino, margine latente, articoli in perdita). Integra un agente dedicato che permette di dialogare in linguaggio naturale ed eseguire scansioni istantanee sui colli di bottiglia commerciali.
2. **Modulo Magazzino:** Fornisce un pannello di gestione CRUD completo per l'inserimento, la visualizzazione e la rimozione manuale degli articoli, con categorie dinamiche lette direttamente dal database.
3. **Modulo Mercato:** L'utente interagisce unicamente con un Agente tramite un'interfaccia Chat. L'agente analizza l'intento dell'utente e decide autonomamente quale sotto-agente specializzato attivare, guidando l'utente attraverso bivi decisionali creati mediante una UI generata dinamicamente (bottoni contestuali).
4. **Monitoraggio dei Prezzi in Background (background_monitor.py)** l file gestisce un ciclo continuo che controlla e aggiorna automaticamente i prezzi dei prodotti a catalogo: All'inizio di ogni ciclo, lo script accede al database centralizzato per recuperare l'elenco completo dei prodotti monitorati, prelevando per ciascun articolo l'identificativo univoco, l'azienda di riferimento e l'ultimo prezzo memorizzato. Successivamente, per ogni singolo prodotto in lista, il sistema avvia una ricerca automatizzata interrogando un servizio web dedicato; questo analizza i canali di shopping online per calcolare il prezzo medio di vendita corrente per quel determinato articolo.

---

## 4. Struttura del Progetto
```text
RetailPulse/
│
├── app.py                     # Punto di ingresso dell'app (Login/Registrazione)
├── populate_db.py             # Script per la generazione e il ripopolamento dei dati di test
├── background_monitor.py      # Script indipendente per l'Agente Silente (Monitoraggio prezzi)
├── requirements.txt           # Dipendenze e librerie di progetto
│
├── core_ai/                   # CORE LOGIC: Definizione ed esecuzione degli Agenti IA
│   ├── cerca_nuovo_prezzo_agent.py # Scraper logico con parsing matematico dei prezzi
│   ├── inventory_analyst.py        # Sotto-Agente specializzato nell'analisi delle giacenze critiche
│   ├── market_explorer.py          # Agente Orchestratore di Mercato e relativi Sotto-Agenti di Trend
│   ├── strategic_advisor_agent.py  # Consulente per la HomePage e gestione dei KPI
│   └── support_agent.py            # Chatbot della Sidebar contestualizzato all'inventario
│
├── pages/                     # SCHERMATE FRONTEND (Gestite da Streamlit)
│   ├── HomePage.py                 # Dashboard principale con l'Orchestratore Aziendale
│   ├── Magazzino.py                # Interfaccia di gestione e azioni rapide sull'inventario
│   └── Mercato.py                  # Schermata di chat interattiva con UI Dinamica
│
├── components/                # COMPONENTI UI RIUTILIZZABILI
│   └── sidebar.py                  # Menu laterale di navigazione con Assistente di Supporto integrato
│
├── utils/                     # UTILITY E HELPER
│   └── db_manager.py               # Layer di astrazione per query e interazioni con SQLite3
│
└── data/                      # PERSISTENZA DATI
    └── retailpulse.db              # Database relazionale dell'applicazione

```

---

---

## 5. Guida all'Installazione

### Prerequisiti

1. **Python 3.10 o superiore** installato.
2. **Ollama** installato sul proprio sistema operativo.
3. **.env** creato un file .env nella cartella principale del progetto con le API key: OLLAMA_API_KEY="la_tua_api_key_di_ollama"
SCRAPER_API_KEY="la_tua_api_key_di_scraperapi"


### Setup Rapido (Script Automatizzati)

Il repository include script per configurare automaticamente l'ambiente virtuale e installare le librerie:

* **Su Windows:** Fare doppio clic sul file `setup_windows.bat`
* **Su Mac/Linux:** Aprire il terminale, concedere i permessi e avviare lo script:
```bash
chmod +x setup_mac_linux.command
./setup_mac_linux.command

```



*(In alternativa, per l'installazione manuale)*:

```bash
cd RetailPulse
python -m venv venv
# Su Windows:
venv\Scripts\activate
# Su Mac/Linux:
source venv/bin/activate
pip install -r requirements.txt

```

---

## 6. Guida all'Utilizzo

### 6.1. Inizializzazione del Database

Prima del primo avvio assoluto, popolare il database relazionale SQLite con l'utente amministratore predefinito e gli articoli di prova:

```bash
python populate_db.py

```

### 6.2. Avvio dell'Applicazione

Per visualizzare ed eseguire l'intero ecosistema software, è necessario aprire due terminali separati (assicurandosi di aver attivato l'ambiente virtuale `venv` in entrambi):

1. **Terminale 1 - Interfaccia Utente (Streamlit):**
```bash
streamlit run app.py

```
*(Oppure avviare tramite `avvia_windows.bat` / `./avvia_mac_linux.command`)*.


2. **Terminale 2 - Agente Silente (Background Monitor):**
```bash
python background_monitor.py

```



### 6.3. Credenziali di Accesso di Test

Al rendering della schermata di login, inserire le credenziali precompilate dallo script di popolarità:

* **Email:** `admin`
* **Password:** `admin`

### 6.4. Navigazione Flussi

* **HomePage:** Consultazione dei KPI finanziari e interazione libera con l'Orchestratore Aziendale per generare grafici storici sui trend dei prezzi o individuare i punti deboli del magazzino.
* **Magazzino:** Visualizzazione tabellare dell'inventario. È possibile inserire un nuovo prodotto tramite form controllato o forzare l'aggiornamento istantaneo del prezzo di un singolo articolo.
* **Mercato:** Interfaccia Chat-First avanzata. Scrivendo una richiesta all'Orchestratore Principale (es. *"Vorrei analizzare il mercato dell'elettronica"*), l'agente risponderà fornendo spiegazioni dettagliate e iniettando dinamicamente bottoni decisionali nel flusso di chat per attivare i lavoratori verticali.

---

## 7. Utilizzo di Strumenti di Intelligenza Artificiale nello Sviluppo

Nel pieno rispetto delle linee guida stabilite per l'esame, si dichiara l'utilizzo di strumenti di Intelligenza Artificiale Generativa come supporto (Co-Piloting) durante la progettazione e la stesura del codice di questo applicativo.

L'apporto dell'IA è stato integrato per ottimizzare i flussi di lavoro e risolvere colli di bottiglia algoritmici, lasciando inalterata la paternità intellettuale, la scelta architetturale e la supervisione logica del codice da parte degli sviluppatori.

**Dettaglio degli strumenti utilizzati e ambiti di applicazione specifici:**

* **Google Gemini / ChatGPT (Supporto Architetturale e Problem Solving):**
* **Ingegnerizzazione Multi-Agente (Sezione Mercato):** Utilizzati per strutturare la logica del file `core_ai/market_explorer.py` e il routing dei messaggi in `pages/Mercato.py`. Hanno supportato la definizione dei prompt di sistema affinché l'Orchestratore producesse risposte JSON stabili, necessarie al frontend di Streamlit per interpretare l'intento e generare dinamicamente componenti grafici (bottoni contestuali per bivi decisionali) bypassando la rigidità della UI classica.
* **Sviluppo dell'Agente Silente Asincrono:** Utilizzati in fase di brainstorming per superare il limite nativo di Streamlit legato al blocco dei thread causato dai cicli di re-run continui. Questo supporto ha guidato la scelta architetturale di separare l'agente di monitoraggio in un processo demone indipendente (`background_monitor.py`) comunicante via polling sul database SQLite.
* **Raffinamento Documentale:** Supporto nella formattazione e organizzazione strutturale della presente documentazione tecnica.


* **GitHub Copilot / IDE AI Assistants (Autocompletamento e Velocizzazione Codice):**
* **Struttura Database e Modulo CRUD:** Autocompletamento sintattico nella scrittura delle istruzioni SQL standard (`CREATE TABLE`, `INSERT INTO`, `SELECT JOIN`) situate all'interno di `utils/db_manager.py`.
* **Generazione dei Dati di Test:** Scrittura assistita del dizionario dati e delle tuple di mock inserite nel file `populate_db.py` per simulare l'andamento e le fluttuazioni storiche dei prezzi dei prodotti.
* **Boilerplate Streamlit:** Scrittura dei componenti ripetitivi della UI (gestione dei form, allocazione delle colonne `st.columns` e configurazione iniziale delle pagine).


```
