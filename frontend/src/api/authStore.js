import { CLE_REFRESH } from './config';

// L'access vit en mémoire (jamais persisté) ; le refresh en localStorage.
let acces = null;
let utilisateur = null;

export const authStore = {
  getAcces: () => acces,
  getUtilisateur: () => utilisateur,
  aUnRefresh: () => Boolean(localStorage.getItem(CLE_REFRESH)),
  getRefresh: () => localStorage.getItem(CLE_REFRESH),

  setSession(nouvelAcces, nouvelUtilisateur) {
    acces = nouvelAcces;
    if (nouvelUtilisateur !== undefined) utilisateur = nouvelUtilisateur;
  },

  setAcces(nouvelAcces) {
    acces = nouvelAcces;
  },

  setRefresh(jeton) {
    if (jeton) localStorage.setItem(CLE_REFRESH, jeton);
  },

  clear() {
    acces = null;
    utilisateur = null;
    localStorage.removeItem(CLE_REFRESH);
  },
};