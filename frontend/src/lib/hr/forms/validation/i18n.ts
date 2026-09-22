// Messages par défaut (api §13 — français), interpolation {param} (semantics §8).
export const defaultMessages: Record<string, string> = {
	'validation.required': 'Ce champ est requis',
	'validation.email': "Format d'email invalide",
	'validation.url': 'URL invalide (http/https requis)',
	'validation.phone': 'Numéro de téléphone invalide',
	'validation.integer': 'Doit être un nombre entier',
	'validation.min': 'La valeur minimale est {value}',
	'validation.max': 'La valeur maximale est {value}',
	'validation.minLength': 'Minimum {value} caractère(s)',
	'validation.maxLength': 'Maximum {value} caractère(s)',
	'validation.regex': 'Format invalide',
	'validation.unique': 'Cette valeur existe déjà',
	'validation.exists': "Cette valeur n'existe pas",
	'validation.oneOf': 'Valeur non autorisée',
	'validation.equalTo': 'Les valeurs ne correspondent pas',
	'validation.minDate': 'Date trop ancienne',
	'validation.maxDate': 'Date trop récente',
	'validation.minItems': 'Sélectionnez au moins {value} élément(s)',
	'validation.maxItems': 'Sélectionnez au plus {value} élément(s)',
	'field.loading': 'Chargement...',
	'field.noResults': 'Aucun résultat',
	'field.search': 'Rechercher...',
	'field.clear': 'Effacer',
	'field.seeMore': 'Voir plus ({count})',
	'action.submit': 'Soumettre',
	'action.reset': 'Réinitialiser',
	'action.cancel': 'Annuler',
	'action.confirm': 'Confirmer',
	'confirm.message': 'Êtes-vous sûr de vouloir continuer ?',
	'form.success': 'Formulaire soumis avec succès',
	'form.error': 'Erreur lors de la soumission',
	'pagination.showing': 'Affichage de {from} à {to} sur {total}',
	'pagination.page': 'Page {current}/{total}',
	'behavior.repeater.min': 'Ajoutez au moins {value} élément(s)',
	'behavior.repeater.max': 'Maximum {value} élément(s)',
	'behavior.repeater.item': 'Item {index} sur {total}',
	'behavior.repeater.add': 'Ajouter',
	'behavior.repeater.remove': 'Supprimer cet élément',
	'behavior.repeater.moveUp': 'Déplacer vers le haut',
	'behavior.repeater.moveDown': 'Déplacer vers le bas',
	'behavior.creatable.add': 'Ajouter « {query} »',
	'behavior.creatable.error': "Échec de la création — vérifiez la connexion puis réessayez.",
	'behavior.manageable.edit': 'Renommer',
	'behavior.manageable.remove': 'Supprimer',
	'behavior.manageable.undeletable': "Suppression impossible : élément encore référencé",
	'behavior.manageable.confirmRemove': 'Supprimer « {label} » ?',
	'behavior.manageable.error': "Échec de l'opération — vérifiez la connexion puis réessayez.",
	'field.file.drop': 'Glissez un fichier ici ou cliquez pour parcourir',
	'field.file.dropMultiple': 'Glissez des fichiers ici ou cliquez pour parcourir',
	'field.file.remove': 'Retirer ce fichier',
	'field.file.cancelUpload': "Annuler l'envoi",
	'field.file.download': 'Télécharger',
	'field.file.tooBig': 'trop volumineux (max {max})',
	'field.file.badType': 'type non accepté',
	'field.file.maxSizeHint': 'Taille max : {max} par fichier',
	'field.tree.search': 'Rechercher…',
	'field.tree.loading': 'Chargement…',
	'field.tree.empty': 'Aucune option',
	'field.tree.noMatch': 'Aucun résultat',
	'field.tree.expand': 'Déplier',
	'field.tree.collapse': 'Replier',
	'field.tree.expandAll': 'Tout déplier',
	'field.tree.collapseAll': 'Tout replier'
};

let overrides: Record<string, string | ((params: any) => string)> = {};

export function setMessages(messages: Record<string, string | ((params: any) => string)>): void {
	overrides = { ...overrides, ...messages };
}

export function resetMessages(): void {
	overrides = {};
}

/** Traduction avec interpolation {param} — semantics §8. */
export function t(key: string, params?: Record<string, any>): string {
	const raw = overrides[key] ?? defaultMessages[key] ?? key;
	const template = typeof raw === 'function' ? raw(params ?? {}) : raw;
	if (!params) return template;
	return template.replace(/\{(\w+)\}/g, (_, k) => String(params[k] ?? `{${k}}`));
}
