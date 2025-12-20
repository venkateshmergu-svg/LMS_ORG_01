module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "primary": "rgb(var(--color-primary) / <alpha-value>)",
        "secondary": "rgb(var(--color-secondary) / <alpha-value>)",
        "success": "rgb(var(--color-success) / <alpha-value>)",
        "warning": "rgb(var(--color-warning) / <alpha-value>)",
        "error": "rgb(var(--color-error) / <alpha-value>)",
      },
      spacing: {
        "safe": "max(1rem, env(safe-area-inset-left))",
      },
    },
  },
  plugins: [],
}
