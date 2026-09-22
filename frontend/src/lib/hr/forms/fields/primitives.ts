// Factories de champs (api §4) : `(id, config?) => FieldConfig` avec `type` auto.
import type { FieldConfig, FileFieldConfig, TreeFieldConfig } from '../core/types.js';

type PartialConfig = Partial<Omit<FieldConfig, 'id' | 'type'>>;

function make<T extends PartialConfig>(type: FieldConfig['type'], id: string, config?: T): FieldConfig {
	return { ...config, id, type } as FieldConfig;
}

// ── Primitifs ──
export const text = (id: string, config?: PartialConfig): FieldConfig => make('text', id, config);
export const number = (id: string, config?: PartialConfig): FieldConfig => make('number', id, config);
export const date = (id: string, config?: PartialConfig): FieldConfig => make('date', id, config);
export const boolean = (id: string, config?: PartialConfig): FieldConfig => make('boolean', id, config);
export const switchField = (id: string, config?: PartialConfig): FieldConfig => make('switch', id, config);

export { switchField as switch };

export const email = (id: string, config?: PartialConfig): FieldConfig => make('email', id, config);
export const password = (id: string, config?: PartialConfig): FieldConfig => make('password', id, config);
export const phone = (id: string, config?: PartialConfig): FieldConfig => make('phone', id, config);
export const currency = (id: string, config?: PartialConfig): FieldConfig => make('currency', id, config);
export const textarea = (id: string, config?: PartialConfig): FieldConfig => make('textarea', id, config);

// ── Sélection ──
export const select = (id: string, config?: PartialConfig): FieldConfig => make('select', id, config);
export const autocomplete = (id: string, config?: PartialConfig): FieldConfig => make('autocomplete', id, config);
export const combobox = (id: string, config?: PartialConfig): FieldConfig => make('combobox', id, config);
export const radio = (id: string, config?: PartialConfig): FieldConfig => make('radio', id, config);
export const checkbox = (id: string, config?: PartialConfig): FieldConfig => make('checkbox', id, config);
export const tree = (id: string, config?: Partial<TreeFieldConfig>): FieldConfig =>
	make('tree', id, config);
export const file = (id: string, config?: Partial<FileFieldConfig>): FieldConfig =>
	make('file', id, config);
