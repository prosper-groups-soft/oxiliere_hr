export interface SubscriptionPlan {
	id: string;
	name: string;
	display_name: string;
	description: string;
	base_price: number;
	extra_user_price?: number;
	yearly_discount_percentage: number;
	billing_type: 'per_user' | 'per_quota';
	quota_users_included?: number;
	quota_max_users?: number;
	max_users?: number;
	max_applications?: number;
	storage_gb?: number;
	api_calls_per_month?: number;
	trial_days: number;
	is_active: boolean;
	is_custom_pricing: boolean;
	requires_approval: boolean;
	is_default: boolean;
	sort_order: number;
}

export interface UserSubscription {
	id: string;
	subscription_plan: SubscriptionPlan;
	start_date: string;
	end_date?: string;
	billing_cycle: 'monthly' | 'yearly';
	is_trial: boolean;
	trial_end_date?: string;
	is_active: boolean;
	next_billing_date?: string;
}

export interface StartTrialRequest {
	plan_name: string;
	billing_cycle: 'monthly' | 'yearly';
}

export interface UpgradeSubscriptionRequest {
	plan_name: string;
	billing_cycle: 'monthly' | 'yearly';
}

export type BillingCycle = 'monthly' | 'yearly';
export type CurrencyCode = 'USD' | 'CDF';
export type PaymentMethod = 'card' | 'bank_transfer';

export type PlanName = 'free' | 'trial' | 'individual' | 'micro' | 'small' | 'medium' | 'large' | 'enterprise';

export interface Billing {
    is_active: boolean;
    billing_name: string;
    billing_email: string;
    company_name: string;
    tax_number: string;
    street_address: string;
    city: string;
    postal_code: string;
    country: 'CD';
    preferred_currency: CurrencyCode;
    preferred_payment_method: PaymentMethod;
    auto_pay: boolean;
    invoice_notes: string;
};
