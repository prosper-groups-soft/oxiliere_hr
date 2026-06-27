// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type WithoutChild<T> = T extends { child?: any } ? Omit<T, 'child'> : T;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type WithoutChildren<T> = T extends { children?: any } ? Omit<T, 'children'> : T;

export type WithoutChildrenOrChild<T> = WithoutChildren<WithoutChild<T>>;

export type WithElementRef<T, U extends HTMLElement = HTMLElement> = T & { ref?: U | null };


/**
 * Interface pour les réponses paginées de l'API
 * Format standard: { results: T[], count: number, next: string|null, previous: string|null }
 */
export interface PaginatedResponse<T> {
	results: T[];
	count: number;
	next: string | null;
	previous: string | null;
}

