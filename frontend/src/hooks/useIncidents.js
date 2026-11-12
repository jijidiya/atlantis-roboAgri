import { useQuery } from '@tanstack/react-query'
import { listerIncidents } from '../api/incidents'

export function useIncidents() {
  return useQuery({
    queryKey: ['incidents'],
    queryFn: listerIncidents,
    refetchInterval: 10000, // 10 s, comme le document d'API
  })
}