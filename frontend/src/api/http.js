import { BASE_URL, CODES_ERREUR } from './config';
import { authStore } from './authStore';

export class ErreurApi extends Error {
  constructor({ code, message, details = {}, statut = 0 }) {
    super(message);
    this.name = 'ErreurApi';
    this.code = code;
    this.details = details;
    this.statut = statut;
  }
}

// File d'attente : un seul refresh à la fois, même si 5 requêtes 401 en parallèle.
let rafraichissementEnCours = null;

async function rafraichir() {
  if (rafraichissementEnCours) return rafraichissementEnCours;

  rafraichissementEnCours = (async () => {
    const refresh = authStore.getRefresh();
    if (!refresh) throw new ErreurApi({ code: CODES_ERREUR.NON_AUTHENTIFIE, message: 'Session absente.' });

    const reponse = await fetch(`${BASE_URL}/auth/rafraichir/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rafraichissement: refresh }),
    });

    if (!reponse.ok) {
      authStore.clear();
      throw new ErreurApi({ code: CODES_ERREUR.NON_AUTHENTIFIE, message: 'Session expirée.' });
    }

    const donnees = await reponse.json();
    authStore.setAcces(donnees.acces);
    authStore.setRefresh(donnees.rafraichissement);
    return donnees.acces;
  })();

  try {
    return await rafraichissementEnCours;
  } finally {
    rafraichissementEnCours = null;
  }
}

const CODE_PAR_STATUT = {
  400: CODES_ERREUR.VALIDATION,
  401: CODES_ERREUR.NON_AUTHENTIFIE,
  403: CODES_ERREUR.ACCES_INTERDIT,
  404: CODES_ERREUR.INTROUVABLE,
  409: CODES_ERREUR.CONFLIT,
  500: CODES_ERREUR.SERVICE_INDISPONIBLE,
};

async function normaliserErreur(reponse) {
  const statut = reponse.status;
  let corps = null;
  try { corps = await reponse.json(); } catch { /* corps vide */ }

  // 1) Format custom documenté : { erreur: { code, message, details } }
  if (corps?.erreur) {
    return {
      code: corps.erreur.code ?? CODE_PAR_STATUT[statut] ?? 'erreur_inconnue',
      message: corps.erreur.message ?? `Erreur HTTP ${statut}`,
      details: corps.erreur.details ?? {},
      statut,
    };
  }

  // 2) Format DRF : { detail: "..." } pour les erreurs globales
  if (corps?.detail) {
    return {
      code: CODE_PAR_STATUT[statut] ?? 'erreur_inconnue',
      message: corps.detail,
      details: {},
      statut,
    };
  }

  // 3) Format DRF : { champ: ["message", ...] } pour les erreurs de serializer
  if (corps && typeof corps === 'object') {
    return {
      code: CODE_PAR_STATUT[statut] ?? 'erreur_inconnue',
      message: 'Certains champs sont invalides.',
      details: corps,
      statut,
    };
  }

  return {
    code: CODE_PAR_STATUT[statut] ?? 'erreur_inconnue',
    message: `Erreur HTTP ${statut}`,
    details: {},
    statut,
  };
}

async function requete(chemin, options = {}, peutReessayer = true) {
  const entetes = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const acces = authStore.getAcces();
  if (acces && !options.sansAuth) {
    entetes.Authorization = `Bearer ${acces}`;
  }

  let reponse;
  try {
    reponse = await fetch(`${BASE_URL}${chemin}`, {
      method: options.method ?? 'GET',
      headers: entetes,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    throw new ErreurApi({
      code: CODES_ERREUR.SERVICE_INDISPONIBLE,
      message: 'Service indisponible, réessayez.',
      statut: 0,
    });
  }

  // 401 → on tente UN refresh, puis on rejoue la requête UNE fois.
  if (reponse.status === 401 && peutReessayer && !options.sansRetry) {
    try {
      await rafraichir();
    } catch {
      throw new ErreurApi({
        code: CODES_ERREUR.NON_AUTHENTIFIE,
        message: 'Session expirée. Reconnectez-vous.',
        statut: 401,
      });
    }
    return requete(chemin, options, false);
  }

  if (!reponse.ok) {
    throw new ErreurApi(await normaliserErreur(reponse));
  }

  if (reponse.status === 204) return null;
  const texte = await reponse.text();
  return texte ? JSON.parse(texte) : null;
}

export const api = {
  get: (chemin, options) => requete(chemin, { ...options, method: 'GET' }),
  post: (chemin, corps, options) => requete(chemin, { ...options, method: 'POST', body: corps }),
  patch: (chemin, corps, options) => requete(chemin, { ...options, method: 'PATCH', body: corps }),
  put: (chemin, corps, options) => requete(chemin, { ...options, method: 'PUT', body: corps }),
  delete: (chemin, options) => requete(chemin, { ...options, method: 'DELETE' }),

  // Pour login et refresh : pas de token, pas de retry (sinon boucle).
  publicPost: (chemin, corps) =>
    requete(chemin, { method: 'POST', body: corps, sansAuth: true, sansRetry: true }),
};