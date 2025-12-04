# Controlador Financeiro - Projeto BMVC III

Este projeto implementa um sistema de controle financeiro pessoal, atendendo aos requisitos do nível BMVC III, incluindo:

1.  **Serviço de Modelos (Objetos Python):** O sistema serve os modelos `User`, `Transaction`, `Investment`, `Subcategory` e `Category` (objetos em Python) através de suas respectivas rotas e serviços.
2.  **CRUD Completo:** Implementação completa das operações **C**riar, **R**eferenciar (Ler), **U**pdate (Atualizar) e **D**elete (Excluir) para o modelo principal `Transaction`.
3.  **Controle de Acesso de Usuários:** Sistema de **LOGIN** e rotas restritas que exigem autenticação.
4.  **Páginas Informativas com CSS/JS:** Todas as páginas carregam arquivos CSS (`style.css`) e JavaScript (`main.js`) plenamente funcionais.

## 1. Configuração e Execução do Projeto

O projeto é construído com **Flask** e utiliza um sistema de persistência de dados baseado em arquivos JSON.

### Pré-requisitos

*   Python 3.x
*   `pip` (gerenciador de pacotes do Python)

### Passos para Execução

1.  **Navegue até o diretório do projeto:**
    ```bash
    cd /caminho/para/financeiro_oo_refactored
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Inicie o servidor Flask:**
    ```bash
    python run.py
    ```
    O servidor será iniciado e estará acessível em `http://127.0.0.1:5000`.

## 2. Roteiro de Demonstração (Requisitos BMVC III)

Siga este roteiro para demonstrar o funcionamento completo do sistema, conforme exigido:

### A. Controle de Acesso (LOGIN e Acesso Restrito)

1.  **Acesso Inicial (Página de Login):**
    *   Abra o navegador em `http://127.0.0.1:5000`. Você será redirecionado automaticamente para a página de **Login**.
    *   **Demonstre o Acesso Restrito:** Tente acessar uma rota restrita diretamente, como `/transactions/`. O sistema deve redirecionar de volta para o Login.

2.  **Cadastro de Usuário:**
    *   Clique em **"Cadastre-se aqui"**.
    *   Preencha o formulário e crie um novo usuário (ex: `usuario: testeuser`, `senha: testesenha`).

3.  **Login:**
    *   Retorne à página de Login.
    *   Faça login com as credenciais criadas.
    *   **Resultado Esperado:** O sistema deve redirecionar para a página de **Transações** (acesso restrito), confirmando o controle de acesso.

### B. CRUD Completo (Modelo Transaction)

Demonstre as 4 operações CRUD na seção **Transações**:

1.  **CREATE (Criar):**
    *   Na página de Transações, clique em **"+ Nova Transação"**.
    *   Preencha o formulário (ex: Tipo: `Receita`, Valor: `1500.00`, Descrição: `Salário`, Categoria: `Salário`).
    *   Clique em **"Criar Transação"**.
    *   **Resultado Esperado:** A transação deve aparecer na lista e o saldo deve ser atualizado.

2.  **READ (Referenciar/Ler):**
    *   A transação criada deve estar visível na tabela da página de Transações, demonstrando a leitura dos dados do modelo.
    *   **Demonstre o CSS/JS:** Mostre que os botões de ação e o menu de navegação estão estilizados (CSS) e que a validação de formulário (JS) está ativa (opcionalmente, tente submeter um formulário vazio).

3.  **UPDATE (Atualizar):**
    *   Clique no ícone de **lápis (✏️)** ao lado da transação criada.
    *   Altere o valor (ex: de `1500.00` para `1600.00`).
    *   Clique em **"Atualizar Transação"**.
    *   **Resultado Esperado:** O valor na lista de transações e o saldo total devem ser atualizados.

4.  **DELETE (Excluir):**
    *   Clique no ícone de **lixeira (🗑️)** ao lado da transação.
    *   Confirme a exclusão no pop-up de confirmação (JS).
    *   **Resultado Esperado:** A transação deve desaparecer da lista e o saldo deve retornar a zero.

### C. Servindo Modelos e Páginas

*   Mencione que o sistema utiliza objetos Python (`Transaction`, `User`, etc.) que são servidos e manipulados pelos **Controllers** e **Services** (ex: `transaction_controller.py`, `finance_service.py`).
*   Mencione que as páginas HTML (templates) são carregadas pelo Flask e utilizam os arquivos estáticos CSS e JS para a apresentação e interatividade.

---
*Este `README.md` foi gerado para auxiliar na sua demonstração BMVC III.*
