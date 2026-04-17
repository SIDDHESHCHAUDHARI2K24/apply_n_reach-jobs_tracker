# Audit Log

| Date | Task ID | Risk area | Outcome | Remaining risk | Owner |
|------|---------|-----------|---------|----------------|-------|
| 2026-04-17 | P1 | Session cookie handling | Cookies are HttpOnly, set by backend. Frontend never touches tokens. | None — depends on backend CORS config. | Backend team |
| 2026-04-17 | P1 | Auth redirect | ProtectedRoute redirects to /auth/login, preserves returnTo state | Verify backend sends Set-Cookie on HTTPS | - |
| 2026-04-17 | P2.T1 | Form validation | Email regex tightened to /^[^\s@]+@[^\s@]+\.[^\s@]+$/ | Validation is client-side only; backend 422 is the real gate | - |
| 2026-04-17 | P3 | Render polling | Capped at 20 retries (~60s), unmount cleanup added | Long renders show timeout message | - |
| 2026-04-17 | P4 | Ingestion compliance | LinkedIn non-scraping notice displayed with background color | Policy enforcement relies on user compliance | - |
| 2026-04-17 | P5.T1 | Opening resume snapshot | Snapshot independence indicator shown in shell + each section | Users must understand snapshot independence | - |
