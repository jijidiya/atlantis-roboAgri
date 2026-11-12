import { useQuery } from '@tanstack/react-query';
import { api } from '../api/http';

export const clesMissions = {
  tout: ['missions'],
  liste: () => ['missions', 'liste'],
  detail: (id) => ['missions', 'detail', id],
};

export function useMissions() {
  return useQuery({
    queryKey: clesMissions.liste(),
    queryFn: () => api.get('/missions/'),
    // 3 s seulement si au moins une mission est active, sinon rien.
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!Array.isArray(data)) return false;
      const actives = data.some((m) =>
        ['planifiee', 'en_cours'].includes(m.statut)
      );
      return actives ? 3_000 : false;
    },
    refetchIntervalInBackground: false,
  });
}

export function useMission(id) {
  return useQuery({
    queryKey: clesMissions.detail(id),
    queryFn: () => api.get(`/missions/${id}/`),
    enabled: Number.isFinite(id),
    refetchInterval: (query) => {
      const s = query.state.data?.statut;
      if (!s) return false;
      const finaux = ['terminee', 'interrompue', 'non_confirmee'];
      return finaux.includes(s) ? false : 3_000;
    },
    refetchIntervalInBackground: false,
  });
}