/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pythonsd/templates/**/*.{html,js}"
  ],
  theme: {
    container: {
      center: true,
      padding: {
        DEFAULT: '1rem',
        sm: '2rem',
        lg: '4rem',
        xl: '6rem',
        '2xl': '12rem',
      },
    },
    extend: {},
  },
  plugins: [],
}
