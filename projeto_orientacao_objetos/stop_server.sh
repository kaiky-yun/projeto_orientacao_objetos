#!/bin/bash

# --- Configurações ---
PORT=8000

echo "Tentando finalizar o processo na porta $PORT..."

# Usa 'lsof' (List Open Files) para encontrar o PID que está usando a porta 8000.
# O comando 'lsof -t -i :8000' retorna apenas o PID do processo.
PIDS=$(lsof -t -i :$PORT)

if [ -z "$PIDS" ]; then
    echo "Nenhum processo encontrado na porta $PORT."
    exit 0
fi

echo "Processos encontrados: $PIDS. Tentando encerrar..."

SUCCESS=0
for PID in $PIDS; do
    echo "Encerrando PID: $PID"
    kill "$PID"
    
    # Espera um pouco para o processo morrer
    sleep 1
    
    # Verifica se o processo realmente morreu
    if ps -p $PID > /dev/null; then
        echo "Processo $PID não finalizado. Tentando kill -9..."
        kill -9 "$PID"
        sleep 1
        
        if ps -p $PID > /dev/null; then
            echo "Aviso: O processo $PID não pôde ser encerrado."
        else
            SUCCESS=1
        fi
    else
        SUCCESS=1
    fi
done

if [ $SUCCESS -eq 1 ]; then
    echo "Servidor(es) na porta $PORT finalizado(s) com sucesso."
else
    echo "Aviso: Pelo menos um processo não pôde ser encerrado."
    exit 1
fi
exit 0
