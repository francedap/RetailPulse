#!/bin/bash
cd "$(dirname "$0")"

echo "=========================================="
echo "  Installazione RetailPulse (Mac/Linux)"
echo "=========================================="
echo ""
echo "1. Creazione ambiente virtuale in corso..."
python3 -m venv venv

echo "2. Attivazione ambiente virtuale..."
source venv/bin/activate

echo "3. Installazione librerie (potrebbe volerci qualche minuto)..."
pip install -r requirements.txt

echo ""
echo "Installazione completata! Chiudi questa finestra."