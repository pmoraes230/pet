
document.addEventListener("DOMContentLoaded", function () {

  // Ativa ícones Lucide
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }

  // ================= ESTADO =================
  let currentRole = "tutor"; // tutor | vet
  let currentMode = "login"; // login | register
  let isSubmitting = false;

  // ================= ELEMENTOS =================
  const authForm = document.getElementById("auth-form");
  const roleInput = document.getElementById("role-input");
  const sidePanel = document.getElementById("side-panel");
  const roleBadge = document.getElementById("role-badge");
  const heroTitle = document.getElementById("hero-title");
  const heroDesc = document.getElementById("hero-desc");

  const tabTutor = document.getElementById("tab-tutor");
  const tabVet = document.getElementById("tab-vet");

  const registerNameField = document.getElementById("register-name-field");
  const dateField = document.getElementById("date-field");
  const cpfCnpjField = document.getElementById("cpf-cnpj-field");
  const crmField = document.getElementById("crmv-field");

  const inputNome = document.querySelector('input[name="nome"]');
  const inputData = document.querySelector('input[name="data_nascimento"]');
  const inputCpfCnpj = document.querySelector('input[name="cpf_cnpj"]');
  const inputCrmv = document.querySelector('input[name="crmv"]');

  const submitBtn = document.getElementById("submit-btn");
  const formTitle = document.getElementById("form-title");
  const formSubtitle = document.getElementById("form-subtitle");
  const toggleText = document.getElementById("toggle-text");
  const toggleBtn = document.getElementById("toggle-btn");

  // CSRF Token (pega uma vez)
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

  // ================= FUNÇÕES AUXILIARES =================
  function updateActionURL() {
    authForm.action = currentMode === "login" ? "/login/" : "/register/";
    console.log("Form action:", authForm.action);
  }

  function updateVisibility() {
    const isRegister = currentMode === "register";

    const toggleField = (container, input, show) => {
      if (!container) return;
      container.classList.toggle("hidden", !show);
      if (input) input.disabled = !show;
    };

    toggleField(registerNameField, inputNome, isRegister);
    toggleField(dateField, inputData, isRegister);
    toggleField(cpfCnpjField, inputCpfCnpj, isRegister);

    const showCrmv = isRegister && currentRole === "vet";
    toggleField(crmField, inputCrmv, showCrmv);
  }

  // ================= MUDANÇA DE ROLE =================
  window.switchRole = function (role) {
    currentRole = role;
    if (roleInput) roleInput.value = role;

    if (role === "tutor") {
      tabTutor.className = "flex-1 py-2 text-sm font-bold rounded-lg bg-white text-gray-800 shadow-sm transition-all";
      tabVet.className = "flex-1 py-2 text-sm font-bold rounded-lg text-gray-500 hover:bg-gray-50 transition-all";

      sidePanel.classList.remove("bg-brand-darkTeal");
      sidePanel.classList.add("bg-brand-purple");

      roleBadge.textContent = "Área do Tutor";
      roleBadge.className = "bg-white/20 text-white px-3 py-1 rounded-full text-xs font-bold backdrop-blur-sm";

      heroTitle.textContent = currentMode === "register" ? "Junte-se a nós!" : "Bem-vindo de volta!";
      heroDesc.textContent = "Acompanhe a saúde emocional e física do seu pet em um só lugar.";

      submitBtn.className = "w-full py-3 rounded-xl font-bold text-white transition-all transform hover:-translate-y-0.5 bg-brand-purple hover:bg-purple-700 shadow-lg shadow-purple-200";
    } else {
      tabVet.className = "flex-1 py-2 text-sm font-bold rounded-lg bg-white text-gray-800 shadow-sm transition-all";
      tabTutor.className = "flex-1 py-2 text-sm font-bold rounded-lg text-gray-500 hover:bg-gray-50 transition-all";

      sidePanel.classList.remove("bg-brand-purple");
      sidePanel.classList.add("bg-brand-darkTeal");

      roleBadge.textContent = "Área do Veterinário";

      heroTitle.textContent = currentMode === "register" ? "Expanda sua clínica" : "Olá, Doutor(a)";
      heroDesc.textContent = "Gerencie seus pacientes, prontuários e conecte-se com novos tutores.";

      submitBtn.className = "w-full py-3 rounded-xl font-bold text-white transition-all transform hover:-translate-y-0.5 bg-brand-darkTeal hover:bg-teal-800 shadow-lg shadow-teal-100";
    }

    updateVisibility();
    updateActionURL();
  };

  // ================= MUDANÇA DE MODO =================
  window.toggleMode = function () {
    currentMode = currentMode === "login" ? "register" : "login";

    if (currentMode === "register") {
      formTitle.textContent = "Crie sua conta";
      formSubtitle.textContent = "É rápido, fácil e gratuito.";
      submitBtn.textContent = "Cadastrar";
      toggleText.textContent = "Já tem uma conta?";
      toggleBtn.textContent = "Fazer Login";
    } else {
      formTitle.textContent = "Acesse sua conta";
      formSubtitle.textContent = "Preencha seus dados para continuar.";
      submitBtn.textContent = "Entrar";
      toggleText.textContent = "Não tem conta?";
      toggleBtn.textContent = "Criar cadastro";
    }

    switchRole(currentRole);
  };

  // ================= MÁSCARA CPF/CNPJ =================
  const cpfCnpjInput = document.getElementById("cpf-cnpj-input");
  if (cpfCnpjInput) {
    cpfCnpjInput.addEventListener("input", e => {
      let v = e.target.value.replace(/\D/g, "");
      if (v.length <= 11) {
        v = v.replace(/(\d{3})(\d)/, "$1.$2")
          .replace(/(\d{3})(\d)/, "$1.$2")
          .replace(/(\d{3})(\d{1,2})$/, "$1-$2");
      } else {
        v = v.replace(/^(\d{2})(\d)/, "$1.$2")
          .replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3")
          .replace(/\.(\d{3})(\d)/, ".$1/$2")
          .replace(/(\d{4})(\d{1,2})$/, "$1-$2");
      }
      e.target.value = v;
    });
  }

  // ================= SUBMISSÃO AJAX =================
  function handleSubmit(event) {
    if (isSubmitting) return;

    isSubmitting = true;
    submitBtn.disabled = true;
    submitBtn.textContent = currentMode === "login" ? "Entrando..." : "Cadastrando...";
}

  // ================= CONTROLE DO MODAL =================
  function showModal(type, title, message, autoCloseMs = 0) {
    const modal = document.getElementById("custom-modal");
    const content = document.getElementById("modal-content");
    const modalTitle = document.getElementById("modal-title");
    const modalMessage = document.getElementById("modal-message");
    const modalIcon = document.getElementById("modal-icon");

    if (!modal) return;

    modalTitle.textContent = title || "Atenção";
    modalMessage.textContent = message || "Operação concluída.";

    // Reset e configuração do ícone
    modalIcon.className = "w-14 h-14 rounded-full flex items-center justify-center text-white text-3xl font-bold shrink-0";
    modalIcon.textContent = "";

    if (type === "success") {
      modalIcon.textContent = "✓";
      modalIcon.classList.add("bg-green-500");
    } else if (type === "error") {
      modalIcon.textContent = "!";
      modalIcon.classList.add("bg-red-500");
    } else {
      modalIcon.textContent = "i";
      modalIcon.classList.add("bg-blue-500");
    }

    // Mostra com animação
    modal.classList.remove("hidden");
    modal.classList.add("flex");

    setTimeout(() => {
      content.classList.remove("scale-95", "opacity-0");
      content.classList.add("scale-100", "opacity-100");
    }, 10);

    if (autoCloseMs > 0) {
      setTimeout(closeModal, autoCloseMs);
    }

    // Foco no botão OK (melhora acessibilidade)
    document.getElementById("modal-ok-btn")?.focus();
  }

  function closeModal() {
    const modal = document.getElementById("custom-modal");
    const content = document.getElementById("modal-content");

    if (!modal) return;

    content.classList.remove("scale-100", "opacity-100");
    content.classList.add("scale-95", "opacity-0");

    setTimeout(() => {
      modal.classList.remove("flex");
      modal.classList.add("hidden");
    }, 300); // tempo da transição
  }

  function handleModalBackdropClick(event) {
    // Só fecha se clicou no fundo (backdrop), não no conteúdo
    if (event.target.id === "custom-modal") {
      closeModal();
    }
  }

  // Opcional: fechar com tecla Esc
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      const modal = document.getElementById("custom-modal");
      if (modal && !modal.classList.contains("hidden")) {
        closeModal();
      }
    }
  });

  // ================= INICIALIZAÇÃO =================
  if (roleInput) roleInput.value = "tutor";
  switchRole("tutor");

  if (authForm) {
    authForm.addEventListener("submit", handleSubmit);
  } else {
    console.warn("Formulário #auth-form não encontrado");
  }

  // Clique fora do modal
  const modalElement = document.getElementById("custom-modal");
  if (modalElement) {
    modalElement.addEventListener("click", handleModalBackdropClick);
  }
});
