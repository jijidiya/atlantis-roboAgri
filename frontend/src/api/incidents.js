import { appeler, enListe } from './client'

export const listerIncidents = async () => enListe(await appeler('/incidents/'))