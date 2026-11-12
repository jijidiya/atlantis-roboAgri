import { useState } from 'react'
import { zones as zonesInitiales } from '../data/zones'
import { decision } from '../utils/decision'

const affichage = {
  suffisante: { texte: 'Suffisante', classe: 'badge-vert' },
  insuffisante: { texte: 'À irriguer', classe: 'badge-orange' },
  invalide: { texte: 'Mesure invalide', classe: 'badge-rouge' },
}

function Irrigation() {
  const [zones, setZones] = useState(zonesInitiales)
  const [message, setMessage] = useState('')
  const [historique, setHistorique] = useState([
    { date: '21 oct. · 06:30', zone: 'Zone A', action: 'Recommandation suivie', source: 'Manuel · Magnificat Kakanda' },
  ])

  function changerSeuil(id, champ, valeur) {
    setZones(zones.map((z) => (z.id === id ? { ...z, [champ]: Number(valeur) } : z)))
    setMessage('')
  }

  function enregistrer() {
    const erreur = zones.find((z) => z.seuilBas >= z.seuilHaut)
    if (erreur) {
      setMessage(`Erreur : dans ${erreur.nom}, le seuil bas doit être inférieur au seuil haut.`)
    } else {
      setMessage('Seuils enregistrés (simulation, pas encore envoyés à l’API).')
    }
  }

  function marquerArrose(zone) {
    const date = new Date().toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' })
    setHistorique([
      { date, zone: zone.nom, action: 'Arrosage effectué (saisi par l’opérateur)', source: 'Manuel · Magnificat Kakanda' },
      ...historique,
    ])
  }

  const aIrriguer = zones.filter((z) => decision(z.humidite, z.seuilBas) === 'insuffisante')

  return (
    <div>
      <div className="titre-ligne">
        <div>
          <h1>Irrigation et seuils</h1>
          <p className="sous-titre">Ajustez les seuils de chaque zone pour une irrigation au plus juste.</p>
        </div>
        <button className="bouton-principal" onClick={enregistrer}>Enregistrer les seuils</button>
      </div>

      {message && <p className="message">{message}</p>}

      {aIrriguer.map((z) => (
        <div key={z.id} className="alerte alerte-orange">
          <strong>{z.nom} : le sol a besoin d’eau</strong>
          <span>Humidité à {z.humidite} %, sous le seuil bas de {z.seuilBas} %. Arrosage recommandé.</span>
        </div>
      ))}

      <div className="grille-zones">
        {zones.map((z) => {
          const etat = decision(z.humidite, z.seuilBas)
          const a = affichage[etat]
          return (
            <div key={z.id} className="carte-mission">
              <div className="carte-mission-haut">
                <strong>{z.nom} · {z.culture}</strong>
                <span className={`badge ${a.classe}`}>{a.texte}</span>
              </div>
              <small className="etiquette">Humidité actuelle</small>
              <p className="stat-valeur">{z.humidite === null ? '—' : `${z.humidite} %`}</p>

              <div className="seuils">
                <label>
                  <small className="etiquette">Seuil bas (%)</small>
                  <input type="number" value={z.seuilBas} onChange={(e) => changerSeuil(z.id, 'seuilBas', e.target.value)} />
                </label>
                <label>
                  <small className="etiquette">Seuil haut (%)</small>
                  <input type="number" value={z.seuilHaut} onChange={(e) => changerSeuil(z.id, 'seuilHaut', e.target.value)} />
                </label>
              </div>

              <small className="etiquette">Recommandation dès {z.seuilBas} %, objectif {z.seuilHaut} %</small>
              {etat === 'insuffisante' && (
                <button className="bouton-petit" onClick={() => marquerArrose(z)}>Marquer comme arrosé</button>
              )}
              {etat === 'invalide' && (
                <small className="texte-rouge">Aucune recommandation : mesure invalide, incident à signaler.</small>
              )}
            </div>
          )
        })}
      </div>

      <h2>Historique d’irrigation</h2>
      <table className="tableau">
        <thead>
          <tr><th>Date et heure</th><th>Parcelle</th><th>Action</th><th>Source</th></tr>
        </thead>
        <tbody>
          {historique.map((h, i) => (
            <tr key={i}>
              <td>{h.date}</td><td>{h.zone}</td><td>{h.action}</td><td>{h.source}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default Irrigation