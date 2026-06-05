@echo off
REM Opcional: mismo efecto que Salidas - Publicar en web en el panel.
REM Recomendado: usar solo el boton del panel (celular o PC).
cd /d %~dp0
call venv\Scripts\activate

set FIREBASE_CMD=firebase.cmd
where firebase.cmd >nul 2>&1
if %ERRORLEVEL% NEQ 0 set FIREBASE_CMD=npx firebase-tools

echo.
echo [1/3] Generando sitio en web-export...
python -c "import os,django; os.environ.setdefault('DJANGO_SETTINGS_MODULE','olala.settings'); django.setup(); from agencia.web_publish import generar_sitio_web_estatico; d,n,f=generar_sitio_web_estatico(); print(f'  OK: {n} paquetes, {f} flyers')"
if %ERRORLEVEL% NEQ 0 goto error

echo.
echo [2/3] Verificando Firebase...
%FIREBASE_CMD% hosting:sites:list --project turigest-ja >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  echo Sesion expirada. Ejecuta: firebase.cmd login --reauth
  goto fin
)

echo.
echo [3/3] Subiendo a olala-viajes.web.app ...
%FIREBASE_CMD% deploy --only hosting:olala --project turigest-ja --non-interactive
if %ERRORLEVEL% EQU 0 (
  echo.
  echo Listo. Abri https://olala-viajes.web.app con Ctrl+F5
) else (
  echo Deploy fallo.
)
goto fin

:error
echo Error al generar el sitio.

:fin
pause
