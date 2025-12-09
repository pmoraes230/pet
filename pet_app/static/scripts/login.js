// Ativa ícones Lucide
lucide.createIcons();

// Estado
let currentRole = window.currentRole || "tutor"; // 'tutor' ou 'vet'
let currentMode = "login"; // 'login' ou 'register'

// Elementos
const sidePanel = document.getElementById("side-panel");
const roleBadge = document.getElementById("role-badge");
const heroTitle = document.getElementById("hero-title");
const heroDesc = document.getElementById("hero-desc");
const tabTutor = document.getElementById("tab-tutor");
const tabVet = document.getElementById("tab-vet");
const crmField = document.getElementById("crmv-field");
const dateField = document.getElementById("date-field");
const cpfCnpjField = document.getElementById("cpf-cnpj-field");
const registerNameField = document.getElementById("register-name-field");
const submitBtn = document.getElementById("submit-btn");
const formTitle = document.getElementById("form-title");
const formSubtitle = document.getElementById("form-subtitle");
const toggleText = document.getElementById("toggle-text");
const toggleBtn = document.getElementById("toggle-btn");
const authForm = document.getElementById("auth-form");

// Checa params da URL
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get("type") === "vet") {
  switchRole("vet");
}

// Função para trocar de papel
function switchRole(role) {
  currentRole = role;

  if (role === "tutor") {
    tabTutor.className = "flex-1 py-2 text-sm font-bold rounded-lg transition-all shadow-sm bg-white text-gray-800";
    tabVet.className = "flex-1 py-2 text-sm font-bold rounded-lg transition-all text-gray-500 hover:text-gray-700";

    sidePanel.classList.remove("bg-brand-darkTeal");
    sidePanel.classList.add("bg-brand-purple");

    roleBadge.textContent = "Área do Tutor";
    heroTitle.textContent = currentMode === "login" ? "Bem-vindo de volta!" : "Junte-se a nós!";
    heroDesc.textContent = "Acompanhe a saúde emocional e física do seu pet em um só lugar.";

    crmField.classList.add("hidden");
    cpfCnpjField?.classList.add("hidden");
    registerNameField.classList.toggle("hidden", currentMode !== "register");

    updateButtonColor("purple");
  } else {
    tabVet.className = "flex-1 py-2 text-sm font-bold rounded-lg transition-all shadow-sm bg-white text-gray-800";
    tabTutor.className = "flex-1 py-2 text-sm font-bold rounded-lg transition-all text-gray-500 hover:text-gray-700";

    sidePanel.classList.remove("bg-brand-purple");
    sidePanel.classList.add("bg-brand-darkTeal");

    roleBadge.textContent = "Área do Veterinário";
    heroTitle.textContent = currentMode === "login" ? "Olá, Doutor(a)" : "Expanda sua clínica";
    heroDesc.textContent = "Gerencie seus pacientes, prontuários e conecte-se com novos tutores.";

    if (currentMode === "register") {
      crmField.classList.remove("hidden");
      cpfCnpjField.classList.remove("hidden");
      registerNameField.classList.remove("hidden");
    } else {
      crmField.classList.add("hidden");
      cpfCnpjField.classList.add("hidden");
      registerNameField.classList.add("hidden");
    }

    updateButtonColor("teal");
  }
}

// Toggle login/register
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

    if (currentRole === "vet") {
      crmField.classList.remove("hidden");
      cpfCnpjField.classList.remove("hidden");
    } else {
      cpfCnpjField?.classList.add("hidden");
    }

    heroTitle.textContent = currentRole === "tutor" ? "Comece agora!" : "Parceria de sucesso";
  } else {
    formTitle.textContent = "Acesse sua conta";
    formSubtitle.textContent = "Preencha seus dados para continuar.";
    submitBtn.textContent = "Entrar";
    toggleText.textContent = "Não tem conta?";
    toggleBtn.textContent = "Criar cadastro";

    registerNameField.classList.add("hidden");
    dateField.classList.add("hidden");
    crmField.classList.add("hidden");
    cpfCnpjField?.classList.add("hidden");

    heroTitle.textContent = currentRole === "tutor" ? "Bem-vindo de volta!" : "Olá, Doutor(a)";
  }
}

// Atualiza cor do botão
function updateButtonColor(color) {
  if (color === "purple") {
    submitBtn.classList.remove("bg-brand-darkTeal");
    submitBtn.classList.add("bg-brand-purple");
  } else {
    submitBtn.classList.remove("bg-brand-purple");
    submitBtn.classList.add("bg-brand-darkTeal");
  }
}

// Máscara CPF / CNPJ
const cpfCnpjInput = document.getElementById("cpf-cnpj-input");
if (cpfCnpjInput) {
  cpfCnpjInput.addEventListener("input", e => {
    let value = e.target.value.replace(/\D/g, "");
    if (value.length <= 11) {
      value = value.replace(/(\d{3})(\d)/, "$1.$2");
      value = value.replace(/(\d{3})(\d)/, "$1.$2");
      value = value.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
    } else {
      value = value.replace(/^(\d{2})(\d)/, "$1.$2");
      value = value.replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3");
      value = value.replace(/\.(\d{3})(\d)/, ".$1/$2");
      value = value.replace(/(\d{4})(\d{1,2})$/, "$1-$2");
    }
    e.target.value = value;
  });
}

// Submit
authForm.onsubmit = handleSubmit;

async function handleSubmit(e) {
  e.preventDefault();

  const email = document.querySelector('input[type="email"]').value.trim();
  const senha = document.querySelector('input[type="password"]').value;
  const nome = document.querySelector("#register-name-field input")?.value.trim() || "";
  const crmv = document.querySelector("#crmv-field input")?.value.trim() || "";
  const nascimento = document.querySelector('#date-field input')?.value.trim() || "";

  if (!email || !senha) {
    showModal("error", "Campos obrigatórios", "Preencha email e senha");
    return;
  }

  const payload = { email, senha, role: currentRole };

  if (currentMode === "register") {
    payload.nome = nome;
    payload.nascimento = nascimento;

    if (currentRole === "vet") {
      const cpfCnpj = cpfCnpjInput.value.replace(/\D/g, "");
      if (!cpfCnpj || !(cpfCnpj.length === 11 || cpfCnpj.length === 14)) {
        showModal("error", "CPF/CNPJ inválido", "Informe um CPF com 11 ou CNPJ com 14 dígitos");
        return;
      }
      payload.cpf_cnpj = cpfCnpj;
      if (crmv) payload.crmv = crmv;
    } else {
      const cpf = cpfCnpjInput.value.replace(/\D/g, "");
      if (!cpf || cpf.length !== 11) {
        showModal("error", "CPF inválido", "O CPF deve conter exatamente 11 dígitos");
        return;
      }
      payload.cpf = cpf;
    }
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

    const result = await response.json();

    if (result.success) {
      showModal("success", "Tudo certo!", currentMode === "login" ? "Login realizado com sucesso!" : "Cadastro realizado com sucesso!");
      setTimeout(() => window.location.href = result.redirect, 1800);
    } else {
      showModal("error", "Erro", result.error || "Verifique os dados e tente novamente");
    }
  } catch (err) {
    showModal("error", "Erro de conexão", "Não foi possível conectar ao servidor.");
  }
}

// Modal
function showModal(type = "info", title = "Atenção", message = "Algo aconteceu") {
  const modal = document.getElementById("custom-modal");
  const icon = document.getElementById("modal-icon");
  const modalTitle = document.getElementById("modal-title");
  const modalMessage = document.getElementById("modal-message");

  icon.className = "w-12 h-12 rounded-full flex items-center justify-center text-white text-2xl";

  if (type === "success") {
    icon.classList.add("bg-green-500");
    icon.innerHTML = "✓";
    modalTitle.textContent = title;
  } else if (type === "error") {
    icon.classList.add("bg-red-500");
    icon.innerHTML = "✕";
    modalTitle.textContent = title;
  } else if (type === "warning") {
    icon.classList.add("bg-yellow-500");
    icon.innerHTML = "!";
    modalTitle.textContent = title;
  } else {
    icon.classList.add("bg-blue-500");
    icon.innerHTML = "i";
    modalTitle.textContent = title;
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

document.getElementById("custom-modal").addEventListener("click", e => {
  if (e.target === e.currentTarget) closeModal();
});
document.addEventListener("keydown", e => {
  if (e.key === "Escape") closeModal();
});
