/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      /* ─── HDS 색상 토큰 ─── */
      fontFamily: {
        sans: [
          "Pretendard",
          '"Apple SD Gothic Neo"',
          '"Apple SD 산돌고딕 Neo"',
          "NanumGothic",
          "sans-serif",
        ],
      },
      colors: {
        border: "#e5e7eb",
        background: {
          DEFAULT: "#ffffff",
          second: "#f3f4f6",
        },
        foreground: {
          DEFAULT: "#111827",
          muted: "#9ca3af",
          second: "#4b5563",
        },
        primary: {
          DEFAULT: "#584de4",
          down: "#f7f6fe",
          foreground: "#ffffff",
          50: "#F7F6FE",
          100: "#EEEDFC",
          200: "#DEDBFA",
          300: "#C8C4F6",
          400: "#BCB8F4",
          500: "#ABA6F1",
          600: "#9B94EF",
          700: "#8A82EC",
          800: "#7971E9",
          900: "#695FE7",
          950: "#584de4",
        },
        destructive: {
          DEFAULT: "#dc2626",
          foreground: "#ffffff",
        },
        "semantic-red": "#EE3A3A",
        "semantic-blue": "#3E8CE8",
        "semantic-green": "#3DAB6A",
        /* ─── HomeForKid 전용 시맨틱 컬러 ─── */
        safety: {
          safe: "#3DAB6A",
          "safe-bg": "#ECFDF5",
          normal: "#F59E0B",
          "normal-bg": "#FFFBEB",
          caution: "#EE3A3A",
          "caution-bg": "#FEF2F2",
        },
      },
      borderRadius: {
        lg: "12px",
        md: "8px",
        sm: "4px",
      },
      boxShadow: {
        card: "0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06)",
        "card-hover":
          "0 4px 6px -1px rgb(0 0 0 / 0.07), 0 2px 4px -2px rgb(0 0 0 / 0.05)",
      },
    },
  },
  plugins: [],
};
