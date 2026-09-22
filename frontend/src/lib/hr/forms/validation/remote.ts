// Vérification serveur pour les validateurs unique/exists (api §6).
// unique({ source: '/api/employees/check-email' }) → GET source?value=…
// Réponse acceptée : boolean direct, { exists }, { available } (inversé),
// { taken }, ou vérité brute. Erreur réseau → true (pas d'échec bloquant
// côté form : la responsabilité réseau reste côté appelant).
import APIEndPoint from '@/hr/utilities/http/rest';

export async function remoteCheck(source: string, value: unknown): Promise<boolean> {
	const endpoint = new APIEndPoint(source, source);
	const json: unknown = await endpoint.list({ value });
	if (typeof json === 'boolean') return json;
	if (json && typeof json === 'object') {
		const o = json as Record<string, unknown>;
		if ('exists' in o) return !!o['exists'];
		if ('available' in o) return !o['available'];
		if ('taken' in o) return !!o['taken'];
	}
	return !!json;
}
