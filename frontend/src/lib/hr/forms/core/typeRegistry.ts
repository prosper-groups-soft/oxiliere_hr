// Registre de types personnalisés (api §14) : defaultRenderer / defaultDataSource / validators / behaviors.
// Pur TS, sans dépendance Svelte. La DataSource par défaut est résolue via resolveDataSource.
import type { TypeDefinition } from './types.js';

const registry = new Map<string, TypeDefinition>();

export function registerType(name: string, definition: TypeDefinition): void {
	registry.set(name, definition);
}

export function getTypeDefinition(name: string): TypeDefinition | undefined {
	return registry.get(name);
}

export function hasType(name: string): boolean {
	return registry.has(name);
}

/** Résout une entité par id via la définition du type (hydratation des renderers
 * riches : valeur définie mais option absente du chargement lazy). */
export async function resolveTypeEntity<T = any>(name: string, id: string): Promise<T | null> {
	const def = registry.get(name);
	if (!def?.resolve) return null;
	return (await def.resolve(id)) as T | null;
}

/** Réservé aux tests : vide le registre. */
export function clearTypes(): void {
	registry.clear();
}
