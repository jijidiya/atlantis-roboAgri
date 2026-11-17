import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/http';
import { clesDecisions } from './useDecisions';

export const clesIrrigations = {
  tout: ['irrigations'],
  liste: (filtres = {}) => ['irrigations', 'liste', filtres],
  seuils: () => ['irrigations', 'seuils'],
};

export function useIrrigations({ zone, statut } = {}) {
  const params = new URLSearchParams();
  if (zone) params.set('zone', zone);
  if (statut) params.set('statut', statut);
  const suffixe = params.toString() ? `?${params}` : '';

  return useQuery({
    queryKey: clesIrrigations.liste({ zone, statut }),
    queryFn: () => api.get(`/irrigations/${suffixe}`),
  });
}

export function useSeuilsZones() {
  return useQuery({
    queryKey: clesIrrigations.seuils(),
    queryFn: () => api.get('/irrigations/seuils/'),
    staleTime: 60_000,
  });
}

/**
 * POST /irrigations/ : arrosage manuel.
 * Erreur 403 = arrosage_interdit (mesure invalide, robot injoignable, etc.).
 * Le backend force utilisateur = request.user via IrrigationManuelleSerializer.
 */
export function useCreerIrrigation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ zone, dureeSecondes }) =>
      api.post('/irrigations/', {
        zone,
        duree_secondes: dureeSecondes,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: clesIrrigations.tout });
      queryClient.invalidateQueries({ queryKey: clesDecisions.tout });
    },
  });
}