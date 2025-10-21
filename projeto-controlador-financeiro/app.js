/**
 * Aplicação Frontend do Controlador Financeiro
 * Gerencia a interface e a comunicação com a API
 */

class FinanceApp {
    constructor() {
        this.transactions = [];
        this.categories = [];
        this.currentReportType = 'category';
        this.init();
    }

    /**
     * Inicializar a aplicação
     */
    async init() {
        this.setupEventListeners();
        await this.checkAPIConnection();
        await this.loadInitialData();
        this.renderDashboard();
    }

    /**
     * Configurar listeners de eventos
     */
    setupEventListeners() {
        // Navegação
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchSection(e.target.dataset.section));
        });

        // Formulário de transação
        document.getElementById('transaction-form').addEventListener('submit', (e) => this.handleAddTransaction(e));

        // Filtros de transações
        document.getElementById('filter-search').addEventListener('input', () => this.renderTransactionsList());
        document.getElementById('filter-type').addEventListener('change', () => this.renderTransactionsList());

        // Relatórios
        document.getElementById('report-by-category').addEventListener('click', () => this.switchReport('category'));
        document.getElementById('report-by-month').addEventListener('click', () => this.switchReport('month'));
    }

    /**
     * Verificar conexão com a API
     */
    async checkAPIConnection() {
        const result = await apiClient.checkHealth();
        const statusIndicator = document.getElementById('api-status-indicator');
        const statusText = document.getElementById('api-status-text');

        if (result.success) {
            statusIndicator.classList.add('connected');
            statusText.textContent = 'API Conectada';
        } else {
            statusIndicator.classList.remove('connected');
            statusText.textContent = 'API Desconectada';
            this.showToast('Aviso: API não está acessível', 'warning');
        }
    }

    /**
     * Carregar dados iniciais
     */
    async loadInitialData() {
        // Carregar transações
        const txResult = await apiClient.getTransactions();
        if (txResult.success) {
            this.transactions = txResult.data.data || [];
        }

        // Carregar categorias
        const catResult = await apiClient.getCategories();
        if (catResult.success) {
            this.categories = catResult.data.data || [];
        }
    }

    /**
     * Trocar de seção
     */
    switchSection(sectionName) {
        // Atualizar botões de navegação
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.section === sectionName) {
                btn.classList.add('active');
            }
        });

        // Mostrar/esconder seções
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(sectionName).classList.add('active');

        // Atualizar dados quando necessário
        if (sectionName === 'dashboard') {
            this.renderDashboard();
        } else if (sectionName === 'transactions') {
            this.renderTransactionsList();
        } else if (sectionName === 'reports') {
            this.renderReport();
        }
    }

    /**
     * Renderizar dashboard
     */
    async renderDashboard() {
        // Atualizar saldo
        const balanceResult = await apiClient.getBalance();
        if (balanceResult.success) {
            const balance = parseFloat(balanceResult.data.data.balance);
            document.getElementById('balance-value').textContent = this.formatCurrency(balance);
        }

        // Atualizar contagem de transações
        document.getElementById('transaction-count').textContent = this.transactions.length;

        // Calcular receitas e despesas
        let totalIncome = 0;
        let totalExpense = 0;

        this.transactions.forEach(tx => {
            const amount = parseFloat(tx.amount.amount);
            if (tx.type === 'income') {
                totalIncome += amount;
            } else {
                totalExpense += amount;
            }
        });

        document.getElementById('total-income').textContent = this.formatCurrency(totalIncome);
        document.getElementById('total-expense').textContent = this.formatCurrency(totalExpense);

        // Renderizar transações recentes (últimas 5)
        const recentTxs = this.transactions.slice(-5).reverse();
        const recentContainer = document.getElementById('recent-transactions');

        if (recentTxs.length === 0) {
            recentContainer.innerHTML = '<p class="empty-state">Nenhuma transação encontrada</p>';
        } else {
            recentContainer.innerHTML = recentTxs.map(tx => this.createTransactionElement(tx)).join('');
        }
    }

    /**
     * Renderizar lista de transações
     */
    renderTransactionsList() {
        const searchTerm = document.getElementById('filter-search').value.toLowerCase();
        const typeFilter = document.getElementById('filter-type').value;

        let filtered = this.transactions.filter(tx => {
            const matchSearch = tx.description.toLowerCase().includes(searchTerm);
            const matchType = !typeFilter || tx.type === typeFilter;
            return matchSearch && matchType;
        });

        const container = document.getElementById('all-transactions');

        if (filtered.length === 0) {
            container.innerHTML = '<p class="empty-state">Nenhuma transação encontrada</p>';
        } else {
            container.innerHTML = filtered.reverse().map(tx => this.createTransactionElement(tx)).join('');

            // Adicionar listeners aos botões de delete
            container.querySelectorAll('.btn-danger').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const txId = e.target.dataset.id;
                    this.handleDeleteTransaction(txId);
                });
            });
        }
    }

    /**
     * Criar elemento de transação
     */
    createTransactionElement(tx) {
        const amount = parseFloat(tx.amount.amount);
        const date = new Date(tx.occurred_at);
        const formattedDate = date.toLocaleDateString('pt-BR');
        const formattedTime = date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

        const typeLabel = tx.type === 'income' ? 'Receita' : 'Despesa';
        const amountDisplay = tx.type === 'income' 
            ? `+ ${this.formatCurrency(amount)}`
            : `- ${this.formatCurrency(amount)}`;

        return `
            <div class="transaction-item ${tx.type}">
                <div class="transaction-info">
                    <div class="transaction-header">
                        <span class="transaction-description">${this.escapeHtml(tx.description)}</span>
                        <span class="transaction-amount">${amountDisplay}</span>
                    </div>
                    <div class="transaction-meta">
                        <span class="transaction-category">${this.escapeHtml(tx.category.name)}</span>
                        <span class="transaction-date">${formattedDate} ${formattedTime}</span>
                    </div>
                </div>
                <div class="transaction-actions">
                    <button class="btn btn-danger" data-id="${tx.id}">Deletar</button>
                </div>
            </div>
        `;
    }

    /**
     * Trocar tipo de relatório
     */
    switchReport(type) {
        this.currentReportType = type;

        // Atualizar botões
        document.getElementById('report-by-category').classList.toggle('active', type === 'category');
        document.getElementById('report-by-month').classList.toggle('active', type === 'month');

        // Atualizar título
        const title = type === 'category' ? 'Relatório por Categoria' : 'Relatório por Mês';
        document.getElementById('report-title').textContent = title;

        this.renderReport();
    }

    /**
     * Renderizar relatório
     */
    async renderReport() {
        const result = await apiClient.getReport(this.currentReportType);
        const container = document.getElementById('report-content');

        if (!result.success) {
            container.innerHTML = `<p class="empty-state">Erro ao carregar relatório: ${result.error}</p>`;
            return;
        }

        const reportData = result.data.data.data || {};
        const entries = Object.entries(reportData);

        if (entries.length === 0) {
            container.innerHTML = '<p class="empty-state">Nenhum dado para exibir</p>';
            return;
        }

        container.innerHTML = entries.map(([label, value]) => {
            const amount = parseFloat(value);
            const isPositive = amount >= 0;
            const displayValue = isPositive 
                ? `+ ${this.formatCurrency(amount)}`
                : `- ${this.formatCurrency(Math.abs(amount))}`;

            return `
                <div class="report-item">
                    <span class="report-item-label">${this.escapeHtml(label)}</span>
                    <span class="report-item-value" style="color: ${isPositive ? '#10B981' : '#EF4444'}">${displayValue}</span>
                </div>
            `;
        }).join('');
    }

    /**
     * Manipular adição de transação
     */
    async handleAddTransaction(e) {
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);

        const transaction = {
            type: formData.get('type'),
            amount: parseFloat(formData.get('amount')),
            description: formData.get('description'),
            category: formData.get('category'),
        };

        // Adicionar data se fornecida
        const dateStr = formData.get('occurred_at');
        if (dateStr) {
            transaction.occurred_at = new Date(dateStr).toISOString();
        }

        // Validar
        if (!transaction.type || !transaction.amount || !transaction.description || !transaction.category) {
            this.showToast('Por favor, preencha todos os campos obrigatórios', 'warning');
            return;
        }

        if (transaction.amount <= 0) {
            this.showToast('O valor deve ser maior que zero', 'warning');
            return;
        }

        // Enviar para API
        const result = await apiClient.createTransaction(transaction);

        if (result.success) {
            this.showToast('Transação adicionada com sucesso!', 'success');
            form.reset();
            await this.loadInitialData();
            this.renderDashboard();
            this.renderTransactionsList();
            this.renderReport();
        } else {
            this.showToast(`Erro: ${result.error}`, 'error');
        }
    }

    /**
     * Manipular deleção de transação
     */
    async handleDeleteTransaction(id) {
        if (!confirm('Tem certeza que deseja deletar esta transação?')) {
            return;
        }

        const result = await apiClient.deleteTransaction(id);

        if (result.success) {
            this.showToast('Transação deletada com sucesso!', 'success');
            await this.loadInitialData();
            this.renderDashboard();
            this.renderTransactionsList();
            this.renderReport();
        } else {
            this.showToast(`Erro: ${result.error}`, 'error');
        }
    }

    /**
     * Mostrar notificação toast
     */
    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = `toast ${type} show`;

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    /**
     * Formatar número como moeda
     */
    formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    }

    /**
     * Escapar caracteres HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Inicializar aplicação quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    new FinanceApp();
});

