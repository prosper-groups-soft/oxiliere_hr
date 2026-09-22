import { goto } from '$app/navigation';

export const HR_BASE = '/hr' as const;
export const hr = (p: string) => `${HR_BASE}${p.startsWith('/') ? p : `/${p}`}`;


export enum MENU_ITEM_TYPE {
	link = 'link',
	router = 'router',
	button = 'button'
}


export type MenuItem = {
	id: string;
	path?: string;
	type: MENU_ITEM_TYPE;
	icon: string;
	label: string;
	countKey?: string;
	onClick?: () => void;
};


export type MenuItemGroup = {
	id: string;
	label?: string;
	items: MenuItem[];
};


export const MENU_ITEMS: MenuItemGroup[] = [
	{
		id: 'general',
		items: [
			{
				id: 'home',
				path: HR_BASE,
				type: MENU_ITEM_TYPE.router,
				icon: 'layout-dashboard',
				label: 'Tableau de bord',
				onClick: () => goto(HR_BASE)
			}
		]
	},
	{
		id: 'talent_group',
		label: 'Gestion des Talents',
		items: [
			{
				id: 'employees',
				path: hr('/employees'),
				type: MENU_ITEM_TYPE.router,
				icon: 'users',
				label: 'Employés',
				onClick: () => goto(hr('/employees'))
			},
			{
				id: 'jobs',
				path: hr('/jobs'),
				type: MENU_ITEM_TYPE.router,
				icon: 'development',
				label: 'Postes & Org.',
				onClick: () => goto(hr('/jobs/chart'))
			},
			{
				id: 'onboarding',
				path: hr('/employees/onboarding'),
				type: MENU_ITEM_TYPE.router,
				icon: 'app',
				label: 'Onboarding',
				countKey: 'onboarding_active',
				onClick: () => goto(hr('/employees/onboarding'))
			},
			{
				id: 'recruitment',
				path: hr('/recruitment'),
				type: MENU_ITEM_TYPE.router,
				icon: 'consulting',
				label: 'Recrutement',
				onClick: () => goto(hr('/recruitment'))
			},
			{
				id: 'performance',
				path: hr('/performance'),
				type: MENU_ITEM_TYPE.router,
				icon: 'target',
				label: 'Évaluations',
				onClick: () => goto(hr('/performance/campaigns'))
			}
		]
	},
	{
		id: 'ops_group',
		label: 'Opérations',
		items: [
			{
				id: 'attendance',
				path: hr('/attendance'),
				type: MENU_ITEM_TYPE.router,
				icon: 'monitoring',
				label: 'Présences',
				onClick: () => goto(hr('/attendance/register'))
			},
			{
				id: 'calendar',
				path: hr('/calendar'),
				type: MENU_ITEM_TYPE.router,
				icon: 'calendar',
				label: 'Calendrier',
				onClick: () => goto(hr('/calendar'))
			},
			{
				id: 'leaves',
				path: hr('/leaves'),
				type: MENU_ITEM_TYPE.router,
				icon: 'calendar-days',
				label: 'Congés',
				countKey: 'leaves_pending',
				onClick: () => goto(hr('/leaves/requests'))
			}
		]
	},
	{
		id: 'finance_group',
		label: 'Finance',
		items: [
			{
				id: 'payroll',
				path: hr('/payroll'),
				type: MENU_ITEM_TYPE.router,
				icon: 'finance',
				label: 'Paie',
				onClick: () => goto(hr('/payroll'))
			},
			{
				id: 'banking',
				path: hr('/banking'),
				type: MENU_ITEM_TYPE.router,
				icon: 'landmark',
				label: 'Comptes Bancaires',
				onClick: () => goto(hr('/banking/accounts'))
			}
		]
	},
	{
		id: 'admin_group',
		label: 'Configuration',
		items: [
			{
				id: 'admin-users',
				path: hr('/admin/users'),
				type: MENU_ITEM_TYPE.router,
				icon: 'shield-check',
				label: 'Utilisateurs',
				onClick: () => goto(hr('/admin/users'))
			},
			{
				id: 'admin-company',
				path: hr('/admin/my-company'),
				type: MENU_ITEM_TYPE.router,
				icon: 'office',
				label: 'Mon Entreprise',
				onClick: () => goto(hr('/admin/my-company'))
			}
		]
	}
];


export const bottomMenuItems: MenuItem[] = [
	{
		id: 'guide',
		type: MENU_ITEM_TYPE.button,
		icon: 'education',
		label: "Centre d'aide",
		onClick: () => {}
	}
];


export const PAGE_LABELS: Record<string, string> = {
	hr:           'Ressources Humaines',
	employees:    'Employés',
	documents:    'Documents',
	family:       'Famille',
	settings:     'Paramètres',
	users:        'Utilisateurs',
	tax:          'Configuration fiscale IPR & Social',
	"my-company": 'Paramètres de l\'entreprise',
	onboarding:   'Onboarding',
	dashboard:    'Tableau de bord',
	jobs:         'Postes & Org.',
	chart:        'Organigramme',
	careers:      'Catalogue des postes',
	mobility:     'Mobilité & Transitions',
	pipeline:     'Pipeline de recrutement',
	recruitment:  'Recrutement',
	candidates:   'Candidats',
	scheduler:    'Planification',
	calendar:     'Calendrier',
	attendance:   'Présences',
	register:     'Suivi quotidien',
	config:       'Gestion des cycles',
	policies:     'Modèles de travail',
	leaves:       'Configuration des congés',
	requests:     'Mes Congés',
	team:         'Vue Équipe',
	banking:      'Comptes Bancaires',
	accounts:     'Mes Comptes',
	directory:    'Institutions',
	payroll:      'Paie',
	"payroll-settings": 'Configuration paie',
	run:          'Exécution',
	payslips:     'Bulletins de paie',
	advances:     'Avances',
	compliance:   'Conformité',
	reports:      'Rapports d\'Exports',
	admin:        'Administration',
	audit:        'Audit Système',
	logs:         'Journal des événements',
	access:       'Sécurité & Accès',
    profile:      'Profil',
    contract:     'Contrat',
    account:      'Accès',
    timeline:     'Parcours',
	education:    'Éducation',
    performance:  'Évaluations',
    reviews:      'Mes Évaluations',
    campaigns:    'Campagnes'
};


export const NAV_CONFIG = {
	// Dimensions
	sidebarWidth: 260,
	sidebarCollapsedWidth: 68,
	topBarHeight: 64,

	// Behaviors
	transitionSpeed: 250,
	mobileBreakpoint: 768,

	// Initial state
	defaultExpanded: true,

	// Limits
	maxBreadcrumbItems: 4
};


export const APP_STORAGE_KEY = 'hr_app_user_settings';


/**
 * Default values for persistent storage.
 * Note: sidebarExpanded now uses NAV_CONFIG.defaultExpanded
 */
export const DEFAULT_SETTINGS = {
	sidebarExpanded: NAV_CONFIG.defaultExpanded,
	theme: 'light' as 'light' | 'dark',
	language: 'fr'
};


export type UserSettings = typeof DEFAULT_SETTINGS;

