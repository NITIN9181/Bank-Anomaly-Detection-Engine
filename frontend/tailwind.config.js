/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        anomaly: {
          volumetric: "#EF4444",
          deviant: "#F59E0B",
          duplicate: "#8B5CF6",
        },
        finance: {
          bg: "#0F172A",
          card: "#1E293B",
          text: "#F8FAFC",
          muted: "#94A3B8",
        },
      },
      fontFamily: {
        mono: ['"Fira Code"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
    },
  },
  plugins: [],
};
