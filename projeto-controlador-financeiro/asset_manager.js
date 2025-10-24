// ==================== GERENCIAMENTO DE ATIVOS PERSONALIZADOS ====================

// Usar a mesma URL base da API
const API_URL = typeof API_BASE_URL !== 'undefined' ? API_BASE_URL.replace('/api', '') : 'http://localhost:5010';

/**
 * Configurar gerenciamento de ativos
 */
function setupAssetManagement() {
    const assetForm = document.getElementById('asset-form');
    
    if (assetForm) {
        assetForm.addEventListener('submit', handleAssetSubmit);
    }
    
    // Carregar ativos ao entrar na seção
    const assetsBtn = document.querySelector('[data-section="assets"]');
    if (assetsBtn) {
        assetsBtn.addEventListener('click', loadAssets);
    }
}

/**
 * Carregar lista de ativos personalizados
 */
async function loadAssets() {
    try {
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
        
        const response = await fetch(`${API_URL}/api/assets`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayAssets(data.data);
        } else {
            showToast(data.error || 'Erro ao carregar ativos', 'error');
        }
    } catch (error) {
        console.error('Erro ao carregar ativos:', error);
        showToast('Erro ao carregar ativos', 'error');
    }
}

/**
 * Exibir lista de ativos
 */
function displayAssets(assets) {
    const container = document.getElementById('assets-list');
    
    if (!assets || assets.length === 0) {
        container.innerHTML = '<p style="text-align:center; color:#666;">Nenhum ativo personalizado cadastrado.</p>';
        return;
    }
    
    container.innerHTML = assets.map(asset => `
        <div class="investment-card" style="border-left-color: ${asset.type === 'crypto' ? '#FF9800' : '#2196F3'};">
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <div>
                    <h4>${asset.name} <span style="font-size:0.8em; color:#666;">(${asset.symbol})</span></h4>
                    <p><strong>Tipo:</strong> ${asset.type === 'stock' ? 'Ação' : 'Criptomoeda'}</p>
                    <p><strong>Preço:</strong> ${formatCurrency(asset.price)}</p>
                    <p style="font-size:0.85em; color:#666;">
                        Atualizado: ${new Date(asset.updated_at).toLocaleString('pt-BR')}
                    </p>
                </div>
                <div style="display:flex; gap:10px;">
                    <button onclick="editAsset('${asset.id}')" class="btn-primary" style="padding:5px 10px; font-size:0.9em;">
                        ✏️ Editar
                    </button>
                    <button onclick="deleteAsset('${asset.id}')" class="btn-delete" style="padding:5px 10px;">
                        🗑️
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Adicionar novo ativo
 */
async function handleAssetSubmit(e) {
    e.preventDefault();
    
    const symbol = document.getElementById('asset-symbol').value.trim().toUpperCase();
    const name = document.getElementById('asset-name').value.trim();
    const type = document.getElementById('asset-type').value;
    const price = parseFloat(document.getElementById('asset-price').value);
    
    if (!symbol || !name || !type || !price || price <= 0) {
        showToast('Preencha todos os campos corretamente', 'error');
        return;
    }
    
    try {
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
        
        const response = await fetch(`${API_URL}/api/assets`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ symbol, name, type, price })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Ativo adicionado com sucesso!', 'success');
            document.getElementById('asset-form').reset();
            loadAssets();
        } else {
            showToast(data.error || 'Erro ao adicionar ativo', 'error');
        }
    } catch (error) {
        console.error('Erro ao adicionar ativo:', error);
        showToast(`Erro ao adicionar ativo: ${error.message}`, 'error');
    }
}

/**
 * Editar ativo existente
 */
async function editAsset(assetId) {
    try {
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
        
        // Buscar dados do ativo
        const response = await fetch(`${API_URL}/api/assets/${assetId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (!data.success) {
            showToast('Erro ao carregar ativo', 'error');
            return;
        }
        
        const asset = data.data;
        
        // Pedir novo preço
        const newPriceStr = prompt(
            `Editar preço de ${asset.name} (${asset.symbol})\n\nPreço atual: R$ ${asset.price.toFixed(2)}\n\nNovo preço (em BRL):`,
            asset.price.toFixed(2)
        );
        
        if (newPriceStr === null) return; // Cancelado
        
        const newPrice = parseFloat(newPriceStr.replace(',', '.'));
        
        if (isNaN(newPrice) || newPrice <= 0) {
            showToast('Preço inválido', 'error');
            return;
        }
        
        // Atualizar preço
        const updateResponse = await fetch(`${API_URL}/api/assets/${assetId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ price: newPrice })
        });
        
        const updateData = await updateResponse.json();
        
        if (updateData.success) {
            showToast('Preço atualizado com sucesso!', 'success');
            loadAssets();
        } else {
            showToast(updateData.error || 'Erro ao atualizar preço', 'error');
        }
    } catch (error) {
        console.error('Erro ao editar ativo:', error);
        showToast('Erro ao editar ativo', 'error');
    }
}

/**
 * Deletar ativo
 */
async function deleteAsset(assetId) {
    if (!confirm('Tem certeza que deseja excluir este ativo?')) {
        return;
    }
    
    try {
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
        
        const response = await fetch(`${API_URL}/api/assets/${assetId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Ativo excluído com sucesso!', 'success');
            loadAssets();
        } else {
            showToast(data.error || 'Erro ao excluir ativo', 'error');
        }
    } catch (error) {
        console.error('Erro ao excluir ativo:', error);
        showToast('Erro ao excluir ativo', 'error');
    }
}

