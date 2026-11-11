import './Connexion.css'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Connexion() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [motDePasse, setMotDePasse] = useState('')
  const [afficher, setAfficher] = useState(false)
  const [erreur, setErreur] = useState('')

  const envoyer = (e) => {
    e.preventDefault()
    if (!email || !motDePasse) {
      setErreur('Veuillez remplir tous les champs.')
      return
    }
    // Connexion fictive : on branchera l'API du binôme B plus tard
    navigate('/')
  }

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
            />
          </label>

          <label className="champ">Mot de passe
            <div className="champ-mdp">
              <input
                type={afficher ? 'text' : 'password'}
                value={motDePasse}
                onChange={(e) => setMotDePasse(e.target.value)}
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

          {erreur && <p className="erreur">{erreur}</p>}

          <button type="submit" className="bouton large">Se connecter</button>
        </form>
      </div>
    </div>
  )
}