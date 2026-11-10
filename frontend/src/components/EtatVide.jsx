// type : 'vide' | 'chargement' | 'erreur'
function EtatVide({ type = 'vide', message }) {
  const textes = {
    vide: 'Aucune donnée à afficher.',
    chargement: 'Chargement…',
    erreur: 'Une erreur est survenue.',
  }
  return (
    <div className={type === 'erreur' ? 'etat etat-erreur' : 'etat'}>
      {message || textes[type]}
    </div>
  )
}

export default EtatVide