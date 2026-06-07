@echo off
REM Publica el catálogo en https://olala-viajes.web.app (Firebase, sin Render).

cd /d %~dp0

set FIREBASE_CMD=firebase.cmd
where firebase.cmd >nul 2>&1
if %ERRORLEVEL% NEQ 0 set FIREBASE_CMD=npx firebase-tools

echo.
echo [1/2] Sincronizando paquetes a Supabase...
if exist venv\Scripts\activate call venv\Scripts\activate
if exist .env (
  python manage.py sincronizar_supabase
) else (
  echo   Sin .env — saltando sync. Creá .env con SUPABASE_SERVICE_KEY.
)

echo.
echo [2/2] Subiendo sitio-publico a olala-viajes.web.app ...
%FIREBASE_CMD% deploy --only hosting:olala --project turigest-ja --non-interactive

if %ERRORLEVEL% EQU 0 (
  echo.
  echo Listo: https://olala-viajes.web.app
) else (
  echo Deploy fallo. Ejecutá: firebase.cmd login --reauth
)
pause
