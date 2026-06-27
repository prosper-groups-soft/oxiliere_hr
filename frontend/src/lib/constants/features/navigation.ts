import { goto } from '$app/navigation';

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
				path: '/',
				type: MENU_ITEM_TYPE.router,
				icon: 'layout-dashboard',
				label: 'Tableau de bord',
				onClick: () => goto('/')
			}
		]
	},
	{
		id: 'talent_group',
		label: 'Gestion des Talents',
		items: [
			{
				id: 'employees',
				path: '/employees',
				type: MENU_ITEM_TYPE.router,
				icon: 'users',
				label: 'Employés',
				onClick: () => goto('/employees')
			},
			{
				id: 'jobs',
				path: '/jobs',
				type: MENU_ITEM_TYPE.router,
				icon: 'development',
				label: 'Postes & Org.',
				onClick: () => goto('/jobs/chart')
			},
			{
				id: 'onboarding',
				path: '/employees/onboarding',
				type: MENU_ITEM_TYPE.router,
				icon: 'app',
				label: 'Onboarding',
				countKey: 'onboarding_active',
				onClick: () => goto('/employees/onboarding')
			},
			{
				id: 'recruitment',
				path: '/recruitment',
				type: MENU_ITEM_TYPE.router,
				icon: 'consulting',
				label: 'Recrutement',
				onClick: () => goto('/recruitment')
			},
			{
				id: 'performance',
				path: '/performance',
				type: MENU_ITEM_TYPE.router,
				icon: 'target',
				label: 'Évaluations',
				onClick: () => goto('/performance/reviews')
			}
		]
	},
	{
		id: 'ops_group',
		label: 'Opérations',
		items: [
			{
				id: 'attendance',
				path: '/attendance',
				type: MENU_ITEM_TYPE.router,
				icon: 'monitoring',
				label: 'Présences',
				onClick: () => goto('/attendance/register')
			},
			{
				id: 'calendar',
				path: '/calendar',
				type: MENU_ITEM_TYPE.router,
				icon: 'calendar',
				label: 'Calendrier',
				onClick: () => goto('/calendar')
			},
			{
				id: 'leaves',
				path: '/leaves',
				type: MENU_ITEM_TYPE.router,
				icon: 'calendar-days',
				label: 'Congés',
				countKey: 'leaves_pending',
				onClick: () => goto('/leaves/requests')
			}
		]
	},
	{
		id: 'finance_group',
		label: 'Finance',
		items: [
			{
				id: 'payroll',
				path: '/payroll',
				type: MENU_ITEM_TYPE.router,
				icon: 'finance',
				label: 'Paie',
				onClick: () => goto('/payroll/payslips')
			},
			{
				id: 'banking',
				path: '/banking',
				type: MENU_ITEM_TYPE.router,
				icon: 'landmark',
				label: 'Comptes Bancaires',
				onClick: () => goto('/banking/accounts')
			}
		]
	},
	{
		id: 'admin_group',
		label: 'Configuration',
		items: [
			{
				id: 'audit',
				path: '/admin/audit',
				type: MENU_ITEM_TYPE.router,
				icon: 'reports',
				label: 'Audit',
				onClick: () => goto('/admin/audit')
			},
			{
				id: 'settings',
				path: '/admin/settings',
				type: MENU_ITEM_TYPE.router,
				icon: 'settings',
				label: 'Paramètres',
				onClick: () => goto('/admin/settings/access')
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

