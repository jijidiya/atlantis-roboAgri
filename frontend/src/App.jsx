import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import TableauDeBord from './pages/TableauDeBord'
import Missions from './pages/Missions'
import Parcelles from './pages/Parcelles'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<TableauDeBord />} />
          <Route path="/missions" element={<Missions />} />
          <Route path="/parcelles" element={<Parcelles />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App