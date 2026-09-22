// Bindings data-aware des types `employee` et `manager` — le module employees
// possède la source (règle avancement §2.1). Enregistrés via
// forms-bindings/index.ts, jamais importés directement par les consommateurs.
import { defineBusinessType } from '@/hr/forms-bindings/defineBusinessType.js';
import { employeesEndpoint } from '@/hr/modules/employees/api/employees.endpoints.js';
import type { Employee, EmployeeFullProfile } from '@/hr/modules/employees/types/types.js';
import { buildFullName } from '@/hr/utilities/common/employee.utils';
import EmployeePicker from '../pickers/EmployeePicker.svelte';

// Nom composé partout dans le même ordre : last_name + middle_name + first_name.
function employeeLabel(e: Employee): string {
	return buildFullName(e) ?? e.name ?? String(e.id);
}

/** retrieve renvoie le profil complet — on l'aligne sur le shape Employee
 * consommé par l'adapter (name composé, prénom/nom bruts, poste). */
function profileToEmployee(p: EmployeeFullProfile): Employee {
	return {
		id: p.id,
		name: buildFullName(p) ?? String(p.id),
		jobTitle: p.job_title ?? '',
		status: '',
		location: '',
		contractType: '',
		joinDate: '',
		phone: p.phone ?? '',
		email: p.email ?? '',
		avatarUrl: p.profile_photo ?? p.user?.photo ?? '',
		role: '',
		first_name: p.first_name,
		middle_name: p.middle_name,
		last_name: p.last_name,
		matricule: p.matricule
	};
}

let registered = false;

/** Enregistre les types métier du module employees (idempotent). */
export function registerEmployeeTypes(): void {
	if (registered) return;
	registered = true;

	defineBusinessType<Employee>('employee', {
		fetch: async ({ search, page, pageSize }) => {
			const res = await employeesEndpoint.list({ search, page, limit: pageSize });
			return res.results ?? [];
		},
		resolve: async (id) => profileToEmployee(await employeesEndpoint.retrieve(id)),
		adapter: {
			value: (e) => String(e.id),
			label: employeeLabel,
			// Liste : EmployeeOut backend (snake_case job_title) ; resolve : profil camel.
			sublabel: (e) => e.jobTitle ?? (e as any).job_title ?? '',
			haystack: (e) =>
				`${e.name ?? ''} ${e.matricule ?? ''} ${e.last_name ?? ''} ${e.middle_name ?? ''} ${e.first_name ?? ''} ${(e as any).job_title ?? ''}`
		},
		// pageSize réduit (10) pour tester le bouton « Voir plus » en dev — remettre à 10+ en prod.
		pageSize: 10,
		renderer: EmployeePicker,
		cacheTtl: 60_000,
		behaviors: ['searchable']
	});

	// `manager` = un employé filtré « a un rôle de manager ». L'API n'expose pas
	// encore de filtre manager et Employee ne porte aucun champ exploitable :
	// on garde le même picker que `employee` en attendant le filtre backend.
	// TODO backend : param `is_manager=true` sur GET /api/employees, puis
	// restreindre le fetch ici.
	defineBusinessType<Employee>('manager', {
		fetch: async ({ search, page, pageSize }) => {
			const res = await employeesEndpoint.list({ search, page, limit: pageSize });
			return res.results ?? [];
		},
		resolve: async (id) => profileToEmployee(await employeesEndpoint.retrieve(id)),
		adapter: {
			value: (e) => String(e.id),
			label: employeeLabel,
			// Liste : EmployeeOut backend (snake_case job_title) ; resolve : profil camel.
			sublabel: (e) => e.jobTitle ?? (e as any).job_title ?? '',
			haystack: (e) =>
				`${e.name ?? ''} ${e.matricule ?? ''} ${e.last_name ?? ''} ${e.middle_name ?? ''} ${e.first_name ?? ''} ${(e as any).job_title ?? ''}`
		},
		renderer: EmployeePicker,
		cacheTtl: 60_000,
		behaviors: ['searchable']
	});
}
