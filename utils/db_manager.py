import sqlite3
import pandas as pd
import hashlib # Libreria integrata in Python per criptare le password
import numpy as np
from datetime import datetime, timedelta
import re

DB_PATH = "data/retailpulse.db"


def init_db():
    """Inizializza il database con le tabelle relazionali necessarie."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Tabella Utenti
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS utenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # 2. Tabella Aziende
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aziende (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            id_proprietario INTEGER NOT NULL,
            FOREIGN KEY (id_proprietario) REFERENCES utenti (id)
        )
    ''')

    # 3. Tabella Prodotti
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prodotti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_azienda INTEGER NOT NULL,
            nome TEXT NOT NULL,
            descrizione TEXT,
            categoria TEXT,
            quantita INTEGER NOT NULL DEFAULT 1,
            prezzo_pagato REAL NOT NULL,
            prezzo_attuale REAL NOT NULL,
            data_inserimento DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (id_azienda) REFERENCES aziende (id)
        )
    ''')

    # 4. Tabella Storico Prezzi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            update_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    

    conn.commit()
    conn.close()

def hash_password(password):
    """Cripta la password usando SHA-256 per non salvarla in chiaro nel DB."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(nickname, email, password, nome_azienda):
    """Registra un nuovo utente e crea la sua azienda associata."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Inserisce l'utente con la password criptata
        cursor.execute('''
            INSERT INTO utenti (nickname, email, password) 
            VALUES (?, ?, ?)
        ''', (nickname, email, hash_password(password)))
        
        user_id = cursor.lastrowid # Prende l'ID appena generato
        
        # 2. Inserisce l'azienda collegandola all'utente appena creato
        cursor.execute('''
            INSERT INTO aziende (nome, id_proprietario) 
            VALUES (?, ?)
        ''', (nome_azienda, user_id))
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Questo errore scatta perché abbiamo impostato l'email come UNIQUE nel DB
        return False 
    finally:
        conn.close()

def verify_login(email, password):
    """Verifica le credenziali e restituisce i dati dell'utente se corrette."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Cerca l'utente facendo il JOIN con l'azienda per recuperare entrambi gli ID
    cursor.execute('''
        SELECT u.id, a.id, u.nickname 
        FROM utenti u
        JOIN aziende a ON u.id = a.id_proprietario
        WHERE u.email = ? AND u.password = ?
    ''', (email, hash_password(password)))
    
    result = cursor.fetchone()
    conn.close()
    
    # Restituisce (user_id, azienda_id, nickname) se trovato, altrimenti None
    return result

def get_nome_azienda(azienda_id):
    """Recupera il nome dell'azienda dato il suo ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM aziende WHERE id = ?", (azienda_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "La Tua Azienda"

def get_dati_magazzino(azienda_id):
    """Estrae i prodotti e calcola i giorni di giacenza usando SQL."""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT 
            nome as Prodotto,
            prezzo_pagato as Prezzo_Acquisto,
            prezzo_attuale as Prezzo_Mercato,
            quantita as Quantita,
            CAST((julianday('now') - julianday(data_inserimento)) AS INTEGER) as Giorno_Giacenza
        FROM prodotti
        WHERE id_azienda = ?
    """
    df = pd.read_sql_query(query, conn, params=(azienda_id,))
    conn.close()
    return df

def add_prodotto(id_azienda, nome, descrizione, categoria, quantita, prezzo_pagato, prezzo_attuale):
    """Inserisce un nuovo prodotto nel database associandolo all'azienda."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # La data di inserimento viene presa in automatico (CURRENT_DATE nel DB)
    cursor.execute('''
        INSERT INTO prodotti (id_azienda, nome, descrizione, categoria, quantita, prezzo_pagato, prezzo_attuale)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (id_azienda, nome, descrizione, categoria, quantita, prezzo_pagato, prezzo_attuale))
    
    conn.commit()
    conn.close()

def get_prodotti_raw(azienda_id):
    """Recupera tutti i campi dei prodotti per la tabella del magazzino."""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT id, nome, descrizione, categoria, quantita, prezzo_pagato, prezzo_attuale, data_inserimento 
        FROM prodotti 
        WHERE id_azienda = ?
        ORDER BY data_inserimento DESC
    """
    df = pd.read_sql_query(query, conn, params=(azienda_id,))
    conn.close()
    return df

def update_prezzo_prodotto(prodotto_id, nuovo_prezzo):
    """Aggiorna il prezzo attuale di un prodotto nel database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE prodotti
        SET prezzo_attuale = ?
        WHERE id = ?
    ''', (nuovo_prezzo, prodotto_id))
    conn.commit()
    conn.close()

def delete_prodotto(prodotto_id):
    """Rimuove definitivamente un prodotto dal database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prodotti WHERE id = ?", (prodotto_id,))
    conn.commit()
    conn.close()


# Puoi richiamare init_db() in fondo a questo file per testarlo subito
if __name__ == "__main__":
    init_db()
    print("Database e tabelle creati con successo!")

def get_dati_trend_temporale(azienda_id):
    """
    Genera dati simulati per il trend di mercato dal momento dell'acquisto a oggi.
    Crea un punto per OGNI GIORNO per garantire linee continue sul grafico.
    """
    import numpy as np
    from datetime import datetime, timedelta
    
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT nome, prezzo_pagato, prezzo_attuale, data_inserimento 
        FROM prodotti 
        WHERE id_azienda = ?
    """
    df = pd.read_sql_query(query, conn, params=(azienda_id,))
    conn.close()

    if df.empty:
        return pd.DataFrame()

    today = datetime.now().date()
    all_data = []

    for index, row in df.iterrows():
        # Leggiamo la data di acquisto
        data_acquisto = datetime.strptime(row['data_inserimento'], '%Y-%m-%d').date()
        giorni_passati = (today - data_acquisto).days
        
        # Se il prodotto è stato aggiunto oggi, simuliamo 2 giorni per tracciare la linea
        if giorni_passati < 1:
            giorni_passati = 1
            data_acquisto = today - timedelta(days=1)

        # MAGIA: Creiamo un punto per OGNI SINGOLO GIORNO passato
        for d in range(giorni_passati + 1):
            data_punto = data_acquisto + timedelta(days=d)
            quota = d / giorni_passati # Percentuale di tempo trascorso (da 0.0 a 1.0)
            
            # Calcoliamo il prezzo in quel giorno
            prezzo_base = row['prezzo_pagato'] + (row['prezzo_attuale'] - row['prezzo_pagato']) * quota
            
            # Aggiungiamo un piccolo "rumore di mercato" casuale, ma non al primo o all'ultimo giorno
            noise = prezzo_base * np.random.uniform(-0.015, 0.015) if 0 < d < giorni_passati else 0
            
            all_data.append({
                "Data": data_punto,
                "Prodotto": row['nome'],
                "Prezzo (€)": round(prezzo_base + noise, 2)
            })

    return pd.DataFrame(all_data)

def estrai_prezzo_da_testo(testo):
    """Estrae il valore numerico più alto da una stringa (il prezzo)."""
    testo_str = str(testo)
    # Cerca numeri decimali o interi
    numeri = re.findall(r"[-+]?\d*\.\d+|\d+", testo_str.replace(',', '.'))
    if not numeri:
        return None
    # Convertiamo e prendiamo il massimo (spesso l'IA cita il modello o quantità, il prezzo è il valore più alto)
    numeri_float = [float(n) for n in numeri]
    return max(numeri_float)

def log_price_update(product_id, price):
    """Registra un aggiornamento di prezzo nello storico."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO price_updates (product_id, price)
        VALUES (?, ?)
    ''', (product_id, price))
    conn.commit()
    conn.close()

def get_price_history(product_id):
    """Recupera lo storico prezzi di un prodotto."""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT price, update_date 
        FROM price_updates 
        WHERE product_id = ?
        ORDER BY update_date ASC
    """
    df = pd.read_sql_query(query, conn, params=(product_id,))
    conn.close()
    return df

def get_all_price_updates(azienda_id):
    """Recupera TUTTI gli aggiornamenti prezzi di tutti i prodotti di un'azienda."""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT p.nome as Prodotto, pu.price, pu.update_date
        FROM price_updates pu
        JOIN prodotti p ON pu.product_id = p.id
        WHERE p.id_azienda = ?
        ORDER BY pu.update_date ASC
    """
    df = pd.read_sql_query(query, conn, params=(azienda_id,))
    conn.close()
    return df
