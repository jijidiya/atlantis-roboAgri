import { useState } from 'react';
import { useConnexion } from '../../hooks/useAuth';

export function PageConnexion() {
  const [email, setEmail] = useState('');
  const [motDePasse, setMotDePasse] = useState('');
  const connexion = useConnexion();

  const soumettre = (e) => {
    e.preventDefault();
    connexion.mutate({ email, motDePasse });
  };

  return (
    <form onSubmit={soumettre} style={{ maxWidth: 400, margin: '4rem auto' }}>
      <h1>Connexion</h1>

      <div>
        <label>Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoFocus
        />
      </div>

      <div>
        <label>Mot de passe</label>
        <input
          type="password"
          value={motDePasse}
          onChange={(e) => setMotDePasse(e.target.value)}
          required
        />
      </div>

      <button type="submit" disabled={connexion.isPending}>
        {connexion.isPending ? 'Connexion…' : 'Se connecter'}
      </button>

      {connexion.isError && (
        <p style={{ color: 'crimson' }}>
          {connexion.error.message}
          {/* Erreurs par champ (DRF) : affichage minimal, à raffiner */}
          {Object.entries(connexion.error.details ?? {}).map(([champ, messages]) => (
            <span key={champ}> — {champ} : {messages.join(', ')}</span>
          ))}
        </p>
      )}
    </form>
  );
}