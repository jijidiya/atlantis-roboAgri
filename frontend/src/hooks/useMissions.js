import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  listerMissions, creerMission, changerEtat, listerParcelles, listerZones,
} from '../api/missions'

export function useMissions() {
  return useQuery({
    queryKey: ['missions'],
    queryFn: listerMissions,
    // actualisation toutes les 3 s tant qu'une mission est en cours
    refetchInterval: (requete) =>
      requete.state.data?.some((m) => m.statut === 'en_cours') ? 3000 : false,
  })
}

export const useParcelles = () =>
  useQuery({ queryKey: ['parcelles'], queryFn: listerParcelles })

export const useZones = (parcelleId) =>
  useQuery({
    queryKey: ['zones', parcelleId],
    queryFn: () => listerZones(parcelleId),
    enabled: !!parcelleId,
  })

export function useCreerMission() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: creerMission,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['missions'] }),
  })
}

export function useChangerEtat() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, action }) => changerEtat(id, action),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['missions'] }),
  })
}