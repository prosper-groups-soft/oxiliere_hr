// Binding géographie (lot P2) — country statique ; city bloqué backend.
// `country` : source statique COUNTRY_OPTIONS (constante projet, import direct
// toléré pour les constantes — cf. CountryField). Consommateurs multiples et
// pas de domaine clair → vit ici (même règle que les enums, avancement §2.1).
// Le dispatcher continue de router vers CountryField.svelte (drapeaux) : le
// registre documente le type et fournit la source par défaut au moteur.
// `city` : AUCUNE source réelle n'existe (pas d'API villes ; les adresses
// backend sont du texte libre) → type volontairement NON enregistré pour
// conserver le fallback injection (dataSource fournie par l'appelant).
import { registerType } from '@/hr/forms/index.js';
import { COUNTRY_OPTIONS } from '@/hr/modules/employees/constants/countries.js';

let registered = false;

/** Enregistre les types géographie (idempotent). */
export function registerGeoTypes(): void {
	if (registered) return;
	registered = true;

	registerType('country', {
		valueType: 'string',
		defaultRenderer: 'country',
		defaultDataSource: {
			type: 'static',
			values: COUNTRY_OPTIONS.map((c) => ({ label: c.label, value: c.value }))
		}
	});
}
