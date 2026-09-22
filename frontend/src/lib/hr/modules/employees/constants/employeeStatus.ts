/**
 * Configuration des statuts employé avec couleurs cohérentes
 * Utilisée par EmployeeCard, EmployeeRow et autres composants
 */
export interface EmployeeStatusConfig {
	dot: string;
	bg: string;
	color: string;
	label: string;
}


export const EMPLOYEE_STATUS_CONFIG: Record<string, EmployeeStatusConfig> = {
	"ACTIVE": {
		dot: "bg-emerald-400",
		bg: "bg-emerald-50",
		color: "text-emerald-600",
		label: "Actif"
	},
	"PROBATION": {
		dot: "bg-blue-400",
		bg: "bg-blue-50",
		color: "text-blue-600",
		label: "Période d'essai"
	},
	"PENDING": {
		dot: "bg-amber-400",
		bg: "bg-amber-50",
		color: "text-amber-600",
		label: "En attente"
	},
	"SUSPENDED": {
		dot: "bg-rose-400",
		bg: "bg-rose-50",
		color: "text-rose-600",
		label: "Suspendu"
	},
	"TERMINATED": {
		dot: "bg-slate-300",
		bg: "bg-slate-100",
		color: "text-slate-500",
		label: "Départ"
	},
	"RESIGNED": {
		dot: "bg-slate-300",
		bg: "bg-slate-100",
		color: "text-slate-500",
		label: "Démission"
	},
	"RETIRED": {
		dot: "bg-indigo-400",
		bg: "bg-indigo-50",
		color: "text-indigo-600",
		label: "Retraité"
	}
};


/**
 * Récupère la configuration d'un statut avec fallback sur "ACTIVE"
 */
export function getEmployeeStatusConfig(status: string | undefined): EmployeeStatusConfig {
	return EMPLOYEE_STATUS_CONFIG[status || ""] || EMPLOYEE_STATUS_CONFIG["ACTIVE"];
}


/**
 * Récupère la configuration du point de statut (utilisé sur les avatars)
 */
export function getEmployeeStatusDotConfig(status: string | undefined) {
	switch (status) {
		case 'ACTIVE':
			return { color: 'bg-emerald-500', title: 'Employé actif' };
		case 'PROBATION':
			return { color: 'bg-blue-500',     title: 'Période d\'essai' };
		case 'PENDING':
			return { color: 'bg-amber-500',   title: 'En attente de début' };
		case 'SUSPENDED':
			return { color: 'bg-red-500',      title: 'Contrat suspendu' };
		case 'MATERNITY_LEAVE':
			return { color: 'bg-amber-400', title: 'Congé maternité' };
		case 'SICK_LEAVE':
			return { color: 'bg-amber-400', title: 'Congé maladie' };
		case 'SABBATICAL':
			return { color: 'bg-amber-400', title: 'Congé sabbatique' };
		case 'TERMINATED':
			return { color: 'bg-slate-400', title: 'Départ' };
		case 'RESIGNED':
			return { color: 'bg-slate-400', title: 'Démission' };
		case 'RETIRED':
			return { color: 'bg-slate-400', title: 'Retraité' };
		default:
			return { color: 'bg-slate-300', title: 'Statut inconnu' };
	}
}

