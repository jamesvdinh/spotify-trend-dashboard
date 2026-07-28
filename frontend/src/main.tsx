import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import './index.css'
import App from './App.tsx'

// HashRouter (not BrowserRouter): GitHub Pages is pure static hosting with no
// server-side rewrites, so a direct request to a path like /dashboard (e.g.
// the backend's post-login redirect) would 404. Hash-based routes
// (/#/dashboard) never hit the server as a real path, so this works
// regardless of host.
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <HashRouter>
      <App />
    </HashRouter>
  </StrictMode>,
)
