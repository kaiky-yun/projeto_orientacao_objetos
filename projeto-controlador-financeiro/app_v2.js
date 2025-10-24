// Controlador Financeiro v2 - Frontend com Autenticação
const API_BASE_URL = 'http://localhost:5010/api';

// Estado da aplicação
let authToken = null;
let currentUser = null;

// ==================== AUTENTICAÇÃO ====================

// Sempre mostrar tela de login ao carregar
document.addEventListener('DOMContentLoaded', () => {
    // Limpar token anterior
    localStorage.removeItem('authToken');
    authToken = null;
    currentUser = null;
    
    showLoginScreen();
    setupAuthForms();
});

function setupAuthForms() {
    // Tabs de login/registro
    document.querySelectorAll('.form-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;
            document.querySelectorAll('.form-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            document.getElementById('login-form').classList.toggle('hidden', tabName !== 'login');
            document.getElementById('register-form').classList.toggle('hidden', tabName !== 'register');
        });
    });
    
    // Form de login
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                authToken = data.data.access_token;
                currentUser = data.data.user;
                // Não armazenar no localStorage - sempre exigir login
                showMainApp();
                showToast('Login realizado com sucesso!', 'success');
            } else {
                showToast(data.error || 'Erro ao fazer login', 'error');
            }
        } catch (error) {
            console.error('Erro ao fazer login:', error);
            showToast('Erro de conexão com o servidor: ' + error.message, 'error');
        }
    });
    
    // Form de registro
    document.getElementById('register-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                authToken = data.data.access_token;
                currentUser = data.data.user;
                // Não armazenar no localStorage - sempre exigir login
                showMainApp();
                showToast('Cadastro realizado com sucesso!', 'success');
            } else {
                // Mostrar erro detalhado
                const errorMsg = data.error || 'Erro ao cadastrar';
                showToast(errorMsg, 'error');
                console.error('Erro no cadastro:', data);
            }
        } catch (error) {
            console.error('Erro ao cadastrar:', error);
            showToast('Erro de conexão com o servidor: ' + error.message, 'error');
        }
    });
}

// Função removida - sempre exigir login manual

function showLoginScreen() {
    document.getElementById('login-screen').style.display = 'block';
    document.getElementById('main-app').style.display = 'none';
}

function showMainApp() {
    const loginScreen = document.getElementById('login-screen');
    const mainApp = document.getElementById('main-app');
    
    // Forçar esconder login e mostrar app
    loginScreen.style.cssText = 'display: none !important;';
    mainApp.style.cssText = 'display: block !important;';
    
    document.getElementById('user-name').textContent = currentUser.username;
    
    setupApp();
    loadDashboard();
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    showLoginScreen();
}

// ==================== CONFIGURAÇÃO DA APLICAÇÃO ====================

function setupApp() {
    // Navegação entre seções
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const section = btn.dataset.section;
            
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.getElementById(section).classList.add('active');
            
            // Carregar dados da seção
            if (section === 'dashboard') loadDashboard();
            if (section === 'transactions') loadTransactions();
            if (section === 'reports') loadReportsSection();
            if (section === 'investments') loadInvestments();
        });
    });
    
    // Form de transação
    document.getElementById('transaction-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await createTransaction();
    });
    
    // Form de investimento
    document.getElementById('investment-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await createInvestment();
    });
    
    // Form de simulação
    document.getElementById('simulation-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await runSimulation();
    });
    
    // Configurar busca de símbolos para investimentos
    setupSymbolSearch();
    
    // Configurar filtro do dashboard com botões
    setupPeriodFilter();
}

// ==================== FILTRO DE PERÍODO ====================

function setupPeriodFilter() {
    const periodBtns = document.querySelectorAll('.period-btn');
    const customDateRange = document.getElementById('custom-date-range');
    const applyCustomBtn = document.getElementById('apply-custom-filter');
    
    let currentPeriod = 'all';
    
    // Evento dos botões de período
    periodBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remover active de todos
            periodBtns.forEach(b => b.classList.remove('active'));
            // Adicionar active no clicado
            btn.classList.add('active');
            
            const period = btn.dataset.period;
            currentPeriod = period;
            
            if (period === 'custom') {
                customDateRange.style.display = 'block';
            } else {
                customDateRange.style.display = 'none';
                applyPeriodFilter(period);
            }
        });
    });
    
    // Botão de aplicar filtro customizado
    applyCustomBtn.addEventListener('click', () => {
        applyPeriodFilter('custom');
    });
}

function applyPeriodFilter(period) {
    const today = new Date();
    let startDate = null;
    let endDate = null;
    
    switch(period) {
        case 'all':
            // Sem filtro
            break;
            
        case 'today':
            startDate = new Date(today.setHours(0, 0, 0, 0));
            endDate = new Date(today.setHours(23, 59, 59, 999));
            break;
            
        case 'week':
            endDate = new Date();
            startDate = new Date();
            startDate.setDate(startDate.getDate() - 7);
            break;
            
        case 'month':
            endDate = new Date();
            startDate = new Date();
            startDate.setMonth(startDate.getMonth() - 1);
            break;
            
        case 'custom':
            const startInput = document.getElementById('dashboard-start-date').value;
            const endInput = document.getElementById('dashboard-end-date').value;
            
            if (startInput) startDate = new Date(startInput);
            if (endInput) endDate = new Date(endInput);
            break;
    }
    
    // Atualizar inputs (para referência)
    if (startDate) {
        document.getElementById('dashboard-start-date').value = startDate.toISOString().split('T')[0];
    } else {
        document.getElementById('dashboard-start-date').value = '';
    }
    
    if (endDate) {
        document.getElementById('dashboard-end-date').value = endDate.toISOString().split('T')[0];
    } else {
        document.getElementById('dashboard-end-date').value = '';
    }
    
    // Recarregar dashboard
    loadDashboard();
}

// ==================== DASHBOARD ====================

async function loadDashboard() {
    try {
        // Obter filtros de data
        const startDate = document.getElementById('dashboard-start-date').value;
        const endDate = document.getElementById('dashboard-end-date').value;
        
        // Construir query params
        let balanceQuery = '';
        let transactionsQuery = '';
        
        if (startDate || endDate) {
            const params = new URLSearchParams();
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);
            balanceQuery = '?' + params.toString();
            transactionsQuery = '?' + params.toString();
        }
        
        const [balanceRes, transactionsRes] = await Promise.all([
            fetch(`${API_BASE_URL}/balance${balanceQuery}`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            }),
            fetch(`${API_BASE_URL}/transactions${transactionsQuery}`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            })
        ]);
        
        const balanceData = await balanceRes.json();
        const transactionsData = await transactionsRes.json();
        
        if (balanceData.success) {
            document.getElementById('balance-value').textContent = 
                formatCurrency(parseFloat(balanceData.data.balance));
        }
        
        if (transactionsData.success) {
            const transactions = transactionsData.data;
            let income = 0, expense = 0;
            
            transactions.forEach(tx => {
                const amount = parseFloat(tx.amount.amount);
                if (tx.type === 'income') income += amount;
                else expense += amount;
            });
            
            document.getElementById('total-income').textContent = formatCurrency(income);
            document.getElementById('total-expense').textContent = formatCurrency(expense);
        }
    } catch (error) {
        showToast('Erro ao carregar dashboard', 'error');
    }
}

// ==================== TRANSAÇÕES ====================

async function loadTransactions() {
    try {
        const response = await fetch(`${API_BASE_URL}/transactions`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayTransactions(data.data);
        }
    } catch (error) {
        showToast('Erro ao carregar transações', 'error');
    }
}

function displayTransactions(transactions) {
    const container = document.getElementById('all-transactions');
    
    if (transactions.length === 0) {
        container.innerHTML = '<p class="empty-state">Nenhuma transação encontrada</p>';
        return;
    }
    
    container.innerHTML = transactions.map(tx => `
        <div class="transaction-item ${tx.type}">
            <div>
                <strong>${tx.description}</strong>
                <span>${tx.category.name}</span>
                <small>${new Date(tx.occurred_at).toLocaleDateString('pt-BR')}</small>
            </div>
            <div>
                <span class="amount ${tx.type}">
                    ${tx.type === 'income' ? '+' : '-'} ${formatCurrency(parseFloat(tx.amount.amount))}
                </span>
                <button onclick="deleteTransaction('${tx.id}')" class="btn-delete">🗑️</button>
            </div>
        </div>
    `).join('');
}

async function createTransaction() {
    const type = document.getElementById('tx-type').value;
    const amount = document.getElementById('tx-amount').value;
    const category = document.getElementById('tx-category').value;
    const description = document.getElementById('tx-description').value;
    const date = document.getElementById('tx-date').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/transactions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                type,
                amount: parseFloat(amount),
                category,
                description,
                occurred_at: date || undefined
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Transação criada com sucesso!', 'success');
            document.getElementById('transaction-form').reset();
            loadTransactions();
            loadDashboard();
        } else {
            showToast(data.error || 'Erro ao criar transação', 'error');
        }
    } catch (error) {
        showToast('Erro de conexão', 'error');
    }
}

async function deleteTransaction(id) {
    if (!confirm('Deseja realmente excluir esta transação?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/transactions/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Transação excluída', 'success');
            loadTransactions();
            loadDashboard();
        }
    } catch (error) {
        showToast('Erro ao excluir', 'error');
    }
}

// ==================== RELATÓRIOS ====================

async function loadReportsSection() {
    try {
        const response = await fetch(`${API_BASE_URL}/reports/available-months`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('report-month');
            select.innerHTML = '<option value="">Todos os meses</option>' +
                data.data.map(month => `<option value="${month}">${month}</option>`).join('');
        }
    } catch (error) {
        showToast('Erro ao carregar meses', 'error');
    }
}

async function loadMonthlyReport() {
    const selectedMonth = document.getElementById('report-month').value;
    
    try {
        let url = `${API_BASE_URL}/reports/monthly-by-category`;
        if (selectedMonth) {
            const [year, month] = selectedMonth.split('-');
            url += `?year=${year}&month=${parseInt(month)}`;
        }
        
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayMonthlyReport(data.data);
        }
    } catch (error) {
        showToast('Erro ao gerar relatório', 'error');
    }
}

function displayMonthlyReport(reportData) {
    const container = document.getElementById('monthly-report-content');
    
    if (Object.keys(reportData).length === 0) {
        container.innerHTML = '<p>Nenhum dado encontrado</p>';
        return;
    }
    
    let html = '';
    for (const [month, categories] of Object.entries(reportData)) {
        html += `<h4>${month}</h4><table class="projection-table">
            <thead><tr><th>Categoria</th><th>Valor</th></tr></thead><tbody>`;
        
        for (const [category, amount] of Object.entries(categories)) {
            const value = parseFloat(amount);
            const className = value >= 0 ? 'income' : 'expense';
            html += `<tr><td>${category}</td><td class="${className}">${formatCurrency(value)}</td></tr>`;
        }
        
        html += '</tbody></table>';
    }
    
    container.innerHTML = html;
}

// ==================== INVESTIMENTOS ====================

async function loadInvestments() {
    try {
        const response = await fetch(`${API_BASE_URL}/investments`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayInvestments(data.data);
        }
    } catch (error) {
        showToast('Erro ao carregar investimentos', 'error');
    }
}

function displayInvestments(investments) {
    const container = document.getElementById('investments-list');
    
    if (investments.length === 0) {
        container.innerHTML = '<p>Nenhum investimento cadastrado</p>';
        return;
    }
    
    container.innerHTML = investments.map(inv => `
        <div class="investment-card">
            <h4>${inv.name} <span style="font-size:0.8em; color:#666;">(${inv.type})</span></h4>
            <p>Valor Inicial: ${formatCurrency(parseFloat(inv.initial_amount.amount))}</p>
            <p>Valor Atual: ${formatCurrency(parseFloat(inv.current_amount.amount))}</p>
            <p>Lucro: <span class="${inv.profit_percentage >= 0 ? 'income' : 'expense'}">
                ${formatCurrency(parseFloat(inv.profit.amount))} (${inv.profit_percentage.toFixed(2)}%)
            </span></p>
            <p>Taxa Mensal: ${(inv.monthly_rate * 100).toFixed(2)}%</p>
            <button onclick="deleteInvestment('${inv.id}')" class="btn-delete">Excluir</button>
        </div>
    `).join('');
}

async function createInvestment() {
    const name = document.getElementById('inv-name').value;
    const type = document.getElementById('inv-type').value;
    const initial_amount = document.getElementById('inv-initial').value;
    const rate = document.getElementById('inv-rate').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/investments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                name,
                type,
                initial_amount: parseFloat(initial_amount),
                monthly_rate: parseFloat(rate) / 100
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Investimento criado!', 'success');
            document.getElementById('investment-form').reset();
            loadInvestments();
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('Erro de conexão', 'error');
    }
}

async function deleteInvestment(id) {
    if (!confirm('Deseja excluir este investimento?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/investments/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            showToast('Investimento excluído', 'success');
            loadInvestments();
        }
    } catch (error) {
        showToast('Erro ao excluir', 'error');
    }
}

// ==================== SIMULAÇÕES ====================

async function runSimulation() {
    const initial = document.getElementById('sim-initial').value;
    const contribution = document.getElementById('sim-contribution').value;
    const rate = document.getElementById('sim-rate').value;
    const months = document.getElementById('sim-months').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/simulations/fixed-contribution`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                initial_amount: parseFloat(initial),
                monthly_contribution: parseFloat(contribution),
                monthly_rate: parseFloat(rate) / 100,
                months: parseInt(months)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displaySimulationResult(data.data);
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('Erro ao simular', 'error');
    }
}

function displaySimulationResult(result) {
    const container = document.getElementById('simulation-result');
    
    const summary = `
        <div style="background:#e8f5e9; padding:15px; border-radius:8px; margin-bottom:20px;">
            <h4>Resumo da Simulação</h4>
            <p><strong>Total Investido:</strong> ${formatCurrency(parseFloat(result.total_contributed))}</p>
            <p><strong>Saldo Final:</strong> ${formatCurrency(parseFloat(result.final_balance))}</p>
            <p><strong>Lucro Total:</strong> <span class="income">${formatCurrency(parseFloat(result.total_profit))}</span></p>
        </div>
    `;
    
    const table = `
        <table class="projection-table">
            <thead>
                <tr>
                    <th>Mês</th>
                    <th>Aporte</th>
                    <th>Saldo Acumulado</th>
                    <th>Lucro</th>
                </tr>
            </thead>
            <tbody>
                ${result.projections.map(p => `
                    <tr>
                        <td>${p.month}</td>
                        <td>${formatCurrency(parseFloat(p.contribution))}</td>
                        <td>${formatCurrency(parseFloat(p.accumulated_balance))}</td>
                        <td class="${parseFloat(p.profit) >= 0 ? 'income' : 'expense'}">
                            ${formatCurrency(parseFloat(p.profit))}
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = summary + table;
}

// ==================== UTILIDADES ====================

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

