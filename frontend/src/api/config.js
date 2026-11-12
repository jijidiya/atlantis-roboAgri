
export const BASE_URL = import.meta.env.VITE_API_URL ?? '/api/v1';

// Clé localStorage du jeton de rafraîchissement (l'access reste en mémoire).
export const CLE_REFRESH = 'roboagri.refresh';

// Codes d'erreur applicatifs (cf. doc API §4.5) — le front s'en sert pour router l'UI.
export const CODES_ERREUR = {
  VALIDATION: 'validation',
  NON_AUTHENTIFIE: 'non_authentifie',
  ACCES_INTERDIT: 'acces_interdit',
  INTROUVABLE: 'introuvable',
  CONFLIT: 'conflit',
  SERVICE_INDISPONIBLE: 'service_indisponible',
};

// Statuts finaux : le polling s'arrête dès qu'on les atteint.
export const STATUTS_MISSION_FINAUX = ['terminee', 'interrompue', 'non_confirmee'];
export const STATUTS_ETAPE_FINAUX = ['terminee', 'interrompue'];
export const STATUTS_IRRIGATION_FINAUX = ['terminee', 'interrompue'];