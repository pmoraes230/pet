// static/js/script.js — 100% FUNCIONAL COM DJANGO

document.addEventListener('DOMContentLoaded', () => {
  const petsDataElement = document.getElementById('pets-data');
  
  // Se não tiver dados (outra página), sai
  if (!petsDataElement) return;

  // Pega os pets reais do Django
  const REAL_PETS = JSON.parse(petsDataElement.textContent);

  const container = document.getElementById('pets-container');
  if (!container) return;

  // Função que cria o card EXATAMENTE como você queria
  function createPetCard(pet) {
    return `
      <div class="bg-white rounded-[32px] p-2 shadow-[0_2px_15px_-3px_rgba(0,0,0,0.07),0_10px_20px_-2px_rgba(0,0,0,0.04)] hover:shadow-2xl transition-all duration-300 border border-gray-100 h-full flex flex-col cursor-pointer"
           onclick="window.location.href='/pet/${pet.id}/'">
        
        <div class="w-full aspect-[4/3] relative rounded-[28px] overflow-hidden">
          <img 
            src="${pet.imageUrl}" 
            alt="${pet.name}" 
            class="w-full h-full object-cover transform hover:scale-105 transition-transform duration-500"
          />
        </div>

        <div class="pt-4 pb-6 px-4 flex-1 flex flex-col">
          <div class="flex justify-between items-baseline mb-6">
            <h3 class="text-2xl font-bold text-gray-900">${pet.name}</h3>
            <span class="text-gray-400 text-xs font-medium">
              ${pet.breed} • ${pet.age}
            </span>
          </div>

          <div class="mt-auto">
            <button class="w-full py-2.5 px-4 bg-[#F8F8F8] hover:bg-white text-black text-sm font-bold rounded-full shadow-[0_2px_5px_rgba(0,0,0,0.05)] border border-gray-200 transition-all active:scale-[0.98] select-none">
              Ver detalhes
            </button>
          </div>
        </div>
      </div>
    `;
  }

  // Renderiza os pets
  if (REAL_PETS.length > 0) {
    container.innerHTML = REAL_PETS.map(createPetCard).join('');
  } else {
    container.innerHTML = `
      <div class="col-span-3 text-center py-20">
        <p class="text-gray-500 text-2xl font-bold mb-4">Nenhum pet cadastrado</p>
        <p class="text-gray-400">Clique em "Adicionar pet" para começar</p>
      </div>
    `;
  }

  // Sidebar ativa (seus itens têm classe .nav-item)
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
      document.querySelectorAll('.nav-item').forEach(nav => {
        nav.classList.remove('bg-[#E9D5FF]', 'text-[#6B21A8]');
        nav.classList.add('text-gray-900', 'hover:bg-gray-50');
      });
      item.classList.add('bg-[#E9D5FF]', 'text-[#6B21A8]');
      item.classList.remove('text-gray-900');
    });
  });

  // Tabs da página de detalhes (funciona em qualquer página que tiver)
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;

      document.querySelectorAll('.tab-btn').forEach(b => {
        if (b.dataset.tab === target) {
          b.classList.add('bg-[#9333EA]', 'text-white');
          b.classList.remove('text-gray-500');
        } else {
          b.classList.remove('bg-[#9333EA]', 'text-white');
          b.classList.add('text-gray-500');
        }
      });

      document.querySelectorAll('.tab-content').forEach(content => {
        content.id === `tab-${target}`
          ? content.classList.remove('hidden')
          : content.classList.add('hidden');
      });
    });
  });
});