import { useState } from 'react'
import Toggle from '../components/Toggle'
import StatusBadge from '../components/StatusBadge'

const onglets = ['Mon compte', 'Robot et connexion', 'Équipe et accès']

const equipe = [
  { nom: 'Magnificat Kakanda', email: 'magnificat@exemple.cd', role: 'Administrateur' },
  { nom: 'Jeanine Makunga', email: 'jeanine.makunga@fermedensele.cd', role: 'Propriétaire' },
]

function Parametres() {
  const [onglet, setOnglet] = useState('Mon compte')
  const [message, setMessage] = useState('')

  // Mon compte
  const [prenom, setPrenom] = useState('Magnificat')
  const [nom, setNom] = useState('Kakanda')
  const [email, setEmail] = useState('magnificat@exemple.cd')
  const [nouveauMdp, setNouveauMdp] = useState('')
  const [notifs, setNotifs] = useState({
    critiques: true,
    missions: true,
    irrigation: true,
  })

  // Robot
  const [cleVisible, setCleVisible] = useState(false)

  function changerNotif(cle, valeur) {
    setNotifs({ ...notifs, [cle]: valeur })
  }

  function enregistrer() {
    if (nouveauMdp !== '' && nouveauMdp.length < 12) {
      setMessage('Erreur : le mot de passe doit contenir au moins 12 caractères.')
      return
    }
    if (!email.includes('@')) {
      setMessage('Erreur : adresse e-mail invalide.')
      return
    }
    setMessage('Modifications enregistrées (simulation, pas encore envoyées à l’API).')
    setNouveauMdp('')
  }

  return (
    <div>
      <div className="titre-ligne">
        <div>
          <h1>Paramètres</h1>
          <p className="sous-titre">Personnalisez votre espace de travail et sécurisez votre compte.</p>
        </div>
        {onglet === 'Mon compte' && (
          <button className="bouton-principal" onClick={enregistrer}>Enregistrer les modifications</button>
        )}
      </div>

      <div className="onglets">
        {onglets.map((o) => (
          <button
            key={o}
            className={o === onglet ? 'onglet actif' : 'onglet'}
            onClick={() => { setOnglet(o); setMessage('') }}
          >
            {o}
          </button>
        ))}
      </div>

      {message && <p className="message">{message}</p>}

      {onglet === 'Mon compte' && (
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
                <input value={email} onChange={(e) => setEmail(e.target.value)} />
              </label>
              <label>
                <small className="etiquette">Nouveau mot de passe</small>
                <input
                  type="password"
                  placeholder="12 caractères minimum"
                  value={nouveauMdp}
                  onChange={(e) => setNouveauMdp(e.target.value)}
                />
              </label>
            </div>
          </div>

          <div className="carte-mission">
            <strong>Notifications</strong>
            <div className="ligne-option">
              <span>Alertes critiques</span>
              <Toggle actif={notifs.critiques} onChange={(v) => changerNotif('critiques', v)} />
            </div>
            <div className="ligne-option">
              <span>Missions du robot</span>
              <Toggle actif={notifs.missions} onChange={(v) => changerNotif('missions', v)} />
            </div>
            <div className="ligne-option">
              <span>Irrigation et seuils</span>
              <Toggle actif={notifs.irrigation} onChange={(v) => changerNotif('irrigation', v)} />
            </div>
            <small className="etiquette">Notifications affichées dans l’application.</small>
          </div>
        </div>
      )}

      {onglet === 'Robot et connexion' && (
        <div className="carte-mission">
          <strong>Robot RB-01</strong>
          <div className="ligne-option"><span>État</span><span className="badge badge-vert">Connecté</span></div>
          <div className="ligne-option"><span>Signal de vie</span><span>toutes les 5 s</span></div>
          <div className="ligne-option"><span>Actualisation de l’interface</span><span>toutes les 3 s</span></div>
          <div className="ligne-option">
            <span>Clé d’API (démonstration)</span>
            <span>
              <code>{cleVisible ? 'rk_demo_8f3a91c2' : 'rk_demo_••••••••'}</code>{' '}
              <button className="bouton-petit" onClick={() => setCleVisible(!cleVisible)}>
                {cleVisible ? 'Masquer' : 'Afficher'}
              </button>
            </span>
          </div>
          <small className="etiquette">
            Valeurs fictives. La vraie clé ne sera jamais écrite dans le code du frontend.
          </small>
        </div>
      )}

      {onglet === 'Équipe et accès' && (
        <table className="tableau">
          <thead>
            <tr><th>Membre</th><th>E-mail</th><th>Rôle</th></tr>
          </thead>
          <tbody>
            {equipe.map((m) => (
              <tr key={m.email}>
                <td><strong>{m.nom}</strong></td>
                <td>{m.email}</td>
                <td><StatusBadge statut={m.role} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default Parametres