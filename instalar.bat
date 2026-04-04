@echo off
echo ============================================
echo    Instalando Sistema Olala Viajes...
echo ============================================
cd /d %~dp0
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
echo.
echo ============================================
echo    Instalacion completada con exito!
echo    Para iniciar el sistema: iniciar.bat
echo ============================================
pause
