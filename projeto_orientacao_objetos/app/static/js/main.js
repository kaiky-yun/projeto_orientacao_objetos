document.addEventListener('DOMContentLoaded', function() {
    initializeAlerts();
    initializeFormValidation();
    initializeDeleteForms();
    initializeCategoryLoad();
});

function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert && alert.parentElement) {
                fadeOut(alert);
            }
        }, 5000);
    });
}

function fadeOut(element) {
    element.style.opacity = '1';
    element.style.transition = 'opacity 0.3s ease';
    
    setTimeout(() => {
        element.style.opacity = '0';
        setTimeout(() => {
            if (element.parentElement) {
                element.parentElement.removeChild(element);
            }
        }, 300);
    }, 100);
}

function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('error');
            isValid = false;
        } else {
            input.classList.remove('error');
        }
    });
    
    return isValid;
}

function initializeDeleteForms() {
    const deleteForms = document.querySelectorAll('.delete-form');
    
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Tem certeza que deseja remover este item? Esta ação não pode ser desfeita.')) {
                e.preventDefault();
            }
        });
    });
}

function initializeCategoryLoad() {
    const typeSelect = document.getElementById('type');
    const categorySelect = document.getElementById('category');

    if (!typeSelect || !categorySelect) return;

    // Função para filtrar as categorias no front-end
    const filterCategories = (type) => {
        const options = categorySelect.querySelectorAll('option[data-type]');
        options.forEach(option => {
            if (option.getAttribute('data-type') === type) {
                option.style.display = '';
            } else {
                option.style.display = 'none';
                option.selected = false; // Desseleciona as categorias ocultas
            }
        });
        // Garante que a opção "Selecione uma categoria" esteja visível
        categorySelect.querySelector('option[value=""]').style.display = '';
    };

    // Adiciona listener para o select de Tipo
    typeSelect.addEventListener('change', () => filterCategories(typeSelect.value));
    
    // Dispara o filtro inicial se um tipo já estiver selecionado (caso de edição)
    if (typeSelect.value) {
        filterCategories(typeSelect.value);
    }
}

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('pt-BR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.textContent = message;
    
    const container = document.querySelector('.main-content') || document.body;
    container.insertBefore(toast, container.firstChild);
    
    setTimeout(() => fadeOut(toast), 3000);
}

const style = document.createElement('style');
style.textContent = `
    input.error,
    select.error,
    textarea.error {
        border-color: #f44336 !important;
        background-color: #ffebee !important;
    }
`;
document.head.appendChild(style);

window.showToast = showToast;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
