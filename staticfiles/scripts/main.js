// 1. Initialize Icons
lucide.createIcons();
document.getElementById('year').textContent = new Date().getFullYear();

// 2. Navbar Scroll Logic
const navbar = document.getElementById('navbar');
const logoText = document.getElementById('logo-text');
const navLinks = document.querySelectorAll('.nav-link');
const mobileToggleBtn = document.getElementById('mobile-toggle-btn');
const mobileIcon = document.getElementById('menu-icon');
const closeIcon = document.getElementById('close-icon');

window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        // Scrolled State
        navbar.classList.remove('bg-transparent', 'py-5');
        navbar.classList.add('bg-white/90', 'backdrop-blur-md', 'shadow-md', 'py-3');
        
        logoText.classList.remove('text-white');
        logoText.classList.add('text-brand-purple');

        navLinks.forEach(link => {
            link.classList.remove('text-gray-100');
            link.classList.add('text-gray-700');
        });
        
        // Mobile toggle color adjustment
        mobileToggleBtn.classList.remove('text-white');
        mobileToggleBtn.classList.add('text-brand-purple');

    } else {
        // Top State
        navbar.classList.add('bg-transparent', 'py-5');
        navbar.classList.remove('bg-white/90', 'backdrop-blur-md', 'shadow-md', 'py-3');
        
        logoText.classList.add('text-white');
        logoText.classList.remove('text-brand-purple');

        navLinks.forEach(link => {
            link.classList.add('text-gray-100');
            link.classList.remove('text-gray-700');
        });

        mobileToggleBtn.classList.add('text-white');
        mobileToggleBtn.classList.remove('text-brand-purple');
    }
});

// 3. Mobile Menu Logic
const mobileMenu = document.getElementById('mobile-menu');
const mobileLinks = document.querySelectorAll('.mobile-link');
let isMobileMenuOpen = false;

function toggleMenu() {
    isMobileMenuOpen = !isMobileMenuOpen;
    if (isMobileMenuOpen) {
        mobileMenu.classList.remove('hidden');
        mobileIcon.classList.add('hidden');
        closeIcon.classList.remove('hidden');
    } else {
        mobileMenu.classList.add('hidden');
        mobileIcon.classList.remove('hidden');
        closeIcon.classList.add('hidden');
    }
}

mobileToggleBtn.addEventListener('click', toggleMenu);

// Close menu when clicking a link
mobileLinks.forEach(link => {
    link.addEventListener('click', () => {
        if (isMobileMenuOpen) toggleMenu();
    });
});
