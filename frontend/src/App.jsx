import { Routes, Route } from 'react-router-dom'
import RouteProtegee from './components/RouteProtegee'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Connexion from './pages/Connexion'
import Carte from './pages/Carte'
import Parcelles from './pages/Parcelles'
import Capteurs from './pages/Capteurs'
import Missions from './pages/Missions'
import Irrigation from './pages/Irrigation'
import Incidents from './pages/Incidents'
import Historique from './pages/Historique'
import Rapports from './pages/Rapports'
import Parametres from './pages/Parametres'
import './App.css'

function App() {
  return (
    <Routes>
      <Route path="/connexion" element={<Connexion />} />

      <Route element={<RouteProtegee />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/carte" element={<Carte />} />
          <Route path="/parcelles" element={<Parcelles />} />
          <Route path="/missions" element={<Missions />} />
          <Route path="/capteurs" element={<Capteurs />} />
          <Route path="/irrigation" element={<Irrigation />} />
          <Route path="/incidents" element={<Incidents />} />
          <Route path="/historique" element={<Historique />} />
          <Route path="/rapports" element={<Rapports />} />
          <Route path="/parametres" element={<Parametres />} />
        </Route>
      </Route>
    </Routes>
  )
}

export default App