import sqlite3
import hashlib
from datetime import datetime, timedelta

DB_PATH = "data/retailpulse.db"

def hash_password(password):
    """Cripta la password usando SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def populate_db():
    """Popola il database con dati di test."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # ===== UTENTE =====
        cursor.execute('''
            INSERT INTO utenti (nickname, email, password) 
            VALUES (?, ?, ?)
        ''', ('admin', 'admin', hash_password('admin')))
        
        user_id = cursor.lastrowid
        print(f"✅ Utente creato con ID: {user_id}")
        
        # ===== AZIENDA =====
        cursor.execute('''
            INSERT INTO aziende (nome, id_proprietario) 
            VALUES (?, ?)
        ''', ('admin', user_id))
        
        azienda_id = cursor.lastrowid
        print(f"✅ Azienda creata con ID: {azienda_id}")
        
        # ===== PRODOTTI =====
        prodotti = [
            (azienda_id, 'Nike Air Force 1', 'Scarpe bianche classic, unisex, taglia 42', 'Sneakers', 8, 89.99, 119.99, '2026-03-15'),
            (azienda_id, 'iPhone 15 Pro', 'Smartphone Apple, 256GB, color Titanium Black', 'Elettronica', 3, 999.00, 1049.00, '2026-02-20'),
            (azienda_id, 'Adidas Ultraboost 23', 'Scarpe da running, nere, taglia 43', 'Sneakers', 5, 179.99, 159.99, '2026-03-10'),
            (azienda_id, 'T-Shirt Gucci', 'T-shirt in cotone, logo ricamato, taglia M', 'Abbigliamento', 12, 45.00, 65.00, '2026-01-05'),
            (azienda_id, 'Sony WH-1000XM5', 'Cuffie wireless con noise cancelling', 'Accessori', 4, 349.00, 389.00, '2026-02-28'),
        ]
        
        cursor.executemany('''
            INSERT INTO prodotti (id_azienda, nome, descrizione, categoria, quantita, prezzo_pagato, prezzo_attuale, data_inserimento)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', prodotti)
        
        print(f"✅ {len(prodotti)} prodotti creati")
        
        # ===== STORICO PREZZI =====
        # Recuperiamo gli ID dei prodotti appena creati
        cursor.execute("SELECT id, nome FROM prodotti WHERE id_azienda = ?", (azienda_id,))
        prodotti_creati = cursor.fetchall()
        
        # Storico per Nike Air Force 1 (ID 1)
        price_updates_1 = [
            (prodotti_creati[0][0], 100.00, '2026-03-16 10:30:00'),
            (prodotti_creati[0][0], 185.00, '2026-03-18 14:15:00'),
            (prodotti_creati[0][0], 62.50, '2026-03-22 09:45:00'),
            (prodotti_creati[0][0], 150.99, '2026-04-10 16:20:00'),
        ]
        
        # Storico per iPhone 15 Pro
        price_updates_2 = [
            (prodotti_creati[1][0], 1020.00, '2026-02-25 11:00:00'),
            (prodotti_creati[1][0], 1030.00, '2026-03-05 13:30:00'),
            (prodotti_creati[1][0], 1040.00, '2026-03-20 15:45:00'),
            (prodotti_creati[1][0], 1099.00, '2026-04-08 12:15:00'),
        ]
        
        # Storico per Adidas Ultraboost 23
        price_updates_3 = [
            (prodotti_creati[2][0], 175.00, '2026-03-12 09:20:00'),
            (prodotti_creati[2][0], 170.00, '2026-03-25 14:00:00'),
            (prodotti_creati[2][0], 162.50, '2026-04-01 10:40:00'),
            (prodotti_creati[2][0], 94.99, '2026-04-12 11:30:00'),
        ]
        
        # Storico per T-Shirt Gucci
        price_updates_4 = [
            (prodotti_creati[3][0], 50.00, '2026-01-10 08:15:00'),
            (prodotti_creati[3][0], 100.00, '2026-02-01 16:45:00'),
            (prodotti_creati[3][0], 60.00, '2026-03-15 10:20:00'),
            (prodotti_creati[3][0], 65.00, '2026-04-05 14:30:00'),
        ]
        
        # Storico per Sony WH-1000XM5
        price_updates_5 = [
            (prodotti_creati[4][0], 360.00, '2026-03-01 09:50:00'),
            (prodotti_creati[4][0], 370.00, '2026-03-15 13:25:00'),
            (prodotti_creati[4][0], 30.00, '2026-03-28 15:10:00'),
            (prodotti_creati[4][0], 389.00, '2026-04-10 11:45:00'),
        ]
        
        all_updates = price_updates_1 + price_updates_2 + price_updates_3 + price_updates_4 + price_updates_5
        
        cursor.executemany('''
            INSERT INTO price_updates (product_id, price, update_date)
            VALUES (?, ?, ?)
        ''', all_updates)
        
        print(f"✅ {len(all_updates)} aggiornamenti di prezzo creati")
        
        conn.commit()
        print("\n🎉 Database popolato con successo!")
        print(f"📝 Credenziali di login:")
        print(f"   Email: utente1@retailpulse.it")
        print(f"   Password: password123")
        
    except sqlite3.IntegrityError as e:
        print(f"⚠️ Errore: {e}")
        print("💡 I dati potrebbero essere già presenti nel database.")
    except Exception as e:
        print(f"❌ Errore: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    populate_db()