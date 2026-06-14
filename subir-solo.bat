@echo off

REM Solo sube web-export a Firebase (sin regenerar). Útil si ya generaste el sitio.



cd /d %~dp0



set FIREBASE_CMD=firebase.cmd

where firebase.cmd >nul 2>&1

if %ERRORLEVEL% NEQ 0 set FIREBASE_CMD=npx firebase-tools



for /f %%A in ('dir /b "web-export\media\salidas\*" 2^>nul ^| find /c /v ""') do set FOTOS=%%A

echo Fotos listas para subir: %FOTOS%

echo.



%FIREBASE_CMD% deploy --only hosting:olala --project turigest-ja --non-interactive

pause

