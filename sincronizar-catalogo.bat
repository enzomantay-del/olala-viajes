@echo off

cd /d %~dp0

if exist venv\Scripts\activate call venv\Scripts\activate

pip install pip-system-certs requests certifi -q

echo Modo rapido: omite fotos y flyers ya subidos.
echo Si faltan flyers de paquetes nuevos, se generan automaticamente.
echo Para regenerar TODOS los flyers: python manage.py sincronizar_supabase --flyers
echo.
python manage.py sincronizar_supabase

pause

