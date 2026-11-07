import { useState } from 'react'
import StatCard from '../components/StatCard'
import StatusBadge from '../components/StatusBadge'
import { incidents as incidentsInitiaux } from '../data/incidents'

function Incidents() {
  const [incidents, setIncidents] = useState(incidentsInitiaux)
  const [selectionId, setSelectionId] = useState('INC-028')
  const [filtreGravite, setFiltreGravite] = useState('Toutes')

  const affiches = filtreGravite === 'Toutes'
    ? incidents
    : incidents.filter((i) => i.gravite === filtreGravite)

  const selection = incidents.find((i) => i.id === selectionId)
  const ouverts = incidents.filter((i) => i.statut !== 'Résolu').length

  function changerStatut(id, statut) {
    setIncidents(incidents.map((i) => (i.id === id ? { ...i, statut } : i)))
  }

  return (
    <div>
      <h1>Incidents et alertes</h1>
      <p className="sous-titre">Priorisez les interventions et gardez une trace de leur résolution.</p>

      <div className="cartes">
        <StatCard titre="Incidents ouverts" valeur={String(ouverts).padStart(2, '0')} details="Une intervention est nécessaire" />
        <StatCard titre="Critiques" valeur={String(incidents.filter((i) => i.gravite === 'Critique' && i.statut !== 'Résolu').length).padStart(2, '0')} details="À traiter en priorité" />
        <StatCard titre="Total" valeur={String(incidents.length).padStart(2, '0')} details="Sur 7 jours" />
      </div>

      <div className="onglets">
        {['Toutes', 'Critique', 'Avertissement', 'Information'].map((g) => (
          <button key={g} className={g === filtreGravite ? 'onglet actif' : 'onglet'} onClick={() => setFiltreGravite(g)}>
            {g}
          </button>
        ))}
      </div>

      <div className="incidents-mise-en-page">
        <table className="tableau">
          <thead>
            <tr><th>Incident</th><th>Gravité</th><th>Zone</th><th>Date</th><th>Statut</th></tr>
          </thead>
          <tbody>
            {affiches.map((i) => (
              <tr key={i.id} className={i.id === selectionId ? 'ligne-selection' : 'ligne-cliquable'} onClick={() => setSelectionId(i.id)}>
                <td><strong>{i.titre}</strong><small>{i.id} · {i.source}</small></td>
                <td><StatusBadge statut={i.gravite} /></td>
                <td>{i.zone}</td>
                <td>{i.date}</td>
                <td><StatusBadge statut={i.statut} /></td>
              </tr>
            ))}
          </tbody>
        </table>

        {selection && (
          <div className="carte-mission panneau-detail">
            <strong>{selection.titre}</strong>
            <small>{selection.id} · {selection.date}</small>
            <div className="badges-ligne">
              <StatusBadge statut={selection.gravite} />
              <StatusBadge statut={selection.statut} />
            </div>
            <p>{selection.detail}</p>
            <strong>Suivi de l’incident</strong>
            <ul>
              {selection.suivi.map((s) => <li key={s}>{s}</li>)}
            </ul>
            <div className="boutons-ligne">
              <button className="bouton-petit" onClick={() => changerStatut(selection.id, 'À traiter')}>Acquitter</button>
              <button className="bouton-principal" onClick={() => changerStatut(selection.id, 'Résolu')}>Résoudre</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Incidents