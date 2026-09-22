// ─────────────────────────────────────────────────────────────
// Declarative Forms — Moteur réactif Svelte 5 runes (api §2, §11)
// Phase 1 (V0.1) : Form/Field, validation synchrone, soumission.
// Les dépendances (Phase 3) et DataSource async (Phase 2) arrivent
// par-dessus sans changer cette API.
// ─────────────────────────────────────────────────────────────
import type {
	ActionConfig,
	FieldConfig,
	FieldInstance,
	FormConfig,
	FormEvent,
	FormInstance,
	FormState,
	FormValidator,
	ValidationContext,
	ValidationResult,
	ValidatorConfig
} from './types.js';
import { t } from '../validation/i18n.js';
import { remoteCheck } from '../validation/remote.js';
import { getTypeDefinition } from './typeRegistry.js';
import { hasBehavior } from './behaviors.js';
import {
	isBusinessType,
	isRepeaterField,
	isRepeaterItemEmpty,
	repeaterBounds,
	repeaterSubFields
} from '../components/renderers/field-helpers.js';
import {
	buildDependencyGraph,
	collectSourceKeys,
	dependentsOf,
	detectCycle,
	evalCondition,
	normalizeDependsOn
} from './dependencies.js';

let formCounter = 0;

/** Clé de donnée d'un champ : `name ?? id` (api §4). */
export function fieldKey(field: Pick<FieldConfig, 'id' | 'name'>): string {
	return field.name ?? field.id;
}

function isEmpty(value: any): boolean {
	if (value === null || value === undefined) return true;
	if (typeof value === 'string') return value.trim() === '';
	if (Array.isArray(value)) return value.length === 0;
	return false;
}

function interpolate(template: string, params?: Record<string, any>): string {
	if (!params) return template;
	return template.replace(/\{(\w+)\}/g, (_, k) => String(params[k] ?? `{${k}}`));
}

function validatorMessage(v: ValidatorConfig, fallbackKey: string, extra?: Record<string, any>): string {
	const params = { ...(v.params ?? {}), ...(extra ?? {}) };
	// RegExp non sérialisable pour l'interpolation → on l'expose en string.
	if (params.pattern instanceof RegExp) params.pattern = String(params.pattern);
	if (typeof v.message === 'function') {
		try {
			return (v.message as (p: any) => string)(params);
		} catch {
			return t(fallbackKey, params);
		}
	}
  if (typeof v.message === 'string')
      return interpolate(v.message, params);
	return t(fallbackKey, params);
}

type FieldOverride = { disabled?: boolean; readonly?: boolean; visible?: boolean };

export function createForm<T extends Record<string, any> = Record<string, any>>(
	config: FormConfig<T>
): FormInstance<T> {
	const formId = config.id ?? `form-${++formCounter}-${Date.now().toString(36)}`;
	const mode = config.mode ?? 'create';
	const timing = config.validationTiming ?? 'onSubmit';
	const autoValidate = !config.disableAutoValidation;

	// ── Invariant 1 : unicité des ids ──
	const seen = new Set<string>();
	for (const f of config.fields) {
		if (seen.has(f.id)) throw new Error(`[forms] Champ dupliqué : id "${f.id}" déjà déclaré.`);
		seen.add(f.id);
	}
	detectCycle(config.fields);

	let depGraph = $state<Map<string, string[]>>(buildDependencyGraph(config.fields));

	let fieldConfigs = $state<FieldConfig[]>([...config.fields]);
	let cfg = $state({ mode, timing, autoValidate });

	let values = $state<Record<string, any>>(buildInitialValues(fieldConfigs, config.entity));
	const initialSnapshot: Record<string, any> = structuredCloneSafe(values);

	/** onLoad (semantics §3) : après hydratation, pour les champs ayant reçu une
	 * valeur de l'entity — post-traitement des données côté appelant. */
	function emitFieldLoad(fields: FieldConfig[]): void {
		for (const f of fields) {
			const k = fieldKey(f);
			if ((config.entity as any)?.[k] !== undefined) f.onLoad?.((config.entity as any)[k]);
		}
	}

	let errors = $state<Record<string, string>>({});
	let touchedMap = $state<Record<string, boolean>>({});
	let dirtySet = $state<Record<string, boolean>>({});
	let overrides = $state<Record<string, FieldOverride>>({});
	let depState = $state<Record<string, { visible?: boolean; enabled?: boolean; required?: boolean }>>({});
	const depTimers = new Map<string, ReturnType<typeof setTimeout>>();
	const computing = new Set<string>();
	let focusedField = $state<string | null>(null);
	let loadingMap = $state<Record<string, boolean>>({});

	let status = $state<FormState['status']>('idle');
	let isSubmitting = $state(false);
	let submitCount = $state(0);
	let lastSubmitted = $state<Record<string, any> | undefined>(undefined);

	const listeners = new Map<FormEvent, Set<(...args: any[]) => void>>();
	function emit(event: FormEvent, ...args: any[]): void {
		listeners.get(event)?.forEach((h) => {
			try {
				h(...args);
			} catch (e) {
				console.error(`[forms] handler "${event}"`, e);
			}
		});
	}

	function fieldConfigOf(name: string): FieldConfig | undefined {
		return fieldConfigs.find((f) => fieldKey(f) === name);
	}

	function isFieldVisible(f: FieldConfig): boolean {
		const k = fieldKey(f);
		const dep = depState[k]?.visible;
		if (dep !== undefined) return dep;
		const ov = overrides[k]?.visible;
		if (ov !== undefined) return ov;
		return f.visible ?? true;
	}

	function isFieldDisabled(f: FieldConfig): boolean {
		const k = fieldKey(f);
		if (depState[k]?.enabled === false) return true;
		const ov = overrides[k]?.disabled;
		if (ov !== undefined) return ov;
		return f.disabled ?? false;
	}

	function isFieldRequired(f: FieldConfig): boolean {
		const k = fieldKey(f);
		const dep = depState[k]?.required;
		if (dep !== undefined) return dep;
		return f.required ?? false;
	}

	function isFieldReadonly(f: FieldConfig): boolean {
		if (cfg.mode === 'view') return true; // semantics §2 : view → tout readonly
		const ov = overrides[fieldKey(f)]?.readonly;
		if (ov !== undefined) return ov;
		return f.readonly ?? false;
	}

	function visibleKeys(): string[] {
		return fieldConfigs.filter(isFieldVisible).map(fieldKey);
	}

	/** Payload soumis (semantics §4) : champs visibles, non disabled, valeur non
	 * undefined ; "" → undefined ; transformation par type (objets métier → id,
	 * Date → ISO, registre : TypeDefinition.transform). Les fichiers (File) sont
	 * sortis du payload et remis au handler via { files } (upload 2-phases).
	 * Clé de sortie : field.out ?? fieldKey (api §4 — mapping backend sans
	 * toucher aux données internes du formulaire). */
	function buildPayload(): { data: T; files: Record<string, File[]> } {
		const data: Record<string, any> = {};
		const files: Record<string, File[]> = {};
		for (const f of fieldConfigs) {
			if (!isFieldVisible(f)) continue;
			if (isFieldDisabled(f)) continue; // semantics §4 : non soumis
			// La valeur interne est indexée par fieldKey ; `out` ne sert que de
			// clé de sortie dans le payload (sinon les champs mappés étaient perdus).
			const k = f.out ?? fieldKey(f);
			const raw = values[fieldKey(f)];
			if (raw === undefined) continue;
			// Repeater (semantics §7) : items vides supprimés avant soumission —
			// la validation min garantit déjà que le tableau reste ≥ min.
			let v = transformValueForPayload(
				f,
				isRepeaterField(f) && Array.isArray(raw) ? raw.filter((x) => !isRepeaterItemEmpty(f, x)) : raw
			);
			// stripEmpty : un champ optionnel laissé vide (null, "", []) n'est pas
			// soumis — 0/false sont conservés (vraies valeurs). Exception : un champ
			// vide mais explicitement modifié (dirty, ex: vidé par l'utilisateur en
			// édition) est soumis à null — sinon le backend conserverait l'ancienne
			// valeur et l'effacement serait impossible.
			if (isEmpty(v)) {
				if (dirtySet[fieldKey(f)]) data[k] = null;
				continue;
			}
			if (v instanceof File) {
				(files[k] ??= []).push(v);
				continue;
			}
			if (Array.isArray(v)) {
				const arr = v.filter((x) => !(x instanceof File));
				const fileItems = v.filter((x) => x instanceof File) as File[];
				if (fileItems.length > 0) files[k] = fileItems;
				if (arr.length === 0 && v.length > 0) continue; // que des fichiers → bag files
				v = arr;
			}
			if (v === undefined) continue;
			data[k] = v;
		}
		return { data: data as T, files };
	}

	/** Transformation d'une valeur de champ pour le payload (semantics §4).
	 * Objets métier {id,…} → id (single ou multiple) ; Date → ISO ; sinon
	 * transform du registre (registerType) si défini. Group repeater : transform
	 * par subfield (registre du type + prop `transform` du subfield). */
	function transformValueForPayload(f: FieldConfig, raw: any): any {
		const registryTransform = getTypeDefinition(f.type)?.transform;
		const subs = isRepeaterField(f) ? repeaterSubFields(f) : [];
		if (subs.length && Array.isArray(raw)) {
			// Group repeater : item = objet — chaque subfield est transformé selon
			// son propre type (registre) et sa prop `transform` éventuelle.
			return raw.map((item) => {
				if (!item || typeof item !== 'object') return item;
				const out = { ...item };
				for (const sf of subs) {
					const k = fieldKey(sf);
					out[k] = transformSingleValue(sf, out[k], getTypeDefinition(sf.type)?.transform ?? (sf as { transform?: (v: any) => any }).transform);
				}
				return out;
			});
		}
		if (Array.isArray(raw)) {
			return raw.map((item) => transformSingleValue(f, item, registryTransform));
		}
		return transformSingleValue(f, raw, registryTransform);
	}

	function transformSingleValue(f: FieldConfig, v: any, registryTransform?: (value: any) => any): any {
		if (registryTransform) {
			try {
				return registryTransform(v);
			} catch {
				return v; // transform du registre : ne casse jamais la soumission
			}
		}
		if (isBusinessType(f.type)) {
			// Objets métier → id (employee/orgUnit/… ; value déjà un id si la source
			// a été normalisée — idempotent)
			if (v && typeof v === 'object' && 'id' in v) return (v as any).id;
			return v;
		}
		if (f.type === 'date' && v instanceof Date) {
			return v.toISOString();
		}
		return v;
	}

	async function runFieldValidators(
		name: string,
		value: any,
		allValues: Record<string, any>
	): Promise<string | null> {
		const f = fieldConfigOf(name);
		if (!f) return null;
		const fieldInst = getField(name)!;

		// required (attribut direct + requiredIf via depState, api §4/§8).
		// Semantics §7 : sur un champ tableau (multiSelect/repeater), required =
		// « au moins un item non vide » (group repeater : un item avec au moins
		// un subfield non vide).
		const arraySemantics = Array.isArray(value) && (isRepeaterField(f) || hasBehavior(f, 'multiSelect'));
		if (isFieldRequired(f)) {
			if (arraySemantics) {
				if ((value as any[]).every((x) => isRepeaterItemEmpty(f, x))) return t('validation.required');
			} else if (isEmpty(value)) {
				return t('validation.required');
			}
		}

		// Validateurs effectifs = validateurs du champ + defaultValidators du registre
		// (api §14). Sur un même type, le validateur du champ gagne (override).
		// Ordre (metamodel §6) : synchrones d'abord, asynchrones ensuite ; à niveau
		// égal, priority décroissant puis ordre de déclaration (tri stable).
		const fieldValidators = f.validators ?? [];
		const declaredTypes = new Set(fieldValidators.map((v) => v.type));
		const defaults = (getTypeDefinition(f.type)?.defaultValidators ?? []).filter(
			(d) => !declaredTypes.has(d.type)
		);
		const isAsyncV = (v: ValidatorConfig) =>
			v.async === true || v.type === 'unique' || v.type === 'exists';
		const list = [...fieldValidators, ...defaults]
			.map((v, i) => ({ v, i }))
			.sort((a, b) => {
				const aa = isAsyncV(a.v) ? 1 : 0;
				const bb = isAsyncV(b.v) ? 1 : 0;
				if (aa !== bb) return aa - bb; // synchrones d'abord
				const pa = a.v.priority ?? 0;
				const pb = b.v.priority ?? 0;
				if (pa !== pb) return pb - pa; // priority décroissant
				return a.i - b.i;              // ordre de déclaration
			})
			.map((x) => x.v);
    const ctx: ValidationContext = {
      form: instance as FormInstance,
      field: fieldInst,
      values: allValues
    };

		// Behavior tableau (multiSelect/repeater, semantics §7) : validateurs de
		// liste (minItems/maxItems/unique) au niveau du tableau, les autres
		// appliqués à chaque item non vide. Bornes min/max du repeater en premier.
		if (arraySemantics) {
			if (isRepeaterField(f)) {
				const { min, max } = repeaterBounds(f);
				if ((value as any[]).length < min) return t('behavior.repeater.min', { value: min });
				if ((value as any[]).length > max) return t('behavior.repeater.max', { value: max });
			}
			const ARRAY_LEVEL = new Set(['minItems', 'maxItems', 'unique']);
			const subs = repeaterSubFields(f);

			// Group repeater (avancement §2.0) : par item, par subfield — required
			// du subfield + ses validateurs, erreur rattachée « Item n · Label : … ».
			if (isRepeaterField(f) && subs.length) {
				const items = value as any[];
				for (let i = 0; i < items.length; i++) {
					const item = items[i];
					if (isRepeaterItemEmpty(f, item)) continue;
					for (const sf of subs) {
						const sv = item[fieldKey(sf)];
						const label = sf.label ?? sf.id;
						const prefix = `Item ${i + 1} · ${label} : `;
						if (sf.required === true && isEmpty(sv)) return prefix + t('validation.required');
						// ctx.field = proxy du subfield (item i) — les validateurs
						// custom voient la valeur, le nom et l'état du subfield.
						const subCtx: ValidationContext = {
							...ctx,
							field: subFieldProxy(fieldInst, i, sf)
						};
						for (const v of sf.validators ?? []) {
							const err = await runOneValidator(v, sv, subCtx);
							if (err) return prefix + err;
						}
					}
				}
				return null;
			}

			for (const v of list) {
				if (v.type === 'required') continue; // déjà géré ci-dessus
				if (ARRAY_LEVEL.has(v.type)) {
					const err = await runOneValidator(v, value, ctx);
					if (err) return err;
					continue;
				}
				for (const item of value as any[]) {
					if (isRepeaterItemEmpty(f, item)) continue;
					const err = await runOneValidator(v, item, ctx);
					if (err) return err;
				}
			}
			return null;
		}

		for (const v of list) {
			const err = await runOneValidator(v, value, ctx);
			if (err) return err;
			}
		return null;
	}

	async function runOneValidator(
		v: ValidatorConfig,
		value: any,
		ctx: ValidationContext
	): Promise<string | null> {
		const empty = isEmpty(value);
		switch (v.type) {
			case 'required':
				return empty ? validatorMessage(v, 'validation.required') : null;
			case 'email': {
				if (empty) return null;
				const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value));
				return ok ? null : validatorMessage(v, 'validation.email');
			}
			case 'url': {
				if (empty) return null;
				try {
					const u = new URL(String(value));
					return u.protocol === 'http:' || u.protocol === 'https:' ? null : validatorMessage(v, 'validation.url');
				} catch {
					return validatorMessage(v, 'validation.url');
				}
			}
			case 'phone': {
				if (empty) return null;
				const digits = String(value).replace(/[^\d]/g, '');
				const ok = digits.length >= 8 && digits.length <= 15;
				return ok ? null : validatorMessage(v, 'validation.phone');
			}
			case 'integer': {
				if (empty) return null;
				const n = Number(value);
				return Number.isInteger(n) ? null : validatorMessage(v, 'validation.integer');
			}
			case 'min': {
				if (empty) return null;
				const n = Number(value);
				const min = Number((v.params as any)?.value);
				return n < min ? validatorMessage(v, 'validation.min', { value: min }) : null;
			}
			case 'max': {
				if (empty) return null;
				const n = Number(value);
				const max = Number((v.params as any)?.value);
				return n > max ? validatorMessage(v, 'validation.max', { value: max }) : null;
			}
			case 'minLength': {
				if (empty) return null;
				const len = String(value).length;
				const min = Number((v.params as any)?.value);
				return len < min ? validatorMessage(v, 'validation.minLength', { value: min }) : null;
			}
			case 'maxLength': {
				if (empty) return null;
				const len = String(value).length;
				const max = Number((v.params as any)?.value);
				return len > max ? validatorMessage(v, 'validation.maxLength', { value: max }) : null;
			}
			case 'oneOf': {
				if (empty) return null;
				const list = ((v.params as any)?.values ?? (v.params as any)?.list ?? []) as any[];
				return list.includes(value) ? null : validatorMessage(v, 'validation.oneOf');
			}
			case 'equalTo': {
				if (empty && (values as any)?.[((v.params as any)?.field ?? (v.params as any)?.other)] == null) return null;
				const other = (values as any)?.[((v.params as any)?.field ?? (v.params as any)?.other)];
				return value === other ? null : validatorMessage(v, 'validation.equalTo');
			}
			case 'minDate': {
				if (empty) return null;
				const min = new Date(String((v.params as any)?.value)).getTime();
				const cur = new Date(String(value)).getTime();
				if (Number.isNaN(cur)) return validatorMessage(v, 'validation.minDate');
				return cur < min ? validatorMessage(v, 'validation.minDate') : null;
			}
			case 'maxDate': {
				if (empty) return null;
				const max = new Date(String((v.params as any)?.value)).getTime();
				const cur = new Date(String(value)).getTime();
				if (Number.isNaN(cur)) return validatorMessage(v, 'validation.maxDate');
				return cur > max ? validatorMessage(v, 'validation.maxDate') : null;
			}
			case 'minItems': {
				if (empty) return null;
				const min = Number((v.params as any)?.value);
				const len = Array.isArray(value) ? value.length : String(value).split(',').filter(Boolean).length;
				return len < min ? validatorMessage(v, 'validation.minItems', { value: min }) : null;
			}
			case 'maxItems': {
				if (empty) return null;
				const max = Number((v.params as any)?.value);
				const len = Array.isArray(value) ? value.length : String(value).split(',').filter(Boolean).length;
				return len > max ? validatorMessage(v, 'validation.maxItems', { value: max }) : null;
			}
			case 'regex': {
				if (empty) return null;
				const pattern = (v.params as any)?.pattern as RegExp | undefined;
				if (!pattern) return null;
				const re = pattern instanceof RegExp ? pattern : new RegExp(String(pattern));
				return re.test(String(value)) ? null : validatorMessage(v, 'validation.regex');
			}
			case 'unique':
			case 'exists': {
				const fn = (v.params as any)?.fn as
					| ((value: any, ctx: ValidationContext) => boolean | Promise<boolean>)
					| undefined;
				const source = (v.params as any)?.source as string | undefined;
				if (!fn && !source) return null;
				loadingMap[ctx.field.name] = true;
				try {
					let ok: boolean;
					if (fn) {
						const r = await fn(value, ctx);
						if (typeof r !== 'boolean') return null;
						ok = r;
					} else {
						// source : la réponse exprime l'existence — unique exige qu'elle soit fausse
						const exists = await remoteCheck(source!, value);
						ok = v.type === 'unique' ? !exists : exists;
					}
					return ok ? null : validatorMessage(v, `validation.${v.type}`);
				} catch {
					return null; // erreur réseau → ne bloque pas la soumission
				} finally {
					loadingMap[ctx.field.name] = false;
				}
			}
			case 'custom': {
				const fn = (v.params as any)?.fn as
					| ((value: any, ctx: ValidationContext) => boolean | Promise<boolean> | ValidationResult | Promise<ValidationResult>)
					| undefined;
				if (!fn) return null;
				const r = await fn(value, ctx);
				if (typeof r === 'boolean') return r ? null : validatorMessage(v, 'validation.regex');
				const res = r as ValidationResult;
				if (res.valid) return null;
				return res.message ?? validatorMessage(v, 'validation.regex');
			}
			default:
				return null;
		}
	}

	// Jeton par exécution : si la valeur change pendant un await (validateur
	// async), le résultat périmé n'est pas écrit dans errors.
	const validationTokens = new Map<string, number>();

	async function validateFieldInternal(name: string): Promise<boolean> {
		const f = fieldConfigOf(name);
		if (!f || !isFieldVisible(f)) {
			delete errors[name];
			return true;
		}
		const token = (validationTokens.get(name) ?? 0) + 1;
		validationTokens.set(name, token);
		const err = await runFieldValidators(name, values[name], { ...values });
		if (validationTokens.get(name) !== token) return true; // exécution périmée
		if (err) errors[name] = err;
		else delete errors[name];
		f.onValidate?.({ valid: !err, message: err ?? undefined, field: name });
		emit('validate', name, !err, err ?? undefined);
		return !err;
	}

	async function validateAll(): Promise<boolean> {
		status = 'validating';
		// Champs visibles uniquement (semantics §4)
		for (const name of visibleKeys()) {
			await validateFieldInternal(name);
		}
		// Nettoie les erreurs des champs devenus invisibles
		for (const k of Object.keys(errors)) {
			if (k !== '_form' && !visibleKeys().includes(k)) delete errors[k];
		}
		// Invariants inter-champs (api §6)
		delete errors['_form'];
		for (const inv of (config.validators ?? []) as FormValidator[]) {
			const res = await inv.validate({ ...values });
			if (!res.valid) {
				if (res.field) errors[res.field] = res.message ?? t('form.error');
				else errors['_form'] = res.message ?? t('form.error');
			}
		}
		const ok = Object.keys(errors).length === 0;
		emit('validate', ok);
		if (!ok) {
			status = 'error';
			emit('error', { ...errors });
		} else if (status === 'validating') {
			status = 'idle';
		}
		return ok;
	}

	function markDirty(name: string, value: any): void {
		const initial = initialSnapshot[name];
		const dirty = !deepEqual(initial, value);
		if (dirty) dirtySet[name] = true;
		else delete dirtySet[name];
	}

	function setValueInternal(name: string, value: any, opts?: { touch?: boolean }): void {
		values[name] = value;
		markDirty(name, value);
		if (opts?.touch) touchedMap[name] = true;
		config.onChange?.(name, value);
		fieldConfigOf(name)?.onChange?.(value);
		emit('change', name, value);
		void evaluateDependents(name);
		if (cfg.autoValidate && cfg.timing === 'reactive') {
			scheduleValidation(name);
		}
	}

	function applyConditions(targetKey: string, changedKey: string): void {
		const f = fieldConfigOf(targetKey);
		const dep = f?.dependencies;
		if (!f || !dep) return;
		const snap = { ...values };
		const v = evalCondition(dep.visibleIf, snap, dep.dependsOn);
		const e = evalCondition(dep.enabledIf, snap, dep.dependsOn);
		const r = evalCondition(dep.requiredIf, snap, dep.dependsOn);
		const prev = depState[targetKey] ?? {};
		const next: typeof prev = { ...prev };
		let changed = false;
		if (v !== undefined && v !== prev.visible) { next.visible = v; changed = true; }
		if (e !== undefined && e !== prev.enabled) { next.enabled = e; changed = true; }
		if (r !== undefined && r !== prev.required) { next.required = r; changed = true; }
		// N'écrit que sur changement réel : une écriture systématique (nouvel objet)
		// re-déclencherait les effets abonnés à depState sans raison.
		if (changed) depState[targetKey] = next;
		// clearOnSourceChange : la source directe a changé → reset
		if (dep.clearOnSourceChange && normalizeDependsOn(dep.dependsOn).includes(changedKey)) {
			values[targetKey] = null;
			markDirty(targetKey, null);
			delete errors[targetKey];
		}
	}

	async function runCompute(targetKey: string): Promise<void> {
		const f = fieldConfigOf(targetKey);
		const compute = f?.dependencies?.compute;
		if (!f || !compute || computing.has(targetKey)) return;
		computing.add(targetKey);
		try {
			const result = await compute({ ...values });
			// Évite la boucle : n'écrit que si différent
		if (!deepEqual(values[targetKey], result)) {
			setValueInternal(targetKey, result);
		}
		} finally {
			computing.delete(targetKey);
		}
	}

	function scheduleCompute(targetKey: string, debounceMs?: number): void {
		const existing = depTimers.get(targetKey);
		if (existing) clearTimeout(existing);
		if (!debounceMs) {
			void runCompute(targetKey);
			return;
		}
		depTimers.set(
			targetKey,
			setTimeout(() => {
				depTimers.delete(targetKey);
				void runCompute(targetKey);
			}, debounceMs)
		);
	}

	/** Évalue les dépendants transitifs d'une clé (conditions + clear + compute). */
	async function evaluateDependents(changedKey: string): Promise<void> {
		const order = dependentsOf(depGraph, changedKey);
		for (const target of order) {
			applyConditions(target, changedKey);
			const f = fieldConfigOf(target);
			if (f?.dependencies?.compute) {
				// Se déclenche si la clé changée est une source (dependsOn ou Record)
			const sources = collectSourceKeys(f.dependencies);
			if (sources.includes(changedKey)) scheduleCompute(target, f.dependencies.debounceMs);
			}
		}
		// Les champs devenus invisibles sortent des erreurs
		for (const k of Object.keys(errors)) {
			if (k === '_form') continue;
			const fc = fieldConfigOf(k);
			if (fc && !isFieldVisible(fc)) delete errors[k];
		}
	}

	function evaluateAll(): void {
		for (const f of fieldConfigs) {
			const dep = f.dependencies;
			if (!dep) continue;
			const k = fieldKey(f);
			const snap = { ...values };
			const next: { visible?: boolean; enabled?: boolean; required?: boolean } = {};
			const v = evalCondition(dep.visibleIf, snap, dep.dependsOn);
			const e = evalCondition(dep.enabledIf, snap, dep.dependsOn);
			const r = evalCondition(dep.requiredIf, snap, dep.dependsOn);
			if (v !== undefined) next.visible = v;
			if (e !== undefined) next.enabled = e;
			if (r !== undefined) next.required = r;
			if (Object.keys(next).length) depState[k] = { ...(depState[k] ?? {}), ...next };
		}
	}

	function refreshGraph(): void {
		depGraph = buildDependencyGraph(fieldConfigs);
	}

	function blurFieldInternal(name: string): void {
		touchedMap[name] = true;
		focusedField = focusedField === name ? null : focusedField;
		fieldConfigOf(name)?.onBlur?.();
		if (cfg.autoValidate && cfg.timing === 'onBlur') {
			void validateFieldInternal(name);
		}
	}

	// ── Debounce de validation async (semantics §3) ──
	// En mode reactive, les champs à validateurs distants (unique/exists, async)
	// ne revalident qu'après un délai (params.debounceMs ?? 400) : un appel serveur
	// par frappe serait inacceptable. Les validateurs sync restent immédiats.
	const validationTimers = new Map<string, ReturnType<typeof setTimeout>>();

	function fieldHasAsyncValidator(f: FieldConfig): boolean {
		return (f.validators ?? []).some(
			(v) => v.async === true || v.type === 'unique' || v.type === 'exists'
		);
	}

	function scheduleValidation(name: string): void {
		const f = fieldConfigOf(name);
		if (!f || !cfg.autoValidate) return;
		if (!fieldHasAsyncValidator(f)) {
			void validateFieldInternal(name);
			return;
		}
		const declared = (f.validators ?? []).find((v) => (v.params as any)?.debounceMs);
		const ms = Number((declared?.params as any)?.debounceMs) || 400;
		clearTimeout(validationTimers.get(name));
		validationTimers.set(
			name,
			setTimeout(() => {
				validationTimers.delete(name);
				void validateFieldInternal(name);
			}, ms)
		);
	}

	// ── FieldInstance ──────────────────────────────────────────
	const fieldListeners = new Map<string, Set<(value: any) => void>>();

	function getField(name: string): FieldInstance | undefined {
		const f = fieldConfigOf(name);
		if (!f) return undefined;
		const key = fieldKey(f);
		return {
			get id() {
				return f.id;
			},
			get name() {
				return key;
			},
			get type() {
				return f.type;
			},
			get value() {
				return values[key];
			},
			get initialValue() {
				return structuredCloneSafe(initialSnapshot[key]);
			},
			get error() {
				return errors[key] ?? null;
			},
			get isValid() {
				return !(key in errors);
			},
			get isDirty() {
				return !!dirtySet[key];
			},
			get isTouched() {
				return !!touchedMap[key];
			},
			get isLoading() {
				return !!loadingMap[key];
			},
			get isFocused() {
				return focusedField === key;
			},
			get isDisabled() {
				return isFieldDisabled(f);
			},
			get isReadonly() {
				return isFieldReadonly(f);
			},
			get isVisible() {
				return isFieldVisible(f);
			},
			get isRequired() {
				return isFieldRequired(f);
			},
			setValue(value: any) {
				setValueInternal(key, value);
				fieldListeners.get(key)?.forEach((h) => h(value));
			},
			setError(error: string | null) {
				if (error) errors[key] = error;
				else delete errors[key];
			},
			setDisabled(disabled: boolean) {
				overrides[key] = { ...(overrides[key] ?? {}), disabled };
			},
			setReadonly(readonly: boolean) {
				overrides[key] = { ...(overrides[key] ?? {}), readonly };
			},
			setVisible(visible: boolean) {
				overrides[key] = { ...(overrides[key] ?? {}), visible };
			},
			focus() {
				focusedField = key;
				fieldConfigOf(key)?.onFocus?.();
				// Focus DOM réel si le renderer a posé data-field
				queueMicrotask(() => {
					const el = document.querySelector<HTMLElement>(`[data-field="${CSS.escape(key)}"]`);
					(el as HTMLElement | null)?.focus?.();
				});
			},
			blur() {
				blurFieldInternal(key);
			},
			reset() {
				values[key] = structuredCloneSafe(initialSnapshot[key]);
				delete errors[key];
				delete touchedMap[key];
				delete dirtySet[key];
			},
			async validate() {
				return validateFieldInternal(key);
			},
			onChange(handler: (value: any) => void) {
				let set = fieldListeners.get(key);
				if (!set) {
					set = new Set();
					fieldListeners.set(key, set);
				}
				set.add(handler);
				return () => {
					set!.delete(handler);
				};
			}
		} satisfies FieldInstance;
	}

	// ── FormInstance ───────────────────────────────────────────
	const instance = {
		get id() {
			return formId;
		},
		get fields() {
			return fieldConfigs.map((f) => getField(fieldKey(f))!);
		},
		get values() {
			return values as T;
		},
		get errors() {
			return errors;
		},
		get isValid() {
			return Object.keys(errors).length === 0;
		},
		get isDirty() {
			return Object.keys(dirtySet).length > 0;
		},
		get isSubmitting() {
			return isSubmitting;
		},
		get state(): FormState {
			return {
				status,
				values: { ...values },
				errors: { ...errors },
				dirtyFields: Object.keys(dirtySet),
				touchedFields: Object.keys(touchedMap).filter((k) => touchedMap[k]),
				isValid: Object.keys(errors).length === 0,
				isDirty: Object.keys(dirtySet).length > 0,
				isSubmitting,
				submitCount,
				lastSubmitted
			};
		},

		async submit(): Promise<void> {
			if (isSubmitting) return;
			isSubmitting = true;
			submitCount += 1;
			try {
				// semantics §3-§4 : validation (champs + globale) AVANT tout appel
				const ok = await validateAll();
				if (!ok) return;
				status = 'submitting';
				const { data, files } = buildPayload();
				emit('submit', data, { files });
				await config.onSubmit?.(data, { files });
				lastSubmitted = { ...values };
				status = 'success';
			} catch (e) {
				status = 'error';
				errors['_form'] = e instanceof Error ? e.message : t('form.error');
				emit('error', e);
				throw e;
			} finally {
				isSubmitting = false;
				if (status === 'submitting') status = 'idle';
			}
		},

		reset(): void {
			const fresh = structuredCloneSafe(initialSnapshot);
			for (const k of Object.keys(values)) delete values[k];
			Object.assign(values, fresh);
			for (const k of Object.keys(errors)) delete errors[k];
			for (const k of Object.keys(touchedMap)) delete touchedMap[k];
			for (const k of Object.keys(dirtySet)) delete dirtySet[k];
			for (const k of Object.keys(depState)) delete depState[k];
			status = 'idle';
			evaluateAll();
			emit('reset');
		},

		async validate(): Promise<boolean> {
			return validateAll();
		},

		getValue(name: any): any {
			return values[name as string];
		},

		setValue(name: any, value: any): void {
			setValueInternal(name as string, value);
		},

		setValues(patch: Partial<T>): void {
			for (const [k, v] of Object.entries(patch)) setValueInternal(k, v);
		},

		/** Hydratation depuis une entité backend (semantics §2) : lit chaque champ
		 * via sa clé interne (fieldKey) ou sa clé de sortie (`out`) — l'entité
		 * métier porte les clés backend (employee_id, account_type…) — et applique
		 * le parse du registre (ex: 'PENDING' → 'pending'). Les valeurs
		 * undefined/null sont ignorées (fallback sur les defaults du champ).
		 * L'instantané initial des champs hydratés est mis à jour : isDirty mesure
		 * ensuite les modifications depuis l'entité chargée (pas depuis les
		 * défauts) — et un champ vidé par l'utilisateur reste détecté « modifié »
		 * pour l'envoi explicite de null au submit. */
		hydrate(entity: Record<string, any> | null): void {
			if (!entity) return;
			for (const f of fieldConfigs) {
				const k = fieldKey(f);
				const direct = (entity as any)[k];
				const viaOut = f.out ? (entity as any)[f.out] : undefined;
				const raw = direct !== undefined ? direct : viaOut;
				if (raw === undefined || raw === null) continue;
				const v = normalizeFieldValue(f, parseEntityValue(f, raw));
				// Snapshot AVANT setValueInternal : markDirty compare à la valeur
				// hydratée → un champ simplement hydraté n'est pas « dirty ».
				initialSnapshot[k] = structuredCloneSafe(v);
				delete dirtySet[k];
				setValueInternal(k, v);
				delete dirtySet[k];
			}
		},

		getField,

		addField(field: FieldConfig): void {
			if (fieldConfigs.some((f) => f.id === field.id)) {
				throw new Error(`[forms] Champ dupliqué : id "${field.id}" déjà déclaré.`);
			}
			detectCycle([...fieldConfigs, field]);
			fieldConfigs = [...fieldConfigs, field];
			refreshGraph();
			const k = fieldKey(field);
			if (!(k in values)) {
				const fromEntity = (config.entity as any)?.[k];
				values[k] = normalizeFieldValue(
					field,
					fromEntity !== undefined ? parseEntityValue(field, fromEntity) : (field.defaultValue ?? null)
				);
				initialSnapshot[k] = structuredCloneSafe(values[k]);
			}
			field.onInit?.(getField(k)!);
			evaluateAll();
		},

		removeField(name: string): void {
			// onDestroy (semantics §3) : nettoyage avant destruction
			fieldConfigOf(name)?.onDestroy?.();
			fieldConfigs = fieldConfigs.filter((f) => fieldKey(f) !== name);
			delete values[name];
			delete errors[name];
			delete touchedMap[name];
			delete dirtySet[name];
			delete depState[name];
			refreshGraph();
		},

		resetField(name: string): void {
			getField(name)?.reset();
		},

		emitCancel(): void {
			emit('cancel');
		},

		setConfig(patch: Partial<FormConfig<T>>): void {
			if (patch.mode) cfg.mode = patch.mode;
			if (patch.validationTiming) cfg.timing = patch.validationTiming;
			if (patch.disableAutoValidation !== undefined) cfg.autoValidate = !patch.disableAutoValidation;
			if (patch.validators) config.validators = patch.validators as FormValidator[];
			if (patch.onSubmit) config.onSubmit = patch.onSubmit;
			if (patch.onCancel) config.onCancel = patch.onCancel;
			if (patch.onChange) config.onChange = patch.onChange;
			if (patch.fields) {
				// onDestroy pour les champs retirés (semantics §3)
				const nextIds = new Set(patch.fields.map((f) => fieldKey(f)));
				for (const f of fieldConfigs) {
					if (!nextIds.has(fieldKey(f))) f.onDestroy?.();
				}
				fieldConfigs = [...patch.fields];
				const fresh = buildInitialValues(fieldConfigs, config.entity);
				for (const k of Object.keys(values)) delete values[k];
				Object.assign(values, fresh);
				Object.assign(initialSnapshot, structuredCloneSafe(fresh));
			}
		},

		on(event: FormEvent, handler: (...args: any[]) => void): () => void {
			let set = listeners.get(event);
			if (!set) {
				set = new Set();
				listeners.set(event, set);
			}
			set.add(handler);
			return () => {
				set!.delete(handler);
			};
		},

		getConfig(): FormConfig<T> {
			return config;
		}
	} satisfies FormInstance<T>;

	// onInit par champ (api §4) + onLoad après hydratation (semantics §3)
	for (const f of fieldConfigs) f.onInit?.(getField(fieldKey(f))!);
	emitFieldLoad(fieldConfigs);
	evaluateAll();

	return instance as FormInstance<T>;
}

// ── Helpers ────────────────────────────────────────────────────

function buildInitialValues(
	fields: FieldConfig[],
	entity?: Record<string, any>
): Record<string, any> {
	const out: Record<string, any> = {};
	for (const f of fields) {
		const k = fieldKey(f);
		const fromEntity = (entity as any)?.[k];
		out[k] = normalizeFieldValue(
			f,
			fromEntity !== undefined ? parseEntityValue(f, fromEntity) : (f.defaultValue ?? null)
		);
	}
	return out;
}

function structuredCloneSafe<T>(v: T): T {
	try {
		return typeof structuredClone === 'function' ? structuredClone(v) : JSON.parse(JSON.stringify(v ?? null));
	} catch {
		return v;
	}
}

/** parse du registre (api §14) : valeur d'entité → valeur de champ — inverse de
 * transform appliqué à la soumission. Ne casse jamais l'hydratation en cas d'erreur. */
function parseEntityValue(f: FieldConfig, v: any): any {
	const parse = getTypeDefinition(f.type)?.parse;
	if (!parse) return v;
	try {
		return parse(v);
	} catch {
		return v;
	}
}

/** Proxy FieldInstance d'un subfield d'un group repeater (validation) :
 * value ↔ items[itemIndex][subKey], name « parent.subKey ». setError/setDisabled…
 * neutres (la remontée d'erreur se fait au niveau du repeater, préfixée « Item n »).
 * Aligné sur le proxy de rendu de RepeaterField.itemField. */
function subFieldProxy(parent: FieldInstance, itemIndex: number, sf: FieldConfig): FieldInstance {
	const key = fieldKey(sf);
	return {
		get id() {
			return `${parent.id}-item-${itemIndex + 1}-${sf.id}`;
		},
		get name() {
			return `${parent.name}.${key}`;
		},
		get type() {
			return sf.type;
		},
		get value() {
			const item = Array.isArray(parent.value) ? parent.value[itemIndex] : null;
			return item && typeof item === 'object' ? (item[key] ?? null) : null;
		},
		get initialValue() {
			const arr = parent.initialValue;
			const item = Array.isArray(arr) ? arr[itemIndex] : null;
			return item && typeof item === 'object' ? (item[key] ?? null) : null;
		},
		get error() {
			return null;
		},
		get isValid() {
			return true;
		},
		get isDirty() {
			return parent.isDirty;
		},
		get isTouched() {
			return parent.isTouched;
		},
		get isLoading() {
			return parent.isLoading;
		},
		get isFocused() {
			return parent.isFocused;
		},
		get isDisabled() {
			return parent.isDisabled;
		},
		get isReadonly() {
			return parent.isReadonly;
		},
		get isVisible() {
			return parent.isVisible;
		},
		get isRequired() {
			return sf.required === true;
		},
		setValue() {},
		setError() {},
		setDisabled() {},
		setReadonly() {},
		setVisible() {},
		focus() {},
		blur() {},
		reset() {},
		validate() {
			return Promise.resolve(true);
		},
		onChange() {
			return () => {};
		}
	} as unknown as FieldInstance;
}

/** Behavior repeater (semantics §7 — hydratation) : la valeur devient un tableau.
 * Scalaire/undefined → enveloppé ([v] / []) ; moins de `min` éléments → items
 * vides ajoutés pour atteindre min. Group repeater (subFields) : chaque item est
 * un objet complété avec les defaultValue des subFields. */
function normalizeFieldValue(f: FieldConfig, v: any): any {
	if (!isRepeaterField(f)) return v;
	const { min } = repeaterBounds(f);
	const subs = repeaterSubFields(f);
	const wrap: any[] = v == null ? [] : Array.isArray(v) ? [...v] : [v];
	const arr = subs.length ? wrap.map((it) => parseSubValues(f, fillSubDefaults(f, it))) : wrap;
	while (arr.length < min) arr.push(subs.length ? fillSubDefaults(f, null) : null);
	return arr;
}

/** Item objet d'un group repeater : subFields absents → defaultValue ?? null. */
function fillSubDefaults(f: FieldConfig, item: any): Record<string, any> {
	const obj: Record<string, any> = item && typeof item === 'object' ? { ...item } : {};
	for (const s of repeaterSubFields(f)) {
		const k = fieldKey(s);
		if (obj[k] === undefined) obj[k] = s.defaultValue ?? null;
	}
	return obj;
}

/** Hydratation group repeater : parse par subfield (registre du type + prop
	* `parse` du subfield) — inverse du transform au payload. Ne casse jamais
	* l'hydratation en cas d'erreur. */
function parseSubValues(f: FieldConfig, item: Record<string, any>): Record<string, any> {
	for (const sf of repeaterSubFields(f)) {
		const k = fieldKey(sf);
		const parse =
			getTypeDefinition(sf.type)?.parse ?? (sf as { parse?: (v: any) => any }).parse;
		if (!parse || item[k] == null) continue;
		try {
			item[k] = parse(item[k]);
		} catch {
			// parse du subfield : ne casse jamais l'hydratation
		}
	}
	return item;
}

function deepEqual(a: any, b: any): boolean {
	if (Object.is(a, b)) return true;
	try {
		return JSON.stringify(a) === JSON.stringify(b);
	} catch {
		return false;
	}
}

/** Exécution d'une ActionConfig contre le formulaire (utilisé par FormView/hosts). */
export async function runFormAction<T extends Record<string, any>>(
	form: FormInstance<T>,
	action: ActionConfig<T>
): Promise<void> {
	const disabled = typeof action.disabled === 'function' ? action.disabled(form) : action.disabled;
	if (disabled) return;
	switch (action.type) {
		case 'submit':
			if (action.handler) await action.handler(form);
			else await form.submit();
			break;
		case 'reset':
			if (action.handler) await action.handler(form);
			else form.reset();
			break;
		default:
			await action.handler?.(form);
	}
}
