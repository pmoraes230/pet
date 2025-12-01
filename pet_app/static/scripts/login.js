lucide.createIcons();

// State
let currentRole = "tutor"; // 'tutor' or 'vet'
let currentMode = "login"; // 'login' or 'register'

// Elements1
const sidePanel = document.getElementById("side-panel");
const roleBadge = document.getElementById("role-badge");
const heroTitle = document.getElementById("hero-title");
const heroDesc = document.getElementById("hero-desc");
const tabTutor = document.getElementById("tab-tutor");
const tabVet = document.getElementById("tab-vet");
const crmField = document.getElementById("crm-field");
const registerNameField = document.getElementById("register-name-field");
const submitBtn = document.getElementById("submit-btn");
const formTitle = document.getElementById("form-title");
const formSubtitle = document.getElementById("form-subtitle");
const toggleText = document.getElementById("toggle-text");
const toggleBtn = document.getElementById("toggle-btn");

// Check URL params for initial role
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get("type") === "vet") {
  switchRole("vet");
}

function switchRole(role) {
  currentRole = role;

  if (role === "tutor") {
    // Style Tabs
    tabTutor.className =
      "flex-1 py-2 text-sm font-bold rounded-lg transition-all shadow-sm bg-white text-gray-800";
    tabVet.className =
      "flex-1 py-2 text-sm font-bold rounded-lg transition-all text-gray-500 hover:text-gray-700";

    // Panel Style
    sidePanel.classList.remove("bg-brand-darkTeal");
    sidePanel.classList.add("bg-brand-purple");

    // Content
    roleBadge.textContent = "Área do Tutor";
    heroTitle.textContent =
      currentMode === "login" ? "Bem-vindo de volta!" : "Junte-se a nós!";
    heroDesc.textContent =
      "Acompanhe a saúde emocional e física do seu pet em um só lugar.";

    crmField.classList.add("hidden");
    updateButtonColor("purple");
  } else {
    // Style Tabs
    tabVet.className =
      "flex-1 py-2 text-sm font-bold rounded-lg transition-all shadow-sm bg-white text-gray-800";
    tabTutor.className =
      "flex-1 py-2 text-sm font-bold rounded-lg transition-all text-gray-500 hover:text-gray-700";

    // Panel Style
    sidePanel.classList.remove("bg-brand-purple");
    sidePanel.classList.add("bg-brand-darkTeal");

    // Content
    roleBadge.textContent = "Área do Veterinário";
    heroTitle.textContent =
      currentMode === "login" ? "Olá, Doutor(a)" : "Expanda sua clínica";
    heroDesc.textContent =
      "Gerencie seus pacientes, prontuários e conecte-se com novos tutores.";

    if (currentMode === "register") crmField.classList.remove("hidden");
    updateButtonColor("teal");
  }
}

function toggleMode() {
  currentMode = currentMode === "login" ? "register" : "login";

  if (currentMode === "register") {
    formTitle.textContent = "Crie sua conta";
    formSubtitle.textContent = "É rápido, fácil e gratuito.";
    submitBtn.textContent = "Cadastrar";
    toggleText.textContent = "Já tem uma conta?";
    toggleBtn.textContent = "Fazer Login";
    registerNameField.classList.remove("hidden");

    if (currentRole === "vet") crmField.classList.remove("hidden");

    // Update Hero text for context
    heroTitle.textContent =
      currentRole === "tutor" ? "Comece agora!" : "Parceria de sucesso";
  } else {
    formTitle.textContent = "Acesse sua conta";
    formSubtitle.textContent = "Preencha seus dados para continuar.";
    submitBtn.textContent = "Entrar";
    toggleText.textContent = "Não tem conta?";
    toggleBtn.textContent = "Criar cadastro";
    registerNameField.classList.add("hidden");
    crmField.classList.add("hidden");

    heroTitle.textContent =
      currentRole === "tutor" ? "Bem-vindo de volta!" : "Olá, Doutor(a)";
  }
}

function updateButtonColor(color) {
  if (color === "purple") {
    submitBtn.classList.remove("bg-brand-darkTeal");
    submitBtn.classList.add("bg-brand-purple");
  } else {
    submitBtn.classList.remove("bg-brand-purple");
    submitBtn.classList.add("bg-brand-darkTeal");
  }
}

function handleLogin(e) {
  e.preventDefault();
  // Mock authentication redirect
  if (currentRole === "tutor") {
    window.location.href = "tutor-dashboard.html";
  } else {
    window.location.href = "vet-dashboard.html";
  }
}
