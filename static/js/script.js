// ===========================
// VARIÁVEIS GLOBAIS
// ===========================

let currentFile = null;
let currentCategory = null;
let currentResponse = null;
let currentContent = null;

// ===========================
// GERENCIAMENTO DE ABAS
// ===========================

document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeUploadZone();
    initializeTextarea();
});

function initializeTabs() {
    const tabs = document.querySelectorAll('.tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;
            
            // Remover active de todas as abas
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Adicionar active na aba clicada
            tab.classList.add('active');
            document.getElementById(`${targetTab}-tab`).classList.add('active');
        });
    });
}

// ===========================
// UPLOAD ZONE - DRAG & DROP
// ===========================

function initializeUploadZone() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');

    // Click para abrir seletor de arquivo
    uploadZone.addEventListener('click', () => fileInput.click());

    // Drag over
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('drag-over');
    });

    // Drag leave
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('drag-over');
    });

    // Drop
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    // Input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
}

// ===========================
// MANIPULAÇÃO DE ARQUIVO
// ===========================

function handleFileSelect(file) {
    const validTypes = ['text/plain', 'application/pdf'];
    const maxSize = 2 * 1024 * 1024; // 2MB

    // Validar tipo
    if (!validTypes.includes(file.type)) {
        showToast('Formato inválido. Use .txt ou .pdf', 'error');
        return;
    }

    // Validar tamanho
    if (file.size > maxSize) {
        showToast('Arquivo muito grande. Máximo: 2MB', 'error');
        return;
    }

    currentFile = file;
    
    // Atualizar UI
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
    document.getElementById('filePreview').classList.add('show');
    document.getElementById('uploadZone').classList.add('has-file');
    
    showToast('Arquivo carregado com sucesso!', 'success');
}

function removeFile() {
    currentFile = null;
    document.getElementById('fileInput').value = '';
    document.getElementById('filePreview').classList.remove('show');
    document.getElementById('uploadZone').classList.remove('has-file');
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// ===========================
// TEXTAREA - CONTADOR
// ===========================

function initializeTextarea() {
    const emailText = document.getElementById('emailText');
    
    emailText.addEventListener('input', () => {
        const count = emailText.value.length;
        document.getElementById('charCount').textContent = count;
        
        // Limitar a 10000 caracteres
        if (count > 10000) {
            emailText.value = emailText.value.substring(0, 10000);
            document.getElementById('charCount').textContent = 10000;
        }
    });
}

// ===========================
// PROCESSAR EMAIL
// ===========================

async function processEmail() {
    const activeTab = document.querySelector('.tab.active').dataset.tab;
    
    // Preparar dados
    const formData = new FormData();

    if (activeTab === 'upload') {
        if (!currentFile) {
            showToast('Selecione um arquivo primeiro', 'error');
            return;
        }
        formData.append('file', currentFile);
    } else {
        const content = document.getElementById('emailText').value.trim();
        if (!content) {
            showToast('Digite o conteúdo do email', 'error');
            return;
        }
        formData.append('text', content);
    }

    // Mostrar loading
    showLoading(true);

    try {
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Erro ao processar email');
        }

        // Exibir resultados
        displayResults(data.category, data.response, data.content_preview || '');
        
        showToast('Email processado com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao processar: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// ===========================
// EXIBIR RESULTADOS
// ===========================

function displayResults(category, response, content) {
    currentCategory = category;
    currentResponse = response;
    currentContent = content;

    // Atualizar badge de categoria
    const categoryBadge = document.getElementById('categoryBadge');
    const categoryIcon = document.getElementById('categoryIcon');
    const categoryText = document.getElementById('categoryText');
    
    categoryBadge.className = 'category-badge ' + category.toLowerCase();
    categoryIcon.textContent = category === 'Produtivo' ? '✓' : '○';
    categoryText.textContent = category;
    
    // Atualizar resposta
    document.getElementById('responseText').textContent = response;
    
    // Mostrar área de resultados
    document.getElementById('resultArea').style.display = 'block';
    
    // Reset feedback
    document.getElementById('correctionOptions').style.display = 'none';
    document.getElementById('correctionCategory').value = '';
    
    // Scroll suave
    document.getElementById('resultArea').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'nearest' 
    });
}

// ===========================
// COPIAR RESPOSTA
// ===========================

function copyResponse() {
    if (!currentResponse) {
        showToast('Nenhuma resposta para copiar', 'error');
        return;
    }

    navigator.clipboard.writeText(currentResponse)
        .then(() => {
            showToast('Resposta copiada!', 'success');
        })
        .catch(() => {
            showToast('Erro ao copiar', 'error');
        });
}

// ===========================
// FEEDBACK
// ===========================

function showCorrectionOptions() {
    document.getElementById('correctionOptions').style.display = 'block';
}

async function sendFeedback(type) {
    if (type === 'incorrect') {
        const correction = document.getElementById('correctionCategory').value;
        if (!correction) {
            showToast('Selecione a categoria correta', 'error');
            return;
        }

        // Enviar feedback com correção
        await submitFeedback(type, correction);
    } else {
        // Feedback positivo
        await submitFeedback(type, null);
    }
}

async function submitFeedback(feedbackType, correction) {
    const formData = new FormData();
    formData.append('original_text', currentContent);
    formData.append('predicted', currentCategory);
    formData.append('feedback_type', feedbackType);
    if (correction) {
        formData.append('correction', correction);
    }

    try {
        const response = await fetch('/feedback', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Feedback enviado! Obrigado por nos ajudar a melhorar.', 'success');
            
            // Reset opções de correção
            document.getElementById('correctionOptions').style.display = 'none';
            document.getElementById('correctionCategory').value = '';
        } else {
            throw new Error(data.error || 'Erro ao enviar feedback');
        }
    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao enviar feedback: ' + error.message, 'error');
    }
}

// ===========================
// LOADING
// ===========================

function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    const btn = document.getElementById('processBtn');
    
    overlay.classList.toggle('show', show);
    btn.disabled = show;
}

// ===========================
// TOAST NOTIFICATIONS
// ===========================

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    toastMessage.textContent = message;
    toast.className = 'toast show ' + type;
    
    // Auto hide após 3 segundos
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ===========================
// UTILIDADES
// ===========================

// Prevenir submit de formulário (se houver)
document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
        });
    });
});

// Log de erros
window.addEventListener('error', (e) => {
    console.error('Erro global:', e.error);
});