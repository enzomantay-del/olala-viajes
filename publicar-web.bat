@echo off
REM Genera el sitio estatico (HTML + flyers JPG) y lo sube a Firebase Hosting.
cd /d %~dp0
call venv\Scripts\activate

echo.
echo [1/2] Generando sitio y flyers en olala-viajes-web...
python -c "import os,django; os.environ.setdefault('DJANGO_SETTINGS_MODULE','olala.settings'); django.setup(); from agencia.web_publish import generar_sitio_web_estatico; d,n,f=generar_sitio_web_estatico(); print(f'  OK: {n} paquetes, {f} flyers en', d)"

echo.
echo [2/2] Subiendo a olala-viajes.web.app ...
cd /d %~dp0\..
firebase deploy --only hosting:olala --project turigest-ja

if %ERRORLEVEL% EQU 0 (
  echo.
  echo Listo. Abri https://olala-viajes.web.app con Ctrl+F5
) else (
  echo.
  echo El deploy fallo. Si no tenes Firebase CLI: npm install -g firebase-tools ^& firebase login
)

pause
