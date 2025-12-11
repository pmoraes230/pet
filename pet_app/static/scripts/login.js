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
const dateField = document.getElementById("date-field");
const cpfField = document.getElementById("cpf-field");
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
    dateField.classList.remove("hidden");
    cpfField.classList.remove("hidden");

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
    cpfField.classList.add("hidden");
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
  const nome = document.querySelector("#register-name-field input")?.value.trim() || "";
  const crmv = document.querySelector("#crm-field input")?.value.trim() || "";
  const cpfInput = document.querySelector("#cpf-field input")?.value || "";
  const cpf = cpfInput.replace(/\D/g, "");
  const nascimento = document.querySelector('#date-field input')?.value.trim() || "";

  // Validações básicas
  if (!email || !senha) {
    showModal("error", "Campos obrigatórios", "Preencha email e senha");
    return;
  }

  // Validações do modo cadastro
  if (currentMode === "register") {
    if (!nome) {
      showModal("warning", "Nome faltando", "Por favor, informe seu nome completo");
      return;
    }
    if (!cpf) {
      showModal("warning", "CPF necessário", "O campo CPF é obrigatório no cadastro");
      return;
    }
    if (cpf.length !== 11) {
      showModal("error", "CPF inválido", "O CPF deve conter exatamente 11 dígitos");
      return;
    }
    if (!nascimento) {
      showModal("warning", "Data de nascimento", "Informe sua data de nascimento");
      return;
    }
  }

  // Monta o payload
  const payload = {
    email,
    senha,
    role: currentRole,
  };

  if (currentMode === "register") {
    payload.nome = nome;
    payload.cpf = cpf;
    payload.nascimento = nascimento;
    if (currentRole === "vet") payload.crmv = crmv;
  }

  const url = currentMode === "login" ? "/login/" : "/register/";

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")?.value || "",
      },
      body: JSON.stringify(payload),
    });

    const contentType = response.headers.get("content-type");

      if (!contentType || !contentType.includes("application/json")) {
        const text = await response.text();
        console.error("Resposta não é JSON:\n", text);

        showModal(
          "error",
          "Erro no servidor",
          "O servidor retornou uma resposta inválida (HTML). Verifique o backend."
        );
        return;
      }

    const result = await response.json();


    if (result.success) {
      showModal("success", "Tudo certo!", currentMode === "login" ? "Login realizado com sucesso!" : "Cadastro realizado com sucesso!");
      setTimeout(() => {
        window.location.href = result.redirect;
      }, 1800);
    } else {
      showModal("error", "Não foi possível continuar", result.error || "Verifique os dados e tente novamente");
    }
  } catch (err) {
    console.error(err);
    showModal("error", "Erro de conexão", "Não foi possível conectar ao servidor. Verifique sua internet e tente novamente.");
  }
}

// Só isso! O resto (trocar abas, modo login/cadastro) continua igual
document.getElementById("auth-form").onsubmit = handleSubmit;

function showModal(type = "info", title = "Atenção", message = "Algo aconteceu") {
  const modal = document.getElementById("custom-modal");
  const icon = document.getElementById("modal-icon");
  const modalTitle = document.getElementById("modal-title");
  const modalMessage = document.getElementById("modal-message");

  // Remove classes anteriores
  icon.className = "w-12 h-12 rounded-full flex items-center justify-center text-white text-2xl";

  // Define tipo
  if (type === "success") {
      icon.classList.add("bg-green-500");
      icon.innerHTML = "✓";
      modalTitle.textContent = title || "Sucesso!";
  } else if (type === "error") {
      icon.classList.add("bg-red-500");
      icon.innerHTML = "✕";
      modalTitle.textContent = title || "Erro";
  } else if (type === "warning") {
      icon.classList.add("bg-yellow-500");
      icon.innerHTML = "!";
      modalTitle.textContent = title || "Atenção";
  } else {
      icon.classList.add("bg-blue-500");
      icon.innerHTML = "i";
      modalTitle.textContent = title || "Informação";
  }

  modalMessage.textContent = message;
  modal.classList.remove("hidden");
  document.getElementById("modal-content").classList.replace("scale-95", "scale-100");
}

function closeModal() {
  const modal = document.getElementById("custom-modal");
  const content = document.getElementById("modal-content");
  content.classList.replace("scale-100", "scale-95");
  setTimeout(() => modal.classList.add("hidden"), 300);
}

// Fecha com ESC ou clique fora
document.getElementById("custom-modal").addEventListener("click", function(e) {
  if (e.target === this) closeModal();
});
document.addEventListener("keydown", function(e) {
  if (e.key === "Escape") closeModal();
});