import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMoi, useDeconnexion, useModifierProfil } from '../hooks/useAuth';
import { useZones, useModifierZone } from '../hooks/useZones';
import Toggle from '../components/Toggle';

const ONGLETS = ['Mon compte', 'Exploitation', 'Notifications'];

const libelleRole = {
  administrateur: 'Administrateur',
  proprietaire: 'Propriétaire',
};

const CLE_NOTIFS = 'roboagri.notifications';

function chargerNotifs() {
  try {
    const brut = localStorage.getItem(CLE_NOTIFS);
    return brut
      ? JSON.parse(brut)
      : { critiques: true, missions: true, irrigation: true };
  } catch {
    return { critiques: true, missions: true, irrigation: true };
  }
}

// --- Onglet Mon compte ------------------------------------------------

function OngletMonCompte() {
  const moi = useMoi();
  const modifier = useModifierProfil();
  const deconnexion = useDeconnexion();
  const navigate = useNavigate();

  const [prenom, setPrenom] = useState(moi.data?.prenom ?? '');
  const [nom, setNom] = useState(moi.data?.nom ?? '');
  const [email, setEmail] = useState(moi.data?.email ?? '');
  const [message, setMessage] = useState(null);

  const modifie =
    prenom !== moi.data?.prenom ||
    nom !== moi.data?.nom ||
    email !== moi.data?.email;

  const enregistrer = () => {
    setMessage(null);
    modifier.mutate(
      { prenom, nom, email },
      {
        onSuccess: () =>
          setMessage({ type: 'succes', texte: 'Modifications enregistrées.' }),
        onError: (err) => {
          const details =
            err.details && Object.entries(err.details).length > 0
              ? ' — ' +
                Object.entries(err.details)
                  .map(
                    ([k, v]) =>
                      `${k} : ${Array.isArray(v) ? v.join(', ') : v}`
                  )
                  .join(' · ')
              : '';
          setMessage({ type: 'erreur', texte: err.message + details });
        },
      }
    );
  };

  const seDeconnecter = () => {
    deconnexion();
    navigate('/connexion', { replace: true });
  };

  return (
    <div className="rangee-cartes">
      <div className="carte-mission">
        <strong>Profil personnel</strong>
        <div className="champs">
          <label>
            <small className="etiquette">Prénom</small>
            <input value={prenom} onChange={(e) => setPrenom(e.target.value)} />
          </label>
          <label>
            <small className="etiquette">Nom</small>
            <input value={nom} onChange={(e) => setNom(e.target.value)} />
          </label>
          <label>
            <small className="etiquette">Adresse e-mail</small>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>
          <label>
            <small className="etiquette">Rôle</small>
            <input
              value={libelleRole[moi.data?.role] ?? moi.data?.role}
              readOnly
              disabled
            />
          </label>
        </div>

        <button
          className="bouton-principal"
          onClick={enregistrer}
          disabled={!modifie || modifier.isPending}
        >
          {modifier.isPending ? 'Enregistrement…' : 'Enregistrer'}
        </button>

        {message && (
          <p
            style={{
              color: message.type === 'erreur' ? 'crimson' : 'green',
              marginTop: '0.75rem',
            }}
          >
            {message.texte}
          </p>
        )}
      </div>

      <div className="carte-mission">
        <strong>Sécurité</strong>
        <p style={{ color: '#888', fontSize: 14 }}>
          Changement de mot de passe : bientôt disponible (endpoint backend à créer).
        </p>

        <hr style={{ margin: '1rem 0' }} />

        <strong>Session</strong>
        <p style={{ color: '#888', fontSize: 14 }}>
          Vous êtes connecté en tant que {moi.data?.email}.
        </p>
        <button className="bouton" onClick={seDeconnecter}>
          Se déconnecter
        </button>
      </div>
    </div>
  );
}

// --- Onglet Exploitation -----------------------------------------------

function LigneZoneAuto({ zone }) {
  const modifier = useModifierZone(zone.zone_id);

  const basculer = (valeur) => {
    modifier.mutate({ irrigation_auto_active: valeur });
  };

  return (
    <tr>
      <td>
        <strong>{zone.nom}</strong>
      </td>
      <td>
        {zone.humidite_minimum} % – {zone.humidite_maximum} %
      </td>
      <td>
        <Toggle actif={zone.irrigation_auto_active} onChange={basculer} />
      </td>
      <td style={{ fontSize: 13, color: '#888' }}>
        {modifier.isError && `Erreur : ${modifier.error.message}`}
        {modifier.isSuccess && 'Enregistré.'}
      </td>
    </tr>
  );
}

function OngletExploitation() {
  const zones = useZones();

  if (zones.isLoading) return <p>Chargement…</p>;
  if (zones.isError) return <p className="erreur">{zones.error.message}</p>;
  if (!zones.data || zones.data.length === 0) {
    return <p>Aucune zone configurable.</p>;
  }

  return (
    <div className="carte-mission">
      <strong>Irrigation automatique par zone</strong>
      <p style={{ color: '#888', fontSize: 14, marginBottom: '1rem' }}>
        Quand l'irrigation automatique est active, une décision d'arrosage favorable
        déclenche l'intervention sans validation humaine.
      </p>
      <table className="tableau">
        <thead>
          <tr>
            <th>Zone</th>
            <th>Seuils</th>
            <th>Auto</th>
            <th>État</th>
          </tr>
        </thead>
        <tbody>
          {zones.data.map((z) => (
            <LigneZoneAuto key={z.zone_id} zone={z} />
          ))}
        </tbody>
      </table>
    </div>
  );
}

// --- Onglet Notifications ----------------------------------------------

function OngletNotifications() {
  const [notifs, setNotifs] = useState(chargerNotifs);

  const changer = (cle, valeur) => {
    const suivant = { ...notifs, [cle]: valeur };
    setNotifs(suivant);
    localStorage.setItem(CLE_NOTIFS, JSON.stringify(suivant));
  };

  return (
    <div className="carte-mission">
      <strong>Notifications</strong>
      <div className="ligne-option">
        <span>Alertes critiques</span>
        <Toggle
          actif={notifs.critiques}
          onChange={(v) => changer('critiques', v)}
        />
      </div>
      <div className="ligne-option">
        <span>Missions du robot</span>
        <Toggle
          actif={notifs.missions}
          onChange={(v) => changer('missions', v)}
        />
      </div>
      <div className="ligne-option">
        <span>Irrigation et seuils</span>
        <Toggle
          actif={notifs.irrigation}
          onChange={(v) => changer('irrigation', v)}
        />
      </div>
      <small className="etiquette">
        Préférences locales (navigateur). Pas encore synchronisées côté serveur.
      </small>
    </div>
  );
}

// --- Page -------------------------------------------------------------

export default function Parametres() {
  const [onglet, setOnglet] = useState('Mon compte');

  return (
    <div>
      <div className="titre-ligne">
        <div>
          <h1>Paramètres</h1>
          <p className="sous-titre">
            Gérez votre profil et l'irrigation automatique de vos zones.
          </p>
        </div>
      </div>

      <div className="onglets">
        {ONGLETS.map((o) => (
          <button
            key={o}
            className={o === onglet ? 'onglet actif' : 'onglet'}
            onClick={() => setOnglet(o)}
          >
            {o}
          </button>
        ))}
      </div>

      {onglet === 'Mon compte' && <OngletMonCompte />}
      {onglet === 'Exploitation' && <OngletExploitation />}
      {onglet === 'Notifications' && <OngletNotifications />}
    </div>
  );
}