import { useState } from 'react'
import StatusBadge from '../components/StatusBadge'
import EtatVide from '../components/EtatVide'
import { adapterMission } from '../api/adaptateurs'
import {
  useMissions, useParcelles, useZones, useCreerMission, useChangerEtat,
} from '../hooks/useMissions'

const onglets = [
  { nom: 'Toutes', codes: null },
  { nom: 'En cours', codes: ['en_cours'] },
  { nom: 'Planifiées', codes: ['planifiee'] },
  { nom: 'Terminées', codes: ['terminee'] },
  { nom: 'À vérifier', codes: ['interrompue', 'non_confirmee'] },
]

// Actions possibles selon le statut (même logique que le backend)
const actions = {
  planifiee: [{ action: 'demarrer', texte: 'Démarrer' }],
  en_cours: [
    { action: 'terminer', texte: 'Terminer' },
    { action: 'interrompre', texte: 'Interrompre' },
  ],
}

const idDe = (o, cle) => o[cle] ?? o.id

function Missions() {
  const { data, isLoading, isError, error } = useMissions()
  const parcelles = useParcelles()
  const [ongletActif, setOngletActif] = useState('Toutes')
  const [parcelleId, setParcelleId] = useState('')
  const [zonesChoisies, setZonesChoisies] = useState([])
  const [message, setMessage] = useState('')

  const zones = useZones(parcelleId)
  const creer = useCreerMission()
  const changer = useChangerEtat()

  if (isLoading) return <EtatVide type="chargement" />
  if (isError) return <EtatVide type="erreur" message={error.message} />

  const missions = data.map((m) => ({ ...adapterMission(m), brut: m }))
  const onglet = onglets.find((o) => o.nom === ongletActif)
  const affichees = onglet.codes
    ? missions.filter((m) => onglet.codes.includes(m.code))
    : missions
  const compter = (o) =>
    o.codes ? missions.filter((m) => o.codes.includes(m.code)).length : missions.length
  const enCours = missions.find((m) => m.code === 'en_cours')
  const pct = (m) => (m.total ? Math.round((m.faits / m.total) * 100) : 0)

  function basculerZone(id) {
    setZonesChoisies(
      zonesChoisies.includes(id) ? zonesChoisies.filter((z) => z !== id) : [...zonesChoisies, id],
    )
  }

  function planifier() {
    setMessage('')
    creer.mutate(
      {
        utilisateur: 1, // provisoire : l'API est ouverte, l'authentification viendra plus tard
        parcelle: Number(parcelleId),
        etapes: zonesChoisies.map((z, i) => ({ numero_ordre: i + 1, zone: z })),
      },
      {
        onSuccess: () => {
          setZonesChoisies([])
          setMessage('Mission planifiée.')
        },
        onError: (e) => setMessage(`Erreur : ${e.message}`),
      },
    )
  }

  const peutPlanifier = parcelleId && zonesChoisies.length > 0 && !creer.isPending

  return (
    <div>
      <h1>Missions</h1>
      <p className="sous-titre">Planifiez les interventions du robot et suivez leur avancement.</p>

      <div className="rangee-cartes">
        <div className="carte-mission">
          {enCours ? (
            <>
              <div className="carte-mission-haut">
                <div>
                  <strong>{enCours.titre} · Parcelle {enCours.parcelle}</strong>
                  <small>{enCours.faits} / {enCours.total} étapes</small>
                </div>
                <span className="gros-pourcentage">{pct(enCours)} %</span>
              </div>
              <div className="barre">
                <div className="barre-remplie" style={{ width: `${pct(enCours)}%` }} />
              </div>
            </>
          ) : (
            <p>Aucune mission en cours.</p>
          )}
        </div>

        <div className="carte-mission">
          <strong>Planification rapide</strong>
          <div className="formulaire-ligne">
            <label className="etiquette">Parcelle</label>
            <select
              value={parcelleId}
              onChange={(e) => { setParcelleId(e.target.value); setZonesChoisies([]) }}
            >
              <option value="">Choisir…</option>
              {(parcelles.data ?? []).map((p) => (
                <option key={idDe(p, 'parcelle_id')} value={idDe(p, 'parcelle_id')}>
                  {p.nom ?? `Parcelle ${idDe(p, 'parcelle_id')}`}
                </option>
              ))}
            </select>

            <label className="etiquette">Zones à visiter (dans l’ordre de sélection)</label>
            {(zones.data ?? []).map((z) => (
              <label key={idDe(z, 'zone_id')}>
                <input
                  type="checkbox"
                  checked={zonesChoisies.includes(idDe(z, 'zone_id'))}
                  onChange={() => basculerZone(idDe(z, 'zone_id'))}
                />{' '}
                {z.nom ?? `Zone ${idDe(z, 'zone_id')}`}
              </label>
            ))}

            <button className="bouton-principal" onClick={planifier} disabled={!peutPlanifier}>
              {creer.isPending ? 'Envoi…' : 'Planifier'}
            </button>
          </div>
          {message && <p className="message">{message}</p>}
        </div>
      </div>

      <div className="onglets">
        {onglets.map((o) => (
          <button
            key={o.nom}
            className={o.nom === ongletActif ? 'onglet actif' : 'onglet'}
            onClick={() => setOngletActif(o.nom)}
          >
            {o.nom} ({compter(o)})
          </button>
        ))}
      </div>

      {changer.isError && <p className="message">Erreur : {changer.error.message}</p>}

      {affichees.length === 0 ? (
        <EtatVide message="Aucune mission pour ce filtre." />
      ) : (
        <table className="tableau">
          <thead>
            <tr>
              <th>Mission</th><th>Parcelle</th><th>Créée le</th>
              <th>Progression</th><th>Statut</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {affichees.map((m) => (
              <tr key={m.id}>
                <td><strong>{m.titre}</strong></td>
                <td>Parcelle {m.parcelle}</td>
                <td>{m.creation}</td>
                <td>{pct(m)} % · {m.faits} / {m.total} étapes</td>
                <td><StatusBadge statut={m.statut} /></td>
                <td>
                  {(actions[m.code] ?? []).map((a) => (
                    <button
                      key={a.action}
                      className="bouton-petit"
                      disabled={changer.isPending}
                      onClick={() => changer.mutate({ id: m.id, action: a.action })}
                    >
                      {a.texte}
                    </button>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default Missions