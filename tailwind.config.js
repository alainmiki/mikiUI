/** @type {import('tailwindcss').Config} */
module.exports = {
  "content": [
    "mikiui/runtime/miki.css",
    "mikiui/runtime/themes/*.css",
    "mikiui/components/**/*.py",
    "mikiui/widgets/**/*.py",
    "mikiui/build/tailwind/*.py", "mikiui/build/tailwind/**/*.py"
  ],
  "theme": {
    "extend": {}
  },
  "plugins": []
};
