import { appeler } from './client'

export const listerMissions = () => appeler('/missions/')
export const obtenirMission = (id) => appeler(`/missions/${id}/`)
export const creerMission = (donnees) =>
  appeler('/missions/', { method: 'POST', body: donnees })