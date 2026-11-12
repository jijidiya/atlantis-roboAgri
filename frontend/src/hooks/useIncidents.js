import { useQuery } from '@tanstack/react-query';
import { api } from '../api/http';

export const clesIncidents = {
  tout: ['incidents'],
  liste: (filtres = {}) => ['incidents', 'liste', filtres],
};

export function useIncidents(filtres = {}) {
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
    // 10 s : les incidents peuvent arriver à tout moment.
    refetchInterval: 10_000,
    refetchIntervalInBackground: false,
  });
}