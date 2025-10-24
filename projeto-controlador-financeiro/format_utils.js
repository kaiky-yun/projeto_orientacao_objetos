// ==================== UTILITÁRIOS DE FORMATAÇÃO ====================

/**
 * Formata um número como moeda brasileira (R$ x.xxx,xx)
 * @param {number} value - Valor a ser formatado
 * @returns {string} - Valor formatado como R$ x.xxx,xx
 */
function formatCurrency(value) {
    if (value === null || value === undefined || isNaN(value)) {
        return 'R$ 0,00';
    }
    
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

/**
 * Converte string de moeda brasileira para número
 * @param {string} currencyString - String no formato R$ x.xxx,xx
 * @returns {number} - Valor numérico
 */
function parseCurrency(currencyString) {
    if (!currencyString) return 0;
    
    // Remove R$, espaços e pontos (milhares)
    let cleaned = currencyString.replace(/R\$\s?/g, '').replace(/\./g, '');
    // Substitui vírgula por ponto (decimal)
    cleaned = cleaned.replace(',', '.');
    
    return parseFloat(cleaned) || 0;
}

/**
 * Formata um número com separadores de milhares brasileiros
 * @param {number} value - Valor a ser formatado
 * @param {number} decimals - Número de casas decimais (padrão: 2)
 * @returns {string} - Valor formatado como x.xxx,xx
 */
function formatNumber(value, decimals = 2) {
    if (value === null || value === undefined || isNaN(value)) {
        return '0,00';
    }
    
    return new Intl.NumberFormat('pt-BR', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(value);
}

/**
 * Formata uma data no padrão brasileiro
 * @param {Date|string} date - Data a ser formatada
 * @param {boolean} includeTime - Se deve incluir hora (padrão: false)
 * @returns {string} - Data formatada
 */
function formatDate(date, includeTime = false) {
    if (!date) return '';
    
    const dateObj = date instanceof Date ? date : new Date(date);
    
    if (includeTime) {
        return dateObj.toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    return dateObj.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

/**
 * Formata uma porcentagem
 * @param {number} value - Valor a ser formatado (ex: 0.08 para 8%)
 * @param {number} decimals - Número de casas decimais (padrão: 2)
 * @returns {string} - Valor formatado como x,xx%
 */
function formatPercent(value, decimals = 2) {
    if (value === null || value === undefined || isNaN(value)) {
        return '0,00%';
    }
    
    return new Intl.NumberFormat('pt-BR', {
        style: 'percent',
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(value);
}

