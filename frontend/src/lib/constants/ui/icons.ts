import {
  Baby, 
  ShieldAlert,
  Users, 
  User,
  UserRoundX,
  CircleUser,
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
  RefreshCw,
  CirclePause,
  UserMinus,
  Grip,
  MapPin,
  Funnel,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  ArrowDownUp,
  Search,
  X,
  CloudUpload,
  Plus,
  House,
  Ellipsis,
  EllipsisVertical,
  Download,
  CircleCheck,
  Eye,
  Phone,
  Image,
  Info,
  CircleAlert,
  ShieldCheck,
  Zap,
  UserCog,
  SquarePen,
  Trash2,
  Expand,
  LayoutDashboard,
  ArrowLeft,
  Printer,
  Star,
  Files,
  GalleryHorizontalEnd,
  type IconProps
} from '@lucide/svelte';
import type { Component } from 'svelte';


type Icon = Component<IconProps, {}>;


export const APPS_ICON: Record<string, Icon> = {
  // Gestion d'équipe et RH 
  'users': Users,
  'circle-user': CircleUser,
  'no-user': UserRoundX,
  'user' : User,
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
  'layout-dashboard': LayoutDashboard,
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
  'shield-alert': ShieldAlert,
  
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
  'heart'  : Heart,
  'baby'   : Baby,
  
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
  'arrow-left': ArrowLeft,
  'search' : Search,
  'close'  : X,
  'x'      : X,
  'plus'   : Plus,
  'add'    : Plus,
  'home'   : House,
  'more-horizontal': Ellipsis,
  'more-vertical': EllipsisVertical,
  'download': Download,
  'eye'    : Eye,
  'check'  : CircleCheck,
  'info'   : Info,
  'alert'  : CircleAlert,
  'phone'  : Phone,
  'file'   : FileText,
  'cloud-upload': CloudUpload,
  'image': Image,
  'pdf': FileText,
  'doc': FileText,
  'docx': FileText,
  'files': Files,
  'jpg': Image,
  'jpeg': Image,
  'png': Image,
  'gif': Image,
  'svg': Image,
  'shield-check': ShieldCheck,
  'circle-pause': CirclePause,
  'user-minus': UserMinus,
  'refresh-cw': RefreshCw,
  'edit': SquarePen,
  'trash': Trash2,
  'delete': Trash2,
  'camera' : Camera,
  'maximize': Expand,
  'expand'  : Expand,
  'sort': ArrowDownUp,
  'print': Printer,
  'star': Star,
  'history': GalleryHorizontalEnd,
  
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
  'bolt'       : Zap,
  'zap'        : Zap,
  'actions'    : UserCog,
  'management' : UserCog,
};


export const APPLICATION_ICON_COLORS = {
  BLUE: ['productivity', 'utilities'],
  GREEN: ['financial', 'sales', 'marketing',],
  AMBER: ['public', 'other', 'social'],
};

