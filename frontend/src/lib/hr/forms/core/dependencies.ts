// Dépendances déclaratives — pur TS, sans Svelte (api §8, semantics §6).
// Évalue visibleIf/enabledIf/requiredIf/reloadIf + graphe dependsOn + cycles.
import type { Condition, FieldConfig } from './types.js';

function keyOf(field: Pick<FieldConfig, 'id' | 'name'>): string {
	return field.name ?? field.id;
}

export function normalizeDependsOn(dep?: string | string[]): string[] {
	if (!dep) return [];
	return Array.isArray(dep) ? [...dep] : [dep];
}

/** Clés sources d'une config : dependsOn + clés des Record<Condition>. */
export function collectSourceKeys(
	dep: NonNullable<FieldConfig['dependencies']>
): string[] {
	const out = new Set<string>(normalizeDependsOn(dep.dependsOn));
	for (const c of [dep.visibleIf, dep.enabledIf, dep.requiredIf, dep.reloadIf]) {
		if (c && typeof c === 'object' && !Array.isArray(c)) {
			for (const k of Object.keys(c as Record<string, Condition>)) out.add(k);
		}
	}
	return [...out];
}

function evalSingle(cond: Condition, value: any): boolean {
	if (typeof cond === 'boolean') return cond;
	if (typeof cond === 'function') {
		try {
			return !!(cond as (v: any) => boolean)(value);
		} catch {
			return false;
		}
	}
	return !!cond;
}

/**
 * Évalue une condition contre les valeurs du formulaire.
 * - undefined → undefined (pas d'avis, garde la valeur statique)
 * - boolean → tel quel
 * - function → appelée avec les valeurs sources dans l'ordre dependsOn ;
 *   sans dependsOn, appelée avec l'objet values complet (compat exemples).
 * - Record → AND des sous-conditions, chacune testée contre values[key].
 */
export function evalCondition(
	cond: Condition | Record<string, Condition> | undefined,
	values: Record<string, any>,
	dependsOn?: string | string[]
): boolean | undefined {
	if (cond === undefined) return undefined;
	if (typeof cond === 'boolean') return cond;
	if (typeof cond === 'function') {
		const sources = normalizeDependsOn(dependsOn);
		try {
			if (sources.length > 0) {
				return !!(
					cond as (...args: any[]) => boolean
				)(...sources.map((k) => values[k]));
			}
			return !!(cond as (v: any) => boolean)(values);
		} catch {
			return false;
		}
	}
	if (typeof cond === 'object') {
		const entries = Object.entries(cond as Record<string, Condition>);
		if (entries.length === 0) return undefined;
		return entries.every(([k, c]) => evalSingle(c, values[k]));
	}
	return undefined;
}

export function buildDependencyGraph(fields: FieldConfig[]): Map<string, string[]> {
	const graph = new Map<string, string[]>();
	for (const f of fields) {
		const dep = f.dependencies;
		if (!dep) continue;
		const target = keyOf(f);
		for (const src of collectSourceKeys(dep)) {
			if (src === target) continue;
			if (!graph.has(src)) graph.set(src, []);
			graph.get(src)!.push(target);
		}
	}
	return graph;
}

/** Ordre topologique des dépendants transitifs d'une clé changée (BFS, sans doublon). */
export function dependentsOf(graph: Map<string, string[]>, changedKey: string): string[] {
	const out: string[] = [];
	const seen = new Set<string>([changedKey]);
	const queue = [...(graph.get(changedKey) ?? [])];
	while (queue.length) {
		const cur = queue.shift()!;
		if (seen.has(cur)) continue;
		seen.add(cur);
		out.push(cur);
		for (const nxt of graph.get(cur) ?? []) if (!seen.has(nxt)) queue.push(nxt);
	}
	return out;
}

/** Throw si cycle dans le graphe de dépendances. */
export function detectCycle(fields: FieldConfig[]): void {
	const graph = buildDependencyGraph(fields);
	const visited = new Set<string>();
	const stack = new Set<string>();
	const path: string[] = [];
	const visit = (node: string): void => {
		if (stack.has(node)) {
			const i = path.indexOf(node);
			const cyc = [...path.slice(i), node].join(' → ');
			throw new Error(`[forms] Dépendance circulaire : ${cyc}`);
		}
		if (visited.has(node)) return;
		visited.add(node);
		stack.add(node);
		path.push(node);
		for (const nxt of graph.get(node) ?? []) visit(nxt);
		stack.delete(node);
		path.pop();
	};
	for (const f of fields) visit(keyOf(f));
}

export function and(...conds: Array<(v: any) => boolean>): (v: any) => boolean {
	return (v: any) => conds.every((c) => c(v));
}

export function or(...conds: Array<(v: any) => boolean>): (v: any) => boolean {
	return (v: any) => conds.some((c) => c(v));
}

export function not(cond: (v: any) => boolean): (v: any) => boolean {
	return (v: any) => !cond(v);
}
