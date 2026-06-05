@echo off
cd /d %~dp0
call venv\Scripts\activate
start "" http://localhost:8000/web/
start "" http://localhost:8000/
python manage.py runserver
