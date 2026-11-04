import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import TableauDeBord from './pages/TableauDeBord'
import Missions from './pages/Missions'
import Parcelles from './pages/Parcelles'
import PageVide from './pages/PageVide'
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
           <Route path="/irrigation" element={<PageVide titre="Irrigation" />} />
           <Route path="/incidents" element={<PageVide titre="Incidents" />} />
           <Route path="/historique" element={<PageVide titre="Historique" />} />
           <Route path="/rapports" element={<PageVide titre="Rapports" />} />
           <Route path="/parametres" element={<PageVide titre="Paramètres" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App