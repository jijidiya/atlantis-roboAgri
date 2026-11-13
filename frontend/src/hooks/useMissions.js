import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/http';
import { STATUTS_MISSION_FINAUX } from '../api/config';

export const clesMissions = {
  tout: ['missions'],
  liste: (filtres = {}) => ['missions', 'liste', filtres],
  detail: (id) => ['missions', 'detail', id],
};

// --- Lecture -----------------------------------------------------------

export function useMissions(filtres = {}) {
  return useQuery({
    queryKey: clesMissions.liste(filtres),
    queryFn: () => api.get('/missions/'),
  });
}

export function useMission(id) {
  return useQuery({
    queryKey: clesMissions.detail(id),
    queryFn: () => api.get(`/missions/${id}/`),
    enabled: Boolean(id),
    // Polling 3 s TANT QUE la mission peut encore changer, sinon rien.
    refetchInterval: (query) => {
      const statut = query.state.data?.statut;
      if (!statut) return false; // pas encore chargée : on attend
      return STATUTS_MISSION_FINAUX.includes(statut) ? false : 3_000;
    },
  });
}

// --- Mutations ---------------------------------------------------------

function invaliderMission(queryClient, id) {
  queryClient.invalidateQueries({ queryKey: clesMissions.tout });
  if (id) queryClient.invalidateQueries({ queryKey: clesMissions.detail(id) });
}

export function useCreerMission() {
  const queryClient = useQueryClient();
  return useMutation({
    // Corps attendu : { parcelle, utilisateur, etapes: [{ numero_ordre, zone }] }
    mutationFn: (corps) => api.post('/missions/', corps),
    onSuccess: () => invaliderMission(queryClient),
  });
}

export function useDemarrerMission(id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => api.post(`/missions/${id}/demarrer/`, {}),
    onSuccess: () => invaliderMission(queryClient, id),
  });
}

export function useInterrompreMission(id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => api.post(`/missions/${id}/interrompre/`, {}),
    onSuccess: () => invaliderMission(queryClient, id),
  });
}

export function useTerminerMission(id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => api.post(`/missions/${id}/terminer/`, {}),
    onSuccess: () => invaliderMission(queryClient, id),
  });
}