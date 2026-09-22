// ────────────────────────────────────────────────────────────────────────
// Declarative Forms — Types (aligné docs/declarative-forms/api.md)
// Couvre api §3→§14 + metamodel §invariants + semantics.
// ────────────────────────────────────────────────────────────────────────

export type FormMode = 'create' | 'edit' | 'view';
export type ValidationTiming = 'onSubmit' | 'onBlur' | 'reactive';

export type FormHostConfig =
	| SheetHostConfig
	| DialogHostConfig
	| DrawerHostConfig
	| InlineHostConfig;

export interface SheetHostConfig {
	type: 'sheet';
	side?: 'right' | 'left' | 'top' | 'bottom';
	width?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full' | string;
	closeOnSubmit?: boolean;
	confirmUnsavedOnClose?: boolean;
}

export interface DialogHostConfig {
	type: 'dialog' | 'modal';
	size?: 'sm' | 'md' | 'lg' | 'xl' | 'full' | string;
	closeOnSubmit?: boolean;
	confirmUnsavedOnClose?: boolean;
}

export interface DrawerHostConfig {
	type: 'drawer';
	position?: 'bottom' | 'right';
}

export interface InlineHostConfig {
	type: 'inline' | 'div' | 'card';
	variant?: 'card' | 'plain' | 'bordered';
}

export interface FormConfig<T extends Record<string, any> = Record<string, any>> {
	id?: string;
	title?: string;
	description?: string;
	host?: FormHostConfig;
	mode?: FormMode;
	entity?: T;
	validationTiming?: ValidationTiming;
	fields: FieldConfig[];
	layout?: LayoutConfig;
	actions?: ActionConfig<T>[];
	validators?: FormValidator[];
	dataSource?: DataSourceConfig;
	onSubmit?: (data: T, extra?: { files?: Record<string, File[]> }) => Promise<void> | void;
	/** Uploader facultatif (champs `file`) : upload en arrière-plan avec
	 * progression/annulation pendant la saisie. Absent → upload 2-phases au
	 * submit (les Files partent dans `{ files }`). */
	uploader?: UploadHandler;
	onCancel?: () => void;
	onChange?: (field: string, value: any) => void;
	theme?: ThemeConfig;
	disableAutoValidation?: boolean;
}

// ── Fields (api §4) ──────────────────────────────────────────

export type FieldType =
	| 'text'
	| 'number'
	| 'date'
	| 'boolean'
	| 'switch'
	| 'email'
	| 'password'
	| 'phone'
	| 'currency'
	| 'textarea'
	| 'select'
	| 'autocomplete'
	| 'combobox'
	| 'radio'
	| 'checkbox'
	| 'file'
	| 'tree'
	| 'employee'
	| 'orgUnit'
	| 'manager'
	| 'contract'
	| 'position'
	| 'organization'
	| 'branch'
	| 'country'
	| 'city'
	| 'leaveType'
	| 'payroll'
	| 'jobFamily'
	| 'seniorityLevel'
	| 'workSite'
	| 'group'
	| 'bankInstitution'
	| 'gender'
	| 'maritalStatus'
	| 'contractType'
	| 'remunerationType'
	| 'paymentPeriod'
	| 'salaryBaseType'
	| 'initialStatus'
	| 'documentType';

export interface FieldConfig {
	id: string;
	name?: string;
	/** Clé de sortie dans le payload soumis (défaut: fieldKey = name ?? id).
	 * Permet de mapper vers un nom backend (ex: snake_case) sans toucher aux
	 * données internes du formulaire : `values`, l'hydratation (`entity`,
	 * `setValues`) et les références inter-champs (`dependsOn`, `compute`)
	 * restent sur fieldKey. S'applique après le transform du registre. */
	out?: string;
	type: FieldType;
	label?: string;
	description?: string;
	placeholder?: string;
	maxLength?: number;
	min?: number;
	max?: number;
	step?: number;
	help?: string;
	icon?: string;
	tooltip?: string;
	badge?: string | { text: string; variant?: 'info' | 'warning' | 'success' | 'danger' | 'neutral' };
	defaultValue?: any;
	required?: boolean;
	readonly?: boolean;
	disabled?: boolean;
	visible?: boolean;
	order?: number;
	group?: string;
	section?: string;
	tags?: string[];
	dataSource?: DataSourceConfig;
	/** false : désactive la barre de recherche des renderers select métier
	 * (défaut true — absent = comportement courant inchangé). */
	searchable?: boolean;
	validators?: ValidatorConfig[];
	behaviors?: BehaviorConfig[];
	dependencies?: DependencyConfig;
	onInit?: (field: FieldInstance) => void;
	onLoad?: (data: any) => void;
	onDestroy?: () => void;
	onFocus?: () => void;
	onBlur?: () => void;
	onInput?: (value: any) => void;
	onChange?: (value: any) => void;
	onValidate?: (result: ValidationResult) => void;
}

export interface BusinessFieldConfig<T = any> extends FieldConfig {
	transform?: (value: T) => any;
	parse?: (value: any) => T;
	filter?: Record<string, any>;
	mode?: 'picker' | 'display' | 'search';
	selection?: 'single' | 'multiple';
}

export interface SelectFieldConfig extends FieldConfig {
	dataSource?: DataSourceConfig;
}

/** Champ `file` (V0.2) : upload 1+ fichiers — valeur = `File` (single) ou
	* `File[]` (multiple) ; `buildPayload` les sort du payload vers `{ files }`.
	* Hydratation : noms de fichiers existants (strings) affichés en lecture. */
export interface FileFieldConfig extends FieldConfig {
	/** Attribut accept natif (ex: 'application/pdf,image/*'). */
	accept?: string;
	/** Sélection multiple (défaut : fichier unique). */
	multiple?: boolean;
	/** Taille max par fichier en octets — fichiers rejetés signalés inline. */
	maxSize?: number;
}

/** Champ `tree` (V1) : rendu arborescent d'une DataSource hiérarchique
 * (premier client : `orgUnit` — DIRECTION → DEPARTMENT → TEAM). La source
 * renvoie des nœuds imbriqués `{ label, value, children? }` (ou `{id,name,children}`) ;
 * la valeur stockée = `value` du/des nœud(s) sélectionné(s). */
export interface TreeFieldConfig extends FieldConfig {
	/** 'single' (défaut) : valeur = id du nœud. 'multiple' : tableau d'ids. */
	selection?: 'single' | 'multiple';
	/** Recherche client-side (filtre l'arbre en gardant les ancêtres des matches). */
	searchable?: boolean;
	/** Niveaux dépliés au chargement (défaut 1 : racines visibles, enfants pliés).
	 * `Infinity` = tout déplier. */
	defaultExpandedDepth?: number;
}

// ── Layout (api §5, récursif) ─────────────────────────────────

export type LayoutConfig =
	| RowLayout
	| ColumnLayout
	| GroupLayout
	| SectionLayout
	| CardLayout
	| TabsLayout
	| AccordionLayout
	| StepperLayout;

export interface RowLayout {
	type: 'row';
	columns: LayoutColumn[];
	gap?: string;
	responsive?: boolean;
}

export interface LayoutColumn {
	fields: string[];
	span?: number;
}

export interface ColumnLayout {
	type: 'column';
	fields: string[] | LayoutConfig;
	gap?: string;
}

export interface GroupLayout {
	type: 'group';
	groups: FormGroup[];
}

export interface FormGroup {
	id?: string;
	label?: string;
	fields: string[];
	layout?: 'row' | 'column' | 'grid';
}

export interface SectionLayout {
	type: 'section';
	sections: FormSection[];
}

export interface FormSection {
	id?: string;
	title: string;
	description?: string;
	fields: string[] | LayoutConfig;
	collapsible?: boolean;
	defaultCollapsed?: boolean;
}

export interface CardLayout {
	type: 'card';
	title?: string;
	description?: string;
	fields: string[] | LayoutConfig;
}

export interface TabsLayout {
	type: 'tabs';
	tabs: FormTab[];
}

export interface FormTab {
	id?: string;
	label: string;
	icon?: string;
	fields: string[] | LayoutConfig;
}

export interface StepperLayout {
	type: 'stepper';
	steps: FormStep[];
	variant?: 'default' | 'vertical' | 'compact';
	allowSkip?: boolean;
}

export interface FormStep {
	id?: string;
	label: string;
	icon?: string;
	description?: string;
	fields: string[] | LayoutConfig;
}

export interface AccordionLayout {
	type: 'accordion';
	items: AccordionItem[];
	multiple?: boolean;
}

export interface AccordionItem {
	id?: string;
	title: string;
	fields: string[] | LayoutConfig;
}

// ── Validation (api §6) ───────────────────────────────────────

export type ValidatorType =
	| 'required'
	| 'email'
	| 'url'
	| 'phone'
	| 'integer'
	| 'min'
	| 'max'
	| 'minLength'
	| 'maxLength'
	| 'regex'
	| 'oneOf'
	| 'equalTo'
	| 'minDate'
	| 'maxDate'
	| 'minItems'
	| 'maxItems'
	| 'unique'
	| 'exists'
	| 'custom';

export interface ValidatorConfig {
	type: ValidatorType;
	message?: string | ((params: any) => string);
	params?: Record<string, any>;
	async?: boolean;
	priority?: number;
}

export interface CustomValidator extends ValidatorConfig {
	type: 'custom';
	params: {
		fn: (
			value: any,
			context: ValidationContext
		) => boolean | Promise<boolean> | ValidationResult | Promise<ValidationResult>;
	};
}

export interface ValidationContext {
	form: FormInstance;
	field: FieldInstance;
	values: Record<string, any>;
}

export interface ValidationResult {
	valid: boolean;
	message?: string;
	field?: string;
}

export interface FormValidator {
	name: string;
	validate: (values: Record<string, any>) => ValidationResult | Promise<ValidationResult>;
}

// ── DataSource (api §7) ───────────────────────────────────────

export type DataSourceConfig =
	| ApiDataSource
	| StoreDataSource
	| StaticDataSource
	| FunctionDataSource
	| PromiseDataSource;

export interface BaseDataSource {
	cache?: {
		ttl: number;
		strategy?: 'memory' | 'session' | 'persistent';
		key?: string;
	};
	/** Débounce de recherche côté renderer (BusinessField) — hérité par tous les types de source. */
	debounceMs?: number;
	/** Stratégie de chargement (metamodel §7). eager (défaut) : au montage ;
	 * lazy : au premier focus/ouverture du picker ; manual : sur action explicite
	 * (bouton « Rechercher ») ; paginated/infinite : par pages (page/pageSize
	 * passés à la source, « Voir plus » concatène). */
	load?: 'eager' | 'lazy' | 'manual' | 'paginated' | 'infinite';
	/** Taille de page pour load 'paginated'/'infinite' (défaut 50). */
	pageSize?: number;
}

export interface ApiDataSource extends BaseDataSource {
	type: 'api';
	endpoint: string;
	method?: 'GET' | 'POST';
	params?: Record<string, any>;
	headers?: Record<string, string>;
	transform?: (data: any) => any;
	debounceMs?: number;
}

export interface StoreDataSource extends BaseDataSource {
	type: 'store';
	store: string;
	property?: string;
}

export interface StaticDataSource extends BaseDataSource {
	type: 'static';
	values: Array<{ label: string; value: any;[key: string]: any }>;
}

export interface FunctionDataSource extends BaseDataSource {
	type: 'function';
	fn: (params?: any) => any | Promise<any>;
}

/** Promesse déjà déclenchée par l'appelant (options pré-chargées) — résolue une
 * seule fois, résultat mis en cache mémoire par le renderer. */
export interface PromiseDataSource extends BaseDataSource {
	type: 'promise';
	promise: Promise<unknown>;
}

// ── Dépendances (api §8) ──────────────────────────────────────

export type Condition = boolean | ((...args: any[]) => boolean);

export interface DependencyConfig {
	dependsOn?: string | string[];
	compute?: (values: Record<string, any>) => any | Promise<any>;
	visibleIf?: Condition | Record<string, Condition>;
	enabledIf?: Condition | Record<string, Condition>;
	requiredIf?: Condition | Record<string, Condition>;
	clearOnSourceChange?: boolean;
	reloadIf?: Condition | Record<string, Condition>;
	debounceMs?: number;
}

// ── Comportements (api §9) ────────────────────────────────────

export type BehaviorType =
	| 'searchable'
	| 'clearable'
	| 'multiSelect'
	| 'repeater'
	| 'creatable'
	| 'virtualized'
	| 'paginated'
	| 'sortable'
	| 'filterable'
	| 'debounced'
	| 'cached'
	| 'async'
	| 'manageable';

export interface BehaviorConfig {
	type: BehaviorType;
	config?: Record<string, any>;
	priority?: number;
}

export interface RepeaterConfig {
	min?: number;
	max?: number;
	sortable?: boolean;
	addItemLabel?: string;
	/** Group repeater (V1) : item = objet — un champ par subField
	 * (`{ nom, tel }`). Interdit d'y mettre un behavior repeater. */
	subFields?: FieldConfig[];
	/** Layout du sous-formulaire d'item (group repeater) — ex: `row`/`column`/`group`.
	 * Absent : grille 2 colonnes simple. Les clés de layout référencent les
	 * fieldKey des subFields. */
	layout?: LayoutConfig;
}

// ── Upload (champs `file`, optionnel) ──────────────────────────────

/** Progression d'un upload de fichier (octets envoyés / total). */
export interface UploadProgress {
	loaded: number;
	total: number;
}

/** Contexte passé à un UploadHandler par le renderer du champ file. */
export interface UploadContext {
	/** fieldKey du champ file à l'origine de l'upload. */
	field: string;
	/** Progression (si le handler la supporte — ex: xhrUploader). */
	onProgress?: (p: UploadProgress) => void;
	/** Annulation (bouton × pendant l'envoi). */
	signal?: AbortSignal;
}

/** Uploader injecté (facultatif, FormConfig.uploader) : uploade un File en
	* arrière-plan pendant la saisie et renvoie la référence stockée dans la valeur
	* du champ (ex: URL/id renvoyé par le serveur). Absent → les Files restent
	* dans la valeur et partent dans `{ files }` au submit (upload 2-phases). */
export type UploadHandler = (file: File, ctx: UploadContext) => Promise<unknown>;

// ── Actions (api §10) ─────────────────────────────────────────

export interface ActionConfig<T extends Record<string, any> = Record<string, any>> {
	type: 'submit' | 'reset' | 'cancel' | 'delete' | 'custom';
	label: string;
	variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
	icon?: string;
	disabled?: boolean | ((form: FormInstance<T>) => boolean);
	confirm?: boolean | string;
	shortcut?: string;
	handler?: (form: FormInstance<T>) => void | Promise<void>;
}

// ── Instances (api §11) ───────────────────────────────────────

export type FormEvent = 'submit' | 'reset' | 'change' | 'validate' | 'error' | 'cancel';

export interface FormInstance<T extends Record<string, any> = Record<string, any>> {
	readonly id: string;
	readonly fields: FieldInstance[];
	readonly values: T;
	readonly isValid: boolean;
	readonly isDirty: boolean;
	readonly isSubmitting: boolean;
	readonly errors: Record<string, string>;
	submit(): Promise<void>;
	reset(): void;
	validate(): Promise<boolean>;
	getValue<K extends keyof T>(name: K): T[K];
	setValue<K extends keyof T>(name: K, value: T[K]): void;
	setValues(values: Partial<T>): void;
	/** Hydratation depuis une entité backend : clés fieldKey ou `out`, parse du
	 * registre appliqué ; undefined/null ignorés (defaults conservés). */
	hydrate(entity: Record<string, any> | null): void;
	getField(name: string): FieldInstance | undefined;
	addField(field: FieldConfig): void;
	removeField(name: string): void;
	resetField(name: string): void;
	emitCancel(): void;
	setConfig(config: Partial<FormConfig<T>>): void;
	on(event: FormEvent, handler: (...args: any[]) => void): () => void;
	readonly state: FormState;
	getConfig(): FormConfig<T>;
}

export interface FieldInstance {
	readonly id: string;
	readonly name: string;
	readonly type: FieldType;
	readonly value: any;
	/** Valeur du champ dans l'instantané initial (hydratation, addField,
	 * setConfig, reset) — base du calcul isDirty. Read-only. */
	readonly initialValue: any;
	readonly error: string | null;
	readonly isValid: boolean;
	readonly isDirty: boolean;
	readonly isTouched: boolean;
	readonly isLoading: boolean;
	readonly isFocused: boolean;
	readonly isDisabled: boolean;
	readonly isReadonly: boolean;
	readonly isVisible: boolean;
	readonly isRequired: boolean;
	setValue(value: any): void;
	setError(error: string | null): void;
	setDisabled(disabled: boolean): void;
	setReadonly(readonly: boolean): void;
	setVisible(visible: boolean): void;
	focus(): void;
	blur(): void;
	reset(): void;
	validate(): Promise<boolean>;
	onChange(handler: (value: any) => void): () => void;
}

export interface FormState {
	status: 'idle' | 'validating' | 'submitting' | 'success' | 'error';
	values: Record<string, any>;
	errors: Record<string, string>;
	dirtyFields: string[];
	touchedFields: string[];
	isValid: boolean;
	isDirty: boolean;
	isSubmitting: boolean;
	submitCount: number;
	lastSubmitted?: Record<string, any>;
}

// ── Thème (api §12) ───────────────────────────────────────────

export type ThemeConfig = 'default' | 'admin' | 'mobile' | 'compact' | CustomTheme;

export interface CustomTheme {
	renderers?: Partial<Record<FieldType, any>>;
	css?: Record<string, string>;
	spacing?: {
		field?: string;
		group?: string;
		section?: string;
	};
}

// ── i18n (api §13) ────────────────────────────────────────────

export interface I18nConfig {
	locale: string;
	messages: Record<string, string | ((params: any) => string)>;
}

// ── Types personnalisés (api §14) ─────────────────────────────

export interface TypeDefinition<T = any> {
	valueType: string;
	defaultRenderer: any;
	defaultBehaviors?: (BehaviorType | BehaviorConfig)[];
	defaultValidators?: ValidatorConfig[];
	defaultDataSource?: DataSourceConfig;
	/** Résolution id → entité brute (hydratation des renderers riches). */
	resolve?: (id: string) => Promise<T | null>;
	transform?: (value: T) => any;
	parse?: (value: any) => T;
}
