import { useQuery } from '@tanstack/react-query';
import { api } from '../api/http';

export const clesMesures = {
  tout: ['mesures'],
  liste: (filtres = {}) => ['mesures', 'liste', filtres],
};

/**
 * Mesures d'une mission ou d'une zone.
 * polling : true pendant une mission active -> refresh toutes les 3 s.
 * Securite : depend de services.lister_mesures cote backend (filtre user a verifier).
 */
export function useMesures({ mission, zone, statut, du, au, polling = false } = {}) {
  const params = new URLSearchParams();
  if (mission) params.set('mission', mission);
  if (zone) params.set('zone', zone);
  if (statut) params.set('statut', statut);
  if (du) params.set('du', du);
  if (au) params.set('au', au);
  const suffixe = params.toString() ? `?${params}` : '';

  return useQuery({
    queryKey: clesMesures.liste({ mission, zone, statut, du, au }),
    queryFn: () => api.get(`/mesures/${suffixe}`),
    enabled: Boolean(mission || zone),
    refetchInterval: polling ? 3000 : false,
  });
}

/**
 * Dernieres mesures toutes zones/missions confondues.
 * Utilise par le Dashboard pour un apercu rapide.
 * polling : true -> refresh toutes les 3 s (pendant une mission active).
 */
export function useMesuresRecentes({ limite = 10, statut = 'valide', polling = false } = {}) {
  const params = new URLSearchParams();
  params.set('page_size', limite);
  if (statut) params.set('statut', statut);

  return useQuery({
    queryKey: ['mesures', 'recentes', { limite, statut }],
    queryFn: () => api.get(`/mesures/?${params}`),
    refetchInterval: polling ? 3000 : false,
  });
}