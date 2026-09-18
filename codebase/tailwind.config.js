/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1e1b4b",
        primary: "#4f46e5",
        canvas: "#f8fafc",
      },
      boxShadow: {
        panel: "0 16px 44px rgba(30, 27, 75, 0.10)",
      },
      keyframes: {
        "pdf-in": {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "typing-dot": {
          "0%, 60%, 100%": { opacity: "0.35", transform: "translateY(0)" },
          "30%": { opacity: "1", transform: "translateY(-3px)" },
        },
      },
      animation: {
        "pdf-in": "pdf-in 240ms ease-out",
        "typing-dot": "typing-dot 900ms ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
