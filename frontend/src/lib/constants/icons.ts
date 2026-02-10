import {
    Users, 
    MessageSquare, 
    FileText, 
    ChartBar,  
    Settings,
    CreditCard, 
    Database, 
    Globe, 
    Lock, 
    Smartphone, 
    Mail,
    Calendar, 
    ShoppingCart, 
    Building2, 
    Briefcase, 
    GraduationCap,
    Heart, 
    Code, 
    Server, 
    Cloud, 
    Target, 
    Camera, 
    Music,
    Video, 
    Calculator, 
    Shield, 
    Activity, 
    LayoutGrid,
    LogOut,
    RefreshCcw,
    Grip,
    MapPin,
    Funnel,
    ChevronDown,
    ChevronLeft,
    ChevronRight,
    ChevronsLeft,
    ChevronsRight,
    Search,
    X,
    Plus,
    type IconProps
} from '@lucide/svelte';
import type { Component } from 'svelte';

type Icon = Component<IconProps, {}>;

export const APPS_ICON: Record<string, Icon> = {
  // Gestion d'équipe et RH 
  'users': Users,
  'team' : Users,
  'hr'   : Users,
  'crm'  : Users,
  
  // Communication
  'chat'     : MessageSquare,
  'messaging': MessageSquare,
  'slack'    : MessageSquare,
  'teams'    : MessageSquare,
  'discord'  : MessageSquare,
  'mail'     : Mail,
  'email'    : Mail,
  
  // Documentation
  'docs'      : FileText,
  'wiki'      : FileText,
  'notion'    : FileText,
  'confluence': FileText,
  
  // Analytics et reporting
  'analytics': ChartBar,
  'dashboard': ChartBar,
  'reports'  : ChartBar,
  
  // Administration
  'settings': Settings,
  'admin'   : Settings,
  'config'  : Settings,
  
  // Finance
  'finance'   : CreditCard,
  'accounting': Calculator,
  'billing'   : CreditCard,
  'stripe'    : CreditCard,
  'paypal'    : CreditCard,
  
  // Base de données
  'database'  : Database,
  'mysql'     : Database,
  'postgresql': Database,
  'mongodb'   : Database,
  
  // Web
  'web'      : Globe,
  'website'  : Globe,
  'wordpress': Globe,
  
  // Sécurité
  'security': Lock,
  'auth'    : Lock,
  'firewall': Shield,
  
  // Mobile
  'mobile': Smartphone,
  'app'   : Smartphone,
  
  // Calendrier
  'calendar': Calendar,
  'schedule': Calendar,
  
  // E-commerce
  'shop'     : ShoppingCart,
  'ecommerce': ShoppingCart,
  'shopify'  : ShoppingCart,
  
  // Entreprise
  'business': Building2,
  'office'  : Building2,
  'erp'     : Building2,
  'location': MapPin,
  'pin'     : MapPin,
  
  // Services professionnels
  'consulting': Briefcase,
  'services'  : Briefcase,
  
  // Éducation
  'education': GraduationCap,
  'learning' : GraduationCap,
  
  // Santé
  'health' : Heart,
  'medical': Heart,
  
  // Développement
  'dev'        : Code,
  'development': Code,
  'git'        : Code,
  'github'     : Code,
  
  // Infrastructure
  'server' : Server,
  'hosting': Server,
  'cloud'  : Cloud,
  'aws'    : Cloud,
  'azure'  : Cloud,
  
  // UI Elements
  'grid'   : LayoutGrid,
  'logout' : LogOut,
  'refresh': RefreshCcw,
  'grip'   : Grip,
  'filter' : Funnel,
  'chevron': ChevronDown,
  'prev'   : ChevronLeft,
  'first'  : ChevronsLeft,
  'next'   : ChevronRight,
  'last'   : ChevronsRight,
  'search' : Search,
  'close'  : X,
  'x'      : X,
  'plus'   : Plus,
  'add'    : Plus,
  
  // Gestion de projet
  'project': Target,
  'task'   : Target,
  'jira'   : Target,
  'trello' : Target,
  
  // Multimédia
  'photo': Camera,
  'music': Music,
  'video': Video,
  'zoom' : Video,
  
  // Monitoring
  'monitoring' : Activity,
  'performance': Activity,
};


export const APPLICATION_ICON_COLORS = {
  BLUE: ['productivity', 'utilities'],
  GREEN: ['financial', 'sales', 'marketing',],
  AMBER: ['public', 'other', 'social'],
};

