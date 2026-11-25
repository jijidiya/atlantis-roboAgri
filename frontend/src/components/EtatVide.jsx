// type : 'vide' | 'chargement' | 'erreur'
// onReessayer : si fourni avec type 'erreur', affiche un bouton « Réessayer ».
function EtatVide({ type = 'vide', message, onReessayer }) {
  const textes = {
    vide: 'Aucune donnée à afficher.',
    chargement: 'Chargement…',
    erreur: 'Une erreur est survenue.',
  }
  const role = type === 'erreur' ? 'alert' : type === 'chargement' ? 'status' : undefined
  return (
    <div className={type === 'erreur' ? 'etat etat-erreur' : 'etat'} role={role}>
      <p style={{ margin: 0 }}>{message || textes[type]}</p>
      {type === 'erreur' && onReessayer && (
        <button className="bouton" style={{ marginTop: 12 }} onClick={onReessayer}>
          Réessayer
        </button>
      )}
    </div>
  )
}

export default EtatVide