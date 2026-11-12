export function decision(humidite, seuilBas) {
  const invalide =
    humidite === null || Number.isNaN(humidite) || humidite < 0 || humidite > 100
  if (invalide) return 'invalide'
  if (humidite < seuilBas) return 'insuffisante'
  return 'suffisante'
}