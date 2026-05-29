/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans:    ['Roboto', 'system-ui', 'sans-serif'],
        display: ['Montserrat', 'system-ui', 'sans-serif'],
        mono:    ['"PT Mono"', 'monospace'],
      },
      colors: {
        // Brand
        'green-dark':   '#1F3A2E',
        'green-accent': '#22c55e',
        // Paper Design tokens
        paper:   '#F7F6F2',
        'paper-border': '#E5E3DC',
      },
    },
  },
  plugins: [],
}
