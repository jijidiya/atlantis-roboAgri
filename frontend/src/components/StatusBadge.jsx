const styles = {
  'En cours': 'badge-bleu',
  'Interrompue': 'badge-rouge',
  'Planifiée': 'badge-violet',
  'Terminée': 'badge-vert',
  'Non confirmée': 'badge-orange',
}

function StatusBadge({ statut }) {
  return <span className={`badge ${styles[statut]}`}>{statut}</span>
}

export default StatusBadge