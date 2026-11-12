function StatCard({ titre, valeur, details, icone: Icone }) {
  return (
    <div className="stat-card">
      <div className="stat-haut">
        <p className="stat-titre">{titre}</p>
        {/* L'icône n'apparaît que si on en passe une : les anciennes pages marchent toujours */}
        {Icone && (
          <span className="stat-icone">
            <Icone size={18} />
          </span>
        )}
      </div>
      <p className="stat-valeur">{valeur}</p>
      <p className="stat-details">{details}</p>
    </div>
  )
}

export default StatCard