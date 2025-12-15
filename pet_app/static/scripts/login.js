document.addEventListener("DOMContentLoaded", function () {
  
  // Ativa ícones Lucide
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }

  // ================= ESTADO =================
  let currentRole = "tutor"; // tutor | vet
  let currentMode = "login"; // login | register

  // ================= ELEMENTOS =================
  const authForm = document.getElementById("auth-form");
  const roleInput = document.getElementById("role-input");
  const sidePanel = document.getElementById("side-panel");
  const roleBadge = document.getElementById("role-badge");
  const heroTitle = document.getElementById("hero-title");
  const heroDesc = document.getElementById("hero-desc");
  
  // Abas
  const tabTutor = document.getElementById("tab-tutor");
  const tabVet = document.getElementById("tab-vet");

  // Campos Containers
  const registerNameField = document.getElementById("register-name-field");
  const dateField = document.getElementById("date-field");
  const cpfCnpjField = document.getElementById("cpf-cnpj-field");
  const crmField = document.getElementById("crmv-field");
  const enderecoField = document.getElementById("endereco-field"); // Adicionei caso tenha endereço

  // Inputs Reais (Para desabilitar quando oculto)
  // Certifique-se que seus inputs no HTML tenham esses IDs ou ajuste aqui
  const inputNome = document.querySelector('input[name="nome"]');
  const inputData = document.querySelector('input[name="data_nascimento"]');
  const inputCpf = document.querySelector('input[name="cpf"]');
  const inputCrmv = document.querySelector('input[name="crmv"]');
  const inputEndereco = document.querySelector('input[name="endereco"]');

  // Botões e Textos
  const submitBtn = document.getElementById("submit-btn");
  const formTitle = document.getElementById("form-title");
  const formSubtitle = document.getElementById("form-subtitle");
  const toggleText = document.getElementById("toggle-text");
  const toggleBtn = document.getElementById("toggle-btn");

  // ================= FUNÇÃO CENTRAL DE URL =================
  // Essa função garante que o formulário vá para a View correta do Django

// ================= FUNÇÃO CENTRAL DE URL (CORRIGIDA) =================
  function updateActionURL() {
    // ATENÇÃO: As URLs devem bater exatamente com o seu urls.py
    
    if (currentMode === "login") {
      // Tanto Tutor quanto Vet usam a mesma URL de login
      authForm.action = "/login/";      
    } else {
      // Tanto Tutor quanto Vet usam a mesma URL de registro
      authForm.action = "/register/";   
    }
    
    console.log("Form Action atualizado para:", authForm.action);
  }

  // ================= VISIBILIDADE E DISABLE =================
  function updateVisibility() {
    const isRegister = currentMode === "register";

    // Helper para mostrar/esconder e habilitar/desabilitar inputs
    const toggleField = (container, input, show) => {
      if (show) {
        container.classList.remove("hidden");
        if(input) input.disabled = false;
      } else {
        container.classList.add("hidden");
        if(input) input.disabled = true;
      }
    };

    // 1. Campos de Cadastro Geral (Nome, Data, Endereço)
    // Aparecem no registro para ambos
    toggleField(registerNameField, inputNome, isRegister);
    toggleField(dateField, inputData, isRegister);
    if(enderecoField) toggleField(enderecoField, inputEndereco, isRegister);

    // 2. CPF (Aparece no registro para Tutor. Se Vet usa CNPJ/CPF, ajuste a lógica)
    // Aqui assumindo que Veterinário e Tutor usam CPF/CNPJ no cadastro
    toggleField(cpfCnpjField, inputCpf, isRegister);

    // 3. CRMV (Apenas Veterinário no Registro)
    const showCrmv = isRegister && currentRole === "vet";
    toggleField(crmField, inputCrmv, showCrmv);
  }

  // ================= MUDANÇA DE ROLE (TUTOR / VET) =================
  window.switchRole = function (role) {
    currentRole = role;
    roleInput.value = role;

    if (role === "tutor") {
      // Estilos Tutor
      tabTutor.className = "flex-1 py-2 text-sm font-bold rounded-lg bg-white text-gray-800 shadow-sm transition-all";
      tabVet.className = "flex-1 py-2 text-sm font-bold rounded-lg text-gray-500 hover:bg-gray-50 transition-all";
      
      sidePanel.classList.remove("bg-brand-darkTeal");
      sidePanel.classList.add("bg-brand-purple"); // Roxo do Tutor

      roleBadge.textContent = "Área do Tutor";
      roleBadge.className = "bg-white/20 text-white px-3 py-1 rounded-full text-xs font-bold backdrop-blur-sm";
      
      heroTitle.textContent = currentMode === "register" ? "Junte-se a nós!" : "Bem-vindo de volta!";
      heroDesc.textContent = "Acompanhe a saúde emocional e física do seu pet em um só lugar.";

      submitBtn.className = "w-full py-3 rounded-xl font-bold text-white transition-all transform hover:-translate-y-0.5 bg-brand-purple hover:bg-purple-700 shadow-lg shadow-purple-200";
    
    } else {
      // Estilos Veterinário
      tabVet.className = "flex-1 py-2 text-sm font-bold rounded-lg bg-white text-gray-800 shadow-sm transition-all";
      tabTutor.className = "flex-1 py-2 text-sm font-bold rounded-lg text-gray-500 hover:bg-gray-50 transition-all";

      sidePanel.classList.remove("bg-brand-purple");
      sidePanel.classList.add("bg-brand-darkTeal"); // Verde do Vet

      roleBadge.textContent = "Área do Veterinário";
      
      heroTitle.textContent = currentMode === "register" ? "Expanda sua clínica" : "Olá, Doutor(a)";
      heroDesc.textContent = "Gerencie seus pacientes, prontuários e conecte-se com novos tutores.";

      submitBtn.className = "w-full py-3 rounded-xl font-bold text-white transition-all transform hover:-translate-y-0.5 bg-brand-darkTeal hover:bg-teal-800 shadow-lg shadow-teal-100";
    }

    updateVisibility();
    updateActionURL(); // Atualiza a URL do form
  };

  // ================= MUDANÇA DE MODO (LOGIN / CADASTRO) =================
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

    // Atualiza Role para atualizar os textos do Hero também
    switchRole(currentRole); 
  };

  // ================= MÁSCARA CPF/CNPJ =================
  const cpfCnpjInput = document.getElementById("cpf-cnpj-input");
  if (cpfCnpjInput) {
    cpfCnpjInput.addEventListener("input", e => {
      let v = e.target.value.replace(/\D/g, "");
      if (v.length <= 11) {
        // CPF
        v = v.replace(/(\d{3})(\d)/, "$1.$2")
             .replace(/(\d{3})(\d)/, "$1.$2")
             .replace(/(\d{3})(\d{1,2})$/, "$1-$2");
      } else {
        // CNPJ
        v = v.replace(/^(\d{2})(\d)/, "$1.$2")
             .replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3")
             .replace(/\.(\d{3})(\d)/, ".$1/$2")
             .replace(/(\d{4})(\d{1,2})$/, "$1-$2");
      }
      e.target.value = v;
    });
  }

  // ================= INICIALIZAÇÃO =================
  // Define estado inicial
  roleInput.value = "tutor";
  switchRole("tutor"); // Isso já chama updateVisibility e updateActionURL
});