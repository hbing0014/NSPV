import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#18221f",
        field: "#f4f7f2",
        line: "#d8e0d7",
        accent: "#1f7a5a",
        amber: "#b66a12"
      }
    }
  },
  plugins: []
};

export default config;

