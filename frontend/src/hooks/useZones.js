import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/http';
import { clesParcelles } from './useParcelles';

export const clesZones = {
  tout: ['zones'],
  liste: (filtres = {}) => ['zones', 'liste', filtres],
  detail: (id) => ['zones', 'detail', id],
  decision: (id) => ['zones', 'decision', id],
};

// GET /zones/?parcelle={id} (le filtre est optionnel).
export function useZones({ parcelle } = {}) {
  return useQuery({
    queryKey: clesZones.liste({ parcelle }),
    queryFn: () => {
      const params = parcelle ? `?parcelle=${parcelle}` : '';
      return api.get(`/zones/${params}`);
    },
    staleTime: 60_000,
  });
}

export function useZone(id) {
  return useQuery({
    queryKey: clesZones.detail(id),
    queryFn: () => api.get(`/zones/${id}/`),
    enabled: Number.isFinite(id),
  });
}

export function useCreerZone() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (donnees) => api.post('/zones/', donnees),
    onSuccess: () => {
      // Une zone appartenant à une parcelle, la parcelle change aussi (zones[]).
      queryClient.invalidateQueries({ queryKey: clesZones.tout });
      queryClient.invalidateQueries({ queryKey: clesParcelles.tout });
    },
  });
}

export function useModifierZone(id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (donnees) => api.patch(`/zones/${id}/`, donnees),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: clesZones.tout });
      queryClient.invalidateQueries({ queryKey: clesParcelles.tout });
    },
  });
}

export function useSupprimerZone() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(`/zones/${id}/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: clesZones.tout });
      queryClient.invalidateQueries({ queryKey: clesParcelles.tout });
    },
  });
}

// GET /zones/{id}/decision/ — forme supposée = serializer Decision.
// À CONFIRMER la première fois : si le backend renvoie autre chose, ajuste ici.
export function useDecisionZone(id, { polling = false } = {}) {
  return useQuery({
    queryKey: clesZones.decision(id),
    queryFn: () => api.get(`/zones/${id}/decision/`),
    enabled: Number.isFinite(id),
    // 3 s uniquement si la zone a l'irrigation auto et qu'on suit la décision.
    refetchInterval: polling ? 3_000 : false,
    refetchIntervalInBackground: false,
  });
}

/**
 * Enregistre les seuils de plusieurs zones en un seul clic.
 * Recoit { [zoneId]: { humidite_minimum, humidite_maximum } }.
 */
export function useModifierSeuilsZones() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (modifications) =>
      Promise.all(
        Object.entries(modifications).map(([id, patch]) =>
          api.patch(`/zones/${id}/`, patch)
        )
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: clesZones.tout });
      queryClient.invalidateQueries({ queryKey: clesParcelles.tout });
    },
  });
}
