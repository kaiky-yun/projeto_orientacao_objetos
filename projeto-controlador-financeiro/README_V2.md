# 💰 Finance Control App v2 - Com Autenticação e Investimentos

Versão 2.0 do projeto desenvolvido por **Kaiky Moreira Yun** para a disciplina de **Orientação a Objetos**.

Esta versão adiciona **autenticação de usuários**, **gerenciamento de investimentos** e **simulação de investimentos** baseada em planilhas Excel fornecidas.

---

## 🆕 Novas Funcionalidades

### 1. Sistema de Autenticação
- **Registro de usuários** com validação de email e senha
- **Login seguro** com JWT (JSON Web Tokens)
- **Proteção de rotas** - todas as operações requerem autenticação
- **Isolamento de dados** - cada usuário vê apenas suas próprias transações e investimentos

### 2. Relatórios Avançados
- **Relatório mensal por categoria** - visualize gastos de cada categoria mês a mês
- **Seletor de mês** - filtre relatórios por período específico
- **Resumo financeiro mensal** - receitas, despesas e saldo por mês
- **Meses disponíveis** - lista automática de períodos com transações

### 3. Gerenciamento de Investimentos
- **CRUD completo** de investimentos
- **Tipos de investimento**: Renda Fixa, Renda Variável, Fundos, Criptomoedas, Outros
- **Cálculo automático** de lucro e rentabilidade
- **Resumo de investimentos** - total investido, valor atual e lucro total

### 4. Simulação de Investimentos
Baseada nas planilhas fornecidas:
- **Simulação com aporte fixo** - projete investimentos com contribuições mensais fixas
- **Simulação com aportes variáveis** - configure aportes diferentes para cada mês
- **Comparação de cenários** - compare múltiplos valores de aporte
- **Simulação a partir de investimento** - use dados de investimentos cadastrados
- **Fórmula**: Saldo[n] = Saldo[n-1] × (1 + taxa) + Aporte[n]

---

## 🧱 Estrutura do Projeto v2

```
projeto-controlador-financeiro/
├─ finance/
│  ├─ __init__.py
│  ├─ models.py                    # Transaction, Money, Category (com user_id)
│  ├─ repository.py                # TransactionRepository (com filtro por usuário)
│  ├─ services.py                  # FinanceService (com user_id)
│  ├─ storage.py                   # JSONStorage
│  ├─ auth_models.py               # User (novo)
│  ├─ auth_repository.py           # UserRepository (novo)
│  ├─ auth_service.py              # AuthService (novo)
│  ├─ investment_models.py         # Investment (novo)
│  ├─ investment_repository.py     # InvestmentRepository (novo)
│  ├─ investment_service.py        # InvestmentService (novo)
│  ├─ simulation_service.py        # SimulationService (novo)
│  └─ report_service.py            # ReportService (novo)
│
├─ api_v2.py                       # API REST com JWT (novo)
├─ index_v2.html                   # Frontend com login (novo)
├─ app_v2.js                       # JavaScript com autenticação (novo)
├─ start_api_v2.sh                 # Script de inicialização (novo)
├─ styles.css                      # Estilos (existente)
└─ README_V2.md                    # Esta documentação
```

---

## 🚀 Como Executar

### 1. Instalar Dependências

```bash
cd projeto-controlador-financeiro
pip install -r requirements.txt
pip install flask flask-cors flask-jwt-extended bcrypt
```

### 2. Iniciar a API v2

```bash
./start_api_v2.sh
```

Ou manualmente:

```bash
python3 api_v2.py
```

A API estará disponível em: **http://localhost:5010**

### 3. Abrir o Frontend

Abra o arquivo `index_v2.html` em um navegador ou use um servidor HTTP:

```bash
python3 -m http.server 8000
```

Acesse: **http://localhost:8000/index_v2.html**

---

## 📡 Endpoints da API v2

### Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/register` | Registrar novo usuário |
| POST | `/api/auth/login` | Fazer login |
| GET | `/api/auth/me` | Obter usuário atual (requer JWT) |

### Transações

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/transactions` | Listar transações do usuário |
| POST | `/api/transactions` | Criar transação |
| GET | `/api/transactions/<id>` | Obter transação específica |
| DELETE | `/api/transactions/<id>` | Deletar transação |
| GET | `/api/balance` | Obter saldo total |
| GET | `/api/categories` | Listar categorias únicas |

### Relatórios

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/report` | Relatório por categoria ou mês |
| GET | `/api/reports/monthly-by-category` | Relatório mensal detalhado por categoria |
| GET | `/api/reports/category-by-month` | Relatório de categoria ao longo dos meses |
| GET | `/api/reports/available-months` | Lista de meses disponíveis |
| GET | `/api/reports/summary-by-month` | Resumo financeiro mensal |

### Investimentos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/investments` | Listar investimentos |
| POST | `/api/investments` | Criar investimento |
| GET | `/api/investments/<id>` | Obter investimento específico |
| PUT | `/api/investments/<id>` | Atualizar investimento |
| DELETE | `/api/investments/<id>` | Deletar investimento |
| GET | `/api/investments/summary` | Resumo dos investimentos |

### Simulações

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/simulations/fixed-contribution` | Simular aporte fixo |
| POST | `/api/simulations/variable-contribution` | Simular aportes variáveis |
| POST | `/api/simulations/compare-scenarios` | Comparar cenários |
| POST | `/api/simulations/from-investment/<id>` | Simular a partir de investimento |

---

## 🔐 Autenticação JWT

Todas as rotas (exceto `/api/auth/register` e `/api/auth/login`) requerem um token JWT no header:

```
Authorization: Bearer <token>
```

O token é obtido após login/registro e armazenado automaticamente no `localStorage` pelo frontend.

---

## 📊 Exemplos de Uso da API

### Registrar Usuário

```bash
curl -X POST http://localhost:5010/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "joao",
    "email": "joao@example.com",
    "password": "senha123"
  }'
```

### Criar Investimento

```bash
curl -X POST http://localhost:5010/api/investments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <seu_token>" \
  -d '{
    "name": "Tesouro Selic 2027",
    "type": "renda_fixa",
    "initial_amount": 5000,
    "monthly_rate": 0.008
  }'
```

### Simular Investimento

```bash
curl -X POST http://localhost:5010/api/simulations/fixed-contribution \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <seu_token>" \
  -d '{
    "initial_amount": 2000,
    "monthly_contribution": 1000,
    "monthly_rate": 0.008,
    "months": 36
  }'
```

---

## 📈 Lógica de Simulação

A simulação de investimentos segue a fórmula das planilhas fornecidas:

**Saldo Acumulado[mês] = Saldo Anterior × (1 + Taxa Mensal) + Aporte[mês]**

### Exemplo:
- Aporte inicial: R$ 2.000
- Aporte mensal: R$ 1.000
- Taxa mensal: 0,8% (0.008)

| Mês | Aporte | Saldo Acumulado | Lucro |
|-----|--------|-----------------|-------|
| 0 | R$ 2.000,00 | R$ 2.000,00 | R$ 0,00 |
| 1 | R$ 1.000,00 | R$ 3.016,00 | R$ 16,00 |
| 2 | R$ 1.000,00 | R$ 4.040,13 | R$ 40,13 |
| ... | ... | ... | ... |
| 36 | R$ 1.000,00 | R$ 42.710,93 | R$ 4.710,93 |

---

## 🗄️ Armazenamento de Dados

Os dados são armazenados localmente em arquivos JSON:

- **Transações**: `~/.finance_app/transactions.json`
- **Usuários**: `~/.finance_app/users.json`
- **Investimentos**: `~/.finance_app/investments.json`

---

## 🧪 Testes

Execute os testes existentes:

```bash
pytest -q
```

---

## 📝 Notas Importantes

1. **Segurança**: Em produção, altere a `JWT_SECRET_KEY` no arquivo `api_v2.py`
2. **Senhas**: São hasheadas com bcrypt antes de serem armazenadas
3. **Compatibilidade**: Transações antigas (sem `user_id`) são atribuídas ao usuário "default"
4. **Taxa de rendimento**: Deve ser informada em decimal (ex: 0.008 = 0,8%)

---

## 🎯 Próximos Passos Sugeridos

- Adicionar gráficos interativos (Chart.js)
- Exportar relatórios em PDF/CSV
- Notificações de metas de investimento
- Integração com APIs de cotações
- Aplicativo mobile (React Native)

---

## 👨‍💻 Desenvolvimento

**Autor:** Kaiky Moreira Yun  
**Disciplina:** Orientação a Objetos  
**Instituição:** Universidade de Brasília (UnB – FGA)  
**Ano:** 2025  
**Versão:** 2.0 (com autenticação e investimentos)

