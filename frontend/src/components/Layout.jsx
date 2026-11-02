import { NavLink, Outlet } from 'react-router-dom'

function Layout() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <h2>RoboAgri-Kin</h2>
        <nav>
          <NavLink to="/">Tableau de bord</NavLink>
          <NavLink to="/missions">Missions</NavLink>
          <NavLink to="/parcelles">Parcelles</NavLink>
        </nav>
      </aside>
      <main className="contenu">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout