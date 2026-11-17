import { useState } from 'react';
import StatusBadge from '../components/StatusBadge';
import { useParcelles } from '../hooks/useParcelles';
import { useZones } from '../hooks/useZones';
import {
  useMissions,
  useCreerMission,
  useDemarrerMission,
  useInterrompreMission,
  useTerminerMission,
} from '../hooks/useMissions';
import { etatRequete } from '../hooks/etatRequete';

const LIBELLES_STATUT = {
  planifiee: 'Planifiée',
  en_cours: 'En cours',
  terminee: 'Terminée',
  interrompue: 'Interrompue',
  non_confirmee: 'Non confirmée',
};

const ONGLETS = [
  { nom: 'Toutes', statuts: null },
  { nom: 'En cours', statuts: ['en_cours'] },
  { nom: 'Planifiées', statuts: ['planifiee'] },
  { nom: 'Terminées', statuts: ['terminee'] },
  { nom: 'À vérifier', statuts: ['interrompue', 'non_confirmee'] },
];

function progression(mission) {
  const total = mission.etapes.length;
  const faits = mission.etapes.filter((e) => e.statut === 'terminee').length;
  return { faits, total, pct: total ? Math.round((faits / total) * 100) : 0 };
}

function formatDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('fr-FR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

// --- Ligne du tableau, avec ses propres boutons d'action ---------------

function LigneMission({ mission, nomParcelle }) {
  const demarrer = useDemarrerMission(mission.mission_id);
  const interrompre = useInterrompreMission(mission.mission_id);
  const terminer = useTerminerMission(mission.mission_id);
  const enAction = demarrer.isPending || interrompre.isPending || terminer.isPending;

  const { faits, total, pct } = progression(mission);

  const actions =
    mission.statut === 'planifiee' ? (
      <button className="bouton-petit" onClick={() => demarrer.mutate()} disabled={enAction}>
        Démarrer
      </button>
    ) : mission.statut === 'en_cours' ? (
      <>
        <button className="bouton-petit" onClick={() => terminer.mutate()} disabled={enAction}>
          Terminer
        </button>
        <button className="bouton-petit" onClick={() => interrompre.mutate()} disabled={enAction}>
          Interrompre
        </button>
      </>
    ) : (
      <span className="badge">—</span>
    );

  return (
    <tr>
      <td>
        <strong>Relevé d’humidité</strong>
        <small>MIS-{mission.mission_id}</small>
      </td>
      <td>{nomParcelle}</td>
      <td>{formatDate(mission.date_debut ?? mission.date_creation)}</td>
      <td>{pct} % · {faits} / {total} étapes</td>
      <td><StatusBadge statut={LIBELLES_STATUT[mission.statut] ?? mission.statut} /></td>
      <td>{actions}</td>
    </tr>
  );
}

// --- Page --------------------------------------------------------------

export default function Missions() {
  const missions = useMissions();
  const parcelles = useParcelles();

  const [ongletActif, setOngletActif] = useState('Toutes');
  const [parcelleId, setParcelleId] = useState('');
  const [zonesChoisies, setZonesChoisies] = useState([]);

  const zones = useZones(parcelleId ? { parcelle: parcelleId } : {});
  const creation = useCreerMission();
  const etat = etatRequete(missions);

  // Résolution des noms de parcelles (pour éviter les IDs dans le tableau)
  const nomsParcelles = Object.fromEntries(
    (parcelles.data ?? []).map((p) => [p.parcelle_id, p.nom])
  );

  const onglet = ONGLETS.find((o) => o.nom === ongletActif);
  const missionsListe = missions.data ?? [];
  const missionsAffichees = onglet.statuts
    ? missionsListe.filter((m) => onglet.statuts.includes(m.statut))
    : missionsListe;

  const compter = (o) =>
    o.statuts ? missionsListe.filter((m) => o.statuts.includes(m.statut)).length : missionsListe.length;

  const missionEnCours = missionsListe.find((m) => m.statut === 'en_cours');

  const cocherZone = (id) =>
    setZonesChoisies((prev) =>
      prev.includes(id) ? prev.filter((z) => z !== id) : [...prev, id]
    );

  const planifier = () => {
    if (!parcelleId || zonesChoisies.length === 0) return;
    creation.mutate(
      {
        parcelle: Number(parcelleId),
        utilisateur: null,
        etapes: zonesChoisies.map((zoneId, i) => ({
          numero_ordre: i + 1,
          zone: zoneId,
        })),
      },
      {
        onSuccess: () => {
          setZonesChoisies([]);
        },
      }
    );
  };

  return (
    <div>
      <h1>Missions</h1>
      <p className="sous-titre">Planifiez les interventions du robot et suivez leur avancement.</p>

      {/* Carte de la mission en cours */}
      <div className="carte-mission">
        {missionEnCours ? (
          <>
            <div className="carte-mission-haut">
              <div>
                <strong>
                  Relevé d’humidité · {nomsParcelles[missionEnCours.parcelle] ?? '—'}
                </strong>
                <small>
                  MIS-{missionEnCours.mission_id} ·{' '}
                  {progression(missionEnCours).faits} / {progression(missionEnCours).total} étapes
                </small>
              </div>
              <span className="gros-pourcentage">
                {progression(missionEnCours).pct} %
              </span>
            </div>
            <div className="barre">
              <div
                className="barre-remplie"
                style={{ width: `${progression(missionEnCours).pct}%` }}
              />
            </div>
          </>
        ) : (
          <p>Aucune mission en cours.</p>
        )}
      </div>

      {/* Formulaire de planification */}
      <div className="carte-mission">
        <strong>Planification rapide</strong>
        <div className="formulaire-ligne">
          <select
            value={parcelleId}
            onChange={(e) => {
              setParcelleId(e.target.value);
              setZonesChoisies([]);
            }}
          >
            <option value="">— Parcelle —</option>
            {(parcelles.data ?? []).map((p) => (
              <option key={p.parcelle_id} value={p.parcelle_id}>
                {p.nom}
              </option>
            ))}
          </select>

          {parcelleId && (
            <div className="zones-champ">
              {(zones.data ?? []).length === 0 && <small>Aucune zone.</small>}
              {(zones.data ?? []).map((z) => (
                <label key={z.zone_id} className="case-zone">
                  <input
                    type="checkbox"
                    checked={zonesChoisies.includes(z.zone_id)}
                    onChange={() => cocherZone(z.zone_id)}
                  />
                  {z.nom}
                </label>
              ))}
            </div>
          )}

          <button
            className="bouton-principal"
            onClick={planifier}
            disabled={creation.isPending || !parcelleId || zonesChoisies.length === 0}
          >
            {creation.isPending ? 'Création…' : 'Planifier'}
          </button>
        </div>

        {creation.isError && (
          <p className="erreur">
            {creation.error.message}
            {creation.error.details &&
              Object.entries(creation.error.details).map(([k, v]) => (
                <span key={k}> — {k} : {Array.isArray(v) ? v.join(', ') : String(v)}</span>
              ))}
          </p>
        )}
      </div>

      {/* Onglets */}
      <div className="onglets">
        {ONGLETS.map((o) => (
          <button
            key={o.nom}
            className={o.nom === ongletActif ? 'onglet actif' : 'onglet'}
            onClick={() => setOngletActif(o.nom)}
          >
            {o.nom} ({compter(o)})
          </button>
        ))}
      </div>

      {/* Tableau */}
      {etat === 'chargement' && <p>Chargement…</p>}
      {etat === 'erreur' && <p className="erreur">{missions.error.message}</p>}
      {etat === 'vide' && <p>Aucune mission.</p>}
      {etat === 'succes' && (
        <table className="tableau">
          <thead>
            <tr>
              <th>Mission</th>
              <th>Parcelle</th>
              <th>Départ prévu</th>
              <th>Progression</th>
              <th>Statut</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {missionsAffichees.map((m) => (
              <LigneMission
                key={m.mission_id}
                mission={m}
                nomParcelle={nomsParcelles[m.parcelle] ?? `Parcelle #${m.parcelle}`}
              />
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}