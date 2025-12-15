document.addEventListener("DOMContentLoaded", function () {

  // Ativa ícones Lucide
  lucide.createIcons();

  // ================= ESTADO =================
  let currentRole = "tutor"; // tutor | vet
  let currentMode = "login"; // login | register

  // ================= ELEMENTOS =================
  const authForm = document.getElementById("auth-form"); // ✅ ADICIONADO
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

  const submitBtn = document.getElementById("submit-btn");
  const formTitle = document.getElementById("form-title");
  const formSubtitle = document.getElementById("form-subtitle");
  const toggleText = document.getElementById("toggle-text");
  const toggleBtn = document.getElementById("toggle-btn");

  // ================= VISIBILIDADE =================
  function updateVisibility() {
    const isRegister = currentMode === "register";
    const isVet = currentRole === "vet";

    registerNameField.classList.toggle("hidden", !isRegister);
    dateField.classList.toggle("hidden", !isRegister);
    cpfCnpjField.classList.toggle("hidden", !isRegister);
    crmField.classList.toggle("hidden", !(isRegister && isVet));
  }

  // ================= ROLE =================
  window.switchRole = function (role) {
    currentRole = role;
    roleInput.value = role;

    if (role === "tutor") {
      tabTutor.className =
        "flex-1 py-2 text-sm font-bold rounded-lg bg-white text-gray-800";
      tabVet.className =
        "flex-1 py-2 text-sm font-bold rounded-lg text-gray-500";

      sidePanel.classList.remove("bg-brand-darkTeal");
      sidePanel.classList.add("bg-brand-purple");

      roleBadge.textContent = "Área do Tutor";
      heroTitle.textContent =
        currentMode === "register" ? "Junte-se a nós!" : "Bem-vindo de volta!";
      heroDesc.textContent =
        "Acompanhe a saúde emocional e física do seu pet em um só lugar.";

      submitBtn.classList.remove("bg-brand-darkTeal");
      submitBtn.classList.add("bg-brand-purple");
    } else {
      tabVet.className =
        "flex-1 py-2 text-sm font-bold rounded-lg bg-white text-gray-800";
      tabTutor.className =
        "flex-1 py-2 text-sm font-bold rounded-lg text-gray-500";

      sidePanel.classList.remove("bg-brand-purple");
      sidePanel.classList.add("bg-brand-darkTeal");

      roleBadge.textContent = "Área do Veterinário";
      heroTitle.textContent =
        currentMode === "register" ? "Expanda sua clínica" : "Olá, Doutor(a)";
      heroDesc.textContent =
        "Gerencie seus pacientes, prontuários e conecte-se com novos tutores.";

      submitBtn.classList.remove("bg-brand-purple");
      submitBtn.classList.add("bg-brand-darkTeal");
    }

    updateVisibility();
  };

  // ================= MODE =================
  window.toggleMode = function () {
    currentMode = currentMode === "login" ? "register" : "login";

    if (currentMode === "register") {
      authForm.action = "/register/"; // ✅ ADICIONADO
      formTitle.textContent = "Crie sua conta";
      formSubtitle.textContent = "É rápido, fácil e gratuito.";
      submitBtn.textContent = "Cadastrar";
      toggleText.textContent = "Já tem uma conta?";
      toggleBtn.textContent = "Fazer Login";
    } else {
      authForm.action = "/login/"; // ✅ ADICIONADO
      formTitle.textContent = "Acesse sua conta";
      formSubtitle.textContent = "Preencha seus dados para continuar.";
      submitBtn.textContent = "Entrar";
      toggleText.textContent = "Não tem conta?";
      toggleBtn.textContent = "Criar cadastro";
    }

    updateVisibility();
  };

  // ================= CPF / CNPJ =================
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

  // ================= INIT =================
  updateVisibility();

});
