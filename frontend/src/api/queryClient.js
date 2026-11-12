import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,           // 30 s : on évite les refetch inutiles
      refetchOnWindowFocus: false, // on gère le polling à la main
      refetchOnReconnect: true,
      // Pas de retry sur les erreurs "définitives" (401/403/404), 1 retry ailleurs.
      retry: (nb, erreur) => {
        if ([401, 403, 404].includes(erreur?.statut)) return false;
        return nb < 1;
      },
    },
    mutations: {
      retry: false,
    },
  },
});