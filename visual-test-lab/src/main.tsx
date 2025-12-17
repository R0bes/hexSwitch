import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ConfigurationProvider } from './contexts/ConfigurationContext.tsx'
import { ElementSelectionProvider } from './contexts/ElementSelectionContext.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ConfigurationProvider>
      <ElementSelectionProvider>
        <App />
      </ElementSelectionProvider>
    </ConfigurationProvider>
  </StrictMode>,
)
