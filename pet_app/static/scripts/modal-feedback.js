// modal-feedback.js
// Funções para exibir e controlar o modal de feedback (mensagens do Django)

// Abre o modal com animação de entrada
function openModal() {
    const modal = document.getElementById('custom-modal');
    const modalContent = document.getElementById('modal-content');
    if (!modal || !modalContent) return;

    // Estado inicial
    modalContent.classList.remove('scale-100');
    modalContent.classList.add('scale-95');

    modal.classList.remove('hidden');

    // Força reflow para garantir animação
    void modalContent.offsetWidth;

    modalContent.classList.remove('scale-95');
    modalContent.classList.add('scale-100');
}

// Fecha o modal com animação de saída
function closeModal() {
    const modal = document.getElementById('custom-modal');
    const modalContent = document.getElementById('modal-content');
    if (!modal || !modalContent) return;

    modalContent.classList.remove('scale-100');
    modalContent.classList.add('scale-95');

    setTimeout(() => {
        modal.classList.add('hidden');
        // Reset para próxima abertura
        modalContent.classList.remove('scale-95');
        modalContent.classList.add('scale-100');
    }, 300); // deve combinar com duration-300 no CSS
}

// Função principal de exibição do modal de feedback
function showFeedbackModal(type = 'info', title = '', message = '', autoCloseMs = 0) {
    const modal = document.getElementById('custom-modal');
    if (!modal) return;

    const iconEl     = document.getElementById('modal-icon');
    const titleEl    = document.getElementById('modal-title');
    const messageEl  = document.getElementById('modal-message');

    // Reset classes e conteúdo
    iconEl.className = 'w-12 h-12 rounded-full flex items-center justify-center text-white text-2xl';

    // Configuração por tipo
    if (type === 'success') {
        iconEl.classList.add('bg-green-500');
        iconEl.innerHTML = '✓';
        titleEl.textContent = title || 'Sucesso';
        titleEl.classList.add('text-green-700');
    } else if (type === 'error') {
        iconEl.classList.add('bg-red-500');
        iconEl.innerHTML = '✕';
        titleEl.textContent = title || 'Erro';
        titleEl.classList.add('text-red-700');
    } else if (type === 'warning') {
        iconEl.classList.add('bg-yellow-500');
        iconEl.innerHTML = '!';
        titleEl.textContent = title || 'Atenção';
        titleEl.classList.add('text-yellow-700');
    } else {
        // info/default
        iconEl.classList.add('bg-blue-500');
        iconEl.innerHTML = 'i';
        titleEl.textContent = title || 'Informação';
        titleEl.classList.add('text-blue-700');
    }

    messageEl.textContent = message;

    // Abre o modal
    openModal();

    // Auto-fechar quando desejado (geralmente success)
    if (autoCloseMs > 0) {
        setTimeout(closeModal, autoCloseMs);
    }
}

// Expõe as funções no escopo global para serem chamadas de qualquer lugar
window.showFeedbackModal = showFeedbackModal;
window.closeModal = closeModal;