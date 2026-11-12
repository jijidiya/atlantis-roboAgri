import { useState } from 'react'
import StatCard from '../components/StatCard'
import StatusBadge from '../components/StatusBadge'
import EtatVide from '../components/EtatVide'
import { useIncidents } from '../hooks/useIncidents'

const libelles = {
  obstacle: 'Obstacle',
  capteur_defaillant: 'Capteur défaillant',
  perte_communication: 'Perte de communication',
  mesure_invalide: 'Mesure invalide',
}

const formatDate = (d) =>
  new Date(d).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' })

const deux = (n) => String(n).padStart(2, '0')

function Incidents() {
  const { data, isLoading, isError, error } = useIncidents()
  const [filtre, setFiltre] = useState('tous')
  const [selectionId, setSelectionId] = useState(null)

  if (isLoading) return <EtatVide type="chargement" />
  if (isError) return <EtatVide type="erreur" message={error.message} />

  const affiches = filtre === 'tous' ? data : data.filter((i) => i.type_incident === filtre)
  const selection = data.find((i) => i.incident_id === selectionId) ?? null

  const il24h = data.filter(
    (i) => Date.now() - new Date(i.date_incident).getTime() < 24 * 3600 * 1000,
  ).length
  const horsMission = data.filter((i) => i.mission === null).length

  return (
    <div>
      <h1>Incidents et alertes</h1>
      <p className="sous-titre">Consultez les incidents signalés par le robot.</p>

      <div className="cartes">
        <StatCard titre="Incidents" valeur={deux(data.length)} details="Au total" />
        <StatCard titre="Dernières 24 h" valeur={deux(il24h)} details="Incidents récents" />
        <StatCard titre="Hors mission" valeur={deux(horsMission)} details="Sans mission associée" />
      </div>

      <div className="onglets">
        {[['tous', 'Tous'], ...Object.entries(libelles)].map(([code, nom]) => (
          <button
            key={code}
            className={code === filtre ? 'onglet actif' : 'onglet'}
            onClick={() => setFiltre(code)}
          >
            {nom}
          </button>
        ))}
      </div>

      {affiches.length === 0 ? (
        <EtatVide message="Aucun incident pour ce filtre." />
      ) : (
        <div className="incidents-mise-en-page">
          <table className="tableau">
            <thead>
              <tr><th>Incident</th><th>Type</th><th>Date</th><th>Mission</th></tr>
            </thead>
            <tbody>
              {affiches.map((i) => (
                <tr
                  key={i.incident_id}
                  className={i.incident_id === selectionId ? 'ligne-selection' : 'ligne-cliquable'}
                  onClick={() => setSelectionId(i.incident_id)}
                >
                  <td><strong>INC-{i.incident_id}</strong></td>
                  <td><StatusBadge statut={libelles[i.type_incident] ?? i.type_incident} /></td>
                  <td>{formatDate(i.date_incident)}</td>
                  <td>{i.mission ? `Mission n° ${i.mission}` : 'Aucune'}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {selection && (
            <div className="carte-mission panneau-detail">
              <strong>INC-{selection.incident_id}</strong>
              <small>{formatDate(selection.date_incident)}</small>
              <div className="badges-ligne">
                <StatusBadge statut={libelles[selection.type_incident] ?? selection.type_incident} />
              </div>
              <p>
                {selection.mission
                  ? `Survenu pendant la mission n° ${selection.mission}.`
                  : 'Survenu en dehors de toute mission.'}
              </p>
              <strong>Mesures liées</strong>
              <p>
                {selection.mesures.length === 0
                  ? 'Aucune mesure liée.'
                  : selection.mesures.map((m) => `#${m}`).join(', ')}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Incidents