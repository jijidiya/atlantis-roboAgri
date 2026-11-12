// c'est à utiliser dans chaque écran pour couvrir chargement/vide/erreur/succès.
export function etatRequete(query) {
  if (query.isLoading) return 'chargement';
  if (query.isError) return 'erreur';

  const donnees = query.data;
  if (donnees == null) return 'vide';
  if (Array.isArray(donnees) && donnees.length === 0) return 'vide';
  if (Array.isArray(donnees?.results) && donnees.results.length === 0) return 'vide';

  return 'succes';
}