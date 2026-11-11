import { NavLink, Outlet } from 'react-router-dom'

export default function Layout({ pages }) {
  return (
    <div className="app">
      <aside className="menu">
        <div className="logo">RoboAgri-Kin</div>
        <nav>
          {pages.map((p) => (
            <NavLink key={p.path} to={p.path} end>
              {p.titre}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="contenu">
        <header className="topbar">
          <span>Ferme de Ndolo</span>
          <span>RB-01 connecté · 78 % · Alain Mbuyi</span>
        </header>
        <main className="page">
          <Outlet />
        </main>
      </div>
    </div>
  )
}