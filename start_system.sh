#!/bin/bash
echo "Smart Tourism Management System - Iniciando..."
echo

# Activar entorno virtual
source venv/bin/activate

# Ejecutar sistema
python main.py --mode full

read -p "Presiona Enter para salir..."
