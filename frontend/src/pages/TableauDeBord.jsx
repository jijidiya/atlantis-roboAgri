import StatCard from '../components/StatCard'

function TableauDeBord() {
  return (
    <div>
      <h1>Tableau de bord</h1>
      <div className="cartes">
        <StatCard titre="Batterie" valeur="78 %" details="Autonomie estimée : 4 h 20" />
        <StatCard titre="Missions du jour" valeur="05" details="1 en cours · 1 terminée" />
      </div>
    </div>
  )
}

export default TableauDeBord