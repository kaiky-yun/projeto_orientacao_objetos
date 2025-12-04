# Guia de Configuração e Execução

## 🚀 Quick Start

### 1. Preparar Ambiente
```bash
# Navegar até o diretório
cd /home/ubuntu/financeiro_oo_refactored

# Criar virtual environment
python3 -m venv venv

# Ativar virtual environment
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Executar Aplicação
```bash
python run.py
```

### 4. Acessar Aplicação
Abra seu navegador e acesse: **http://localhost:5000**

---

## 📋 Requisitos

- **Python 3.8+**
- **pip** (gerenciador de pacotes)
- **Navegador moderno** (Chrome, Firefox, Safari, Edge)

---

## 🔧 Configuração Detalhada

### Variáveis de Ambiente (Opcional)

Crie um arquivo `.env` na raiz do projeto:

```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
```

### Estrutura de Diretórios de Dados

A aplicação cria automaticamente:
```
~/.financeiro_app/
├── users.json
├── transactions.json
├── investments.json
└── *.json.bak  (backups automáticos)
```

---

## 🧪 Teste a Aplicação

### 1. Criar Conta de Teste
- Clique em "Cadastre-se aqui"
- Preencha:
  - Username: `teste_usuario`
  - Email: `teste@example.com`
  - Senha: `senha123`
  - Confirmar Senha: `senha123`
- Clique em "Cadastrar"

### 2. Fazer Login
- Clique em "Faça login aqui"
- Preencha:
  - Username/Email: `teste_usuario`
  - Senha: `senha123`
- Clique em "Entrar"

### 3. Testar Transações
- Clique em "Transações"
- Clique em "+ Nova Transação"
- Preencha:
  - Tipo: Receita
  - Valor: 1000.00
  - Descrição: Salário mensal
  - Categoria: Salário
- Clique em "Criar Transação"

### 4. Testar Investimentos
- Clique em "Investimentos"
- Clique em "+ Novo Investimento"
- Preencha:
  - Nome: Ações VALE
  - Tipo: Renda Variável
  - Valor Inicial: 5000.00
  - Valor Atual: 5500.00
  - Taxa Mensal: 0.5
- Clique em "Criar Investimento"

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'flask'"
**Solução**: Ative o virtual environment e instale as dependências
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Erro: "Address already in use"
**Solução**: A porta 5000 está em uso. Mude a porta em `run.py`:
```python
app.run(host='0.0.0.0', port=5001)  # Usar porta 5001
```

### Erro: "Permission denied" ao criar arquivos
**Solução**: Verifique permissões do diretório `~/.financeiro_app/`
```bash
mkdir -p ~/.financeiro_app
chmod 755 ~/.financeiro_app
```

### Dados não persistem
**Solução**: Verifique se o diretório `~/.financeiro_app/` existe e tem permissões de escrita
```bash
ls -la ~/.financeiro_app/
```

---

## 📚 Estrutura de Arquivos Importantes

### Configuração
- `config.py` - Configurações da aplicação
- `run.py` - Ponto de entrada

### Aplicação
- `app/__init__.py` - Factory da aplicação
- `app/models/` - Modelos de domínio
- `app/repositories/` - Acesso a dados
- `app/services/` - Lógica de negócio
- `app/controllers/` - Rotas (Views)

### Frontend
- `app/templates/` - Templates HTML/Jinja2
- `app/static/css/style.css` - Estilos
- `app/static/js/main.js` - JavaScript

---

## 🔐 Segurança

### Senhas
- Mínimo 6 caracteres
- Criptografadas com bcrypt
- Nunca armazenadas em texto plano

### Sessões
- Expiram após 7 dias
- Protegidas por cookie seguro
- Requerem login para acessar dados

### Validação
- Todos os inputs são validados
- Proteção contra SQL injection (JSON storage)
- CSRF ready (estrutura preparada)

---

## 📊 Estrutura de Dados

### Arquivo: users.json
```json
{
  "uuid-do-usuario": {
    "id": "uuid-do-usuario",
    "username": "usuario",
    "email": "usuario@example.com",
    "password_hash": "bcrypt-hash",
    "created_at": "2025-12-03T10:30:00+00:00"
  }
}
```

### Arquivo: transactions.json
```json
{
  "user-id": [
    {
      "id": "uuid-transacao",
      "type": "income",
      "amount": {"amount": "1000.00"},
      "description": "Salário",
      "category": {"name": "Salário"},
      "user_id": "user-id",
      "occurred_at": "2025-12-03T10:30:00+00:00"
    }
  ]
}
```

### Arquivo: investments.json
```json
{
  "user-id": [
    {
      "id": "uuid-investimento",
      "name": "Ações VALE",
      "type": "renda_variavel",
      "initial_amount": {"amount": "5000.00"},
      "current_amount": {"amount": "5500.00"},
      "monthly_rate": 0.5,
      "user_id": "user-id",
      "start_date": "2025-12-03T10:30:00+00:00",
      "notes": "Investimento em ações"
    }
  ]
}
```

---

## 🚀 Deployment

### Para Produção

1. **Instale um servidor WSGI:**
```bash
pip install gunicorn
```

2. **Execute com Gunicorn:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

3. **Configure variáveis de ambiente:**
```bash
export FLASK_ENV=production
export SECRET_KEY=sua-chave-secreta-segura
```

---

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique o console do navegador (F12)
2. Verifique os logs do Flask
3. Consulte o arquivo `README.md`

---

**Última atualização**: Dezembro 2025
