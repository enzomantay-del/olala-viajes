@echo off
REM Restaura fotos desde media/salidas/ y publica la web con todas las imágenes.

cd /d %~dp0
call venv\Scripts\activate

echo.
echo === Diagnostico de fotos ===
python manage.py diagnosticar_fotos
echo.

if not exist .env (
  echo.
  echo AVISO: No hay archivo .env
  echo Si usas Cloudinary, crea .env con CLOUDINARY_URL=cloudinary://...
  echo Si usas la base de Render, agrega DATABASE_URL=postgres://...
  echo.
)

echo === Subiendo fotos locales al almacenamiento ===
python manage.py subir_fotos_salidas
if %ERRORLEVEL% NEQ 0 goto error

echo.
echo === Publicando en Firebase ===
call publicar-web.bat
goto fin

:error
echo Error. Revisa los mensajes de arriba.

:fin
