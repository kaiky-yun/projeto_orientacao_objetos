/**
 * Cliente API para o Controlador Financeiro
 * Encapsula a comunicação HTTP com o backend Flask
 */

class FinanceAPIClient {
    constructor(baseURL = 'http://localhost:5010') {
        this.baseURL = baseURL;
        this.isConnected = false;
    }

    /**
     * Método auxiliar para fazer requisições HTTP
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, config);
            
            // Tentar parsear JSON, mas lidar com respostas vazias
            let data;
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            }

            if (!response.ok) {
                throw new Error(data?.error || `HTTP ${response.status}: ${response.statusText}`);
            }

            return {
                success: true,
                data: data,
                status: response.status
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                status: null
            };
        }
    }

    /**
     * Verificar saúde da API
     */
    async checkHealth() {
        const result = await this.request('/api/health');
        this.isConnected = result.success;
        return result;
    }

    /**
     * Listar todas as transações
     * @param {string} startDate - Data inicial (YYYY-MM-DD)
     * @param {string} endDate - Data final (YYYY-MM-DD)
     */
    async getTransactions(startDate = null, endDate = null) {
        let endpoint = '/api/transactions';
        const params = [];
        if (startDate) params.push(`start_date=${startDate}`);
        if (endDate) params.push(`end_date=${endDate}`);
        if (params.length > 0) {
            endpoint += '?' + params.join('&');
        }
        return this.request(endpoint);
    }

    /**
     * Obter uma transação específica pelo ID
     */
    async getTransaction(id) {
        return this.request(`/api/transactions/${id}`);
    }

    /**
     * Criar uma nova transação
     * @param {Object} transaction - Objeto com type, amount, description, category, occurred_at (opcional)
     */
    async createTransaction(transaction) {
        return this.request('/api/transactions', {
            method: 'POST',
            body: JSON.stringify(transaction)
        });
    }

    /**
     * Deletar uma transação
     */
    async deleteTransaction(id) {
        return this.request(`/api/transactions/${id}`, {
            method: 'DELETE'
        });
    }

    /**
     * Obter saldo total
     * @param {string} startDate - Data inicial (YYYY-MM-DD)
     * @param {string} endDate - Data final (YYYY-MM-DD)
     */
    async getBalance(startDate = null, endDate = null) {
        let endpoint = '/api/balance';
        const params = [];
        if (startDate) params.push(`start_date=${startDate}`);
        if (endDate) params.push(`end_date=${endDate}`);
        if (params.length > 0) {
            endpoint += '?' + params.join('&');
        }
        return this.request(endpoint);
    }

    /**
     * Gerar relatório agrupado por categoria ou mês
     * @param {string} groupBy - 'category' ou 'month'
     * @param {string} startDate - Data inicial (YYYY-MM-DD)
     * @param {string} endDate - Data final (YYYY-MM-DD)
     */
    async getReport(groupBy = 'category', startDate = null, endDate = null) {
        let endpoint = `/api/report?group_by=${groupBy}`;
        if (startDate) endpoint += `&start_date=${startDate}`;
        if (endDate) endpoint += `&end_date=${endDate}`;
        return this.request(endpoint);
    }

    /**
     * Obter lista de categorias únicas
     */
    async getCategories() {
        return this.request('/api/categories');
    }
}

// Instância global do cliente API
const apiClient = new FinanceAPIClient();

