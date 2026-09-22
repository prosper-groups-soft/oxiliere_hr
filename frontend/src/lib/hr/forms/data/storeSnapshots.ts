// Pont testable vers les stores de l'app (principe standalone, vision §3) :
// forms/ n'importe jamais un store réel. L'appelant enregistre un snapshot :
// registerStoreSnapshot('orgUnits', [...]) puis dataSource: { type: 'store', store: 'orgUnits' }.
const snapshots = new Map<string, unknown>();

export function registerStoreSnapshot(name: string, value: unknown): void {
	snapshots.set(name, value);
}

export function getStoreSnapshot(name: string, property?: string): unknown {
	const root = snapshots.get(name);
	if (root == null) return undefined;
	if (!property) return root;
	if (typeof root === 'object' && root !== null) {
		return (root as Record<string, unknown>)[property];
	}
	return undefined;
}

/** Réservé aux tests : vide les snapshots. */
export function clearStoreSnapshots(): void {
	snapshots.clear();
}
