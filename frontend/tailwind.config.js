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
        explainability: {
          confidenceLow: "#10B981",      // emerald-500 (0-50%)
          confidenceMedium: "#F59E0B",   // amber-500 (50-70%)
          confidenceHigh: "#F97316",    // orange-500 (70-85%)
          confidenceCritical: "#EF4444", // red-500 (85-100%)
          featureVolumetric: "#EF4444",  // red
          featureBehavioral: "#F59E0B",  // amber
          featureStructural: "#8B5CF6",  // violet
          featureTemporal: "#3B82F6",    // blue
        }
      },
      fontFamily: {
        mono: ['"Fira Code"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
    },
  },
  plugins: [],
};
