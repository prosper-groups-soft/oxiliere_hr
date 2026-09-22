// Contrats des bindings data-aware des types métier.
// Règle d'architecture (avancement §2) : le binding d'un type vit dans le
// module qui possède sa source de données (ex: employee → modules/employees/forms).
// Ce fichier définit les contrats partagés ; `forms-bindings/index.ts` agrège.
// forms/ reste standalone : seuls les bindings connaissent endpoints/stores.

import type { ValidatorConfig, BehaviorType, BehaviorConfig } from '@/hr/forms/core/types.js';

/** Entité brute quelconque (Employee, OrgUnit, Branch…) — a au moins un id. */
export interface BizEntity {
	id: string | number;
}

/** Requête de recherche standard passée à une source paginée. */
export interface BizSearchParams {
	search?: string;
	page?: number;
	pageSize?: number;
	/** Valeurs des champs dependsOn (cascade, ex: { orgUnitId }) — cf. resolveDataSource. */
	filter?: Record<string, any>;
}

/** Adaptateur d'entité : comment mapper l'entité brute du module en option du picker. */
export interface BizEntityAdapter<T extends BizEntity> {
	/** Valeur soumise (id, string). */
	value: (entity: T) => string;
	/** Label principal affiché. */
	label: (entity: T) => string;
	/** Sous-titre optionnel (dept–poste, type d'unité…). */
	sublabel?: (entity: T) => string | undefined;
	/** Marque l'entité non supprimable (ex: famille avec postes rattachés) —
	 * l'UI désactive l'action de suppression. */
	undeletable?: (entity: T) => boolean;
	/** Recherche client de secours (concat des champs cherchables). */
	haystack?: (entity: T) => string;
}

/** Définition data-aware d'un type métier — consommée par `defineBusinessType`. */
export interface BizTypeDefinition<T extends BizEntity = BizEntity> {
	/** Charge une page d'entités (recherche + pagination déléguées au backend). */
	fetch: (params: BizSearchParams) => Promise<T[]>;
	/** Résout une entité par id (hydratation) — optionnel. */
	resolve?: (id: string) => Promise<T | null>;
	/** Mapping entité → option. */
	adapter: BizEntityAdapter<T>;
	/** Renderer personnalisé (composant Svelte) — défaut : 'business' (BusinessField). */
	renderer?: any;
	/** Comportements par défaut (searchable, cached… — BehaviorConfig autorisé
	 * pour porter une config, ex: creatable.onCreate). */
	behaviors?: (BehaviorType | BehaviorConfig)[];
	/** Validateurs par défaut (exists…). */
	validators?: ValidatorConfig[];
	/** TTL du cache source (défaut : pas de cache). */
	cacheTtl?: number;
	/** Taille de page (défaut 10). */
	pageSize?: number;
	/** false : le backend renvoie la liste complète (non paginée) — pas de
	 * pagination côté moteur, pas de « Voir plus ». Défaut : true. */
	paginated?: boolean;
}

/** Définition d'un type énuméré statique (options figées, pas de backend). */
export interface BizEnumDefinition {
	options: { label: string; value: string }[];
	validators?: ValidatorConfig[];
}
