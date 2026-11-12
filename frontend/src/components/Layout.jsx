import { NavLink, Outlet } from 'react-router-dom'
import {
  LayoutDashboard, Map as MapIcon, Layers, Route as RouteIcon, Radio,
  Droplets, TriangleAlert, History, ChartColumn, Settings,
  Bell, BatteryMedium, Sprout,
} from 'lucide-react'

const liens = [
  { chemin: '/', nom: 'Tableau de bord', icone: LayoutDashboard },
  { chemin: '/carte', nom: 'Carte des parcelles', icone: MapIcon },
  { chemin: '/parcelles', nom: 'Gestion des parcelles', icone: Layers },
  { chemin: '/missions', nom: 'Missions', icone: RouteIcon },
  { chemin: '/capteurs', nom: 'Capteurs', icone: Radio },
  { chemin: '/irrigation', nom: 'Irrigation', icone: Droplets },
  { chemin: '/incidents', nom: 'Incidents', icone: TriangleAlert },
  { chemin: '/historique', nom: 'Historique', icone: History },
  { chemin: '/rapports', nom: 'Rapports', icone: ChartColumn },
  { chemin: '/parametres', nom: 'Paramètres', icone: Settings },
]

function Layout() {
  return (
    <div className="layout">
      <div className="sidebar-place">
        <aside className="sidebar">
          <div className="logo">
            <Sprout size={24} />
            <div className="texte-menu">
              <strong>RoboAgri-Kin</strong>
              <small>CULTIVER AVEC PRÉCISION</small>
            </div>
          </div>

          <nav>
            {liens.map(({ chemin, nom, icone: Icone }) => (
              <NavLink key={chemin} to={chemin} end={chemin === '/'}>
                <Icone size={18} />
                <span className="texte-menu">{nom}</span>
              </NavLink>
            ))}
          </nav>
        </aside>
      </div>

      <div className="principal">
        <header className="entete">
          <span className="fil">Ferme de Nsele</span>
          <div className="entete-droite">
            <span className="badge-robot">RB-01 connecté</span>
            <span className="batterie"><BatteryMedium size={18} /> 78 %</span>
            <Bell size={18} />
            <div className="profil">
              <span className="avatar">MK</span>
              <div>
                <strong>Magnificat Kakanda</strong>
                <small>Responsable</small>
              </div>
            </div>
          </div>
        </header>
        <main className="contenu">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout