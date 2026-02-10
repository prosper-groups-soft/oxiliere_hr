import type { SubscriptionPlan } from "./subscriptions";


export enum UserRole {
  SUPERADMIN = "superadmin",
  ADMIN = "admin",
  MEMBER = "member"
};

export type UserStatus = 'active' | 'inactive' | 'pending' | 'suspended';

export interface Member {
  id: string;
  email: string;
  name: string;
  created: string;
  modified: string;
  is_admin: boolean;
  is_active: boolean;
  joined_at: string;
  last_activity: string;
  user: string;
  organization: string;
}

export interface MemberUser {
  last_login: string | null;
  first_name: string;
  last_name: string;
  is_active: boolean;
  id: string;
  email: string;
  phone_number: string;
  job_title: string;
  birthdate: string;
  address: string;
  website: string;
  bio: string;
  language: string;
  timezone: string;
  photo: string | null;
}

export interface MemberDetail {
  user: MemberUser;
  created: string;
  modified: string;
  is_admin: boolean;
  is_owner: boolean;
  id: string;
  is_active: boolean;
  joined_at: string;
  last_activity: string;
  organization: string;
}


export enum OrganizationType {
  COMPANY = 'company',
  NONPROFIT = 'nonprofit',
  EDUCATION = 'education',
  GOVERNMENT = 'government',
  NGO = 'ngo',
  HOSPITAL = 'hospital',
  OTHER = 'other'
}

export enum OrganizationSize {
  MICRO = 'micro',
  SMALL = 'small',
  MEDIUM = 'medium',
  LARGE = 'large',
  ENTERPRISE = 'enterprise'
}

export enum OrganizationVisibility {
  PUBLIC = 'public',
  PRIVATE = 'private'
};

export enum Industry {
  TECHNOLOGY = 'technology',
  HEALTHCARE = 'healthcare',
  FINANCE = 'finance',
  EDUCATION = 'education',
  MANUFACTURING = 'manufacturing',
  RETAIL = 'retail',
  AGRICULTURE = 'agriculture',
  CONSTRUCTION = 'construction',
  TRANSPORTATION = 'transportation',
  ENERGY = 'energy',
  TELECOMMUNICATIONS = 'telecommunications',
  MEDIA = 'media',
  HOSPITALITY = 'hospitality',
  REAL_ESTATE = 'real_estate',
  CONSULTING = 'consulting',
  LEGAL = 'legal',
  NONPROFIT = 'nonprofit',
  GOVERNMENT = 'government',
  MINING = 'mining',
  OTHER = 'other'
};

export enum TimeZone {
  KINSHASA = 'Africa/Kinshasa',
  LUBUMBASHI = 'Africa/Lubumbashi',
  DAKAR = 'Africa/Dakar',
  NAIROBI = 'Africa/Nairobi'
};

export enum Language {
  FRANCAIS = 'fr'
};

export interface InitialFormStep1 {
  name: string;
  slug: string;
  description: string;
};

export interface InitialFormStep2 {
  website: string;
  email: string;
  organization_type: OrganizationType;
  industry: Industry;
  size: OrganizationSize;
  visibility: OrganizationVisibility;
  location: string;
  timezone: TimeZone;
};

export interface OrganizationData {
  name: string;
  slug: string;
  description: string;
  website: string;
  email: string;
  organization_type: OrganizationType;
  industry: Industry;
  company_size: OrganizationSize;
  visibility: OrganizationVisibility;
  location: string;
  timezone: TimeZone;
}


export interface Organization {
  created_at: string;
  updated_at: string;
  role: UserRole;
  name: string;
  is_active: boolean;
  slug: string;
  description: string;
  website: string;
  email: string | null;
  phone: string | null;
  siret: string | null;
  vat_number: string | null;
  rccm_number: string | null;
  logo: string;
  location: string;
  address: string;
  industry: string;
  company_size: OrganizationSize;
  postal_code: string;
  country: string;
  current_plan_name: string;
  subscription_status: 'none' | 'active' | 'trial' | 'expired' | 'cancelled';
  timezone: TimeZone;
  language: string;
  currency: 'USD' | 'CDF';
  is_platform_admin: boolean;
  visibility: OrganizationVisibility;
  organization_type: OrganizationType;
  subscription_plan: SubscriptionPlan;
};

export interface OrganizationSettings {
  id: string;
  email_notifications: boolean;
  billing_notifications: boolean;
  security_notifications: boolean;
  can_be_contacted: boolean;
  enforce_2fa: boolean;
  api_access_enabled: boolean;
}


export interface CurrentOrganization {
  id?: string
  name: string
  slug: string
  is_active: boolean
  is_platform_admin: boolean
  organization_type: string
  logo_url?: string
};

export interface CurrentOrganizationSubscription {
  plan_name: string;
  previous_plan_name: string;
  effective_price: number;
  effective_extra_user_price: number;
  is_custom_pricing: boolean;
  is_trial: boolean;
  duration_days: number;
  id: string;
  organization: string;
  subscription_plan: string;
  previous_plan: string;
  agreed_price: number;
  agreed_extra_user_price: number;
  start_date: string;
  end_date: string;
  is_yearly: boolean;
  notes: string;
  change_reason: 'initial' | 'upgrade' | 'downgrade' | 'renewal' | 'cancellation' | 'trial_start' | 'trial_end';
  is_active: boolean;
  created_at: string;
  updated_at: string;
  organization_id: string;
  organization_name: string;
  previous_plan_id: string;
  is_active_trial: boolean;
  is_expired_trial: boolean;
  days_remaining: number;
  total_cost: number;
}

export interface InvitationUser {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  photo: string | null;
}

export interface InvitationOrganization {
  id: string;
  name: string;
  slug: string;
  email: string;
  logo: string | null;
  description: string;
  website: string;
}

export type InvitationStatus = 'pending' | 'accepted' | 'rejected' | 'canceled';

export interface OrganizationInvitation {
  id: string;
  invitee: InvitationUser;
  invited_by: InvitationUser;
  organization: InvitationOrganization;
  status: InvitationStatus;
  is_admin: boolean;
  created_at?: string;
  action_at?: string;
}

