@echo off
cd /d %~dp0
if exist venv\Scripts\activate call venv\Scripts\activate
pip install pip-system-certs requests certifi -q
python manage.py sincronizar_supabase
pause
