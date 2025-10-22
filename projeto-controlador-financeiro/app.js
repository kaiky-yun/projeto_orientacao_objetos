/**
 * Aplicação Frontend do Controlador Financeiro
 * Gerencia a interface e a comunicação com o backend Flask
 */

class FinanceApp {
    constructor() {
        this.transactions = [];
        this.categories = [];
        this.currentReportType = 'category';
        this.currentFilter = 'all';
        this.filterStartDate = null;
        this.filterEndDate = null;
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

        // Filtros de tempo
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleFilterChange(e.target.dataset.filter));
        });
        document.getElementById('apply-custom-filter').addEventListener('click', () => this.applyCustomFilter());
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
     * Obter transações filtradas por data
     */
    async getFilteredTransactions() {
        if (!this.filterStartDate && !this.filterEndDate) {
            return this.transactions;
        }

        const result = await apiClient.getTransactions(
            this.filterStartDate,
            this.filterEndDate
        );

        if (result.success) {
            return result.data.data || [];
        }
        return this.transactions; // Retorna todas as transações se houver erro na API
    }

    /**
     * Manipular mudança de filtro de tempo
     */
    handleFilterChange(filterType) {
        this.currentFilter = filterType;

        // Atualizar botões
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.filter === filterType) {
                btn.classList.add('active');
            }
        });

        // Mostrar/esconder inputs customizados
        const customRange = document.getElementById('custom-date-range');
        if (filterType === 'custom') {
            customRange.style.display = 'grid';
        } else {
            customRange.style.display = 'none';
            this.applyPresetFilter(filterType);
        }
    }

    /**
     * Aplicar filtro pré-definido
     */
    applyPresetFilter(filterType) {
        const now = new Date();
        let startDate = null;
        let endDate = null;

        switch (filterType) {
            case 'today':
                startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);
                break;
            case 'week':
                const weekStart = new Date(now);
                weekStart.setDate(now.getDate() - now.getDay());
                startDate = new Date(weekStart.getFullYear(), weekStart.getMonth(), weekStart.getDate());
                endDate = now;
                break;
            case 'month':
                startDate = new Date(now.getFullYear(), now.getMonth(), 1);
                endDate = now;
                break;
            case 'all':
            default:
                startDate = null;
                endDate = null;
                break;
        }

        this.filterStartDate = startDate ? startDate.toISOString().split('T')[0] : null;
        this.filterEndDate = endDate ? endDate.toISOString().split('T')[0] : null;

        this.renderDashboard();
    }

    /**
     * Aplicar filtro customizado
     */
    applyCustomFilter() {
        const startDateInput = document.getElementById('filter-start-date').value;
        const endDateInput = document.getElementById('filter-end-date').value;

        if (!startDateInput && !endDateInput) {
            this.showToast('Por favor, selecione pelo menos uma data', 'warning');
            return;
        }

        this.filterStartDate = startDateInput || null;
        this.filterEndDate = endDateInput || null;

        this.renderDashboard();
    }

    /**
     * Renderizar dashboard
     */
    async renderDashboard() {
        // Obter transações filtradas para exibição no dashboard
        const filteredTxs = await this.getFilteredTransactions();

        // Atualizar saldo com filtro
        const balanceResult = await apiClient.getBalance(
            this.filterStartDate,
            this.filterEndDate
        );
        if (balanceResult.success) {
            const balance = parseFloat(balanceResult.data.data.balance);
            document.getElementById('balance-value').textContent = this.formatCurrency(balance);
        }

        // Atualizar contagem de transações
        document.getElementById('transaction-count').textContent = filteredTxs.length;

        // Calcular receitas e despesas
        let totalIncome = 0;
        let totalExpense = 0;

        filteredTxs.forEach(tx => {
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
        const recentTxs = filteredTxs.slice(-5).reverse();
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

        return `
            <div class="transaction-item ${tx.type}">
                <div class="transaction-info">
                    <div class="transaction-header">
                        <span class="transaction-description">${this.escapeHtml(tx.description)}</span>
                        <span class="transaction-amount ${tx.type}">${tx.type === 'income' ? '+' : '-'} ${this.formatCurrency(amount)}</span>
                    </div>
                    <div class="transaction-meta">
                        <span class="transaction-category">${this.escapeHtml(tx.category.name)}</span>
                        <span>${formattedDate} às ${formattedTime}</span>
                    </div>
                </div>
                <div class="transaction-actions">
                    <button class="btn btn-danger" data-id="${tx.id}">Deletar</button>
                </div>
            </div>
        `;
    }

    /**
     * Manipular adição de transação
     */
    async handleAddTransaction(event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);

        const data = {
            type: formData.get('type'),
            amount: parseFloat(formData.get('amount')),
            description: formData.get('description'),
            category: formData.get('category'),
            occurred_at: formData.get('occurred_at') ? new Date(formData.get('occurred_at')).toISOString() : null,
        };

        const result = await apiClient.createTransaction(data);

        if (result.success) {
            this.showToast('Transação adicionada com sucesso!', 'success');
            form.reset();
            await this.loadInitialData(); // Recarregar todas as transações
            this.renderDashboard();
            this.renderTransactionsList();
        } else {
            this.showToast(`Erro: ${result.error}`, 'error');
        }
    }

    /**
     * Trocar de tipo de relatório
     */
    switchReport(reportType) {
        this.currentReportType = reportType;

        // Atualizar botões
        document.getElementById('report-by-category').classList.toggle('active', reportType === 'category');
        document.getElementById('report-by-month').classList.toggle('active', reportType === 'month');

        // Atualizar título
        document.getElementById('report-title').textContent = `Relatório por ${reportType === 'category' ? 'Categoria' : 'Mês'}`;

        // Renderizar relatório
        this.renderReport();
    }

    /**
     * Renderizar relatório
     */
    async renderReport() {
        const result = await apiClient.getReport(this.currentReportType, this.filterStartDate, this.filterEndDate);
        const container = document.getElementById('report-content');

        if (result.success) {
            const data = result.data.data; // Agora 'data' é um objeto
            const keys = Object.keys(data);

            if (keys.length === 0) {
                container.innerHTML = '<p class="empty-state">Nenhum dado para exibir</p>';
            } else {
                // Mapear o objeto para um array de elementos HTML
                container.innerHTML = keys.map(key => {
                    const amount = parseFloat(data[key]);
                    return `
                        <div class="report-item">
                            <span class="report-item-label">${this.escapeHtml(key)}</span>
                            <span class="transaction-amount ${amount >= 0 ? 'income' : 'expense'}">${this.formatCurrency(amount)}</span>
                        </div>
                    `;
                }).join('');
            }
        } else {
            container.innerHTML = '<p class="empty-state">Erro ao carregar relatório</p>';
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
