export const incidents = [
  { id: 'INC-028', titre: 'Humidité faible', source: 'CAP-B01', gravite: 'Critique', zone: 'Zone B', date: '21 oct. · 10:35', statut: 'Ouvert',
    detail: 'Humidité de 21 %, sous le seuil bas de 30 %. Vérifiez l’arrosage avant la prochaine mission.',
    suivi: ['10:35 · Seuil franchi, alerte créée', '11:15 · Contrôle du sol sec planifié'] },
  { id: 'INC-027', titre: 'Obstacle détecté', source: 'Robot RB-01', gravite: 'Avertissement', zone: 'Zone C', date: '21 oct. · 09:48', statut: 'À traiter',
    detail: 'Le robot s’est arrêté devant un obstacle. Mission MIS-104 interrompue.',
    suivi: ['09:48 · Obstacle détecté, robot arrêté'] },
  { id: 'INC-026', titre: 'Mesure temporairement absente', source: 'CAP-A01', gravite: 'Information', zone: 'Zone A', date: '20 oct. · 14:12', statut: 'Résolu',
    detail: 'Une mesure n’a pas été reçue, la suivante est arrivée normalement.',
    suivi: ['14:12 · Mesure absente', '14:20 · Mesure reçue, incident résolu'] },
  { id: 'INC-025', titre: 'Batterie faible', source: 'Robot RB-01', gravite: 'Avertissement', zone: 'Base', date: '19 oct. · 16:40', statut: 'Résolu',
    detail: 'Tension de la batterie basse, retour à la base.',
    suivi: ['16:40 · Batterie faible', '17:30 · Batterie rechargée'] },
]