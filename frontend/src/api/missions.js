import { appeler, enListe } from './client'

export const listerMissions = async () => enListe(await appeler('/missions/'))
export const creerMission = (donnees) =>
  appeler('/missions/', { method: 'POST', body: donnees })
export const changerEtat = (id, action) =>
  appeler(`/missions/${id}/${action}/`, { method: 'POST' })

export const listerParcelles = async () => enListe(await appeler('/parcelles/'))
export const listerZones = async (parcelleId) =>
  enListe(await appeler(`/zones/?parcelle=${parcelleId}`))