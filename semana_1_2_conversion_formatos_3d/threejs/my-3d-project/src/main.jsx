import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './model-viewer.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
)
