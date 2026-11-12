import { useQuery } from '@tanstack/react-query';
import { api } from '../api/http';

export const clesMesures = {
  tout: ['mesures'],
  recentes: (limit) => ['mesures', 'recentes', limit],
  parMission: (missionId) => ['mesures', 'mission', missionId],
};

// 100 dernières mesures, tous statuts confondus (valide + invalide + manquante).
// Tri par date desc côté client (l'ordering n'est pas documenté côté API).
export function useMesuresRecentes({ limit = 100 } = {}) {
  return useQuery({
    queryKey: clesMesures.recentes(limit),
    queryFn: async () => {
      const reponse = await api.get(`/mesures/?page_size=${limit}`);
      const liste = Array.isArray(reponse) ? reponse : reponse?.results ?? [];
      return [...liste].sort(
        (a, b) => new Date(b.date_heure_mesure) - new Date(a.date_heure_mesure)
      );
    },
    staleTime: 30_000,
  });
}

// Mesures d'une mission, en polling 3 s tant que la mission n'est pas finie.
export function useMesuresMission(missionId, { statutMission } = {}) {
  const finaux = ['terminee', 'interrompue', 'non_confirmee'];
  return useQuery({
    queryKey: clesMesures.parMission(missionId),
    queryFn: async () => {
      const reponse = await api.get(`/mesures/?mission=${missionId}&page_size=100`);
      return Array.isArray(reponse) ? reponse : reponse?.results ?? [];
    },
    enabled: Number.isFinite(missionId),
    refetchInterval: statutMission && !finaux.includes(statutMission) ? 3_000 : false,
    refetchIntervalInBackground: false,
  });
}