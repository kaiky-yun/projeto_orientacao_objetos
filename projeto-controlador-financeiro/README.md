# 💰 Finance Control App (Orientação a Objetos • Python)

Projeto desenvolvido por **Kaiky Moreira Yun** para a disciplina de **Orientação a Objetos**, aplicando os princípios fundamentais da programação orientada a objetos na prática, através de um **sistema de controle financeiro** simples e funcional.

O aplicativo foi construído em **Python**, seguindo uma **arquitetura em camadas** e utilizando padrões de projeto como **Repository**, **Service Layer** e **Value Object**.  
Os dados são armazenados localmente em **JSON**, sem necessidade de banco de dados ou dependências externas, e o sistema conta com **modo interativo via terminal**, pensado para um usuário leigo.

---

## 🧱 Estrutura do Projeto

```bash
finance-control-app/
├─ finance/
│  ├─ __init__.py
│  ├─ models.py         # Entidades principais (Transaction, Money, Category)
│  ├─ repository.py     # Interface e implementação do repositório
│  ├─ services.py       # Regras de negócio (FinanceService)
│  ├─ storage.py        # Persistência em arquivo JSON
│  └─ cli.py            # Interface interativa em terminal (menu)
│
├─ tests/
│  ├─ conftest.py
│  ├─ test_models.py
│  └─ test_services.py
│
├─ uml/
│  ├─ domain.puml       # Diagrama de classes
│  └─ use_cases.puml    # Diagrama de casos de uso
│
├─ requirements.txt
└─ README.md
```

---

## ⚙️ Tecnologias e Conceitos Aplicados

- **Python 3.12**
- **Programação Orientada a Objetos (POO)**
  - Encapsulamento, abstração e coesão entre classes.
- **Padrões de Projeto**
  - Repository, Service Layer, Value Object.
- **Testes Automatizados** com `pytest`
- **Armazenamento Persistente** com JSON
- **Interface de Linha de Comando (CLI)**
  - Menu interativo totalmente guiado pelo usuário.
- **UML** gerado com PlantUML.

---

## ▶️ Execução do Aplicativo

### 1. Criar ambiente virtual e instalar dependências
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Executar o modo interativo
```bash
python -m finance.cli
```

O sistema exibe um menu simples com as opções:

```
================= FINANCE CONTROL =================
1) Ver saldo
2) Listar lançamentos
3) Adicionar lançamento
4) Relatório por categoria
5) Relatório por mês
6) Remover lançamentos
7) Sair
===================================================
```

Todos os dados são armazenados automaticamente em:
```
~/.finance_app/transactions.json
```

---

## ✅ Execução de Testes

Os testes cobrem modelos, repositórios e serviços, garantindo integridade das regras de negócio.

```bash
pytest -q
```

### Benchmark de desempenho (opcional)
```bash
pytest --benchmark-only
```

---

## 🧩 UML e Documentação Visual

Os diagramas UML foram criados com **PlantUML** para representar:

- **Diagrama de Classes (domain.puml)** — modelagem das entidades, repositórios e serviços.
- **Diagrama de Casos de Uso (use_cases.puml)** — interação do usuário com o sistema.

### Como visualizar
- No VS Code, instale a extensão **PlantUML (by jebbs)**.
- Abra o arquivo `.puml` → `Preview Current Diagram`.
- Ou use o editor online: [plantuml.com/plantuml](https://plantuml.com/plantuml).

---

## 🧪 Roteiro de Apresentação (para vídeo)

### 🕐 1. Introdução
- Objetivo do projeto e contexto da disciplina.
- Explicar que o foco foi aplicar POO com um caso real: controle financeiro pessoal.

### 🧱 2. Arquitetura
- Mostrar a estrutura do projeto e explicar cada camada.
- Justificar uso dos padrões Repository, Service e Value Object.

### 💡 3. Domínio
- Apresentar `Transaction`, `Category` e `Money`.
- Mostrar como o modelo garante integridade e coesão.

### 💾 4. Persistência
- Explicar o fluxo: `JSONStorage → Repository → FinanceService`.

### 🖥️ 5. Demonstração
- Mostrar o menu interativo no terminal.
- Adicionar, listar, ver saldo, gerar relatórios e remover lançamentos.

### 🧪 6. Testes
- Executar `pytest -q` e explicar a cobertura.
- Comentar sobre o benchmark de performance.

### 🧭 7. UML
- Exibir os diagramas UML e explicar as relações entre classes.

### 🎬 8. Conclusão
- Comentar sobre aprendizados e melhorias futuras (ex: GUI, SQLite, API REST).

---

## 🚀 Próximos Passos

- Adicionar suporte a múltiplos usuários.
- Exportação de relatórios em CSV.
- Interface gráfica (Tkinter ou PyQt).
- Integração com banco de dados (SQLite).

---

📌 **Autor:** [Kaiky Moreira Yun](https://www.linkedin.com/in/kaiky-moreira-yun)  
🎓 **Disciplina:** Orientação a Objetos — Universidade de Brasília (UnB – FGA)  
🗓️ **Ano:** 2025  
