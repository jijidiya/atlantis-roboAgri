import { useMemo } from 'react';
import StatCard from '../components/StatCard';
import StatusBadge from '../components/StatusBadge';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/http';
import { useMissions } from '../hooks/useMissions';
import { useZones } from '../hooks/useZones';
import { useDecisions } from '../hooks/useDecisions';
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine,
} from 'recharts';

const COULEURS = ['#166534', '#b45309', '#6aa583', '#3b7fc4', '#a43b3b'];
const JOURS = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'];

function ilYA7Jours() {
  const d = new Date();
  d.setDate(d.getDate() - 7);
  return d;
}

export default function Rapports() {
  const dateLimite = useMemo(ilYA7Jours, []);
  const dateLimiteISO = dateLimite.toISOString();

  // 1) Mesures valides des 7 derniers jours (page_size large pour agréger).
  const mesures = useQuery({
    queryKey: ['rapports', 'mesures', dateLimiteISO],
    queryFn: () =>
      api.get(`/mesures/?statut=valide&du=${dateLimiteISO}&page_size=1000`),
  });

  // 2) Décisions recommandées des 7 derniers jours.
  const decisions = useDecisions({ statut: 'recommandee' });

  // 3) Missions (toutes) — filtrées par date côté client.
  const missions = useMissions();

  // 4) Zones du compte.
  const zones = useZones();

  const zonesParId = useMemo(() => {
    const map = new Map();
    for (const z of zones.data ?? []) map.set(z.zone_id, z);
    return map;
  }, [zones.data]);

  const mesuresListe = mesures.data?.results ?? [];
  const decisionsListe = decisions.data?.results ?? [];
  const missionsListe = missions.data ?? [];

  // --- Agrégat 1 : activité des missions sur 7 jours (par jour) ---------

  const activite = useMemo(() => {
    const parDate = new Map();
    for (const m of missionsListe) {
      const d = new Date(m.date_creation);
      if (d < dateLimite) continue;
      const cle = d.toISOString().slice(0, 10);
      if (!parDate.has(cle)) {
        parDate.set(cle, {
          jour: `${JOURS[d.getDay()]} ${String(d.getDate()).padStart(2, '0')}`,
          terminees: 0,
          autres: 0,
        });
      }
      const bucket = parDate.get(cle);
      if (m.statut === 'terminee') bucket.terminees += 1;
      else bucket.autres += 1;
    }
    return [...parDate.values()];
  }, [missionsListe, dateLimite]);

  // --- Agrégat 2 : humidité moyenne par heure et par zone ---------------

  const { dataHumidite, zonesPourGraph } = useMemo(() => {
    // Prépare la liste des zones qui ont au moins 1 mesure.
    const zonesAvecMesures = new Set(mesuresListe.map((m) => m.zone));
    const zonesPourGraph = [...zonesAvecMesures].slice(0, 5).map((zoneId, i) => ({
      zone_id: zoneId,
      nom: zonesParId.get(zoneId)?.nom ?? `Zone #${zoneId}`,
      couleur: COULEURS[i % COULEURS.length],
    }));

    // Groupe par heure : { '06:00': { zone_1: [42, 44], zone_2: [38] } }
    const parHeure = new Map();
    for (const m of mesuresListe) {
      const d = new Date(m.date_heure_mesure);
      const heure = `${String(d.getHours()).padStart(2, '0')}:00`;
      if (!parHeure.has(heure)) parHeure.set(heure, { heure });
      const bucket = parHeure.get(heure);
      if (!bucket[m.zone]) bucket[m.zone] = [];
      bucket[m.zone].push(Number(m.valeur_humidite));
    }

    // Moyenne par zone pour chaque heure.
    const dataHumidite = [...parHeure.values()]
      .sort((a, b) => a.heure.localeCompare(b.heure))
      .map((bucket) => {
        const ligne = { heure: bucket.heure };
        for (const z of zonesPourGraph) {
          const valeurs = bucket[z.zone_id];
          if (valeurs && valeurs.length > 0) {
            ligne[z.zone_id] =
              Math.round((valeurs.reduce((s, v) => s + v, 0) / valeurs.length) * 10) / 10;
          }
        }
        return ligne;
      });

    return { dataHumidite, zonesPourGraph };
  }, [mesuresListe, zonesParId]);

  // --- Agrégat 3 : stats globales ---------------------------------------

  const stats = useMemo(() => {
    const totalMissions = missionsListe.filter((m) => new Date(m.date_creation) >= dateLimite).length;
    const terminees = missionsListe.filter(
      (m) => new Date(m.date_creation) >= dateLimite && m.statut === 'terminee'
    ).length;
    const taux = totalMissions > 0 ? Math.round((terminees / totalMissions) * 100) : 0;

    const humidites = mesuresListe.map((m) => Number(m.valeur_humidite)).filter(Number.isFinite);
    const moyenneHumidite =
      humidites.length > 0
        ? (humidites.reduce((s, v) => s + v, 0) / humidites.length).toFixed(1)
        : '—';

    const totalRecos = decisionsListe.filter(
      (d) => new Date(d.date_decision) >= dateLimite
    ).length;

    return { totalMissions, terminees, taux, moyenneHumidite, totalRecos };
  }, [missionsListe, mesuresListe, decisionsListe, dateLimite]);

  // --- Agrégat 4 : comparaison par zone ---------------------------------

  const comparaison = useMemo(() => {
    return (zones.data ?? []).map((zone) => {
      const mesuresZone = mesuresListe.filter((m) => m.zone === zone.zone_id);
      const humidites = mesuresZone.map((m) => Number(m.valeur_humidite)).filter(Number.isFinite);
      const humiditeMoy =
        humidites.length > 0
          ? Math.round((humidites.reduce((s, v) => s + v, 0) / humidites.length) * 10) / 10
          : null;

      const recos = decisionsListe.filter(
        (d) => d.zone === zone.zone_id && new Date(d.date_decision) >= dateLimite
      ).length;

      const nbMissions = missionsListe.filter((m) =>
        (m.etapes ?? []).some((e) => e.zone === zone.zone_id)
      ).length;

      // État : comparé aux seuils de la zone.
      let etat = 'Stable';
      if (humiditeMoy == null) {
        etat = 'Sans donnée';
      } else if (humiditeMoy < Number(zone.humidite_minimum)) {
        etat = 'Sol sec';
      } else if (humiditeMoy > Number(zone.humidite_maximum)) {
        etat = 'Excès d’eau';
      }

      return {
        zone: zone.nom,
        humidite: humiditeMoy,
        recommandations: recos,
        missions: nbMissions,
        etat,
      };
    });
  }, [zones.data, mesuresListe, decisionsListe, missionsListe, dateLimite]);

  // --- États de chargement / erreur ------------------------------------

  const enChargement =
    mesures.isLoading || decisions.isLoading || missions.isLoading || zones.isLoading;
  const erreur =
    mesures.error || decisions.error || missions.error || zones.error;

  if (enChargement) {
    return <div className="carte">Chargement des rapports…</div>;
  }
  if (erreur) {
    return (
      <div className="carte">
        <p style={{ color: 'crimson' }}>{erreur.message}</p>
      </div>
    );
  }

  return (
    <div>
      <div className="titre-ligne">
        <div>
          <h1>Rapports et statistiques</h1>
          <p className="sous-titre">
            Transformez les données du terrain en décisions éclairées.
          </p>
        </div>
        <button className="bouton-principal" onClick={() => window.print()}>
          Générer un rapport
        </button>
      </div>

      <div className="cartes">
        <StatCard
          titre="Missions de la semaine"
          valeur={String(stats.totalMissions)}
          details="7 derniers jours"
        />
        <StatCard
          titre="Taux d’achèvement"
          valeur={`${stats.taux} %`}
          details={`${stats.terminees} missions terminées sur ${stats.totalMissions}`}
        />
        <StatCard
          titre="Humidité moyenne"
          valeur={`${stats.moyenneHumidite} %`}
          details="Mesures valides · 7 jours"
        />
        <StatCard
          titre="Recommandations d’arrosage"
          valeur={String(stats.totalRecos)}
          details="Sur 7 jours"
        />
      </div>

      <div className="rangee-graphiques">
        <div className="carte-mission">
          <strong>Activité des missions</strong>
          {activite.length === 0 ? (
            <p style={{ color: '#888', padding: '1rem 0' }}>Aucune mission sur la période.</p>
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={activite}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="jour" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Bar dataKey="terminees" name="Terminées" stackId="a" fill="#166534" />
                <Bar dataKey="autres" name="Autres statuts" stackId="a" fill="#d6a85c" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="carte-mission">
          <strong>Humidité par zone</strong>
          {dataHumidite.length === 0 ? (
            <p style={{ color: '#888', padding: '1rem 0' }}>
              Pas assez de mesures valides sur la période.
            </p>
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={dataHumidite}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="heure" />
                <YAxis domain={[0, 100]} unit=" %" />
                <Tooltip />
                <Legend />
                <ReferenceLine y={30} stroke="#c2410c" strokeDasharray="5 5" label="Seuil bas" />
                {zonesPourGraph.map((z) => (
                  <Line
                    key={z.zone_id}
                    type="monotone"
                    dataKey={String(z.zone_id)}
                    name={z.nom}
                    stroke={z.couleur}
                    dot={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <h2>Comparaison des zones</h2>
      {comparaison.length === 0 ? (
        <p style={{ padding: '1rem', color: '#888' }}>Aucune zone.</p>
      ) : (
        <table className="tableau">
          <thead>
            <tr>
              <th>Zone</th>
              <th>Humidité</th>
              <th>Recommandations · 7 j</th>
              <th>Missions</th>
              <th>État</th>
            </tr>
          </thead>
          <tbody>
            {comparaison.map((z) => (
              <tr key={z.zone}>
                <td>{z.zone}</td>
                <td>{z.humidite != null ? `${z.humidite} %` : '—'}</td>
                <td>{z.recommandations}</td>
                <td>{z.missions}</td>
                <td><StatusBadge statut={z.etat} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}