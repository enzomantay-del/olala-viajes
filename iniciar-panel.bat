@echo off
REM Panel de gestión en tu PC (no usa Render).

cd /d %~dp0
if exist venv\Scripts\activate call venv\Scripts\activate

echo Panel: http://127.0.0.1:8000/
echo Catálogo público: https://olala-viajes.web.app
echo.
python manage.py runserver 127.0.0.1:8000
