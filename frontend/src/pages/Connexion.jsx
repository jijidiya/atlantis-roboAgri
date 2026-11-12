import './Connexion.css'
import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useConnexion } from '../hooks/useAuth'

export default function Connexion() {
  const navigate = useNavigate()
  const location = useLocation()
  const connexion = useConnexion()

  const [email, setEmail] = useState('')
  const [motDePasse, setMotDePasse] = useState('')
  const [afficher, setAfficher] = useState(false)
  const [erreurLocale, setErreurLocale] = useState('')

  const destination = location.state?.depuis?.pathname ?? '/'

  const envoyer = (e) => {
    e.preventDefault()
    setErreurLocale('')

    if (!email || !motDePasse) {
      setErreurLocale('Veuillez remplir tous les champs.')
      return
    }

    connexion.mutate(
      { email, motDePasse },
      {
        onSuccess: () => navigate(destination, { replace: true }),
      }
    )
  }

  // Erreur renvoyée par l'API (codes normalisés par api/http.js)
  const erreurApi = connexion.isError ? connexion.error : null
  const messageErreur =
    erreurLocale ||
    erreurApi?.message ||
    ''

  return (
    <div className="connexion">
      <div className="connexion-visuel">
        <div className="connexion-marque">RoboAgri-Kin</div>
        <div>
          <h2>Votre terre. Votre robot. Une vision claire.</h2>
          <p>Surveillez vos parcelles, suivez vos mesures et prenez les bonnes décisions, au bon moment.</p>
          <div className="connexion-chiffres">
            <span><strong>12,4 ha</strong> de surface suivie</span>
            <span><strong>3 zones</strong> sous surveillance</span>
            <span><strong>1 robot</strong> connecté</span>
          </div>
        </div>
      </div>

      <div className="connexion-formulaire">
        <form onSubmit={envoyer}>
          <h1>Heureux de vous revoir</h1>
          <p className="sous-titre">Connectez-vous pour garder le lien avec votre terrain.</p>

          <label className="champ">Adresse e-mail
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="vous@fermedenzola.cd"
              autoComplete="email"
              disabled={connexion.isPending}
            />
          </label>

          <label className="champ">Mot de passe
            <div className="champ-mdp">
              <input
                type={afficher ? 'text' : 'password'}
                value={motDePasse}
                onChange={(e) => setMotDePasse(e.target.value)}
                autoComplete="current-password"
                disabled={connexion.isPending}
              />
              <button type="button" onClick={() => setAfficher(!afficher)}>
                {afficher ? 'Masquer' : 'Afficher'}
              </button>
            </div>
          </label>

          <div className="ligne-options">
            <label><input type="checkbox" defaultChecked /> Se souvenir de moi</label>
            <a href="#">Mot de passe oublié ?</a>
          </div>

          {messageErreur && <p className="erreur">{messageErreur}</p>}

          {/* Erreurs par champ renvoyées par DRF (ex: email invalide, mot de passe requis) */}
          {erreurApi?.details && Object.keys(erreurApi.details).length > 0 && (
            <ul className="erreur">
              {Object.entries(erreurApi.details).map(([champ, messages]) => (
                <li key={champ}>
                  {champ} : {Array.isArray(messages) ? messages.join(', ') : String(messages)}
                </li>
              ))}
            </ul>
          )}

          <button type="submit" className="bouton large" disabled={connexion.isPending}>
            {connexion.isPending ? 'Connexion…' : 'Se connecter'}
          </button>
        </form>
      </div>
    </div>
  )
}