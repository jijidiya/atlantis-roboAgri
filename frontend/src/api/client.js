const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

export class ErreurApi extends Error {
  constructor(status, code, message, details) {
    super(message)
    this.status = status
    this.code = code
    this.details = details
  }
}

export async function appeler(chemin, options = {}) {
  const reponse = await fetch(`${BASE}${chemin}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
    body: options.body ? JSON.stringify(options.body) : undefined,
  })
  if (reponse.status === 204) return null
  const donnees = await reponse.json().catch(() => null)
  if (!reponse.ok) {
    const e = donnees?.erreur
    throw new ErreurApi(
      reponse.status,
      e?.code ?? 'ERREUR_INTERNE',
      e?.message ?? 'Erreur inattendue',
      e?.details,
    )
  }
  return donnees
}