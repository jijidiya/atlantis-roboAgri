const libelles = {
  planifiee: 'Planifiée',
  en_cours: 'En cours',
  terminee: 'Terminée',
  interrompue: 'Interrompue',
  non_confirmee: 'Non confirmée',
}

export function adapterMission(m) {
  const etapes = m.etapes ?? []
  const faites = etapes.filter((e) => e.statut === 'terminee').length
  return {
    id: m.mission_id,
    titre: `Mission n° ${m.mission_id}`,
    parcelle: m.parcelle,
    statut: libelles[m.statut] ?? m.statut,
    code: m.statut,
    faits: faites,
    total: etapes.length,
    creation: new Date(m.date_creation).toLocaleString('fr-FR', {
      dateStyle: 'short',
      timeStyle: 'short',
    }),
  }
}