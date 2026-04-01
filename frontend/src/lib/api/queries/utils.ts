export function getStaleTime(min: number) {
	return import.meta.env.DEV ? 0 : min * 60 * 1000;
}
