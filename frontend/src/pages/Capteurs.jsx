import { useState } from 'react'

const zonesInit = [
  { zone: 'Zone A', capteur: 'CAP-A01', humidite: 42, temperature: 26.3, heure: '21 oct. · 10:42', couleur: '#1f6b43' },
  { zone: 'Zone B', capteur: 'CAP-B01', humidite: 21, temperature: 29.1, heure: '21 oct. · 10:40', couleur: '#d98a1f' },
  { zone: 'Zone C', capteur: 'CAP-C01', humidite: 56, temperature: 27.0, heure: '21 oct. · 10:38', couleur: '#3b7fc4' },
]

const histHumidite = {
  'Zone A': [44, 43, 45, 42, 41, 42, 42],
  'Zone B': [30, 28, 26, 24, 23, 22, 21],
  'Zone C': [55, 56, 57, 56, 55, 56, 56],
}
const histTemperature = {
  'Zone A': [24, 25, 26, 27, 27, 26, 26],
  'Zone B': [26, 27, 28, 29, 30, 29, 29],
  'Zone C': [25, 26, 26, 27, 27, 27, 27],
}

function etat(humidite) {
  if (humidite < 30) return { texte: 'Sol sec', classe: 'badge rouge' }
  if (humidite > 70) return { texte: 'Trop humide', classe: 'badge orange' }
  return { texte: 'Optimal', classe: 'badge vert' }
}

function Graphique({ donnees, zones, min, max }) {
  const largeur = 600
  const hauteur = 120
  const y = (v) => hauteur - ((v - min) / (max - min)) * hauteur
  return (
    <svg viewBox={`0 0 ${largeur} ${hauteur}`} className="courbe">
      {zones.map((z) => (
        <polyline
          key={z.zone}
          fill="none"
          stroke={z.couleur}
          strokeWidth="3"
          points={donnees[z.zone]
            .map((v, i) => `${(i * largeur) / (donnees[z.zone].length - 1)},${y(v)}`)
            .join(' ')}
        />
      ))}
    </svg>
  )
}

export default function Capteurs() {
  const [mesures, setMesures] = useState(zonesInit)

  const actualiser = () => {
    setMesures(
      mesures.map((m) => ({
        ...m,
        humidite: Math.max(5, Math.min(95, m.humidite + Math.round(Math.random() * 6 - 3))),
        temperature: Math.round((m.temperature + (Math.random() * 1.2 - 0.6)) * 10) / 10,
        heure: "À l'instant",
      }))
    )
  }

  const moyHumidite = Math.round(mesures.reduce((s, m) => s + m.humidite, 0) / mesures.length)
  const moyTemp = (mesures.reduce((s, m) => s + m.temperature, 0) / mesures.length).toFixed(1)

  return (
    <div>
      <div className="entete">
        <div>
          <h1>Capteurs et mesures</h1>
          <p className="sous-titre">Des mesures fiables pour comprendre l'état de vos sols.</p>
        </div>
        <button className="bouton" onClick={actualiser}>Actualiser</button>
      </div>

      <div className="stats">
        {mesures.map((m) => (
          <div className="carte" key={m.zone}>
            <p className="carte-titre">Humidité · {m.zone}</p>
            <p className="carte-valeur" style={{ color: m.couleur }}>{m.humidite} %</p>
            <p className="carte-detail">{etat(m.humidite).texte}</p>
          </div>
        ))}
        <div className="carte">
          <p className="carte-titre">Température moyenne</p>
          <p className="carte-valeur">{moyTemp} °C</p>
          <p className="carte-detail">Humidité moyenne : {moyHumidite} %</p>
        </div>
      </div>

      <div className="grille-egale">
        <div className="carte">
          <h2>Humidité du sol</h2>
          <Graphique donnees={histHumidite} zones={mesures} min={0} max={80} />
          <div className="legende">
            {mesures.map((m) => (
              <span key={m.zone}><i style={{ background: m.couleur }} /> {m.zone}</span>
            ))}
          </div>
        </div>
        <div className="carte">
          <h2>Température du sol</h2>
          <Graphique donnees={histTemperature} zones={mesures} min={20} max={35} />
          <div className="legende">
            {mesures.map((m) => (
              <span key={m.zone}><i style={{ background: m.couleur }} /> {m.zone}</span>
            ))}
          </div>
        </div>
      </div>

      <div className="carte">
        <h2>Derniers relevés</h2>
        <table className="tableau">
          <thead>
            <tr><th>Capteur</th><th>Zone</th><th>Humidité</th><th>Température</th><th>Dernier relevé</th><th>État</th></tr>
          </thead>
          <tbody>
            {mesures.map((m) => {
              const e = etat(m.humidite)
              return (
                <tr key={m.capteur}>
                  <td>{m.capteur}</td>
                  <td>{m.zone}</td>
                  <td>{m.humidite} %</td>
                  <td>{m.temperature} °C</td>
                  <td>{m.heure}</td>
                  <td><span className={e.classe}>{e.texte}</span></td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}