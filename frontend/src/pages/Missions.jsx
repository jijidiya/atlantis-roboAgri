import { useState } from 'react'
import StatusBadge from '../components/StatusBadge'
import { missions as missionsInitiales } from '../data/missions'
import { transitions } from '../data/transitions'

function pourcentage(m) {
  return Math.round((m.faits / m.total) * 100)
}

const onglets = [
  { nom: 'Toutes', statuts: null },
  { nom: 'En cours', statuts: ['En cours'] },
  { nom: 'Planifiées', statuts: ['Planifiée'] },
  { nom: 'Terminées', statuts: ['Terminée'] },
  { nom: 'À vérifier', statuts: ['Interrompue', 'Non confirmée'] },
]

function Missions() {
  const [missions, setMissions] = useState(missionsInitiales)
  const [ongletActif, setOngletActif] = useState('Toutes')

  // États du formulaire « Planification rapide »
  const [nom, setNom] = useState('Relevé d’humidité')
  const [parcelle, setParcelle] = useState('Zone A · Maïs')

  const onglet = onglets.find((o) => o.nom === ongletActif)
  const missionsAffichees = onglet.statuts
    ? missions.filter((m) => onglet.statuts.includes(m.statut))
    : missions

  function compter(o) {
    return o.statuts
      ? missions.filter((m) => o.statuts.includes(m.statut)).length
      : missions.length
  }

  function changerStatut(id, nouveauStatut) {
    setMissions(
      missions.map((m) => (m.id === id ? { ...m, statut: nouveauStatut } : m))
    )
  }

  function planifier() {
    const numero = 100 + missions.length + 1
    const nouvelle = {
      id: `MIS-${numero}`,
      nom,
      robot: 'RB-01',
      parcelle,
      depart: 'Aujourd’hui',
      faits: 0,
      total: 8,
      statut: 'Planifiée',
    }
    setMissions([...missions, nouvelle])
  }

  const enCours = missions.find((m) => m.statut === 'En cours')

  return (
    <div>
      <h1>Missions</h1>
      <p className="sous-titre">Planifiez les interventions du robot et suivez leur avancement.</p>

      {/* Carte de la mission en cours */}
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

      {/* Formulaire de planification rapide */}
      <div className="carte-mission">
        <strong>Planification rapide</strong>
        <div className="formulaire-ligne">
          <select value={nom} onChange={(e) => setNom(e.target.value)}>
            <option>Relevé d’humidité</option>
            <option>Contrôle du sol sec</option>
            <option>Inspection des cultures</option>
          </select>
          <select value={parcelle} onChange={(e) => setParcelle(e.target.value)}>
            <option>Zone A · Maïs</option>
            <option>Zone B · Tomates</option>
            <option>Zone C · Manioc</option>
          </select>
          <button className="bouton-principal" onClick={planifier}>Planifier</button>
        </div>
      </div>

      {/* Onglets */}
      <div className="onglets">
        {onglets.map((o) => (
          <button
            key={o.nom}
            className={o.nom === ongletActif ? 'onglet actif' : 'onglet'}
            onClick={() => setOngletActif(o.nom)}
          >
            {o.nom} ({compter(o)})
          </button>
        ))}
      </div>

      {/* Tableau */}
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
          {missionsAffichees.map((m) => (
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