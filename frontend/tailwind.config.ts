/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        earth: {
          50: '#f9f7f4',
          100: '#f0ebe2',
          200: '#e0d5c7',
          300: '#ccbaa4',
          400: '#b89b80',
          500: '#a98566',
          600: '#8c6a50',
          700: '#725543',
          800: '#5e4739',
          900: '#4e3c31',
        },
        terracotta: {
          400: '#d4836a',
          500: '#c46a4e',
        },
        sand: {
          100: '#faf7f2',
          200: '#f2ece0',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
