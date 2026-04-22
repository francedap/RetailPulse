#!/bin/bash
# Questo comando si assicura che il terminale parta dalla cartella giusta
cd "$(dirname "$0")"

echo "=========================================="
echo "  Avvio di RetailPulse in corso..."
echo "=========================================="
echo "Non chiudere questa finestra finché usi l'app."
echo ""

source venv/bin/activate
streamlit run app.py