@echo off
cd /d %~dp0
call .\backend\.venv\Scripts\activate
python -m pip install -r .\backend\requirements.txt
python -m uvicorn backend.main:app --reload
