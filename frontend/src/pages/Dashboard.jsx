const stats = [
  { titre: 'État du robot', valeur: 'Connecté', detail: 'RB-01 · mis à jour il y a 2 min' },
  { titre: 'Batterie', valeur: '78 %', detail: 'Autonomie estimée : 4 h 32' },
  { titre: 'Missions du jour', valeur: '05', detail: '1 en cours · 3 planifiées' },
  { titre: 'Incidents ouverts', valeur: '02', detail: '1 critique · 1 avertissement' },
]

const humidite = [
  { zone: 'Zone A', couleur: '#1f6b43', valeurs: [44, 43, 45, 42, 41, 42, 42] },
  { zone: 'Zone B', couleur: '#d98a1f', valeurs: [30, 28, 26, 24, 23, 22, 21] },
  { zone: 'Zone C', couleur: '#3b7fc4', valeurs: [55, 56, 57, 56, 55, 56, 56] },
]

const missions = [
  { nom: 'Relevé d\'humidité · 65 %', zone: 'Zone A', heure: '10:15', statut: 'En cours' },
  { nom: 'Inspection des cultures', zone: 'Zone C', heure: '09:40', statut: 'Interrompue' },
  { nom: 'Contrôle du sol', zone: 'Zone B', heure: '11:15', statut: 'Planifiée' },
  { nom: 'Relevé de température', zone: 'Zone A', heure: '08:00', statut: 'Terminée' },
]

const alertes = [
  { type: 'critique', titre: 'Humidité faible · Zone B', texte: '21 % mesuré, sous le seuil de 30 %. À irriguer.' },
  { type: 'attention', titre: 'Obstacle détecté · Zone C', texte: 'Passage à contrôler avant la reprise.' },
]

const classeStatut = {
  'En cours': 'badge bleu',
  'Interrompue': 'badge rouge',
  'Planifiée': 'badge violet',
  'Terminée': 'badge vert',
}

function Courbe({ valeurs, couleur }) {
  const largeur = 600
  const points = valeurs
    .map((v, i) => `${(i * largeur) / (valeurs.length - 1)},${120 - v * 2}`)
    .join(' ')
  return <polyline points={points} fill="none" stroke={couleur} strokeWidth="3" />
}

export default function Dashboard() {
  return (
    <div>
      <div className="entete">
        <div>
          <h1>Tableau de bord</h1>
          <p className="sous-titre">
            Bonjour Alain, voici l'essentiel de votre exploitation aujourd'hui.
          </p>
        </div>
        <span className="date">21 octobre 2026</span>
      </div>

      <div className="stats">
        {stats.map((s) => (
          <div className="carte" key={s.titre}>
            <p className="carte-titre">{s.titre}</p>
            <p className="carte-valeur">{s.valeur}</p>
            <p className="carte-detail">{s.detail}</p>
          </div>
        ))}
      </div>

      <div className="grille-2">
        <div className="carte">
          <h2>Évolution de l'humidité du sol</h2>
          <svg viewBox="0 0 600 120" className="courbe">
            {humidite.map((h) => (
              <Courbe key={h.zone} valeurs={h.valeurs} couleur={h.couleur} />
            ))}
          </svg>
          <div className="legende">
            {humidite.map((h) => (
              <span key={h.zone}>
                <i style={{ background: h.couleur }} /> {h.zone}
              </span>
            ))}
          </div>
        </div>

        <div className="carte">
          <h2>À votre attention</h2>
          {alertes.map((a) => (
            <div className={`alerte ${a.type}`} key={a.titre}>
              <strong>{a.titre}</strong>
              <p>{a.texte}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="carte">
        <h2>Missions récentes</h2>
        <table className="tableau">
          <thead>
            <tr>
              <th>Mission</th>
              <th>Zone</th>
              <th>Heure</th>
              <th>Statut</th>
            </tr>
          </thead>
          <tbody>
            {missions.map((m) => (
              <tr key={m.nom}>
                <td>{m.nom}</td>
                <td>{m.zone}</td>
                <td>{m.heure}</td>
                <td><span className={classeStatut[m.statut]}>{m.statut}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}