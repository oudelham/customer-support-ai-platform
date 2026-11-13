# Customer Support Frontend — Vite

Vite + React + TypeScript frontend compatible with the Java backend.

## Development

```bash
npm install
cp .env.example .env
npm run dev
```

Vite: http://localhost:5173
Java API: http://localhost:8080/api/v1

## Production

```bash
npm run build
npm run preview
```

The Docker image serves Vite's `dist/` output with nginx.

## CRA removed

- `react-scripts`
- `public/index.html`
- `REACT_APP_*`
- CRA scripts

Vite uses:

- root `index.html`
- `src/main.tsx`
- `VITE_*` environment variables
- `import.meta.env.VITE_*`
- `npm run dev`
- `npm run build`
- `npm run preview`
