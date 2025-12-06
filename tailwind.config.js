/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./templates/**/*.html", "./static/**/*.js"],
    theme: {
        extend: {
            colors: {
                dark: {
                    900: '#0f172a', // Slate 900
                    800: '#1e293b', // Slate 800
                    700: '#334155', // Slate 700
                    600: '#475569', // Slate 600
                },
                primary: {
                    500: '#0ea5e9', // Sky 500
                    600: '#0284c7', // Sky 600
                },
                accent: {
                    teal: '#14b8a6', // Teal 500
                    amber: '#f59e0b', // Amber 500
                    rose: '#f43f5e', // Rose 500
                }
            },
            fontFamily: {
                sans: ['Poppins', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
