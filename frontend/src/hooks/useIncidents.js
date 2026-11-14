import { useQuery } from '@tanstack/react-query';
import { api } from '../api/http';

export const clesIncidents = {
  tout: ['incidents'],
  liste: (filtres = {}) => ['incidents', 'liste', filtres],
};

/**
 * Liste des incidents.
 * polling : true (par defaut) -> refresh toutes les 10 s.
 *           false -> aucune requete supplementaire (page Historique, Dashboard).
 */
export function useIncidents({ polling = true, ...filtres } = {}) {
  return useQuery({
    queryKey: clesIncidents.liste(filtres),
    queryFn: () => {
      const params = new URLSearchParams();
      Object.entries(filtres).forEach(([k, v]) => {
        if (v != null && v !== '') params.append(k, v);
      });
      const qs = params.toString();
      return api.get(`/incidents/${qs ? `?${qs}` : ''}`);
    },
    // 10 s : les incidents peuvent arriver a tout moment (page Incidents).
    // Desactive sur les pages statiques (Historique, Dashboard).
    refetchInterval: polling ? 10_000 : false,
    refetchIntervalInBackground: false,
  });
}