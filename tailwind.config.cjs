module.exports = {
  darkMode: "class",
  content: ["./frontend/index.html", "./frontend/src/**/*.{ts,tsx}"] ,
  theme: {
    extend: {
      fontFamily: {
        inter: ["'Inter Tight'", "sans-serif"],
      },
      colors: {
        neon: {
          green: "#39ff14",
          blue: "#00ffff",
          pink: "#ff00ff",
        },
      },
    },
  },
    plugins: [require("tailwindcss-animate")],
  };
