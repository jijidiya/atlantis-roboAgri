import { useState } from 'react'
import { evenements } from '../data/historique'

const onglets = ['Toute l’activité', 'Missions', 'Mesures', 'Incidents', 'Irrigation']

function Historique() {
  const [onglet, setOnglet] = useState('Toute l’activité')
  const [recherche, setRecherche] = useState('')
  const [zone, setZone] = useState('Toutes')

  const affiches = evenements
    .filter((e) => onglet === 'Toute l’activité' || e.type === onglet)
    .filter((e) => zone === 'Toutes' || e.zone === zone)
    .filter((e) =>
      `${e.titre} ${e.detail} ${e.source}`.toLowerCase().includes(recherche.toLowerCase())
    )

  function exporterCsv() {
    const entetes = ['Date', 'Événement', 'Détail', 'Zone', 'Source', 'Résultat']
    const lignes = affiches.map((e) =>
      [e.date, e.titre, e.detail, e.zone, e.source, e.resultat]
        .map((v) => `"${v}"`)
        .join(';')
    )
    const contenu = '\uFEFF' + [entetes.join(';'), ...lignes].join('\n')
    const blob = new Blob([contenu], { type: 'text/csv;charset=utf-8;' })
    const lien = document.createElement('a')
    lien.href = URL.createObjectURL(blob)
    lien.download = 'historique.csv'
    lien.click()
  }

  return (
    <div>
      <div className="titre-ligne">
        <div>
          <h1>Historique d’activité</h1>
          <p className="sous-titre">Retrouvez chaque mission, mesure et intervention.</p>
        </div>
        <button className="bouton-principal" onClick={exporterCsv}>Exporter en CSV</button>
      </div>

      <div className="onglets">
        {onglets.map((o) => (
          <button key={o} className={o === onglet ? 'onglet actif' : 'onglet'} onClick={() => setOnglet(o)}>
            {o}
          </button>
        ))}
      </div>

      <div className="filtres">
        <input
          type="text"
          placeholder="Rechercher dans l’historique..."
          value={recherche}
          onChange={(e) => setRecherche(e.target.value)}
        />
        <select value={zone} onChange={(e) => setZone(e.target.value)}>
          <option>Toutes</option>
          <option>Zone A</option>
          <option>Zone B</option>
          <option>Zone C</option>
        </select>
      </div>

      <table className="tableau">
        <thead>
          <tr><th>Date et heure</th><th>Événement</th><th>Zone</th><th>Source</th><th>Résultat</th></tr>
        </thead>
        <tbody>
          {affiches.map((e, i) => (
            <tr key={i}>
              <td>{e.date}</td>
              <td><strong>{e.titre}</strong><small>{e.detail}</small></td>
              <td>{e.zone}</td>
              <td>{e.source}</td>
              <td>{e.resultat}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="sous-titre">{affiches.length} événement(s) affiché(s) sur {evenements.length}</p>
    </div>
  )
}

export default Historique