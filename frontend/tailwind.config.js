/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'vrhost': {
          'primary': '#10b981',
          'secondary': '#059669',
          'dark': '#1f2937',
          'darker': '#111827',
        }
      }
    },
  },
  plugins: [],
}
