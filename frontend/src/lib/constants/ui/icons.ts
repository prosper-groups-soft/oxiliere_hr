import type { Component } from 'svelte';
import type { IconProps } from '@lucide/svelte';
import { Package } from '@lucide/svelte';


type Icon = Component<IconProps, {}>;


// Mapping des noms d'icônes vers les modules Lucide
// Utilise lazy loading pour éviter de charger toutes les icônes au démarrage
export const ICON_MODULES: Record<string, () => Promise<any>> = {
	// Gestion d'équipe et RH
	users: () => import('@lucide/svelte').then(m => m.Users),
	'circle-user': () => import('@lucide/svelte').then(m => m.CircleUser),
	'no-user': () => import('@lucide/svelte').then(m => m.UserRoundX),
	user: () => import('@lucide/svelte').then(m => m.User),
	team: () => import('@lucide/svelte').then(m => m.Users),
	hr: () => import('@lucide/svelte').then(m => m.Users),
	crm: () => import('@lucide/svelte').then(m => m.Users),
	'user-check': () => import('@lucide/svelte').then(m => m.UserCheck),
	'user-cog': () => import('@lucide/svelte').then(m => m.UserCog),
	'user-minus': () => import('@lucide/svelte').then(m => m.UserMinus),
	'user-plus': () => import('@lucide/svelte').then(m => m.UserPlus),
	'user-search': () => import('@lucide/svelte').then(m => m.UserSearch),

	// Feedback & Évaluation
	'thumbs-up': () => import('@lucide/svelte').then(m => m.ThumbsUp),
	'thumbs-down': () => import('@lucide/svelte').then(m => m.ThumbsDown),
	'trending-up': () => import('@lucide/svelte').then(m => m.TrendingUp),

	// Communication
	'message-square': () => import('@lucide/svelte').then(m => m.MessageSquare),
	chat: () => import('@lucide/svelte').then(m => m.MessageSquare),
	messaging: () => import('@lucide/svelte').then(m => m.MessageSquare),
	slack: () => import('@lucide/svelte').then(m => m.MessageSquare),
	teams: () => import('@lucide/svelte').then(m => m.MessageSquare),
	discord: () => import('@lucide/svelte').then(m => m.MessageSquare),
	linkedin: () => import('@lucide/svelte').then(m => m.Linkedin),
	mail: () => import('@lucide/svelte').then(m => m.Mail),
	email: () => import('@lucide/svelte').then(m => m.Mail),
	message: () => import('@lucide/svelte').then(m => m.Send),
	send: () => import('@lucide/svelte').then(m => m.Send),
	'paper-plane': () => import('@lucide/svelte').then(m => m.Send),
	inbox: () => import('@lucide/svelte').then(m => m.Inbox),

	// Documentation
	docs: () => import('@lucide/svelte').then(m => m.FileText),
	wiki: () => import('@lucide/svelte').then(m => m.FileText),
	notion: () => import('@lucide/svelte').then(m => m.FileText),
	confluence: () => import('@lucide/svelte').then(m => m.FileText),
	'book-open': () => import('@lucide/svelte').then(m => m.BookOpen),
	file: () => import('@lucide/svelte').then(m => m.FileText),
	'file-text': () => import('@lucide/svelte').then(m => m.FileText),
	'file-check': () => import('@lucide/svelte').then(m => m.FileCheck),
	files: () => import('@lucide/svelte').then(m => m.Files),
	'file-plus': () => import('@lucide/svelte').then(m => m.FilePlus),
	folder: () => import('@lucide/svelte').then(m => m.Folder),
	'folder-open': () => import('@lucide/svelte').then(m => m.FolderOpen),
	'align-left': () => import('@lucide/svelte').then(m => m.TextAlignStart),
	list: () => import('@lucide/svelte').then(m => m.List),
	'list-check': () => import('@lucide/svelte').then(m => m.ListCheck),

	// Analytics et reporting
	analytics: () => import('@lucide/svelte').then(m => m.ChartBar),
	dashboard: () => import('@lucide/svelte').then(m => m.ChartBar),
	'layout-dashboard': () => import('@lucide/svelte').then(m => m.LayoutDashboard),
	reports: () => import('@lucide/svelte').then(m => m.ChartBar),
	'chart-area': () => import('@lucide/svelte').then(m => m.ChartArea),
	activity: () => import('@lucide/svelte').then(m => m.Activity),
	monitoring: () => import('@lucide/svelte').then(m => m.Activity),
	performance: () => import('@lucide/svelte').then(m => m.Activity),

	// Administration
	settings: () => import('@lucide/svelte').then(m => m.Settings),
	admin: () => import('@lucide/svelte').then(m => m.Settings),
	config: () => import('@lucide/svelte').then(m => m.Settings),
	'settings-2': () => import('@lucide/svelte').then(m => m.Settings2),

	// Finance
	finance: () => import('@lucide/svelte').then(m => m.CreditCard),
	accounting: () => import('@lucide/svelte').then(m => m.Calculator),
	billing: () => import('@lucide/svelte').then(m => m.CreditCard),
	stripe: () => import('@lucide/svelte').then(m => m.CreditCard),
	paypal: () => import('@lucide/svelte').then(m => m.CreditCard),
	bank: () => import('@lucide/svelte').then(m => m.Landmark),
	'dollar-sign': () => import('@lucide/svelte').then(m => m.DollarSign),
	wallet: () => import('@lucide/svelte').then(m => m.Wallet),
	landmark: () => import('@lucide/svelte').then(m => m.Landmark),
	banknote: () => import('@lucide/svelte').then(m => m.Banknote),
	coins: () => import('@lucide/svelte').then(m => m.Coins),
	receipt: () => import('@lucide/svelte').then(m => m.Receipt),
	calculator: () => import('@lucide/svelte').then(m => m.Calculator),
	power: () => import('@lucide/svelte').then(m => m.Power),

	// Base de données
	database: () => import('@lucide/svelte').then(m => m.Database),
	mysql: () => import('@lucide/svelte').then(m => m.Database),
	postgresql: () => import('@lucide/svelte').then(m => m.Database),
	mongodb: () => import('@lucide/svelte').then(m => m.Database),
	server: () => import('@lucide/svelte').then(m => m.Server),
	hosting: () => import('@lucide/svelte').then(m => m.Server),

	// Web
	web: () => import('@lucide/svelte').then(m => m.Globe),
	website: () => import('@lucide/svelte').then(m => m.Globe),
	wordpress: () => import('@lucide/svelte').then(m => m.Globe),
	globe: () => import('@lucide/svelte').then(m => m.Globe),

	// Sécurité
	security: () => import('@lucide/svelte').then(m => m.Lock),
	auth: () => import('@lucide/svelte').then(m => m.Lock),
	firewall: () => import('@lucide/svelte').then(m => m.Shield),
	shield: () => import('@lucide/svelte').then(m => m.Shield),
	'shield-alert': () => import('@lucide/svelte').then(m => m.ShieldAlert),
	'shield-check': () => import('@lucide/svelte').then(m => m.ShieldCheck),
	key: () => import('@lucide/svelte').then(m => m.Key),
	lock: () => import('@lucide/svelte').then(m => m.Lock),
	unlock: () => import('@lucide/svelte').then(m => m.LockOpen),

	// Mobile
	mobile: () => import('@lucide/svelte').then(m => m.Smartphone),
	app: () => import('@lucide/svelte').then(m => m.Smartphone),

	// Calendrier
	calendar: () => import('@lucide/svelte').then(m => m.Calendar),
	schedule: () => import('@lucide/svelte').then(m => m.Calendar),
	'calendar-days': () => import('@lucide/svelte').then(m => m.CalendarDays),
	'calendar-clock': () => import('@lucide/svelte').then(m => m.CalendarClock),
	'calendar-off': () => import('@lucide/svelte').then(m => m.CalendarOff),
	'calendar-minus': () => import('@lucide/svelte').then(m => m.CalendarMinus),
	'calendar-plus': () => import('@lucide/svelte').then(m => m.CalendarPlus),
	'calendar-range': () => import('@lucide/svelte').then(m => m.CalendarRange),
	clock: () => import('@lucide/svelte').then(m => m.Clock),
	'stethoscope': () => import('@lucide/svelte').then(m => m.Stethoscope),
	'clipboard-list': () => import('@lucide/svelte').then(m => m.ClipboardList),
	time: () => import('@lucide/svelte').then(m => m.Clock),
	sun: () => import('@lucide/svelte').then(m => m.Sun),
	cake: () => import('@lucide/svelte').then(m => m.Cake),

	// E-commerce
	shop: () => import('@lucide/svelte').then(m => m.ShoppingCart),
	ecommerce: () => import('@lucide/svelte').then(m => m.ShoppingCart),
	shopify: () => import('@lucide/svelte').then(m => m.ShoppingCart),
	cart: () => import('@lucide/svelte').then(m => m.ShoppingCart),
	'tag': () => import('@lucide/svelte').then(m => m.Tag),

	// Entreprise
	business: () => import('@lucide/svelte').then(m => m.Building2),
	corporate_fare: () => import('@lucide/svelte').then(m => m.Building),
	building: () => import('@lucide/svelte').then(m => m.Building),
	'building-2': () => import('@lucide/svelte').then(m => m.Building2),
	office: () => import('@lucide/svelte').then(m => m.Building2),
	erp: () => import('@lucide/svelte').then(m => m.Building2),
	location: () => import('@lucide/svelte').then(m => m.MapPin),
	pin: () => import('@lucide/svelte').then(m => m.MapPin),
	'map-pin': () => import('@lucide/svelte').then(m => m.MapPin),
	store: () => import('@lucide/svelte').then(m => m.Store),
	briefcase: () => import('@lucide/svelte').then(m => m.Briefcase),
	consulting: () => import('@lucide/svelte').then(m => m.Briefcase),
	services: () => import('@lucide/svelte').then(m => m.Briefcase),

	// Éducation
	education: () => import('@lucide/svelte').then(m => m.GraduationCap),
	learning: () => import('@lucide/svelte').then(m => m.GraduationCap),
	'graduation-cap': () => import('@lucide/svelte').then(m => m.GraduationCap),
	brain: () => import('@lucide/svelte').then(m => m.Brain),

	// Santé
	health: () => import('@lucide/svelte').then(m => m.Heart),
	medical: () => import('@lucide/svelte').then(m => m.Heart),
	heart: () => import('@lucide/svelte').then(m => m.Heart),
	baby: () => import('@lucide/svelte').then(m => m.Baby),

	// Transport / Logistique
	truck: () => import('@lucide/svelte').then(m => m.Truck),
	moving: () => import('@lucide/svelte').then(m => m.Truck),
	'ellipsis': () => import('@lucide/svelte').then(m => m.Ellipsis),

	// Développement
	dev: () => import('@lucide/svelte').then(m => m.Code),
	development: () => import('@lucide/svelte').then(m => m.Code),
	git: () => import('@lucide/svelte').then(m => m.Code),
	'git-branch': () => import('@lucide/svelte').then(m => m.GitBranch),
	github: () => import('@lucide/svelte').then(m => m.Code),
	code: () => import('@lucide/svelte').then(m => m.Code),

	// Infrastructure
	cloud: () => import('@lucide/svelte').then(m => m.Cloud),
	aws: () => import('@lucide/svelte').then(m => m.Cloud),
	azure: () => import('@lucide/svelte').then(m => m.Cloud),

	// UI Elements
	grid: () => import('@lucide/svelte').then(m => m.LayoutGrid),
	'layout-grid': () => import('@lucide/svelte').then(m => m.LayoutGrid),
	logout: () => import('@lucide/svelte').then(m => m.LogOut),
	refresh: () => import('@lucide/svelte').then(m => m.RefreshCcw),
	'refresh-cw': () => import('@lucide/svelte').then(m => m.RefreshCw),
	'refresh-ccw': () => import('@lucide/svelte').then(m => m.RefreshCcw),
	rotate: () => import('@lucide/svelte').then(m => m.RefreshCcw),
	grip: () => import('@lucide/svelte').then(m => m.Grip),
	filter: () => import('@lucide/svelte').then(m => m.Funnel),
	funnel: () => import('@lucide/svelte').then(m => m.Funnel),
	chevron: () => import('@lucide/svelte').then(m => m.ChevronDown),
	'chevron-down': () => import('@lucide/svelte').then(m => m.ChevronDown),
	'chevron-up': () => import('@lucide/svelte').then(m => m.ChevronUp),
	'chevron-left': () => import('@lucide/svelte').then(m => m.ChevronLeft),
	'chevron-right': () => import('@lucide/svelte').then(m => m.ChevronRight),
	prev: () => import('@lucide/svelte').then(m => m.ChevronLeft),
	first: () => import('@lucide/svelte').then(m => m.ChevronsLeft),
	next: () => import('@lucide/svelte').then(m => m.ChevronRight),
	last: () => import('@lucide/svelte').then(m => m.ChevronsRight),
	'arrow-left': () => import('@lucide/svelte').then(m => m.ArrowLeft),
	'arrow-up': () => import('@lucide/svelte').then(m => m.ArrowUp),
	'arrow-right': () => import('@lucide/svelte').then(m => m.ArrowRight),
	'arrow-down': () => import('@lucide/svelte').then(m => m.ArrowDown),
	'arrow-down-up': () => import('@lucide/svelte').then(m => m.ArrowDownUp),
	'arrow-up-left': () => import('@lucide/svelte').then(m => m.ArrowUpLeft),
	'arrow-up-right': () => import('@lucide/svelte').then(m => m.ArrowUpRight),
	'arrow-left-right': () => import('@lucide/svelte').then(m => m.ArrowLeftRight),
	'arrow-down-left': () => import('@lucide/svelte').then(m => m.ArrowDownLeft),
	'arrow-down-right': () => import('@lucide/svelte').then(m => m.ArrowDownRight),
	search: () => import('@lucide/svelte').then(m => m.Search),
	'search-x': () => import('@lucide/svelte').then(m => m.SearchX),
	close: () => import('@lucide/svelte').then(m => m.X),
	x: () => import('@lucide/svelte').then(m => m.X),
	archive: () => import('@lucide/svelte').then(m => m.Archive),
	plus: () => import('@lucide/svelte').then(m => m.Plus),
	add: () => import('@lucide/svelte').then(m => m.Plus),
	minus: () => import('@lucide/svelte').then(m => m.Minus),
	home: () => import('@lucide/svelte').then(m => m.House),
	house: () => import('@lucide/svelte').then(m => m.House),
	'more-horizontal': () => import('@lucide/svelte').then(m => m.Ellipsis),
	'more-vertical': () => import('@lucide/svelte').then(m => m.EllipsisVertical),
	download: () => import('@lucide/svelte').then(m => m.Download),
	upload: () => import('@lucide/svelte').then(m => m.Upload),
	'cloud-upload': () => import('@lucide/svelte').then(m => m.CloudUpload),
	eye: () => import('@lucide/svelte').then(m => m.Eye),
	'eye-off': () => import('@lucide/svelte').then(m => m.EyeOff),
	check: () => import('@lucide/svelte').then(m => m.Check),
	'circle-check': () => import('@lucide/svelte').then(m => m.CircleCheck),
	info: () => import('@lucide/svelte').then(m => m.Info),
	alert: () => import('@lucide/svelte').then(m => m.CircleAlert),
	'alert-octagon': () => import('@lucide/svelte').then(m => m.OctagonAlert),
	'circle-alert': () => import('@lucide/svelte').then(m => m.CircleAlert),
	'alert-circle': () => import('@lucide/svelte').then(m => m.CircleAlert),
	circle: () => import('@lucide/svelte').then(m => m.Circle),
	'circle-x': () => import('@lucide/svelte').then(m => m.CircleX),
	'circle-plus': () => import('@lucide/svelte').then(m => m.CirclePlus),
	'triangle-alert': () => import('@lucide/svelte').then(m => m.TriangleAlert),
	phone: () => import('@lucide/svelte').then(m => m.Phone),
	'phone-off': () => import('@lucide/svelte').then(m => m.PhoneOff),
	image: () => import('@lucide/svelte').then(m => m.Image),
	pdf: () => import('@lucide/svelte').then(m => m.FileText),
	doc: () => import('@lucide/svelte').then(m => m.FileText),
	docx: () => import('@lucide/svelte').then(m => m.FileText),
	jpg: () => import('@lucide/svelte').then(m => m.Image),
	jpeg: () => import('@lucide/svelte').then(m => m.Image),
	png: () => import('@lucide/svelte').then(m => m.Image),
	gif: () => import('@lucide/svelte').then(m => m.Image),
	svg: () => import('@lucide/svelte').then(m => m.Image),
	'circle-pause': () => import('@lucide/svelte').then(m => m.CirclePause),
	play: () => import('@lucide/svelte').then(m => m.Play),
	pause: () => import('@lucide/svelte').then(m => m.Pause),
	edit: () => import('@lucide/svelte').then(m => m.SquarePen),
	trash: () => import('@lucide/svelte').then(m => m.Trash2),
	'trash-2': () => import('@lucide/svelte').then(m => m.Trash2),
	delete: () => import('@lucide/svelte').then(m => m.Trash2),
	camera: () => import('@lucide/svelte').then(m => m.Camera),
	photo: () => import('@lucide/svelte').then(m => m.Camera),
	maximize: () => import('@lucide/svelte').then(m => m.Expand),
	expand: () => import('@lucide/svelte').then(m => m.Expand),
	sort: () => import('@lucide/svelte').then(m => m.ArrowDownUp),
	print: () => import('@lucide/svelte').then(m => m.Printer),
	'flower-2': () => import('@lucide/svelte').then(m => m.Flower2),
	star: () => import('@lucide/svelte').then(m => m.Star),
	history: () => import('@lucide/svelte').then(m => m.GalleryHorizontalEnd),
	layers: () => import('@lucide/svelte').then(m => m.Layers),
	target: () => import('@lucide/svelte').then(m => m.Target),
	project: () => import('@lucide/svelte').then(m => m.Target),
	task: () => import('@lucide/svelte').then(m => m.Target),
	jira: () => import('@lucide/svelte').then(m => m.Target),
	trello: () => import('@lucide/svelte').then(m => m.Target),
	network: () => import('@lucide/svelte').then(m => m.Network),
	copy: () => import('@lucide/svelte').then(m => m.Copy),
	'layout-template': () => import('@lucide/svelte').then(m => m.LayoutTemplate),
	crosshair: () => import('@lucide/svelte').then(m => m.Crosshair),
	scale: () => import('@lucide/svelte').then(m => m.Scale),
	save: () => import('@lucide/svelte').then(m => m.Save),
	kanban: () => import('@lucide/svelte').then(m => m.Kanban),
	'door-open': () => import('@lucide/svelte').then(m => m.DoorOpen),
	'file-x': () => import('@lucide/svelte').then(m => m.FileX),
	hash: () => import('@lucide/svelte').then(m => m.Hash),

	// Multimédia
	music: () => import('@lucide/svelte').then(m => m.Music),
	video: () => import('@lucide/svelte').then(m => m.Video),
	zoom: () => import('@lucide/svelte').then(m => m.Video),
	'circle-play': () => import('@lucide/svelte').then(m => m.CirclePlay),
	'play-circle': () => import('@lucide/svelte').then(m => m.CirclePlay),

	// Monitoring
	bolt: () => import('@lucide/svelte').then(m => m.Zap),
	zap: () => import('@lucide/svelte').then(m => m.Zap),
	actions: () => import('@lucide/svelte').then(m => m.UserCog),
	management: () => import('@lucide/svelte').then(m => m.UserCog),
	loader: () => import('@lucide/svelte').then(m => m.Loader),
	'loader-2': () => import('@lucide/svelte').then(m => m.Loader),

	// Postes & Organisation
	award: () => import('@lucide/svelte').then(m => m.Award),
	crown: () => import('@lucide/svelte').then(m => m.Crown),
	quote: () => import('@lucide/svelte').then(m => m.Quote),
	flag: () => import('@lucide/svelte').then(m => m.Flag),
	'share-2': () => import('@lucide/svelte').then(m => m.Share2),
	'rotate-ccw': () => import('@lucide/svelte').then(m => m.RotateCcw),
	'rotate-cw': () => import('@lucide/svelte').then(m => m.RotateCw),
	coffee: () => import('@lucide/svelte').then(m => m.Coffee),
	'list-filter': () => import('@lucide/svelte').then(m => m.ListFilter),
	'external-link': () => import('@lucide/svelte').then(m => m.ExternalLink),
	male: () => import('@lucide/svelte').then(m => m.Mars),
	female: () => import('@lucide/svelte').then(m => m.Venus),
	'help-circle': () => import('@lucide/svelte').then(m => m.CircleQuestionMark),
};

// Cache des icônes déjà chargées
const iconCache = new Map<string, Icon>();

/**
 * Get the application icon by its name/codename
 * @param appName - Name or codename of the application
 * @returns Promise<Icon> - Lucide icon component
 */
export async function getAppIconAsync(appName: string): Promise<Icon> {
	if (!appName) return Package;

	// Normalize the name
	const normalizedName = appName
		.toLowerCase()
		.trim()
		.replace(/[\s_\.]+/g, '-')
		.replace(/[^\w-]/g, '');

	// Check cache first
	if (iconCache.has(normalizedName)) {
		return iconCache.get(normalizedName)!;
	}

	// Try to load the icon
	const loader = ICON_MODULES[normalizedName] || 
		ICON_MODULES[appName.toLowerCase().trim()] ||
		ICON_MODULES[normalizedName.split('-').find(k => k.length > 2) || ''];

	if (loader) {
		try {
			const icon = await loader();
			iconCache.set(normalizedName, icon);
			return icon;
		} catch (e) {
			console.warn(`Failed to load icon: ${appName}`, e);
		}
	}

	return Package;
}

/**
 * Verify if the icon exists in the mapping
 * @param appName - Name or codename of the application
 * @returns true if the specific icon exists
 */
export function hasAppIcon(appName: string): boolean {
	if (!appName) return false;

	const normalizedName = appName
		.toLowerCase()
		.trim()
		.replace(/[\s_\.]+/g, '-')
		.replace(/[^\w-]/g, '');

	return !!(ICON_MODULES[normalizedName] || ICON_MODULES[appName.toLowerCase().trim()]);
}

export const APPLICATION_ICON_COLORS = {
	BLUE: ['productivity', 'utilities'],
	GREEN: ['financial', 'sales', 'marketing'],
	AMBER: ['public', 'other', 'social']
};

