import { useMemo } from 'react';
import { useMesures } from '../hooks/useMesures';
import { useZones } from '../hooks/useZones';
import { formaterDateHeure } from '../utils/formatage';

const COULEURS = ['#1f6b43', '#d98a1f', '#3b7fc4', '#a43bb8', '#c44a3b'];

function etatHumidite(humidite, zone) {
  if (humidite == null) return { texte: 'Sans donnée', classe: 'badge' };
  const min = Number(zone?.humidite_minimum ?? 0);
  const max = Number(zone?.humidite_maximum ?? 100);
  if (humidite < min) return { texte: 'Sol sec', classe: 'badge rouge' };
  if (humidite > max) return { texte: 'Trop humide', classe: 'badge orange' };
  return { texte: 'Optimal', classe: 'badge vert' };
}

function Courbe({ valeurs, couleur, largeur = 600, hauteur = 120 }) {
  if (!valeurs || valeurs.length < 2) return null;
  const min = Math.min(...valeurs);
  const max = Math.max(...valeurs);
  const etendue = Math.max(1, max - min);
  const points = valeurs
    .map((v, i) => {
      const x = (i * largeur) / (valeurs.length - 1);
      const y = hauteur - 10 - ((v - min) / etendue) * (hauteur - 20);
      return `${x},${y}`;
    })
    .join(' ');
  return (
    <polyline points={points} fill="none" stroke={couleur} strokeWidth="3" />
  );
}

export default function Capteurs() {
  // Polling 3 s : page de monitoring. Mets `polling: false` si tu trouves ça trop agressif.
  const mesures = useMesures({ statut: 'valide', polling: true });
  const zones = useZones();

  const zonesParId = useMemo(() => {
    const map = new Map();
    for (const z of zones.data ?? []) map.set(z.zone_id, z);
    return map;
  }, [zones.data]);

  const mesuresListe = mesures.data?.results ?? [];

  // Regroupe les mesures par zone.
  const parZone = useMemo(() => {
    const map = new Map();
    for (const m of mesuresListe) {
      if (!map.has(m.zone)) map.set(m.zone, []);
      map.get(m.zone).push(m);
    }
    return map;
  }, [mesuresListe]);

  // Dernière mesure par zone (pour les cartes de stats).
  const dernieres = useMemo(() => {
    const out = [];
    for (const [zoneId, mesuresZone] of parZone.entries()) {
      const zone = zonesParId.get(zoneId);
      if (!zone) continue; // ignore les zones d'autres comptes (defense en profondeur)
      const triees = [...mesuresZone].sort(
        (a, b) => new Date(b.date_heure_mesure) - new Date(a.date_heure_mesure)
      );
      out.push({ zone, mesure: triees[0] });
    }
    return out;
  }, [parZone, zonesParId]);

  // Séries pour les courbes : 20 derniers points par zone, ordre chronologique.
  const series = useMemo(() => {
    const resultat = [];
    let i = 0;
    for (const [zoneId, mesuresZone] of parZone.entries()) {
      const zone = zonesParId.get(zoneId);
      if (!zone) continue;
      const triees = [...mesuresZone]
        .sort((a, b) => new Date(a.date_heure_mesure) - new Date(b.date_heure_mesure))
        .slice(-20);
      const valeurs = triees
        .map((m) => Number(m.valeur_humidite))
        .filter(Number.isFinite);
      if (valeurs.length < 2) continue;
      resultat.push({
        zoneId,
        nom: zone.nom,
        couleur: COULEURS[i % COULEURS.length],
        valeurs,
      });
      i += 1;
    }
    return resultat;
  }, [parZone, zonesParId]);

  // Moyenne globale des mesures valides (toutes zones du compte).
  const moyHumidite = useMemo(() => {
    const vals = mesuresListe
      .filter((m) => zonesParId.has(m.zone))
      .map((m) => Number(m.valeur_humidite))
      .filter(Number.isFinite);
    if (vals.length === 0) return null;
    return Math.round((vals.reduce((s, v) => s + v, 0) / vals.length) * 10) / 10;
  }, [mesuresListe, zonesParId]);

  // 20 dernières mesures toutes zones confondues.
  const dernieresMesures = useMemo(() => {
    return [...mesuresListe]
      .filter((m) => zonesParId.has(m.zone))
      .sort((a, b) => new Date(b.date_heure_mesure) - new Date(a.date_heure_mesure))
      .slice(0, 20);
  }, [mesuresListe, zonesParId]);

  const actualiser = () => {
    mesures.refetch();
    zones.refetch();
  };

  const enChargement = mesures.isLoading || zones.isLoading;
  const erreur = mesures.error || zones.error;

  if (enChargement) {
    return <div className="carte">Chargement des capteurs…</div>;
  }
  if (erreur) {
    return (
      <div className="carte">
        <p style={{ color: 'crimson' }}>{erreur.message}</p>
        <button className="bouton" onClick={actualiser}>Réessayer</button>
      </div>
    );
  }

  return (
    <div>
      <div className="entete">
        <div>
          <h1>Capteurs et mesures</h1>
          <p className="sous-titre">
            Des mesures fiables pour comprendre l'état de vos sols.
          </p>
        </div>
        <button className="bouton" onClick={actualiser} disabled={mesures.isFetching}>
          {mesures.isFetching ? 'Actualisation…' : 'Actualiser'}
        </button>
      </div>

      <div className="stats">
        {dernieres.length === 0 && (
          <div className="carte">
            <p className="carte-titre">Aucune mesure</p>
            <p className="carte-valeur">—</p>
            <p className="carte-detail">Le robot n'a pas encore envoyé de mesure.</p>
          </div>
        )}
        {dernieres.map(({ zone, mesure }) => {
          const h = mesure.valeur_humidite != null ? Number(mesure.valeur_humidite) : null;
          const etat = etatHumidite(h, zone);
          return (
            <div className="carte" key={zone.zone_id}>
              <p className="carte-titre">Humidité · {zone.nom}</p>
              <p className="carte-valeur">
                {h != null ? `${h} %` : '—'}
              </p>
              <p className="carte-detail">
                <span className={etat.classe}>{etat.texte}</span>
              </p>
            </div>
          );
        })}
        <div className="carte">
          <p className="carte-titre">Humidité moyenne</p>
          <p className="carte-valeur">{moyHumidite != null ? `${moyHumidite} %` : '—'}</p>
          <p className="carte-detail">{mesuresListe.length} mesure(s) valide(s)</p>
        </div>
      </div>

      <div className="carte">
        <h2>Humidité du sol</h2>
        {series.length === 0 ? (
          <p style={{ color: '#888', padding: '1rem 0' }}>
            Pas encore assez de mesures valides pour tracer une courbe (2 minimum par zone).
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
        <h2>Derniers relevés</h2>
        {dernieresMesures.length === 0 ? (
          <p style={{ color: '#888', padding: '1rem 0' }}>Aucun relevé.</p>
        ) : (
          <table className="tableau">
            <thead>
              <tr>
                <th>Zone</th>
                <th>Point · lecture</th>
                <th>Humidité</th>
                <th>Valeur brute</th>
                <th>Statut</th>
                <th>Dernier relevé</th>
              </tr>
            </thead>
            <tbody>
              {dernieresMesures.map((m) => {
                const zone = zonesParId.get(m.zone);
                const h = m.valeur_humidite != null ? Number(m.valeur_humidite) : null;
                const etat = etatHumidite(h, zone);
                return (
                  <tr key={m.mesure_id}>
                    <td>{zone?.nom ?? `Zone #${m.zone}`}</td>
                    <td>
                      P{m.numero_point} · L{m.numero_lecture}
                    </td>
                    <td>{h != null ? `${h} %` : '—'}</td>
                    <td>{m.valeur_brute ?? '—'}</td>
                    <td>
                      <span className={etat.classe}>{etat.texte}</span>
                    </td>
                    <td>{formaterDateHeure(m.date_heure_mesure)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}