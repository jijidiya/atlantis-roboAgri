const styles = {
  'En cours': 'badge-bleu',
  'Interrompue': 'badge-rouge',
  'Planifiée': 'badge-violet',
  'Terminée': 'badge-vert',
  'Non confirmée': 'badge-orange',

  'Critique': 'badge-rouge',
  'Avertissement': 'badge-orange',
  'Information': 'badge-bleu',
  'Ouvert': 'badge-rouge',
  'À traiter': 'badge-orange',
  'Résolu': 'badge-vert',

  'Optimal': 'badge-vert',
  'Sol sec': 'badge-orange',

  'Administrateur': 'badge-vert',
  'Propriétaire': 'badge-bleu',

  'Obstacle': 'badge-orange',
  'Capteur défaillant': 'badge-rouge',
  'Perte de communication': 'badge-violet',
  'Mesure invalide': 'badge-rouge',
}

function StatusBadge({ statut }) {
 return <span className={`badge ${styles[statut] || 'badge-bleu'}`}>{statut}</span>
}

export default StatusBadge