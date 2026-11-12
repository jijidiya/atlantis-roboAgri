import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/http';

export const clesParcelles = {
  tout: ['parcelles'],
  liste: () => ['parcelles', 'liste'],
  detail: (id) => ['parcelles', 'detail', id],
};

// GET /parcelles/ → tableau brut, zones[] incluses.
export function useParcelles() {
  return useQuery({
    queryKey: clesParcelles.liste(),
    queryFn: () => api.get('/parcelles/'),
    staleTime: 60_000, // données de config : pas besoin de polling
  });
}

export function useParcelle(id) {
  return useQuery({
    queryKey: clesParcelles.detail(id),
    queryFn: () => api.get(`/parcelles/${id}/`),
    enabled: Number.isFinite(id),
  });
}

export function useCreerParcelle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (donnees) => api.post('/parcelles/', donnees),
    onSuccess: () => {
      // Parcelles + zones (car zones embarquées côté parcelle) : on invalide tout.
      queryClient.invalidateQueries({ queryKey: clesParcelles.tout });
      queryClient.invalidateQueries({ queryKey: ['zones'] });
    },
  });
}

export function useModifierParcelle(id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (donnees) => api.patch(`/parcelles/${id}/`, donnees),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: clesParcelles.tout });
      queryClient.invalidateQueries({ queryKey: ['zones'] });
    },
  });
}

export function useSupprimerParcelle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(`/parcelles/${id}/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: clesParcelles.tout });
      queryClient.invalidateQueries({ queryKey: ['zones'] });
    },
  });
}