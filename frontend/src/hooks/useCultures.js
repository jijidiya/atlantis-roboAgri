import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/http';

export const clesCultures = {
  tout: ['cultures'],
  liste: () => ['cultures', 'liste'],
};

export function useCultures() {
  return useQuery({
    queryKey: clesCultures.liste(),
    queryFn: () => api.get('/cultures/'),
    staleTime: 5 * 60_000,
  });
}

export function useCreerCulture() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (donnees) => api.post('/cultures/', donnees),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: clesCultures.tout }),
  });
}