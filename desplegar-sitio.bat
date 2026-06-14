@echo off

REM Genera paginas para compartir y sube sitio-publico a Firebase.



cd /d %~dp0



set FIREBASE_CMD=firebase.cmd

where firebase.cmd >nul 2>&1

if %ERRORLEVEL% NEQ 0 set FIREBASE_CMD=npx firebase-tools



echo.

echo [1/2] Generando paginas para compartir (WhatsApp/Facebook)...

if exist venv\Scripts\python.exe (

  venv\Scripts\python.exe manage.py generar_paginas_web

) else (

  python manage.py generar_paginas_web

)



echo.

echo [2/2] Subiendo sitio-publico a https://olala-viajes.web.app ...

echo Si falla la autenticacion: firebase.cmd login --reauth

echo.



%FIREBASE_CMD% deploy --only hosting:olala --project turigest-ja --non-interactive



if %ERRORLEVEL% EQU 0 (

  echo.

  echo Listo. Abri https://olala-viajes.web.app y refresca con Ctrl+F5

) else (

  echo.

  echo Deploy fallo. Ejecuta: firebase.cmd login --reauth

)



pause


