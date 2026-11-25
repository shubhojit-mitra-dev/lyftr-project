/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#000000',
        card: '#171717',
        border: '#262626',
        openai: {
          bg: '#000000',
          sidebar: '#0d0d0d',
          card: '#171717',
          surface: '#212121',
          border: '#262626',
          muted: '#a3a3a3',
          teal: '#10a37f',
          tealHover: '#0e8c6d',
        },
      },
      fontFamily: {
        sans: ['OpenAI Sans', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
