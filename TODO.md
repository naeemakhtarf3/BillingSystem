# Fix SPA Routing on Render

## Current Status
- Backend serves API under `/api/v1/`
- Frontend is React SPA with client-side routing
- On Render, only backend runs, frontend static files aren't served
- Navigating to `/patient/payment/success?session_id=...` returns 404

## Tasks
- [x] Modify `backend/app/main.py` to serve static files from `frontend/dist` and add catch-all route for SPA
- [x] Update `render.yaml` build command to build frontend and copy dist files to backend
- [x] Build frontend and copy dist to backend directory
- [x] Test routing locally (server started, browser testing disabled)
- [ ] Deploy and verify on Render
