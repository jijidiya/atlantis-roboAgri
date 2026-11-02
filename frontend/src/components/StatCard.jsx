function StatCard({ titre, valeur, details }) {
  return (
    <div className="stat-card">
      <p className="stat-titre">{titre}</p>
      <p className="stat-valeur">{valeur}</p>
      <p className="stat-details">{details}</p>
    </div>
  )
}

export default StatCard