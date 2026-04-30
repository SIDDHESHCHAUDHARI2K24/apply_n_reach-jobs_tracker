# Frontend (Next.js + TypeScript)

This frontend now runs on Next.js App Router with Tailwind CSS v4 and Vitest.

## Scripts

- `npm run dev` - start local development server
- `npm run build` - build production bundle
- `npm run start` - run production server
- `npm run lint` - run ESLint
- `npm run test` - run Vitest test suite

## Structure Notes

- Next.js entrypoint is `app/layout.tsx` and `app/[[...slug]]/page.tsx`.
- Legacy route rendering is mounted through `src/next/LegacyApp.tsx`.
- Shared frontend modules remain under `src/app`, `src/features`, and `src/core`.
- Global design tokens and utilities are defined in `src/index.css`.

## Environment

Set `NEXT_PUBLIC_API_BASE_URL` to point to the backend API.
If missing, the frontend defaults to `http://localhost:8000`.
