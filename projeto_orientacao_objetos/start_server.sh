#!/bin/bash

# --- Configurações ---
# Assumindo que o script está na raiz do projeto 'financeiro_project'
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$PROJECT_DIR/flask_server.pid"
APP_URL="http://localhost:8000"
VENV_PATH="$PROJECT_DIR/venv/bin/activate"

# Verifica se o servidor já está rodando
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null; then
        echo "Servidor Flask já está rodando (PID: $PID). Finalize-o primeiro."
        exit 1
    else
        # Limpa o arquivo PID se o processo não existir
        rm -f "$PID_FILE"
    fi
fi

echo "Iniciando servidor Flask..."

# 1. Iniciar o servidor em segundo plano e salvar o PID
# A ativação do venv precisa ser feita na mesma subshell que executa o python
(
    cd "$PROJECT_DIR"
    
    # Tenta usar o python do venv diretamente para maior robustez
    PYTHON_EXEC="$PROJECT_DIR/venv/bin/python"
    
    if [ ! -f "$PYTHON_EXEC" ]; then
        echo "Erro: Executável Python do venv não encontrado em $PYTHON_EXEC. Certifique-se de que o venv está criado."
        exit 1
    fi
    
    # Executa o servidor, redirecionando a saída para um arquivo de log para diagnóstico
    # O log é crucial para saber por que o servidor não está ligando
    "$PYTHON_EXEC" run.py > "$PROJECT_DIR/flask_server.log" 2>&1 &
) &

# Captura o PID do último processo em background (a subshell que roda o Flask)
PID=$!
echo $PID > "$PID_FILE"

# Aguarda um momento para o servidor iniciar
sleep 3

echo "Servidor iniciado com PID: $PID"

# 2. Abrir a aplicação no navegador (macOS)
echo "Abrindo a aplicação em $APP_URL"

# Tenta abrir usando o comando 'open' padrão do macOS
open "$APP_URL"

# Solução de fallback: Tenta abrir usando o AppleScript, que é mais robusto no Automator/Atalhos
if [ $? -ne 0 ]; then
    osascript -e "open location \"$APP_URL\""
fi

exit 0
