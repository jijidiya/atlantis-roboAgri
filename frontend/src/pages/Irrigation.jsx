import { useState } from 'react';
import { useZones, useModifierSeuilsZones } from '../hooks/useZones';
import { useDecisionCourante } from '../hooks/useDecisions';
import { useCreerIrrigation, useIrrigations } from '../hooks/useIrrigations';
import { etatRequete } from '../hooks/etatRequete';

const TYPE_DECISION = {
  humidite_suffisante: { texte: 'Suffisante', classe: 'badge-vert' },
  humidite_insuffisante: { texte: 'À irriguer', classe: 'badge-orange' },
  mesure_invalide: { texte: 'Mesure invalide', classe: 'badge-rouge' },
};

function CarteZoneIrrigation({ zone, modification, onModifier }) {
  const decision = useDecisionCourante(zone.zone_id);
  const arrosage = useCreerIrrigation();
  const [duree, setDuree] = useState(20);

  const min = modification?.humidite_minimum ?? zone.humidite_minimum;
  const max = modification?.humidite_maximum ?? zone.humidite_maximum;

  const typeDec = decision.data?.type_decision;
  const badge = typeDec ? TYPE_DECISION[typeDec] : null;
  const aIrriguer = typeDec === 'humidite_insuffisante';
  const invalide = typeDec === 'mesure_invalide';

  const refus = arrosage.error?.statut === 403;

  const arroser = () => {
    arrosage.mutate({ zone: zone.zone_id, dureeSecondes: duree });
  };

  return (
    <div className="carte-mission">
      <div className="carte-mission-haut">
        <strong>
          {zone.nom}
          {zone.cultures?.length > 0 && ` · ${zone.cultures.map((c) => c.nom).join(', ')}`}
        </strong>
        {badge && <span className={`badge ${badge.classe}`}>{badge.texte}</span>}
      </div>

      <small className="etiquette">Humidité actuelle</small>
      <p className="stat-valeur">
        {decision.isLoading
          ? '…'
          : decision.data?.humidite_moyenne != null
          ? `${decision.data.humidite_moyenne} %`
          : '—'}
      </p>

      {decision.data?.justification && (
        <small className="etiquette">{decision.data.justification}</small>
      )}

      <div className="seuils">
        <label>
          <small className="etiquette">Seuil bas (%)</small>
          <input
            type="number"
            value={min}
            onChange={(e) =>
              onModifier(zone.zone_id, 'humidite_minimum', Number(e.target.value))
            }
          />
        </label>
        <label>
          <small className="etiquette">Seuil haut (%)</small>
          <input
            type="number"
            value={max}
            onChange={(e) =>
              onModifier(zone.zone_id, 'humidite_maximum', Number(e.target.value))
            }
          />
        </label>
      </div>

      <small className="etiquette">
        Recommandation dès {min} %, objectif {max} %
      </small>

      {aIrriguer && (
        <div className="actions">
          <label>
            Durée (s)
            <input
              type="number"
              min="1"
              value={duree}
              onChange={(e) => setDuree(Number(e.target.value))}
              disabled={arrosage.isPending}
            />
          </label>
          <button
            className="bouton-petit"
            onClick={arroser}
            disabled={arrosage.isPending || duree < 1}
          >
            {arrosage.isPending ? 'Envoi…' : 'Marquer comme arrosé'}
          </button>
        </div>
      )}

      {invalide && (
        <small className="texte-rouge">
          Aucune recommandation : mesure invalide, incident à signaler.
        </small>
      )}

      {refus && (
        <p className="erreur">
          Arrosage refusé : {arrosage.error.message}
          {arrosage.error.details?.validite && (
            <> (mesure : {arrosage.error.details.validite})</>
          )}
        </p>
      )}
      {arrosage.isError && !refus && (
        <p className="erreur">{arrosage.error.message}</p>
      )}
      {arrosage.isSuccess && <p className="succes">Arrosage enregistré.</p>}
    </div>
  );
}

export default function Irrigation() {
  const zones = useZones();
  const irrigations = useIrrigations();
  const enregistrerSeuils = useModifierSeuilsZones();

  const [modifications, setModifications] = useState({});
  const [message, setMessage] = useState('');

  const etat = etatRequete(zones);

  const modifier = (zoneId, champ, valeur) => {
    setMessage('');
    setModifications((prev) => {
      const zone = zones.data.find((z) => z.zone_id === zoneId);
      const base = prev[zoneId] ?? {
        humidite_minimum: zone.humidite_minimum,
        humidite_maximum: zone.humidite_maximum,
      };
      return { ...prev, [zoneId]: { ...base, [champ]: valeur } };
    });
  };

  const sauvegarder = () => {
    const entrees = Object.entries(modifications);
    if (entrees.length === 0) {
      setMessage('Aucune modification.');
      return;
    }

    // Validation locale : humidite_minimum < humidite_maximum
    for (const [id, patch] of entrees) {
      if (patch.humidite_minimum >= patch.humidite_maximum) {
        const zone = zones.data.find((z) => z.zone_id === Number(id));
        setMessage(
          `Erreur : dans ${zone?.nom ?? `la zone #${id}`}, le seuil bas doit être inférieur au seuil haut.`
        );
        return;
      }
    }

    enregistrerSeuils.mutate(modifications, {
      onSuccess: () => {
        setModifications({});
        setMessage('Seuils enregistrés.');
      },
      onError: (err) => setMessage(`Erreur : ${err.message}`),
    });
  };

  const zoneNom = (zoneId) =>
    zones.data?.find((z) => z.zone_id === zoneId)?.nom ?? `Zone #${zoneId}`;

  return (
    <div>
      <div className="titre-ligne">
        <div>
          <h1>Irrigation et seuils</h1>
          <p className="sous-titre">
            Ajustez les seuils de chaque zone pour une irrigation au plus juste.
          </p>
        </div>
        <button
          className="bouton-principal"
          onClick={sauvegarder}
          disabled={enregistrerSeuils.isPending}
        >
          {enregistrerSeuils.isPending ? 'Enregistrement…' : 'Enregistrer les seuils'}
        </button>
      </div>

      {message && <p className="message">{message}</p>}

      {etat === 'chargement' && <p>Chargement…</p>}
      {etat === 'erreur' && <p className="erreur">{zones.error.message}</p>}
      {etat === 'vide' && <p>Aucune zone.</p>}
      {etat === 'succes' && (
        <div className="grille-zones">
          {zones.data.map((z) => (
            <CarteZoneIrrigation
              key={z.zone_id}
              zone={z}
              modification={modifications[z.zone_id]}
              onModifier={modifier}
            />
          ))}
        </div>
      )}

      <h2>Historique d’irrigation</h2>
      {irrigations.isLoading && <p>Chargement…</p>}
      {irrigations.isError && (
        <p className="erreur">{irrigations.error.message}</p>
      )}
      {irrigations.data && (
        <table className="tableau">
          <thead>
            <tr>
              <th>Date et heure</th>
              <th>Zone</th>
              <th>Durée</th>
              <th>Volume</th>
              <th>Source</th>
              <th>Statut</th>
            </tr>
          </thead>
          <tbody>
            {irrigations.data.results.length === 0 && (
              <tr>
                <td colSpan="6">Aucune irrigation enregistrée.</td>
              </tr>
            )}
            {irrigations.data.results.map((i) => (
              <tr key={i.irrigation_id}>
                <td>
                  {i.date_debut
                    ? new Date(i.date_debut).toLocaleString('fr-FR')
                    : '—'}
                </td>
                <td>{zoneNom(i.zone)}</td>
                <td>{i.duree_secondes} s</td>
                <td>{i.volume_ml ?? '—'} ml</td>
                <td>{i.automatique ? 'Automatique' : 'Manuelle'}</td>
                <td>{i.statut}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}