export function formaterSuperficie(val) {
  if (val == null) return '—';
  const n = Number(val);
  if (Number.isNaN(n)) return val;
  return `${n.toLocaleString('fr-FR', { maximumFractionDigits: 2 })} m²`;
}

export function formaterPourcentage(val) {
  if (val == null) return '—';
  const n = Number(val);
  if (Number.isNaN(n)) return val;
  return `${n.toFixed(1)} %`;
}

export function formaterDateHeure(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('fr-FR', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formaterHeure(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

// Dernière humidité connue par zone (via les mesures récentes).
export function humiditeParZone(mesures) {
  const map = new Map();
  for (const m of mesures ?? []) {
    if (m.statut !== 'valide' || m.valeur_humidite == null) continue;
    if (!map.has(m.zone)) {
      map.set(m.zone, Number(m.valeur_humidite));
    }
  }
  return map;
}

// Statut visuel d'une zone à partir de son humidité actuelle et de ses seuils.
export function etatZone(humidite, zone) {
  if (humidite == null) return { label: 'Aucune mesure', classe: 'badge' };
  const min = Number(zone.humidite_minimum);
  const max = Number(zone.humidite_maximum);
  if (humidite < min) return { label: 'Sec', classe: 'badge rouge' };
  if (humidite > max) return { label: 'Humide', classe: 'badge rouge' };
  return { label: 'Optimal', classe: 'badge vert' };
}