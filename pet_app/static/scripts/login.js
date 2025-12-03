lucide.createIcons();

// State
let currentRole = window.currentRole || "tutor"; // 'tutor' or 'vet'
let currentMode = "login"; // 'login' or 'register'

// Elements1
const sidePanel = document.getElementById("side-panel");
const roleBadge = document.getElementById("role-badge");
const heroTitle = document.getElementById("hero-title");
const heroDesc = document.getElementById("hero-desc");
const tabTutor = document.getElementById("tab-tutor");
const tabVet = document.getElementById("tab-vet");
const crmField = document.getElementById("crm-field");
const dateField = document.getElementById("date-field")
const cpfField = document.getElementById("cpf-field")
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
    dateField.classList.remove('hidden')
    cpfField.classList.remove("hidden")

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
    dateField.classList.add("hidden");
    cpfField.classList.add("hidden")
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

async function handleSubmit(e) {
  e.preventDefault();

  const email = document.querySelector('input[type="email"]').value.trim();
  const senha = document.querySelector('input[type="password"]').value;
  const nome = document.querySelector('#register-name-field input')?.value.trim() || "";
  const crmv = document.querySelector('#crm-field input')?.value.trim() || "";
  const cpf = document.querySelector('#cpf-field input')?.value.trim() || "";
  const nascimento = document.querySelector('date-field input')?.value.trim() | "";

  if (!email || !senha) {
      alert("Preencha email e senha");
      return;
  }

  const payload = {
      email,
      senha,
      role: currentRole,
      cpf,
      nascimento
  };

  // Só adiciona nome/crmv se estiver em modo cadastro
  if (currentMode === "register") {
      payload.nome = nome;
      payload.cpf,
      payload.nascimento
      if (currentRole === "vet") payload.crmv = crmv;
  }

  const url = currentMode === "login" ? "/login/" : "/register/";

  try {
      const response = await fetch(url, {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]')?.value || ""
          },
          body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (result.success) {
          window.location.href = result.redirect;
      } else {
          alert(result.error || "Ocorreu um erro");
      }
  } catch (err) {
      console.error(err);
      alert("Erro de conexão");
  }
}

// Só isso! O resto (trocar abas, modo login/cadastro) continua igual
document.getElementById("auth-form").onsubmit = handleSubmit;