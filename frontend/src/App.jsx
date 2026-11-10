import '@fontsource/inter/400.css'
import '@fontsource/inter/600.css'
import '@fontsource/inter/700.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import TableauDeBord from './pages/TableauDeBord'
import Missions from './pages/Missions'
import Parcelles from './pages/Parcelles'
import PageVide from './pages/PageVide'
import Irrigation from './pages/Irrigation'
import Incidents from './pages/Incidents'
import Historique from './pages/Historique'
import Rapports from './pages/Rapports'
import Parametres from './pages/Parametres'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<TableauDeBord />} />
          <Route path="/missions" element={<Missions />} />
          <Route path="/parcelles" element={<Parcelles />} />
          <Route path="/carte" element={<PageVide titre="Carte des parcelles" />} />
          <Route path="/capteurs" element={<PageVide titre="Capteurs" />} />
           <Route path="/irrigation" element={<Irrigation titre="Irrigation" />} />
           <Route path="/incidents" element={<Incidents titre="Incidents" />} />
           <Route path="/historique" element={<Historique titre="Historique" />} />
           <Route path="/rapports" element={<Rapports titre="Rapports" />} />
           <Route path="/parametres" element={<Parametres />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App