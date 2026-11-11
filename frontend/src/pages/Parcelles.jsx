import { useState } from 'react'

const parcelles = [
  { id: 1, nom: 'Zone A · Plaine nord', culture: 'Maïs', surface: 4.6, humidite: 42, etat: 'Optimal' },
  { id: 2, nom: 'Zone B · Jardin est', culture: 'Tomates', surface: 3.2, humidite: 21, etat: 'Sec' },
  { id: 3, nom: 'Zone C · Coteau sud', culture: 'Manioc', surface: 4.6, humidite: 56, etat: 'Optimal' },
]

const classeEtat = { Optimal: 'badge vert', Sec: 'badge rouge' }

export default function Parcelles() {
  const [recherche, setRecherche] = useState('')
  const [culture, setCulture] = useState('Toutes')

  const total = parcelles.reduce((s, p) => s + p.surface, 0)
  const cultures = ['Toutes', ...new Set(parcelles.map((p) => p.culture))]

  const visibles = parcelles.filter(
    (p) =>
      p.nom.toLowerCase().includes(recherche.toLowerCase()) &&
      (culture === 'Toutes' || p.culture === culture)
  )

  return (
    <div>
      <div className="entete">
        <div>
          <h1>Gestion des parcelles</h1>
          <p className="sous-titre">Organisez vos cultures et gardez vos zones de surveillance à jour.</p>
        </div>
        <button className="bouton">+ Ajouter une parcelle</button>
      </div>

      <div className="stats">
        <div className="carte"><p className="carte-titre">Superficie totale</p><p className="carte-valeur">{total.toFixed(1)} ha</p></div>
        <div className="carte"><p className="carte-titre">Parcelles actives</p><p className="carte-valeur">{String(parcelles.length).padStart(2, '0')}</p></div>
        <div className="carte"><p className="carte-titre">Cultures suivies</p><p className="carte-valeur">{String(cultures.length - 1).padStart(2, '0')}</p></div>
        <div className="carte"><p className="carte-titre">Parcelles à surveiller</p><p className="carte-valeur">{String(parcelles.filter((p) => p.etat !== 'Optimal').length).padStart(2, '0')}</p></div>
      </div>

      <div className="carte" style={{ marginBottom: 16 }}>
        <div className="barre-filtres">
          <input
            className="recherche"
            placeholder="Rechercher une parcelle…"
            value={recherche}
            onChange={(e) => setRecherche(e.target.value)}
          />
          <select value={culture} onChange={(e) => setCulture(e.target.value)} className="select">
            {cultures.map((c) => <option key={c}>{c}</option>)}
          </select>
          <button className="onglet" onClick={() => { setRecherche(''); setCulture('Toutes') }}>
            Réinitialiser
          </button>
        </div>

        <table className="tableau">
          <thead>
            <tr><th>Parcelle</th><th>Culture</th><th>Surface</th><th>Humidité</th><th>État</th></tr>
          </thead>
          <tbody>
            {visibles.map((p) => (
              <tr key={p.id}>
                <td>{p.nom}</td>
                <td>{p.culture}</td>
                <td>{p.surface} ha</td>
                <td>{p.humidite} %</td>
                <td><span className={classeEtat[p.etat]}>{p.etat}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="carte">
        <h2>Répartition des surfaces</h2>
        {parcelles.map((p) => (
          <div key={p.id} className="repartition">
            <span>{p.culture}</span>
            <div className="barre">
              <div className="barre-remplie" style={{ width: `${(p.surface / total) * 100}%` }} />
            </div>
            <strong>{Math.round((p.surface / total) * 100)} %</strong>
          </div>
        ))}
      </div>
    </div>
  )
}