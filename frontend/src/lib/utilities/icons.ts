import {
    Users, MessageSquare, FileText, ChartBar,  Settings,
    CreditCard, Database, Globe, Lock, Smartphone, Mail,
    Calendar, ShoppingCart, Building2, Briefcase, GraduationCap,
    Heart, Code, Server, Cloud, Target, Camera, Music,
    Video, Calculator, Shield, Activity, Package,
    type IconProps
} from '@lucide/svelte';
import type { Component } from 'svelte';


type Icon = Component<IconProps, {}>;

/**
 * Mapping of icons applications essentials for name/codename
 * Icon fallback : Package for applications without specific icon
 */
export const APPS_ICON: Record<string, Icon> = {
    // Gestion d'équipe et RH
    // 
    'users': Users,
    'team': Users,
    'hr': Users,
    'crm': Users,
    
    // Communication
    'chat': MessageSquare,
    'messaging': MessageSquare,
    'slack': MessageSquare,
    'teams': MessageSquare,
    'discord': MessageSquare,
    'mail': Mail,
    'email': Mail,
    
    // Documentation
    'docs': FileText,
    'wiki': FileText,
    'notion': FileText,
    'confluence': FileText,
    
    // Analytics et reporting
    'analytics': ChartBar,
    'dashboard': ChartBar,
    'reports': ChartBar,
    
    // Administration
    'settings': Settings,
    'admin': Settings,
    'config': Settings,
    
    // Finance
    'finance': CreditCard,
    'accounting': Calculator,
    'billing': CreditCard,
    'stripe': CreditCard,
    'paypal': CreditCard,
    
    // Base de données
    'database': Database,
    'mysql': Database,
    'postgresql': Database,
    'mongodb': Database,
    
    // Web
    'web': Globe,
    'website': Globe,
    'wordpress': Globe,
    
    // Sécurité
    'security': Lock,
    'auth': Lock,
    'firewall': Shield,
    
    // Mobile
    'mobile': Smartphone,
    'app': Smartphone,
    
    // Calendrier
    'calendar': Calendar,
    'schedule': Calendar,
    
    // E-commerce
    'shop': ShoppingCart,
    'ecommerce': ShoppingCart,
    'shopify': ShoppingCart,
    
    // Entreprise
    'business': Building2,
    'office': Building2,
    'erp': Building2,
    
    // Services professionnels
    'consulting': Briefcase,
    'services': Briefcase,
    
    // Éducation
    'education': GraduationCap,
    'learning': GraduationCap,
    
    // Santé
    'health': Heart,
    'medical': Heart,
    
    // Développement
    'dev': Code,
    'development': Code,
    'git': Code,
    'github': Code,
    
    // Infrastructure
    'server': Server,
    'hosting': Server,
    'cloud': Cloud,
    'aws': Cloud,
    'azure': Cloud,
    
    // Gestion de projet
    'project': Target,
    'task': Target,
    'jira': Target,
    'trello': Target,
    
    // Multimédia
    'photo': Camera,
    'music': Music,
    'video': Video,
    'zoom': Video,
    
    // Monitoring
    'monitoring': Activity,
    'performance': Activity,
};

/**
 * Get the application icon by its name/codename
 * @param appName - Name or codename of the application
 * @param fallback - Default icon if matching is found 
 * @returns Lucide icon matching
 */
export function getAppIcon(appName: string, fallback: Icon = Package): Icon {
    if (!appName) return fallback;
    
    // Normalize the name (miniscules, remplace spaces and spcial caracters by the hyphens)
    const normalizedName = appName
        .toLowerCase()
        .trim()
        .replace(/[\s_\.]+/g, '-')
        .replace(/[^\w-]/g, '');
    
    // Search first the corresponding name
    if (APPS_ICON[normalizedName]) {
        return APPS_ICON[normalizedName];
    }
    
    // Search the orginal name in minuscules
    const lowerName = appName.toLowerCase().trim();
    if (APPS_ICON[lowerName]) {
        return APPS_ICON[lowerName];
    }
    
    // Search the partials keys words
    const keywords = normalizedName.split('-');
    for (const keyword of keywords) {
        if (keyword.length > 2 && APPS_ICON[keyword]) {
            return APPS_ICON[keyword];
        }
    }
    
    // Return the default icon
    return fallback;
}

/**
 * Verify if the icon exists in a specific app
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
    
    return !!(APPS_ICON[normalizedName] || APPS_ICON[appName.toLowerCase().trim()]);
};

