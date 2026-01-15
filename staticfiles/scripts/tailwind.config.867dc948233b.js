tailwind.config = {
    theme: {
      extend: {
        fontFamily: {
          sans: ['Inter', 'sans-serif'],
        },
        colors: {
          brand: {
            purple: '#6D28D9', // violet-700
            lightPurple: '#8B5CF6', // violet-500
            teal: '#14B8A6', // teal-500
            darkTeal: '#0F766E', // teal-700
          }
        },
        animation: {
            'slide-up': 'slideUp 0.4s ease-out forwards',
        },
        keyframes: {
            slideUp: {
                '0%': { opacity: '0', transform: 'translateY(20px)' },
                '100%': { opacity: '1', transform: 'translateY(0)' },
            }
        }
      }
    }
  }