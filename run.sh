#!/bin/bash
# ============================================================
# Script de execução do pipeline (Linux/Mac)
# Uso: ./run.sh input/video.mp4
# ============================================================
export LD_LIBRARY_PATH=$(find $(pwd)/venv/lib/python3.10/site-packages/nvidia -name "lib" -type d | paste -sd ":" -)
source venv/bin/activate
python run_pipeline.py "$@"
