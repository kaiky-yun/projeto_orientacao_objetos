// ==================== FUNÇÕES DE COTAÇÃO ====================

/**
 * Busca o preço atual de uma ação
 */
async function getStockPrice(symbol, region = 'US') {
    try {
        const response = await fetch(`${API_BASE_URL}/prices/stock/${symbol}?region=${region}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        
        if (data.success) {
            return data.data;
        } else {
            console.error('Erro ao buscar cotação:', data.error);
            return null;
        }
    } catch (error) {
        console.error('Erro de conexão:', error);
        return null;
    }
}

/**
 * Busca o preço atual de uma criptomoeda
 */
async function getCryptoPrice(symbol) {
    try {
        const response = await fetch(`${API_BASE_URL}/prices/crypto/${symbol}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        
        if (data.success) {
            return data.data;
        } else {
            console.error('Erro ao buscar cotação:', data.error);
            return null;
        }
    } catch (error) {
        console.error('Erro de conexão:', error);
        return null;
    }
}

/**
 * Busca símbolos de ações/criptos
 */
async function searchSymbols(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/prices/search?q=${encodeURIComponent(query)}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        
        if (data.success) {
            return data.data;
        } else {
            return [];
        }
    } catch (error) {
        console.error('Erro ao buscar símbolos:', error);
        return [];
    }
}

/**
 * Adiciona campo de busca de símbolo ao formulário de investimento
 */
function setupSymbolSearch() {
    const form = document.getElementById('investment-form');
    const typeSelect = document.getElementById('inv-type');
    const nameInput = document.getElementById('inv-name');
    
    // Verificar se os elementos existem
    if (!form || !typeSelect || !nameInput) {
        console.warn('Elementos do formulário de investimento não encontrados. Busca de símbolos não será configurada.');
        return;
    }
    
    // Criar container para busca de símbolo
    const searchContainer = document.createElement('div');
    searchContainer.id = 'symbol-search-container';
    searchContainer.style.display = 'none';
    searchContainer.innerHTML = `
        <div class="form-group">
            <label for="symbol-search">Buscar Ação/Cripto</label>
            <input type="text" id="symbol-search" placeholder="Digite o nome ou símbolo...">
            <div id="symbol-results" class="symbol-results"></div>
        </div>
        <div class="form-group">
            <label for="symbol-input">Símbolo</label>
            <input type="text" id="symbol-input" placeholder="Ex: AAPL, PETR4.SA, BTC-USD" readonly>
        </div>
        <div class="form-group">
            <button type="button" id="fetch-price-btn" class="btn btn-secondary">
                🔄 Buscar Cotação Atual
            </button>
        </div>
        <div id="price-info" class="price-info" style="display: none;"></div>
    `;
    
    // Inserir após o campo de tipo
    typeSelect.parentElement.parentElement.after(searchContainer);
    
    // Mostrar/esconder busca baseado no tipo
    typeSelect.addEventListener('change', () => {
        const type = typeSelect.value;
        if (type === 'renda_variavel' || type === 'criptomoeda') {
            searchContainer.style.display = 'block';
        } else {
            searchContainer.style.display = 'none';
        }
    });
    
    // Busca de símbolos
    const symbolSearch = document.getElementById('symbol-search');
    const symbolResults = document.getElementById('symbol-results');
    const symbolInput = document.getElementById('symbol-input');
    
    let searchTimeout;
    symbolSearch.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        const query = symbolSearch.value.trim();
        
        if (query.length < 2) {
            symbolResults.innerHTML = '';
            return;
        }
        
        searchTimeout = setTimeout(async () => {
            const results = await searchSymbols(query);
            
            if (results.length > 0) {
                symbolResults.innerHTML = results.map(r => 
                    `<div class="symbol-result-item" data-symbol="${r.symbol}">
                        <strong>${r.symbol}</strong> - ${r.name}
                    </div>`
                ).join('');
                
                // Adicionar evento de clique nos resultados
                document.querySelectorAll('.symbol-result-item').forEach(item => {
                    item.addEventListener('click', () => {
                        const symbol = item.dataset.symbol;
                        symbolInput.value = symbol;
                        symbolSearch.value = item.textContent.trim();
                        symbolResults.innerHTML = '';
                    });
                });
            } else {
                symbolResults.innerHTML = '<div class="no-results">Nenhum resultado encontrado</div>';
            }
        }, 300);
    });
    
    // Buscar cotação
    document.getElementById('fetch-price-btn').addEventListener('click', async () => {
        const symbol = symbolInput.value.trim();
        const type = typeSelect.value;
        
        if (!symbol) {
            showToast('Digite um símbolo primeiro', 'warning');
            return;
        }
        
        showToast('Buscando cotação...', 'info');
        
        let priceData;
        if (type === 'criptomoeda') {
            priceData = await getCryptoPrice(symbol);
        } else {
            const region = symbol.includes('.SA') ? 'BR' : 'US';
            priceData = await getStockPrice(symbol, region);
        }
        
        if (priceData) {
            // Atualizar campos do formulário
            nameInput.value = priceData.name;
            document.getElementById('inv-initial').value = priceData.price;
            
            // Mostrar informações da cotação
            const priceInfo = document.getElementById('price-info');
            priceInfo.style.display = 'block';
            priceInfo.innerHTML = `
                <div class="price-card">
                    <h4>📊 Cotação Atual</h4>
                    <p><strong>${priceData.name}</strong> (${priceData.symbol})</p>
                    <p class="price-value">${formatCurrency(priceData.price)}</p>
                    <p class="price-details">
                        Máxima: ${formatCurrency(priceData.day_high)} | 
                        Mínima: ${formatCurrency(priceData.day_low)}
                    </p>
                    <p class="price-source">Fonte: ${priceData.source}</p>
                    <p class="price-timestamp">Atualizado: ${new Date(priceData.timestamp).toLocaleString('pt-BR')}</p>
                </div>
            `;
            
            showToast('Cotação obtida com sucesso!', 'success');
        } else {
            showToast('Não foi possível obter a cotação', 'error');
        }
    });
}

// CSS adicional para os resultados de busca
const style = document.createElement('style');
style.textContent = `
    .symbol-results {
        max-height: 200px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 4px;
        margin-top: 5px;
        background: white;
    }
    
    .symbol-result-item {
        padding: 10px;
        cursor: pointer;
        border-bottom: 1px solid #eee;
    }
    
    .symbol-result-item:hover {
        background: #f5f5f5;
    }
    
    .symbol-result-item:last-child {
        border-bottom: none;
    }
    
    .no-results {
        padding: 10px;
        color: #999;
        text-align: center;
    }
    
    .price-info {
        margin-top: 15px;
    }
    
    .price-card {
        background: #f9f9f9;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
    }
    
    .price-card h4 {
        margin-top: 0;
        color: #4CAF50;
    }
    
    .price-value {
        font-size: 24px;
        font-weight: bold;
        color: #2196F3;
        margin: 10px 0;
    }
    
    .price-details {
        font-size: 14px;
        color: #666;
    }
    
    .price-source, .price-timestamp {
        font-size: 12px;
        color: #999;
        margin: 5px 0;
    }
    
    .btn-secondary {
        background: #2196F3;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
    }
    
    .btn-secondary:hover {
        background: #1976D2;
    }
`;
document.head.appendChild(style);

