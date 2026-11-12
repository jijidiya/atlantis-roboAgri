import { useQuery } from '@tanstack/react-query'
import { listerMissions, obtenirMission } from '../api/missions'

const cles = {
  liste: ['missions', 'liste'],
  detail: (id) => ['missions', 'detail', id],
}

export function useMissions() {
  return useQuery({ queryKey: cles.liste, queryFn: listerMissions })
}

export function useMission(id) {
  return useQuery({
    queryKey: cles.detail(id),
    queryFn: () => obtenirMission(id),
    refetchInterval: (requete) =>
      requete.state.data?.statut === 'en_cours' ? 3000 : false,
  })
}