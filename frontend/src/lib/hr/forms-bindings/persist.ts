// Helper de persistance (côté app — PAS dans forms/, invariant vision §3 :
// `forms/` reste standalone, sans endpoint ni store métier). Ce fichier vit
// dans forms-bindings/, le point de couplage bindings ↔ app autorisé.
//
// Rôle : réduire le `onSubmit` d'un sheet déclaratif à une déclaration —
// quelle mutation create/update appeler, comment cibler l'entité en édition.
// Le moteur garde tout le processus (validation, payload avec clés `out` +
// transform registre, isSubmitting, closeOnSubmit) ; ce helper ne fait que
// router le payload prêt vers la mutation TanStack passée par l'appelant.
//
// Pourquoi des fonctions et pas des URLs : les mutations portent déjà
// l'invalidation du cache, l'auth et les toasts d'erreur (onError) — passer
// des URLs brutes dupliquerait cette couche (cf. avancement §3.9).

/** Arguments d'édition : id de l'entité + payload prêt (clés `out`). */
export interface PersistUpdateArgs {
	id: string;
	data: Record<string, any>;
}

export interface PersistConfig {
	/** Mutation de création — reçoit le payload du moteur. */
	create: (payload: Record<string, any>) => Promise<unknown>;
	/** Mutation d'édition — reçoit { id, data } (ou tout ce que la mutation attend). */
	update: (args: PersistUpdateArgs) => Promise<unknown>;
	/** Id de l'entité en édition — null/undefined ⇒ mode création. */
	idOf?: () => string | number | null | undefined;
	/** Enrichissement du payload prêt (ex: `account_name`, champ hors formulaire). */
	merge?: (data: Record<string, any>, mode: 'create' | 'edit') => Record<string, any>;
}

/** Construit un handler `onSubmit` compatible FormConfig à partir des
 * mutations de l'appelant. `create` est requis ; sans `update`/`idOf`, le
 * formulaire est en création seule (la présence d'un id bascule en édition). */
export function persist(config: PersistConfig): (data: Record<string, any>) => Promise<void> {
	return async (data) => {
		const id = config.idOf?.();
		if (id != null && config.update) {
			const extra = config.merge?.(data, 'edit') ?? data;
			await config.update({ id: String(id), data: extra });
		} else {
			const extra = config.merge?.(data, 'create') ?? data;
			await config.create(extra);
		};
	};
}
