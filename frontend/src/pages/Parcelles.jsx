import { useState, useMemo } from 'react';
import { useParcelles } from '../hooks/useParcelles';
import { useMesuresRecentes } from '../hooks/useMesures';
import { etatRequete } from '../hooks/etatRequete';
import {
  formaterSuperficie,
  formaterPourcentage,
  humiditeParZone,
  etatZone,
} from '../utils/formatage';

export default function Parcelles() {
  const parcellesQuery = useParcelles();
  const mesuresQuery = useMesuresRecentes({ limit: 200 });
  const [recherche, setRecherche] = useState('');
  const [culture, setCulture] = useState('Toutes');

  const etat = etatRequete(parcellesQuery);

  // Liste plate de zones avec leur parcelle parente, prête pour le tableau.
  const zonesPlates = useMemo(() => {
    const liste = parcellesQuery.data ?? [];
    return liste.flatMap((p) =>
      (p.zones ?? []).map((z) => ({
        ...z,
        parcelleNom: p.nom,
        parcelleId: p.parcelle_id,
      }))
    );
  }, [parcellesQuery.data]);

  const humidites = useMemo(
    () => humiditeParZone(mesuresQuery.data ?? []),
    [mesuresQuery.data]
  );

  const toutesCultures = useMemo(() => {
    const set = new Set();
    for (const z of zonesPlates) {
      for (const c of z.cultures ?? []) set.add(c.nom);
    }
    return ['Toutes', ...set];
  }, [zonesPlates]);

  const visibles = zonesPlates.filter((z) => {
    const okNom = z.nom.toLowerCase().includes(recherche.toLowerCase())
      || z.parcelleNom.toLowerCase().includes(recherche.toLowerCase());
    const cultureZone = z.cultures?.[0]?.nom ?? null;
    const okCulture = culture === 'Toutes' || cultureZone === culture;
    return okNom && okCulture;
  });

  const nbParcelles = parcellesQuery.data?.length ?? 0;
  const totalSurface = (parcellesQuery.data ?? [])
    .reduce((s, p) => s + (Number(p.superficie) || 0), 0);
  const nbCultures = toutesCultures.length - 1;
  const nbASurveiller = zonesPlates.filter((z) => {
    const h = humidites.get(z.zone_id);
    if (h == null) return false;
    return h < Number(z.humidite_minimum) || h > Number(z.humidite_maximum);
  }).length;

  if (etat === 'chargement') {
    return <div className="carte">Chargement des parcelles…</div>;
  }

  if (etat === 'erreur') {
    return (
      <div className="carte">
        <p>Impossible de charger les parcelles.</p>
        <p style={{ color: 'crimson' }}>{parcellesQuery.error.message}</p>
        <button className="bouton" onClick={() => parcellesQuery.refetch()}>
          Réessayer
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="entete">
        <div>
          <h1>Gestion des parcelles</h1>
          <p className="sous-titre">
            Organisez vos cultures et gardez vos zones de surveillance à jour.
          </p>
        </div>
        <button className="bouton" disabled title="Création disponible au module suivant">
          + Ajouter une parcelle
        </button>
      </div>

      <div className="stats">
        <div className="carte">
          <p className="carte-titre">Superficie totale</p>
          <p className="carte-valeur">
            {(totalSurface / 10000).toFixed(1)} ha
          </p>
        </div>
        <div className="carte">
          <p className="carte-titre">Parcelles</p>
          <p className="carte-valeur">{String(nbParcelles).padStart(2, '0')}</p>
        </div>
        <div className="carte">
          <p className="carte-titre">Cultures suivies</p>
          <p className="carte-valeur">{String(nbCultures).padStart(2, '0')}</p>
        </div>
        <div className="carte">
          <p className="carte-titre">Zones à surveiller</p>
          <p className="carte-valeur">{String(nbASurveiller).padStart(2, '0')}</p>
        </div>
      </div>

      <div className="carte" style={{ marginBottom: 16 }}>
        <div className="barre-filtres">
          <input
            className="recherche"
            placeholder="Rechercher une zone ou une parcelle…"
            value={recherche}
            onChange={(e) => setRecherche(e.target.value)}
          />
          <select
            value={culture}
            onChange={(e) => setCulture(e.target.value)}
            className="select"
          >
            {toutesCultures.map((c) => <option key={c}>{c}</option>)}
          </select>
          <button
            className="onglet"
            onClick={() => { setRecherche(''); setCulture('Toutes'); }}
          >
            Réinitialiser
          </button>
        </div>

        {visibles.length === 0 ? (
          <p style={{ padding: '1rem', color: '#888' }}>Aucune zone ne correspond.</p>
        ) : (
          <table className="tableau">
            <thead>
              <tr>
                <th>Zone / Parcelle</th>
                <th>Culture</th>
                <th>Surface</th>
                <th>Humidité</th>
                <th>État</th>
              </tr>
            </thead>
            <tbody>
              {visibles.map((z) => {
                const h = humidites.get(z.zone_id);
                const etatZ = etatZone(h, z);
                return (
                  <tr key={z.zone_id}>
                    <td>
                      <strong>{z.nom}</strong>
                      <div style={{ fontSize: 12, color: '#888' }}>
                        {z.parcelleNom}
                      </div>
                    </td>
                    <td>
                      {z.cultures?.length ? z.cultures.map((c) => c.nom).join(', ') : '—'}
                    </td>
                    <td>{formaterSuperficie(z.superficie)}</td>
                    <td>{formaterPourcentage(h)}</td>
                    <td><span className={etatZ.classe}>{etatZ.label}</span></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      <div className="carte">
        <h2>Répartition des surfaces</h2>
        {(parcellesQuery.data ?? []).map((p) => {
          const surface = Number(p.superficie) || 0;
          const pct = totalSurface > 0 ? (surface / totalSurface) * 100 : 0;
          return (
            <div key={p.parcelle_id} className="repartition">
              <span>{p.nom}</span>
              <div className="barre">
                <div className="barre-remplie" style={{ width: `${pct}%` }} />
              </div>
              <strong>{Math.round(pct)} %</strong>
            </div>
          );
        })}
      </div>
    </div>
  );
}