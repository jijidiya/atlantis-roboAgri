import { useState, useMemo } from 'react';
import { useMissions } from '../hooks/useMissions';
import { useMesures } from '../hooks/useMesures';
import { useIncidents } from '../hooks/useIncidents';
import { useIrrigations } from '../hooks/useIrrigations';
import { useZones } from '../hooks/useZones';
import { formaterDateHeure } from '../utils/formatage';

const ONGLETS = [
  { cle: 'tout', nom: 'Toute l’activité' },
  { cle: 'missions', nom: 'Missions' },
  { cle: 'mesures', nom: 'Mesures' },
  { cle: 'incidents', nom: 'Incidents' },
  { cle: 'irrigation', nom: 'Irrigation' },
];

const labelIncident = {
  obstacle: 'Obstacle',
  capteur_defaillant: 'Capteur défaillant',
  perte_communication: 'Perte de communication',
  mesure_invalide: 'Mesure invalide',
};

const labelStatut = {
  planifiee: 'Planifiée',
  en_cours: 'En cours',
  terminee: 'Terminée',
  interrompue: 'Interrompue',
  non_confirmee: 'Non confirmée',
};

// Normalise les 4 sources en une forme commune pour l'onglet "Toute l'activité".
function versEvenement(type, item, zoneNom) {
  switch (type) {
    case 'missions':
      return {
        id: `m-${item.mission_id}`,
        date: item.date_creation,
        type: 'Missions',
        titre: `Mission MIS-${item.mission_id}`,
        detail: `Parcelle #${item.parcelle} · ${item.etapes?.length ?? 0} étape(s)`,
        source: 'Système',
        resultat: labelStatut[item.statut] ?? item.statut,
      };
    case 'mesures':
      return {
        id: `me-${item.mesure_id}`,
        date: item.date_heure_mesure,
        type: 'Mesures',
        titre: `Mesure #${item.mesure_id}`,
        detail: `Zone ${zoneNom(item.zone)} · point ${item.numero_point} · lecture ${item.numero_lecture}`,
        source: item.message ? `Message ${item.message}` : 'Robot',
        resultat:
          item.valeur_humidite != null
            ? `${item.valeur_humidite} % (${item.statut})`
            : item.statut,
      };
    case 'incidents':
      return {
        id: `i-${item.incident_id}`,
        date: item.date_incident,
        type: 'Incidents',
        titre: labelIncident[item.type_incident] ?? item.type_incident,
        detail: item.mission ? `Mission MIS-${item.mission}` : 'Sans mission',
        source: 'Système',
        resultat: 'À vérifier',
      };
    case 'irrigation':
      return {
        id: `ir-${item.irrigation_id}`,
        date: item.date_debut,
        type: 'Irrigation',
        titre: `Arrosage ${item.automatique ? 'automatique' : 'manuel'}`,
        detail: `Zone ${zoneNom(item.zone)} · ${item.duree_secondes} s`,
        source: item.automatique ? 'Automatique' : 'Manuelle',
        resultat: labelStatut[item.statut] ?? item.statut,
      };
    default:
      return null;
  }
}

export default function Historique() {
  const [onglet, setOnglet] = useState('tout');
  const [recherche, setRecherche] = useState('');
  const [zoneFiltre, setZoneFiltre] = useState('Toutes');

  // Charges les 4 sources (chacune avec son propre cache TanStack).
  const missions = useMissions();
  const mesures = useMesures({ zone: zoneFiltre !== 'Toutes' ? Number(zoneFiltre) : undefined });
  const incidents = useIncidents({ polling: false });
  const irrigations = useIrrigations({ zone: zoneFiltre !== 'Toutes' ? Number(zoneFiltre) : undefined });
  const zonesQuery = useZones();

  const zonesParId = useMemo(() => {
    const map = new Map();
    for (const z of zonesQuery.data ?? []) map.set(z.zone_id, z);
    return map;
  }, [zonesQuery.data]);

  const zoneNom = (id) => zonesParId.get(id)?.nom ?? `#${id}`;

  // Fusion "Toute l'activité" — on prend la 1re page de chaque source.
  const tousEvenements = useMemo(() => {
    const liste = [];
    for (const m of missions.data ?? []) liste.push(versEvenement('missions', m, zoneNom));
    for (const m of mesures.data?.results ?? []) liste.push(versEvenement('mesures', m, zoneNom));
    for (const i of incidents.data?.results ?? []) liste.push(versEvenement('incidents', i, zoneNom));
    for (const i of irrigations.data?.results ?? []) liste.push(versEvenement('irrigation', i, zoneNom));
    return liste.filter(Boolean).sort((a, b) => new Date(b.date) - new Date(a.date));
  }, [missions.data, mesures.data, incidents.data, irrigations.data, zonesParId]);

  // Filtres locaux : recherche texte + zone (déjà appliquée côté serveur pour mesures/irrigations).
  const filtrer = (evts) =>
    evts.filter((e) => {
      if (!e) return false;
      const texte = `${e.titre} ${e.detail} ${e.source} ${e.resultat}`.toLowerCase();
      return texte.includes(recherche.toLowerCase());
    });

  const affiches = useMemo(() => {
    if (onglet === 'tout') return filtrer(tousEvenements);
    // Onglets unitaires : reconstruit depuis la source concernée.
    const source = {
      missions: (missions.data ?? []).map((m) => versEvenement('missions', m, zoneNom)),
      mesures: (mesures.data?.results ?? []).map((m) => versEvenement('mesures', m, zoneNom)),
      incidents: (incidents.data?.results ?? []).map((i) => versEvenement('incidents', i, zoneNom)),
      irrigation: (irrigations.data?.results ?? []).map((i) => versEvenement('irrigation', i, zoneNom)),
    }[onglet];
    return filtrer(source ?? []);
  }, [onglet, tousEvenements, missions.data, mesures.data, incidents.data, irrigations.data, recherche]);

  // État agrégé (chargement si au moins une source charge encore pour l'onglet actif).
  const sourcesActives = {
    tout: [missions, mesures, incidents, irrigations],
    missions: [missions],
    mesures: [mesures],
    incidents: [incidents],
    irrigation: [irrigations],
  }[onglet];
  const enChargement = sourcesActives.some((q) => q.isLoading);
  const erreur = sourcesActives.find((q) => q.isError)?.error;

  function exporterCsv() {
    const entetes = ['Date', 'Type', 'Événement', 'Détail', 'Source', 'Résultat'];
    const lignes = affiches.map((e) =>
      [formaterDateHeure(e.date), e.type, e.titre, e.detail, e.source, e.resultat]
        .map((v) => `"${String(v ?? '').replace(/"/g, '""')}"`)
        .join(';')
    );
    const contenu = '\uFEFF' + [entetes.join(';'), ...lignes].join('\n');
    const blob = new Blob([contenu], { type: 'text/csv;charset=utf-8;' });
    const lien = document.createElement('a');
    lien.href = URL.createObjectURL(blob);
    lien.download = `historique-${onglet}.csv`;
    lien.click();
  }

  return (
    <div>
      <div className="titre-ligne">
        <div>
          <h1>Historique d’activité</h1>
          <p className="sous-titre">Retrouvez chaque mission, mesure et intervention.</p>
        </div>
        <button className="bouton-principal" onClick={exporterCsv} disabled={affiches.length === 0}>
          Exporter en CSV
        </button>
      </div>

      <div className="onglets">
        {ONGLETS.map((o) => (
          <button
            key={o.cle}
            className={o.cle === onglet ? 'onglet actif' : 'onglet'}
            onClick={() => setOnglet(o.cle)}
          >
            {o.nom}
          </button>
        ))}
      </div>

      <div className="filtres">
        <input
          type="text"
          placeholder="Rechercher dans l’historique..."
          value={recherche}
          onChange={(e) => setRecherche(e.target.value)}
        />
        <select value={zoneFiltre} onChange={(e) => setZoneFiltre(e.target.value)}>
          <option>Toutes</option>
          {(zonesQuery.data ?? []).map((z) => (
            <option key={z.zone_id} value={z.zone_id}>
              {z.nom}
            </option>
          ))}
        </select>
      </div>

      {enChargement && <p>Chargement…</p>}
      {erreur && <p className="erreur">{erreur.message}</p>}
      {!enChargement && !erreur && affiches.length === 0 && (
        <p style={{ padding: '1rem', color: '#888' }}>Aucun événement ne correspond.</p>
      )}

      {!enChargement && !erreur && affiches.length > 0 && (
        <table className="tableau">
          <thead>
            <tr>
              <th>Date et heure</th>
              <th>Type</th>
              <th>Événement</th>
              <th>Source</th>
              <th>Résultat</th>
            </tr>
          </thead>
          <tbody>
            {affiches.map((e) => (
              <tr key={e.id}>
                <td>{formaterDateHeure(e.date)}</td>
                <td>{e.type}</td>
                <td>
                  <strong>{e.titre}</strong>
                  <small>{e.detail}</small>
                </td>
                <td>{e.source}</td>
                <td>{e.resultat}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {!enChargement && !erreur && (
        <p className="sous-titre">
          {affiches.length} événement(s) affiché(s)
          {onglet === 'tout' && ' — 1re page de chaque source'}
        </p>
      )}
    </div>
  );
}