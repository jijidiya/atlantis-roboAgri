import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/http';
import { authStore } from '../api/authStore';

export const clesAuth = {
  tout: ['auth'],
  moi: () => ['auth', 'moi'],
};

export function useConnexion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ email, motDePasse }) =>
      api.publicPost('/auth/connexion/', { email, mot_de_passe: motDePasse }),

    onSuccess: (donnees) => {
      authStore.setSession(donnees.acces, donnees.utilisateur);
      authStore.setRefresh(donnees.rafraichissement);
      // On amorce le cache : pas besoin de re-fetch /auth/moi/ juste après.
      queryClient.setQueryData(clesAuth.moi(), donnees.utilisateur);
    },
  });
}

export function useMoi() {
  return useQuery({
    queryKey: clesAuth.moi(),
    queryFn: () => api.get('/auth/moi/'),
    // On tente /moi seulement si on a un refresh OU un access : sinon visiteur anonyme.
    enabled: authStore.aUnRefresh() || Boolean(authStore.getAcces()),
    staleTime: Infinity,
  });
}

export function useModifierProfil() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (corps) => api.patch('/auth/moi/', corps),
    onSuccess: (data) => {
      // Met à jour le cache pour tous les écrans qui lisent useMoi().
      queryClient.setQueryData(clesAuth.moi(), data);
    },
  });
}

export function useDeconnexion() {
  const queryClient = useQueryClient();
  return () => {
    authStore.clear();
    queryClient.clear();
  };
}