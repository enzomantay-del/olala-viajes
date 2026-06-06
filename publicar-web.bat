@echo off
REM Redirige olala-viajes.web.app hacia el catálogo en Render (opcional, una sola vez).

cd /d %~dp0

set FIREBASE_CMD=firebase.cmd
where firebase.cmd >nul 2>&1
if %ERRORLEVEL% NEQ 0 set FIREBASE_CMD=npx firebase-tools

echo.
echo Subiendo redireccion de web.app hacia onrender.com/web ...
echo (Si falla: firebase.cmd login --reauth)
echo.

%FIREBASE_CMD% deploy --only hosting:olala --project turigest-ja --non-interactive

if %ERRORLEVEL% EQU 0 (
  echo.
  echo Listo. web.app redirige a https://olala-viajes.onrender.com/web/
) else (
  echo.
  echo Deploy fallo. El catalogo igual funciona en onrender.com/web
)

pause
