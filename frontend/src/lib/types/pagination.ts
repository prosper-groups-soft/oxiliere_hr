/**
 * Represents the structure of a paginated API response, commonly used by Django REST Framework and Ninja Extra.
 * @template T The type of the items in the results array.
 */
export type PaginatedResponse<T> = {
	count: number;
	next: string | null;
	previous: string | null;
	results: T[];
};
