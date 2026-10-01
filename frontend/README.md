# Pharmacy POS Web/PWA (React + Tailwind)

This responsive app works in desktop and mobile browsers. On Android/iOS, use the browser's **Add to Home Screen** command for an app-like launcher.

## WebStorm development setup

1. Open this folder in WebStorm.
2. Copy `.env.example` to `.env`; set `VITE_API_URL` to the backend URL.
3. In the terminal run `npm install`, then `npm run dev`.
4. Open `http://localhost:5173` and sign in with the initial administrator credentials configured in the backend `.env`.

## Production build

Run `npm run build`; deploy the generated `dist/` folder to Nginx, Netlify, Cloudflare Pages, or another static host. Set `VITE_API_URL=https://api.yourdomain.com/api` **before** building. HTTPS is required for secure remote/mobile use.

For Docker: `docker build --build-arg VITE_API_URL=https://api.yourdomain.com/api -t pharmacy-web .` and run the image on port 80.

## Go-live checklist

- Put PostgreSQL and the API on a private server/network; expose only HTTPS ports.
- Use a strong JWT secret and database password; change the starter admin password.
- Set backend CORS to the exact frontend origin.
- Schedule encrypted `pg_dump` backups and test restoration.
- Use a UPS for the pharmacy router/server and test receipt-print layout before launch.
- Import medicines/opening stock, create staff accounts/roles, then perform a purchase and a sale as acceptance tests.

