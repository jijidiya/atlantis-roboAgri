export const transitions = {
  'Planifiée': ['En cours'],
  'En cours': ['Terminée', 'Interrompue', 'Non confirmée'],
  'Interrompue': ['En cours'],
  'Non confirmée': ['Terminée', 'Interrompue'],
  'Terminée': [],
}