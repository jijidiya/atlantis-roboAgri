import { useState } from 'react'

const zonesInitiales = [
  {
    id: 'A',
    nom: 'Zone A · Maïs',
    humidite: 42,
    etat: 'Optimal',
    couleur: '#1f6b43',
    points: '60,60 260,40 300,200 80,230',
  },
  {
    id: 'B',
    nom: 'Zone B · Tomates',
    humidite: 21,
    etat: 'Sec',
    couleur: '#d98a1f',
    points: '330,50 540,70 520,200 320,180',
  },
  {
    id: 'C',
    nom: 'Zone C · Manioc',
    humidite: 56,
    etat: 'Optimal',
    couleur: '#1f6b43',
    points: '300,230 520,230 540,340 280,350',
  },
]

const robot = { x: 170, y: 130 }

const incidents = [
  { id: 1, zone: 'B', titre: 'Humidité faible', x: 420, y: 125, type: 'critique' },
  { id: 2, zone: 'C', titre: 'Obstacle détecté', x: 400, y: 290, type: 'attention' },
]

export default function Carte() {
  const [zones, setZones] = useState(zonesInitiales)
  const [choisie, setChoisie] = useState(null)
  const [recherche, setRecherche] = useState('')
  const [formulaireOuvert, setFormulaireOuvert] = useState(false)
  const [nomZone, setNomZone] = useState('')
  const [culture, setCulture] = useState('')
  const [humidite, setHumidite] = useState('40')
  const [message, setMessage] = useState('')

  const visibles = zones.filter((z) =>
    z.nom.toLowerCase().includes(recherche.toLowerCase())
  )

  const ajouterZone = (e) => {
    e.preventDefault()

    const prochainId = String.fromCharCode(65 + zones.length)

    // Position indicative pour la représentation SVG
    const index = zones.length - 3
    const x = 15 + (index % 3) * 185
    const y = 250 + Math.floor(index / 3) * 60

    const nouvelleZone = {
      id: prochainId,
      nom: `${nomZone} · ${culture}`,
      humidite: Number(humidite),
      etat: Number(humidite) < 30 ? 'Sec' : 'Optimal',
      couleur: '#176b45',
      points: `${x},${y} ${x + 145},${y} ${x + 145},${y + 45} ${x},${y + 45}`,
    }

    setZones((anciennes) => [...anciennes, nouvelleZone])
    setChoisie(prochainId)
    setRecherche('')
    setNomZone('')
    setCulture('')
    setHumidite('40')
    setFormulaireOuvert(false)
    setMessage(`${nouvelleZone.nom} a été ajoutée avec succès.`)
  }

  return (
    <div>
      <div className="entete">
        <div>
          <h1>Carte des parcelles</h1>
          <p className="sous-titre">
            Localisez votre robot et suivez l'état de chaque zone en temps réel.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <button
            className="bouton"
            onClick={() => {
              setFormulaireOuvert(!formulaireOuvert)
              setMessage('')
            }}
          >
            + Ajouter une zone
          </button>

          <button className="bouton" onClick={() => setChoisie('A')}>
            Centrer sur RB-01
          </button>
        </div>
      </div>

      {message && (
        <p className="badge vert" role="status" style={{ marginBottom: 16 }}>
          {message}
        </p>
      )}

      {formulaireOuvert && (
        <div className="carte" style={{ marginBottom: 20 }}>
          <h2>Ajouter une nouvelle zone</h2>

          <form onSubmit={ajouterZone}>
            <div style={{ display: 'grid', gap: 14, maxWidth: 450 }}>
              <label className="champ">
                Nom de la zone
                <input
                  type="text"
                  value={nomZone}
                  onChange={(e) => setNomZone(e.target.value)}
                  placeholder="Ex. Zone Nord"
                  required
                />
              </label>

              <label className="champ">
                Type de culture
                <select
                  value={culture}
                  onChange={(e) => setCulture(e.target.value)}
                  required
                >
                  <option value="">Choisir une culture</option>
                  <option value="Maïs">Maïs</option>
                  <option value="Tomates">Tomates</option>
                  <option value="Manioc">Manioc</option>
                  <option value="Haricots">Haricots</option>
                  <option value="Autre">Autre</option>
                </select>
              </label>

              <label className="champ">
                Taux d'humidité (%)
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={humidite}
                  onChange={(e) => setHumidite(e.target.value)}
                  required
                />
              </label>

              <div style={{ display: 'flex', gap: 10 }}>
                <button type="submit" className="bouton">
                  Enregistrer la zone
                </button>

                <button
                  type="button"
                  className="bouton"
                  onClick={() => setFormulaireOuvert(false)}
                >
                  Annuler
                </button>
              </div>
            </div>
          </form>
        </div>
      )}

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
              <g key={z.id}>
                <polygon
                  points={z.points}
                  fill={z.couleur}
                  fillOpacity={choisie === z.id ? 0.45 : 0.2}
                  stroke={z.couleur}
                  strokeWidth={choisie === z.id ? 4 : 2}
                  opacity={visibles.includes(z) ? 1 : 0.2}
                  onClick={() => setChoisie(z.id)}
                  style={{ cursor: 'pointer' }}
                />
                <text
                  x={Number(z.points.split(' ')[0].split(',')[0]) + 8}
                  y={Number(z.points.split(' ')[0].split(',')[1]) + 20}
                  fontSize="12"
                  fill="#1e293b"
                  fontWeight="600"
                  pointerEvents="none"
                >
                  {z.id}
                </text>
              </g>
            ))}

            {incidents.map((i) => (
              <circle
                key={i.id}
                cx={i.x}
                cy={i.y}
                r="9"
                fill={i.type === 'critique' ? '#d33' : '#e0a020'}
                stroke="white"
                strokeWidth="2"
              />
            ))}

            <circle
              cx={robot.x}
              cy={robot.y}
              r="12"
              fill="#1f6b43"
              stroke="white"
              strokeWidth="3"
            />

            <text
              x={robot.x + 16}
              y={robot.y + 4}
              fontSize="13"
              fill="#1f6b43"
              fontWeight="700"
            >
              RB-01
            </text>
          </svg>

          <div className="legende">
            <span><i style={{ background: '#1f6b43' }} /> Robot / Zone</span>
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
            <h2>État des parcelles ({zones.length})</h2>

            {visibles.map((z) => (
              <div
                key={z.id}
                className={choisie === z.id ? 'ligne-zone choisie' : 'ligne-zone'}
                onClick={() => setChoisie(z.id)}
                style={{ cursor: 'pointer' }}
              >
                <span>{z.nom}</span>
                <strong style={{ color: z.couleur }}>
                  {z.humidite} %
                </strong>
              </div>
            ))}

            {visibles.length === 0 && (
              <p>Aucune zone trouvée.</p>
            )}
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