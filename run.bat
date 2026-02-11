@echo off
REM ============================================================
REM Script de execução do pipeline (Windows)
REM Uso: run.bat input\video.mp4
REM Ou arraste o vídeo sobre run.bat
REM ============================================================
cd /d "%~dp0"

REM Ativa o ambiente virtual (tenta venv311, venv ou .venv)
if exist venv311\Scripts\activate.bat (
    call venv311\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)
python run_pipeline.py %*
pause
