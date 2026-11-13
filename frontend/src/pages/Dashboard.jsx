import { useMemo } from 'react';
import { useMoi } from '../hooks/useAuth';
import { useParcelles } from '../hooks/useParcelles';
import { useMissions } from '../hooks/useMissions';
import { useIncidents } from '../hooks/useIncidents';
import { useMesuresRecentes } from '../hooks/useMesures';
import { etatRequete } from '../hooks/etatRequete';
import { formaterHeure, formaterDateHeure } from '../utils/formatage';

const classeStatut = {
  planifiee: 'badge violet',
  en_cours: 'badge bleu',
  terminee: 'badge vert',
  interrompue: 'badge rouge',
  non_confirmee: 'badge',
};

const labelStatut = {
  planifiee: 'Planifiée',
  en_cours: 'En cours',
  terminee: 'Terminée',
  interrompue: 'Interrompue',
  non_confirmee: 'Non confirmée',
};

const labelIncident = {
  obstacle: 'Obstacle',
  capteur_defaillant: 'Capteur défaillant',
  perte_communication: 'Perte de communication',
  mesure_invalide: 'Mesure invalide',
};

function Courbe({ valeurs, couleur, largeur = 600, hauteur = 120 }) {
  if (!valeurs || valeurs.length < 2) return null;
  const min = Math.min(...valeurs);
  const max = Math.max(...valeurs);
  const etendue = Math.max(1, max - min);
  const points = valeurs
    .map((v, i) => {
      const x = (i * largeur) / (valeurs.length - 1);
      // Normalise dans [10, hauteur-10] pour ne pas coller aux bords.
      const y = hauteur - 10 - ((v - min) / etendue) * (hauteur - 20);
      return `${x},${y}`;
    })
    .join(' ');
  return (
    <polyline points={points} fill="none" stroke={couleur} strokeWidth="3" />
  );
}

const COULEURS = ['#1f6b43', '#d98a1f', '#3b7fc4', '#a43bb8', '#c44a3b'];

export default function Dashboard() {
  const moi = useMoi();
  const parcelles = useParcelles();
  const missions = useMissions();
  const incidents = useIncidents();
  // CORRECTION 1 : le hook attend `limite`, pas `limit`.
  const mesures = useMesuresRecentes({ limite: 200 });

  const zoneParId = useMemo(() => {
    const map = new Map();
    for (const p of parcelles.data ?? []) {
      for (const z of p.zones ?? []) map.set(z.zone_id, z);
    }
    return map;
  }, [parcelles.data]);

  // Séries d'humidité : on groupe les mesures valides par zone, limitées à 20 points.
  const series = useMemo(() => {
    // CORRECTION 2 : /mesures/ est paginé -> { count, results }.
    const liste = mesures.data?.results ?? [];
    const parZone = new Map();
    for (const m of liste) {
      if (m.statut !== 'valide' || m.valeur_humidite == null) continue;
      if (!parZone.has(m.zone)) parZone.set(m.zone, []);
      parZone.get(m.zone).push(Number(m.valeur_humidite));
    }
    const resultat = [];
    let i = 0;
    for (const [zoneId, valeurs] of parZone.entries()) {
      const zone = zoneParId.get(zoneId);
      if (!zone || valeurs.length < 3) continue;
      resultat.push({
        zoneId,
        nom: zone.nom,
        couleur: COULEURS[i % COULEURS.length],
        valeurs: valeurs.slice(0, 20).reverse(), // ordre chronologique
      });
      i += 1;
      if (resultat.length >= 5) break;
    }
    return resultat;
  }, [mesures.data, zoneParId]);

  // Missions triées par date de création desc.
  const missionsRecentes = useMemo(() => {
    const liste = Array.isArray(missions.data) ? missions.data : [];
    return [...liste]
      .sort((a, b) => new Date(b.date_creation) - new Date(a.date_creation))
      .slice(0, 5);
  }, [missions.data]);

  // Incidents récents.
  const incidentsRecents = useMemo(() => {
    const liste = Array.isArray(incidents.data)
      ? incidents.data
      : incidents.data?.results ?? [];
    return [...liste]
      .sort((a, b) => new Date(b.date_incident) - new Date(a.date_incident))
      .slice(0, 3);
  }, [incidents.data]);

  const statsMissions = useMemo(() => {
    const liste = Array.isArray(missions.data) ? missions.data : [];
    const enCours = liste.filter((m) => m.statut === 'en_cours').length;
    const planifiees = liste.filter((m) => m.statut === 'planifiee').length;
    return { enCours, planifiees };
  }, [missions.data]);

  const etatGlobal = etatRequete(parcelles);
  if (etatGlobal === 'chargement') {
    return <div className="carte">Chargement du tableau de bord…</div>;
  }
  if (etatGlobal === 'erreur') {
    return (
      <div className="carte">
        <p style={{ color: 'crimson' }}>{parcelles.error.message}</p>
        <button className="bouton" onClick={() => parcelles.refetch()}>
          Réessayer
        </button>
      </div>
    );
  }

  const dateAujourdhui = new Date().toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  const stats = [
    {
      titre: 'État du robot',
      valeur: 'En attente',
      detail: 'API robot non branchée',
    },
    {
      titre: 'Missions du jour',
      valeur: String(missionsRecentes.length).padStart(2, '0'),
      detail: `${statsMissions.enCours} en cours · ${statsMissions.planifiees} planifiée(s)`,
    },
    {
      titre: 'Incidents ouverts',
      valeur: String(incidentsRecents.length).padStart(2, '0'),
      detail: 'voir page Incidents',
    },
    {
      titre: 'Parcelles',
      valeur: String(parcelles.data?.length ?? 0).padStart(2, '0'),
      detail: 'voir page Parcelles',
    },
  ];

  return (
    <div>
      <div className="entete">
        <div>
          <h1>Tableau de bord</h1>
          <p className="sous-titre">
            Bonjour {moi.data?.prenom ?? ''}, voici l'essentiel de votre exploitation aujourd'hui.
          </p>
        </div>
        <span className="date">{dateAujourdhui}</span>
      </div>

      <div className="stats">
        {stats.map((s) => (
          <div className="carte" key={s.titre}>
            <p className="carte-titre">{s.titre}</p>
            <p className="carte-valeur">{s.valeur}</p>
            <p className="carte-detail">{s.detail}</p>
          </div>
        ))}
      </div>

      <div className="grille-2">
        <div className="carte">
          <h2>Évolution de l'humidité du sol</h2>
          {series.length === 0 ? (
            <p style={{ color: '#888', padding: '1rem 0' }}>
              Pas encore assez de mesures valides pour tracer une courbe.
            </p>
          ) : (
            <>
              <svg viewBox="0 0 600 120" className="courbe">
                {series.map((s) => (
                  <Courbe key={s.zoneId} valeurs={s.valeurs} couleur={s.couleur} />
                ))}
              </svg>
              <div className="legende">
                {series.map((s) => (
                  <span key={s.zoneId}>
                    <i style={{ background: s.couleur }} /> {s.nom}
                  </span>
                ))}
              </div>
            </>
          )}
        </div>

        <div className="carte">
          <h2>À votre attention</h2>
          {incidentsRecents.length === 0 && (
            <p style={{ color: '#888' }}>Aucun incident récent.</p>
          )}
          {incidentsRecents.map((i) => (
            <div className="alerte critique" key={i.incident_id}>
              <strong>
                {labelIncident[i.type_incident] ?? i.type_incident}
              </strong>
              <p>
                {formaterDateHeure(i.date_incident)}
                {i.mission && ` · mission #${i.mission}`}
              </p>
            </div>
          ))}
        </div>
      </div>

      <div className="carte">
        <h2>Missions récentes</h2>
        {missionsRecentes.length === 0 ? (
          <p style={{ color: '#888' }}>Aucune mission enregistrée.</p>
        ) : (
          <table className="tableau">
            <thead>
              <tr>
                <th>Mission</th>
                <th>Parcelle</th>
                <th>Heure</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              {missionsRecentes.map((m) => (
                <tr key={m.mission_id}>
                  <td>Mission #{m.mission_id}</td>
                  <td>{m.parcelle}</td>
                  <td>{formaterHeure(m.date_creation)}</td>
                  <td>
                    <span className={classeStatut[m.statut] ?? 'badge'}>
                      {labelStatut[m.statut] ?? m.statut}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}