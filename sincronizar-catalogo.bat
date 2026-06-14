@echo off

cd /d %~dp0

if exist venv\Scripts\activate call venv\Scripts\activate

pip install pip-system-certs requests certifi -q

echo Modo rapido: omite fotos y flyers ya subidos.
echo Para regenerar flyers: python manage.py sincronizar_supabase --flyers
echo.
python manage.py sincronizar_supabase

pause

