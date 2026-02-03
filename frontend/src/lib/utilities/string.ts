export function get_initials(...args: string[]) {
    return args
        .filter((arg) => arg && typeof arg === 'string' && arg.trim().length > 0)
        .map((arg) => arg.trim().charAt(0).toUpperCase())
        .join('');
}


export const formatShortTime = (date: Date) => {
	return date.toLocaleTimeString('en-US', {
		hour: 'numeric',
		minute: '2-digit',
		hour12: true
	});
};


export const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

