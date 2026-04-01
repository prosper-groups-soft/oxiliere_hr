export const formatShortTime = (date: Date) => {
	return date.toLocaleTimeString('en-US', {
		hour: 'numeric',
		minute: '2-digit',
		hour12: true
	});
};

export const formatDate = (dateString: string, showTime = false, shortFormat = false) => {
	if (shortFormat) {
		return new Date(dateString).toLocaleDateString('fr-FR', {
			year: 'numeric',
			month: '2-digit',
			day: '2-digit'
		});
	}

	return new Date(dateString).toLocaleDateString('fr-FR', {
		year: 'numeric',
		month: 'long',
		day: 'numeric',
		hour: showTime ? '2-digit' : undefined,
		minute: showTime ? '2-digit' : undefined
	});
};

export const calculateAge = (birthDate: string) => {
	const birth = new Date(birthDate);
	const today = new Date();
	let age = today.getFullYear() - birth.getFullYear();
	const monthDiff = today.getMonth() - birth.getMonth();
	if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
		age--;
	}
	return age;
};
