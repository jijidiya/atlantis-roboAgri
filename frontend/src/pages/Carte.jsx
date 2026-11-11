import { useState } from 'react'

const zones = [
  { id: 'A', nom: 'Zone A · Maïs', humidite: 42, etat: 'Optimal', couleur: '#1f6b43', points: '60,60 260,40 300,200 80,230' },
  { id: 'B', nom: 'Zone B · Tomates', humidite: 21, etat: 'Sec', couleur: '#d98a1f', points: '330,50 540,70 520,200 320,180' },
  { id: 'C', nom: 'Zone C · Manioc', humidite: 56, etat: 'Optimal', couleur: '#1f6b43', points: '300,230 520,230 540,340 280,350' },
]

const robot = { x: 170, y: 130 }
const incidents = [
  { id: 1, zone: 'B', titre: 'Humidité faible', x: 420, y: 125, type: 'critique' },
  { id: 2, zone: 'C', titre: 'Obstacle détecté', x: 400, y: 290, type: 'attention' },
]

export default function Carte() {
  const [choisie, setChoisie] = useState(null)
  const [recherche, setRecherche] = useState('')

  const visibles = zones.filter((z) =>
    z.nom.toLowerCase().includes(recherche.toLowerCase())
  )

  return (
    <div>
      <div className="entete">
        <div>
          <h1>Carte des parcelles</h1>
          <p className="sous-titre">Localisez votre robot et suivez l'état de chaque zone en temps réel.</p>
        </div>
        <button className="bouton" onClick={() => setChoisie('A')}>Centrer sur RB-01</button>
      </div>

      <div className="carte-layout">
        <div className="carte">
          <input
            className="recherche"
            placeholder="Rechercher une zone…"
            value={recherche}
            onChange={(e) => setRecherche(e.target.value)}
          />
          <svg viewBox="0 0 600 380" className="plan">
            <rect width="600" height="380" fill="#eef3ec" />
            {zones.map((z) => (
              <polygon
                key={z.id}
                points={z.points}
                fill={z.couleur}
                fillOpacity={choisie === z.id ? 0.45 : 0.2}
                stroke={z.couleur}
                strokeWidth={choisie === z.id ? 4 : 2}
                opacity={visibles.includes(z) ? 1 : 0.2}
                onClick={() => setChoisie(z.id)}
                style={{ cursor: 'pointer' }}
              />
            ))}
            {incidents.map((i) => (
              <circle key={i.id} cx={i.x} cy={i.y} r="9"
                fill={i.type === 'critique' ? '#d33' : '#e0a020'} stroke="white" strokeWidth="2" />
            ))}
            <circle cx={robot.x} cy={robot.y} r="12" fill="#1f6b43" stroke="white" strokeWidth="3" />
            <text x={robot.x + 16} y={robot.y + 4} fontSize="13" fill="#1f6b43" fontWeight="700">RB-01</text>
          </svg>
          <div className="legende">
            <span><i style={{ background: '#1f6b43' }} /> Robot</span>
            <span><i style={{ background: '#d33' }} /> Incident critique</span>
            <span><i style={{ background: '#e0a020' }} /> Avertissement</span>
          </div>
        </div>

        <div>
          <div className="carte" style={{ marginBottom: 16 }}>
            <h2>Robot RB-01</h2>
            <p><span className="badge vert">Connecté</span></p>
            <p className="carte-detail">Batterie 78 % · Position : Zone A</p>
          </div>

          <div className="carte" style={{ marginBottom: 16 }}>
            <h2>État des parcelles</h2>
            {visibles.map((z) => (
              <div
                key={z.id}
                className={choisie === z.id ? 'ligne-zone choisie' : 'ligne-zone'}
                onClick={() => setChoisie(z.id)}
              >
                <span>{z.nom}</span>
                <strong style={{ color: z.couleur }}>{z.humidite} %</strong>
              </div>
            ))}
          </div>

          <div className="carte">
            <h2>Incidents localisés</h2>
            {incidents.map((i) => (
              <div className={`alerte ${i.type}`} key={i.id}>
                <strong>{i.titre}</strong> · Zone {i.zone}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}