import type { FieldConfig } from '../../core/types.js';
import { hasBehavior, repeaterConfigOf } from '../../core/behaviors.js';
import { getTypeDefinition } from '../../core/typeRegistry.js';

export const BUSINESS_TYPES = new Set<FieldConfig['type']>([
	'orgUnit',
	'employee',
	'manager',
	'contract',
	'position',
	'organization',
	'branch',
	'jobFamily',
	'leaveType',
	'payroll',
	'seniorityLevel',
	'workSite',
	'group',
	'bankInstitution',
	'gender',
	'maritalStatus',
	'contractType',
	'remunerationType',
	'paymentPeriod',
	'salaryBaseType',
	'initialStatus',
	'documentType'
]);

export function isBusinessType(type: FieldConfig['type']): boolean {
	return BUSINESS_TYPES.has(type);
}

/** Sélection multiple : prop `selection: 'multiple'` ou behavior `multiSelect`
 * (metamodel §8 — le behavior change le type de la valeur en tableau). */
export function isMultipleSelection(config: FieldConfig): boolean {
	return (config as { selection?: string }).selection === 'multiple' || hasBehavior(config, 'multiSelect');
}

/** Types simples éligibles au behavior repeater (semantics §7 — pas de repeater
 * imbriqué, ni boolean/radio/currency dont la valeur n'est pas un scalaire). */
const REPEATER_TYPES = new Set<FieldConfig['type']>([
	'text',
	'email',
	'password',
	'phone',
	'textarea',
	'number',
	'date',
	'select',
	'combobox',
	'autocomplete',
	'country',
	'city'
]);

export function isRepeaterField(config: FieldConfig): boolean {
	return hasBehavior(config, 'repeater') && REPEATER_TYPES.has(config.type);
}

export function repeaterBounds(config: FieldConfig): {
	min: number;
	max: number;
	sortable: boolean;
} {
	const c = repeaterConfigOf(config);
	return { min: c.min ?? 0, max: c.max ?? Infinity, sortable: c.sortable ?? false };
}

function isEmptyValue(v: any): boolean {
	if (v === null || v === undefined) return true;
	if (typeof v === 'string') return v.trim() === '';
	if (Array.isArray(v)) return v.length === 0;
	return false;
}

/** SubFields d'un group repeater (item = objet) — [] si repeater scalaire. */
export function repeaterSubFields(config: FieldConfig): FieldConfig[] {
	return repeaterConfigOf(config).subFields ?? [];
}

/** Item vide ? Scalaire : valeur vide. Group repeater : objet dont TOUS les
	* subFields sont vides. */
export function isRepeaterItemEmpty(config: FieldConfig, item: any): boolean {
	const subs = repeaterSubFields(config);
	if (!subs.length) return isEmptyValue(item);
	if (!item || typeof item !== 'object') return isEmptyValue(item);
	return subs.every((s) => isEmptyValue(item[(s as { name?: string }).name ?? s.id]));
}

/** Copie d'une config de champ sans le behavior repeater — anti-récursion
	* (FieldRenderer re-rendrait un RepeaterField sinon). */
export function withoutRepeaterBehavior(config: FieldConfig): FieldConfig {
	return {
		...config,
		behaviors: (config.behaviors ?? []).filter((b) => b.type !== 'repeater')
	} as FieldConfig;
}

export function inputTypeFor(type: FieldConfig['type']): string {
	switch (type) {
		case 'email':
			return 'email';
		case 'password':
			return 'password';
		case 'number':
		case 'currency':
			return 'number';
		case 'date':
			return 'date';
		case 'phone':
			return 'tel';
		default:
			return 'text';
	}
}

export function staticOptions(config: FieldConfig): Array<{ label: string; value: unknown }> {
	const ds = config.dataSource ?? getTypeDefinition(config.type)?.defaultDataSource;
	if (ds?.type === 'static') return ds.values;
	return [];
}

export function multiSelectLabel(
	values: string[],
	options: Array<{ label: string; value: unknown }>
): string {
	const labels = values
		.map((v) => options.find((o) => String(o.value) === v)?.label ?? v)
		.filter(Boolean);
	if (!labels.length) return '';
	return labels.length <= 2 ? labels.join(', ') : `${labels.length} sélectionnée(s)`;
}
