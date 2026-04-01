export function getInitials(...args: string[]) {
	return args
		.filter((arg) => arg && typeof arg === 'string' && arg.trim().length > 0)
		.map((arg) => arg.trim().charAt(0).toUpperCase())
		.join('')
		.slice(0, 2);
}
