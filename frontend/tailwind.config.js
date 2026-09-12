/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      keyframes: {
        pulseHighlightAmber: {
          '0%, 100%': { backgroundColor: 'rgba(245, 158, 11, 0.06)', boxShadow: 'inset 0 0 0 1px rgba(245, 158, 11, 0.25)' },
          '50%': { backgroundColor: 'rgba(245, 158, 11, 0.18)', boxShadow: 'inset 0 0 0 1px rgba(245, 158, 11, 0.6), 0 0 20px rgba(245, 158, 11, 0.25)' },
        },
        pulseHighlightSky: {
          '0%, 100%': { backgroundColor: 'rgba(6, 182, 212, 0.06)', boxShadow: 'inset 0 0 0 1px rgba(6, 182, 212, 0.25)' },
          '50%': { backgroundColor: 'rgba(6, 182, 212, 0.18)', boxShadow: 'inset 0 0 0 1px rgba(6, 182, 212, 0.6), 0 0 20px rgba(6, 182, 212, 0.25)' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'pulse-ticket': 'pulseHighlightAmber 2s ease-in-out infinite',
        'pulse-asset': 'pulseHighlightSky 2s ease-in-out infinite',
        'fade-in': 'fadeIn 0.2s ease-out forwards',
      },
    },
  },
  plugins: [],
}
