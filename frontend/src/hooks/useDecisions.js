import { useQuery } from '@tanstack/react-query';
import { api } from '../api/http';

export const clesDecisions = {
  tout: ['decisions'],
  liste: (filtres = {}) => ['decisions', 'liste', filtres],
  courante: (zoneId) => ['decisions', 'courante', zoneId],
};

/**
 * Liste des decisions d'irrigation.
 * Filtres : zone, statut (recommandee, autorisee, refusee).
 */
export function useDecisions({ zone, statut } = {}) {
  const params = new URLSearchParams();
  if (zone) params.set('zone', zone);
  if (statut) params.set('statut', statut);
  const suffixe = params.toString() ? `?${params}` : '';

  return useQuery({
    queryKey: clesDecisions.liste({ zone, statut }),
    queryFn: () => api.get(`/decisions/${suffixe}`),
  });
}

/**
 * Decision courante d'une zone.
 * Endpoint : GET /zones/{id}/decision/
 */
export function useDecisionCourante(zoneId) {
  return useQuery({
    queryKey: clesDecisions.courante(zoneId),
    queryFn: () => api.get(`/zones/${zoneId}/decision/`),
    enabled: Boolean(zoneId),
    staleTime: 30000,
  });
}