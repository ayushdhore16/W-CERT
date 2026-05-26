/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cyber-black': '#0a0b10',
        'cyber-gray': '#1a1d2d',
        'cyber-blue': '#00f0ff',
        'cyber-silver': '#e0e0e0',
        'alert-red': '#ff003c',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Orbitron', 'monospace'], // For headers to look techy
      },
      boxShadow: {
        'neon': '0 0 5px #00f0ff, 0 0 10px #00f0ff',
        'neon-red': '0 0 5px #ff003c, 0 0 10px #ff003c',
      }
    },
  },
  plugins: [],
}
