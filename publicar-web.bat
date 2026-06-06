@echo off
REM Publica olala-viajes.web.app desde tu PC (con todas las fotos).

cd /d %~dp0
call venv\Scripts\activate

set FIREBASE_CMD=firebase.cmd
where firebase.cmd >nul 2>&1
if %ERRORLEVEL% NEQ 0 set FIREBASE_CMD=npx firebase-tools

if exist .env (
  echo.
  echo [1/3] Subiendo fotos locales a Cloudinary...
  python manage.py subir_fotos_salidas
) else (
  echo.
  echo [1/3] Sin archivo .env — las fotos se copian solo desde media/salidas/
  echo        Para Cloudinary: crea .env con CLOUDINARY_URL=cloudinary://...
)

echo.
echo [2/3] Generando sitio en web-export...
python -c "import os,django; os.environ.setdefault('DJANGO_SETTINGS_MODULE','olala.settings'); django.setup(); from agencia.web_publish import generar_sitio_web_estatico; d,n,f=generar_sitio_web_estatico(); print(f'  OK: {n} paquetes, {f} flyers')"
if %ERRORLEVEL% NEQ 0 goto error

for /f %%A in ('dir /b "web-export\media\salidas\*" 2^>nul ^| find /c /v ""') do set FOTOS=%%A
echo   Fotos en web-export: %FOTOS%

echo.
echo [3/3] Subiendo a olala-viajes.web.app ...
echo   (Si falla: firebase.cmd login --reauth)
echo.
%FIREBASE_CMD% deploy --only hosting:olala --project turigest-ja --non-interactive
if %ERRORLEVEL% EQU 0 (
  echo.
  echo Listo. Abri https://olala-viajes.web.app con Ctrl+F5
) else (
  echo.
  echo Deploy fallo. Copiá el mensaje de error de arriba.
)
goto fin

:error
echo Error al generar el sitio.

:fin
pause
