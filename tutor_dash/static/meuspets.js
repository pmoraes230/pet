// Dados Mockados dos Pets
const MOCK_PETS = [
    {
      id: '1',
      name: 'Paçoca',
      breed: 'Vira-lata',
      age: '4 Anos',
      imageUrl: 'https://images.unsplash.com/photo-1537151625747-768eb6cf92b2?auto=format&fit=crop&w=600&q=80' 
    },
    {
      id: '2',
      name: 'Luna',
      breed: 'Siamês',
      age: '2 Anos',
      imageUrl: 'https://images.unsplash.com/photo-1513245543132-31f507417b26?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: '3',
      name: 'Thor',
      breed: 'Bulldog frances',
      age: '4 Anos',
      imageUrl: 'https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&w=600&q=80'
    }
];
  
// Função para criar o HTML de um Card de Pet
function createPetCard(pet) {
return `
    <div class="bg-white rounded-[32px] p-2 shadow-[0_2px_15px_-3px_rgba(0,0,0,0.07),0_10px_20px_-2px_rgba(0,0,0,0.04)] hover:shadow-lg transition-shadow duration-300 border border-gray-100 h-full flex flex-col">
    <!-- Image Container -->
    <div class="w-full aspect-[4/3] relative rounded-[28px] overflow-hidden">
        <img 
        src="${pet.imageUrl}" 
        alt="${pet.name}" 
        class="w-full h-full object-cover transform hover:scale-105 transition-transform duration-500"
        />
    </div>

    <!-- Content -->
    <div class="pt-4 pb-6 px-4 flex-1 flex flex-col">
        <div class="flex justify-between items-baseline mb-6">
        <h3 class="text-2xl font-bold text-gray-900">${pet.name}</h3>
        <span class="text-gray-400 text-xs font-medium">
            ${pet.breed} • ${pet.age}
        </span>
        </div>

        <div class="mt-auto">
        <button class="w-full py-2.5 px-4 bg-[#F8F8F8] hover:bg-white text-black text-sm font-bold rounded-full shadow-[0_2px_5px_rgba(0,0,0,0.05)] border border-gray-200 transition-all active:scale-[0.98]">
            Ver detalhes
        </button>
        </div>
    </div>
    </div>
`;
}
  
// Função Principal de Renderização
function init() {
    const container = document.getElementById('pets-container');
    
    if (container) {
        // Gera o HTML de todos os pets e insere no container
        container.innerHTML = MOCK_PETS.map(pet => createPetCard(pet)).join('');
    }

    // Lógica da Sidebar (Simples toggle de classe para demonstrar estado ativo)
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
        // Remove estado ativo de todos
        navItems.forEach(nav => {
            nav.className = 'nav-item w-full text-left px-4 py-2.5 rounded-2xl text-sm font-semibold text-gray-900 hover:bg-gray-50 transition-colors';
        });

        // Adiciona estado ativo ao clicado
        item.className = 'nav-item w-full text-left px-4 py-2.5 rounded-2xl text-sm font-semibold bg-[#E9D5FF] text-[#6B21A8] transition-colors';
        });
    });
}
  
// Inicializa quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', init);
