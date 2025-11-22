/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Dark theme palette
                background: '#1e1f29',
                surface: '#282a36',
                primary: '#bd93f9',
                secondary: '#6272a4',
                accent: '#50fa7b',
                danger: '#ff5555',
                warning: '#ffb86c',
                text: '#f8f8f2',
            },
        },
    },
    plugins: [],
}
