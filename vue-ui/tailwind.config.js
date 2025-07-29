/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      backgroundColor: {
        'dark': {
          900: '#111827', // Main background
          800: '#1F2937', // Modal/card backgrounds
          700: '#374151', // Secondary elements
        }
      }
    },
  },
  plugins: [],
}

