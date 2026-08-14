// Tailwind CSS configuration for MikiUI.
// Generate this file with:  npm run tailwind:config '{"theme":"dark","daisyui":true}'
// Or edit directly — MikiUI's build system will merge these settings.
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "mikiui/runtime/miki.css",
    "mikiui/runtime/themes/*.css",
    "mikiui/components/**/*.py",
    "mikiui/widgets/**/*.py",
    "mikiui/**/*.html",
    "./components/**/*.{html,js,jsx,ts,tsx}",
    "./widgets/**/*.{html,js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "var(--miki-accent)",
        bg: "var(--miki-bg)",
        fg: "var(--miki-fg)",
      },
    },
  },
  plugins: [
    // DaisyUI is optional — uncomment if installed:
    // require("daisyui"),
  ],
  // DaisyUI theme (bridges to MikiUI theme variables):
  daisyui: {
    themes: ["mikiui-light", "mikiui-dark", "mikiui-solarized-dark", "mikiui-dracula"],
    base: true,
    styled: true,
    prefix: "miki-",
  },
};
