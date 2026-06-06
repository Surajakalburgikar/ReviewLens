# ReviewLens — Frontend Client

React 19 + Vite frontend for the ReviewLens sentiment analysis platform.

*   **Live App:** [https://review-lens-mocha.vercel.app/](https://review-lens-mocha.vercel.app/)
*   **Production API:** [https://reviewlens-n7nt.onrender.com](https://reviewlens-n7nt.onrender.com)

## Setup

```bash
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
npm run dev
```

Open `http://localhost:5173`

## Build for Production

```bash
npm run build
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Backend API URL (no trailing slash) |

## Deployment

Deploy on Vercel. Set `VITE_API_BASE_URL` to your Render backend URL.
`vercel.json` handles SPA routing automatically.
