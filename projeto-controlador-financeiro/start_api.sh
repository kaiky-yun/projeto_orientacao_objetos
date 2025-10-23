#!/bin/bash
# Ativa o ambiente virtual e executa a API

echo "Ativando ambiente virtual..."
source .venv/bin/activate

echo "Iniciando API..."
python3 api.py

