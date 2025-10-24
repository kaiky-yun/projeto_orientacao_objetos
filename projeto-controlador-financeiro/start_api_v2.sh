#!/bin/bash
# Script para iniciar a API v2 do Controlador Financeiro

echo "🚀 Iniciando API v2 do Controlador Financeiro..."
echo "📍 Porta: 5010"
echo "🔐 Autenticação: JWT habilitada"
echo ""

cd "$(dirname "$0")"
python3 api_v2.py

