import { Routes, Route } from 'react-router-dom'
import Layout from './Layout.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Connexion from './pages/Connexion.jsx'
import Carte from './pages/Carte.jsx'
import Parcelles from './pages/Parcelles.jsx'
import Capteurs from './pages/Capteurs.jsx'

const pages = [
  { path: '/', titre: 'Tableau de bord', element: <Dashboard /> },
  { path: '/carte', titre: 'Carte des parcelles', element: <Carte /> },
  { path: '/parcelles', titre: 'Gestion des parcelles', element: <Parcelles /> },
  { path: '/missions', titre: 'Missions', element: <h1>Missions</h1> },
  { path: '/capteurs', titre: 'Capteurs et mesures', element: <Capteurs /> },
]

function App() {
  return (
    <Routes>
      <Route path="/connexion" element={<Connexion />} />
      <Route element={<Layout pages={pages} />}>
        {pages.map((p) => (
          <Route key={p.path} path={p.path} element={p.element} />
        ))}
      </Route>
    </Routes>
  )
}

export default App
