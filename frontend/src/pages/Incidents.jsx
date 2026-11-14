import { useState, useMemo } from 'react';
import StatCard from '../components/StatCard';
import { useIncidents } from '../hooks/useIncidents';
import { useMissions } from '../hooks/useMissions';
import { etatRequete } from '../hooks/etatRequete';
import { formaterDateHeure } from '../utils/formatage';

const TYPES = [
  { cle: 'obstacle', label: 'Obstacle', classe: 'badge orange' },
  { cle: 'capteur_defaillant', label: 'Capteur défaillant', classe: 'badge rouge' },
  { cle: 'perte_communication', label: 'Perte de communication', classe: 'badge violet' },
  { cle: 'mesure_invalide', label: 'Mesure invalide', classe: 'badge bleu' },
];

const typeInfo = Object.fromEntries(TYPES.map((t) => [t.cle, t]));

export default function Incidents() {
  const [filtreType, setFiltreType] = useState(null);
  const [selectionId, setSelectionId] = useState(null);

  // Polling 10 s actif (page dédiée — la donnée peut changer à tout moment).
  const incidents = useIncidents(filtreType ? { type_incident: filtreType } : {});
  const missions = useMissions();

  const etat = etatRequete(incidents);

  const liste = incidents.data?.results ?? [];
  const total = incidents.data?.count ?? liste.length;

  const missionsParId = useMemo(() => {
    const map = new Map();
    for (const m of missions.data ?? []) map.set(m.mission_id, m);
    return map;
  }, [missions.data]);

  const selection = liste.find((i) => i.incident_id === selectionId);

  const compterType = (cle) => liste.filter((i) => i.type_incident === cle).length;

  return (
    <div>
      <h1>Incidents et alertes</h1>
      <p className="sous-titre">
        Consultez les incidents signalés par le robot et les capteurs.
      </p>

      <div className="cartes">
        <StatCard
          titre="Total"
          valeur={String(total).padStart(2, '0')}
          details="Toutes périodes"
        />
        <StatCard
          titre="Capteur"
          valeur={String(compterType('capteur_defaillant')).padStart(2, '0')}
          details="Capteur défaillant"
        />
        <StatCard
          titre="Communication"
          valeur={String(compterType('perte_communication')).padStart(2, '0')}
          details="Perte de signal"
        />
      </div>

      <div className="onglets">
        <button
          className={filtreType === null ? 'onglet actif' : 'onglet'}
          onClick={() => setFiltreType(null)}
        >
          Tous
        </button>
        {TYPES.map((t) => (
          <button
            key={t.cle}
            className={t.cle === filtreType ? 'onglet actif' : 'onglet'}
            onClick={() => setFiltreType(t.cle)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {etat === 'chargement' && <p>Chargement…</p>}
      {etat === 'erreur' && <p className="erreur">{incidents.error.message}</p>}
      {etat === 'vide' && (
        <p style={{ padding: '1rem', color: '#888' }}>Aucun incident.</p>
      )}
      {etat === 'succes' && (
        <div className="incidents-mise-en-page">
          <table className="tableau">
            <thead>
              <tr>
                <th>Incident</th>
                <th>Type</th>
                <th>Mission</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {liste.map((i) => {
                const info = typeInfo[i.type_incident] ?? {
                  label: i.type_incident,
                  classe: 'badge',
                };
                return (
                  <tr
                    key={i.incident_id}
                    className={
                      i.incident_id === selectionId ? 'ligne-selection' : 'ligne-cliquable'
                    }
                    onClick={() => setSelectionId(i.incident_id)}
                  >
                    <td>
                      <strong>INC-{String(i.incident_id).padStart(3, '0')}</strong>
                      <small>{i.mesures?.length ?? 0} mesure(s) liée(s)</small>
                    </td>
                    <td>
                      <span className={info.classe}>{info.label}</span>
                    </td>
                    <td>{i.mission ? `MIS-${i.mission}` : '—'}</td>
                    <td>{formaterDateHeure(i.date_incident)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {selection && (
            <div className="carte-mission panneau-detail">
              <strong>INC-{String(selection.incident_id).padStart(3, '0')}</strong>
              <small>{formaterDateHeure(selection.date_incident)}</small>
              <div className="badges-ligne">
                <span className={typeInfo[selection.type_incident]?.classe ?? 'badge'}>
                  {typeInfo[selection.type_incident]?.label ?? selection.type_incident}
                </span>
              </div>
              {selection.mission && (
                <p>Mission liée : MIS-{selection.mission}</p>
              )}
              <p>Mesures concernées : {selection.mesures?.length ?? 0}</p>
              <p style={{ color: '#888', fontSize: 13 }}>
                La gestion (acquitter / résoudre) n’est pas exposée par l’API actuelle.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}