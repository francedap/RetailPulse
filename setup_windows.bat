@echo off
echo ==========================================
echo   Installazione RetailPulse (Windows)
echo ==========================================
echo.
echo 1. Creazione ambiente virtuale in corso...
python -m venv venv

echo 2. Attivazione ambiente virtuale...
call venv\Scripts\activate

echo 3. Installazione librerie (potrebbe volerci qualche minuto)...
pip install -r requirements.txt

echo.
echo Installazione completata con successo! Ora puoi chiudere questa finestra.
pause