#!/bin/bash
cd /home/ubuntu/projeto_orientacao_objetos/projeto-controlador-financeiro
nohup python3 api_v2.py > api.log 2>&1 &
echo "API iniciada em background. Ver logs com: tail -f api.log"
nohup ./start_http.sh > frontend.log 2>&1 &
echo "Frontend iniciado em background. Acesse na porta 8010."

