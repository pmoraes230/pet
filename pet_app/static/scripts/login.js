document.addEventListener("DOMContentLoaded", function () {

  // Ativa ícones Lucide (se estiver usando)
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }

  // ================= ESTADO =================
  let currentRole = "tutor";   // tutor | vet
  let currentMode = "login";   // login | register

  // ================= ELEMENTOS =================
  const authForm       = document.getElementById("auth-form");
  const roleInput      = document.getElementById("role-input");
  const sidePanel      = document.getElementById("side-panel");
  const roleBadge      = document.getElementById("role-badge");
  const heroTitle      = document.getElementById("hero-title");
  const heroDesc       = document.getElementById("hero-desc");

  const tabTutor       = document.getElementById("tab-tutor");
  const tabVet         = document.getElementById("tab-vet");

  const registerNameField = document.getElementById("register-name-field");
  const dateField      = document.getElementById("date-field");
  const cpfCnpjField   = document.getElementById("cpf-cnpj-field");
  const crmvField      = document.getElementById("crmv-field");

  const submitBtn      = document.getElementById("submit-btn");
  const formTitle      = document.getElementById("form-title");
  const formSubtitle   = document.getElementById("form-subtitle");
  const toggleText     = document.getElementById("toggle-text");
  const toggleBtn      = document.getElementById("toggle-btn");

  // URLs definidas via data attributes (melhor prática)
  const loginUrl    = authForm?.dataset.loginUrl    || "/login/";
  const registerUrl = authForm?.dataset.registerUrl || "/register/";

  // ================= FUNÇÕES AUXILIARES =================
  function updateActionURL() {
    if (authForm) {
      authForm.action = currentMode === "login" ? loginUrl : registerUrl;
    }
  }

  function updateVisibility() {
    const isRegister = currentMode === "register";

    // Função auxiliar para mostrar/esconder campos
    const toggleField = (container, show) => {
      if (container) {
        container.classList.toggle("hidden", !show);
      }
    };

    toggleField(registerNameField, isRegister);
    toggleField(dateField,      isRegister);
    toggleField(cpfCnpjField,   isRegister);

    // CRMV só aparece no cadastro de vet
    const showCrmv = isRegister && currentRole === "vet";
    toggleField(crmvField, showCrmv);
  }

  // ================= MUDANÇA DE ROLE =================
  window.switchRole = function (role) {
    currentRole = role;
    if (roleInput) roleInput.value = role;

    if (role === "tutor") {
      // Estilo Tutor
      tabTutor.className = "flex-1 py-2 text-sm font-bold rounded-lg bg-white text-gray-800 shadow-sm transition-all";
      tabVet.className   = "flex-1 py-2 text-sm font-bold rounded-lg text-gray-500 hover:bg-gray-50 transition-all";

      sidePanel.classList.remove("bg-brand-darkTeal");
      sidePanel.classList.add("bg-brand-purple");

      roleBadge.textContent = "Área do Tutor";
      roleBadge.className = "inline-block px-3 py-1 bg-white/20 rounded-full text-xs font-bold uppercase tracking-wide text-white";

      heroTitle.textContent = currentMode === "register" ? "Junte-se a nós!" : "Bem-vindo de volta!";
      heroDesc.textContent  = "Acompanhe a saúde emocional e física do seu pet em um só lugar.";

      submitBtn.className = "w-full bg-brand-purple text-white py-4 rounded-xl font-bold shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all";
    } else {
      // Estilo Veterinário
      tabVet.className   = "flex-1 py-2 text-sm font-bold rounded-lg bg-white text-gray-800 shadow-sm transition-all";
      tabTutor.className = "flex-1 py-2 text-sm font-bold rounded-lg text-gray-500 hover:bg-gray-50 transition-all";

      sidePanel.classList.remove("bg-brand-purple");
      sidePanel.classList.add("bg-brand-darkTeal");

      roleBadge.textContent = "Área do Veterinário";
      roleBadge.className = "inline-block px-3 py-1 bg-white/20 rounded-full text-xs font-bold uppercase tracking-wide text-white";

      heroTitle.textContent = currentMode === "register" ? "Expanda sua clínica" : "Olá, Doutor(a)";
      heroDesc.textContent  = "Gerencie seus pacientes, prontuários e conecte-se com novos tutores.";

      submitBtn.className = "w-full bg-brand-darkTeal text-white py-4 rounded-xl font-bold shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all";
    }

    updateVisibility();
    updateActionURL();
  };

  // ================= MUDANÇA DE MODO (login ↔ register) =================
  window.toggleMode = function () {
    currentMode = currentMode === "login" ? "register" : "login";

    if (currentMode === "register") {
      formTitle.textContent    = "Crie sua conta";
      formSubtitle.textContent = "É rápido, fácil e gratuito.";
      submitBtn.textContent    = "Cadastrar";
      toggleText.textContent   = "Já tem uma conta?";
      toggleBtn.textContent    = "Fazer Login";
    } else {
      formTitle.textContent    = "Acesse sua conta";
      formSubtitle.textContent = "Preencha seus dados para continuar.";
      submitBtn.textContent    = "Entrar";
      toggleText.textContent   = "Não tem conta?";
      toggleBtn.textContent    = "Criar cadastro";
    }

    switchRole(currentRole);  // atualiza também os textos do hero com base no novo modo
  };

  // ================= MÁSCARA CPF / CNPJ =================
  const cpfCnpjInput = document.getElementById("cpf-cnpj-input");
  if (cpfCnpjInput) {
    cpfCnpjInput.addEventListener("input", function (e) {
      let v = e.target.value.replace(/\D/g, "");

      if (v.length <= 11) {
        // CPF: 000.000.000-00
        v = v.replace(/(\d{3})(\d)/, "$1.$2")
             .replace(/(\d{3})(\d)/, "$1.$2")
             .replace(/(\d{3})(\d{1,2})$/, "$1-$2");
      } else {
        // CNPJ: 00.000.000/0000-00
        v = v.replace(/^(\d{2})(\d)/, "$1.$2")
             .replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3")
             .replace(/\.(\d{3})(\d)/, ".$1/$2")
             .replace(/(\d{4})(\d{1,2})$/, "$1-$2");
      }

      e.target.value = v;
    });
  }

  // Função para abrir modal genérico
function showModal(type = 'info', title, message, autoCloseMs = 0) {
    const modal = document.getElementById('custom-modal');
    const modalContent = document.getElementById('modal-content');
    const iconEl = document.getElementById('modal-icon');
    const titleEl = document.getElementById('modal-title');
    const messageEl = document.getElementById('modal-message');

    // Reset classes
    iconEl.className = 'w-12 h-12 rounded-full flex items-center justify-center text-white text-2xl';

    if (type === 'success') {
        iconEl.classList.add('bg-green-500');
        iconEl.innerHTML = '✓';
        titleEl.textContent = title || 'Sucesso';
        titleEl.classList.add('text-green-700');
    } 
    else if (type === 'error') {
        iconEl.classList.add('bg-red-500');
        iconEl.innerHTML = '✕';
        titleEl.textContent = title || 'Erro';
        titleEl.classList.add('text-red-700');
    } 
    else if (type === 'warning') {
        iconEl.classList.add('bg-yellow-500');
        iconEl.innerHTML = '!';
        titleEl.textContent = title || 'Atenção';
        titleEl.classList.add('text-yellow-700');
    } 
    else {
        iconEl.classList.add('bg-blue-500');
        iconEl.innerHTML = 'i';
        titleEl.textContent = title || 'Informação';
        titleEl.classList.add('text-blue-700');
    }

    messageEl.textContent = message;
    modal.classList.remove('hidden');
    modalContent.classList.remove('scale-95');
    modalContent.classList.add('scale-100');

    // Auto-fechar se definido
    if (autoCloseMs > 0) {
        setTimeout(closeModal, autoCloseMs);
    }
}

// Função para fechar modal
function closeModal() {
    const modal = document.getElementById('custom-modal');
    const modalContent = document.getElementById('modal-content');
    modalContent.classList.remove('scale-100');
    modalContent.classList.add('scale-95');
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 300); // tempo da animação
}

  // ================= INICIALIZAÇÃO =================
  if (roleInput) roleInput.value = "tutor";
  switchRole("tutor");        // inicia com tutor selecionado
  updateActionURL();          // define action inicial
  updateVisibility();         // esconde campos de cadastro inicialmente
});