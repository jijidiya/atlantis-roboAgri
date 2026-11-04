import { useState } from 'react'
import StatusBadge from '../components/StatusBadge'
import { missions as missionsInitiales } from '../data/missions'
import { transitions } from '../data/transitions'

function pourcentage(m) {
  return Math.round((m.faits / m.total) * 100)
}

function Missions() {
  const [missions, setMissions] = useState(missionsInitiales)

  function changerStatut(id, nouveauStatut) {
    setMissions(
      missions.map((m) => (m.id === id ? { ...m, statut: nouveauStatut } : m))
    )
  }

  const enCours = missions.find((m) => m.statut === 'En cours')

  return (
    <div>
      <h1>Missions</h1>
      <p className="sous-titre">Planifiez les interventions du robot et suivez leur avancement.</p>

      <div className="carte-mission">
        {enCours ? (
          <>
            <div className="carte-mission-haut">
              <div>
                <strong>{enCours.nom} · {enCours.parcelle}</strong>
                <small>{enCours.id} · Robot {enCours.robot} · {enCours.faits} / {enCours.total} points</small>
              </div>
              <span className="gros-pourcentage">{pourcentage(enCours)} %</span>
            </div>
            <div className="barre">
              <div className="barre-remplie" style={{ width: `${pourcentage(enCours)}%` }} />
            </div>
          </>
        ) : (
          <p>Aucune mission en cours.</p>
        )}
      </div>

      <table className="tableau">
        <thead>
          <tr>
            <th>Mission</th>
            <th>Parcelle</th>
            <th>Départ prévu</th>
            <th>Progression</th>
            <th>Statut</th>
            <th>Actions (test)</th>
          </tr>
        </thead>
        <tbody>
          {missions.map((m) => (
            <tr key={m.id}>
              <td>
                <strong>{m.nom}</strong>
                <small>{m.id} · Robot {m.robot}</small>
              </td>
              <td>{m.parcelle}</td>
              <td>{m.depart}</td>
              <td>{pourcentage(m)} % · {m.faits} / {m.total} points</td>
              <td><StatusBadge statut={m.statut} /></td>
              <td>
                {transitions[m.statut].map((s) => (
                  <button key={s} className="bouton-petit" onClick={() => changerStatut(m.id, s)}>
                    → {s}
                  </button>
                ))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default Missions