import type { CurrentOrganization, } from "./organization";

/**
 * Represents a user in the system
 */
export interface User {
    id: string;
    email: string;
    photo?: string;
    first_name: string;
    last_name: string;
    individual_plan_name: string;
    individual_subscription_status: string;
}

/**
 * Simplified user information
 */
export interface UserSimple {
    id: string;
    email?: string;
    photo?: string;
    first_name?: string;
    last_name?: string;
}


export interface SessionUser extends User {
    current_organization?: CurrentOrganization 
}


export type InvoiceStatus = 'draft' | 'pending' | 'paid' | 'overdue' | 'cancelled' | 'refunded';

export interface InvoiceItem {
    id: string;
    name: string;
    description?: string;
    quantity: number;
    unit_price: number;
    total_price: number;
    metadata?: Record<string, any>;
}

export interface Invoice {
    id: string;
    invoice_number: string;
    status: InvoiceStatus;
    subtotal: number;
    tax_rate: number;
    tax_amount: number;
    total: number;
    currency: string;
    issue_date: string;
    due_date: string;
    paid_date?: string;
    period_start: string;
    period_end: string;
    description: string;
    notes?: string;
    payment_reference?: string;
    user: string;
    user_subscription?: string;
    items: InvoiceItem[];
}

export interface InvoiceStats {
    total_invoices: number;
    pending_invoices: number;
    paid_invoices: number;
    overdue_invoices: number;
    cancelled_invoices: number;
    refunded_invoices: number;
    total_amount_pending: number;
    total_amount_paid: number;
    total_amount_refunded: number;
}

export interface InvoiceSummary {
    period: string;
    total_invoices: number;
    total_amount: number;
    paid_amount: number;
    pending_amount: number;
    cancelled_amount: number;
    refunded_amount: number;
}

export type RefundRequestStatus = 'pending' | 'approved' | 'rejected' | 'processed' | 'cancelled';
export type RefundRequestReason = 'duplicate_payment' | 'service_not_received' | 'billing_error' | 'cancellation' | 'technical_issue' | 'other';

export interface RefundRequest {
    id: string;
    status: RefundRequestStatus;
    reason: RefundRequestReason;
    description: string;
    requested_amount: number;
    approved_amount?: number;
    currency: string;
    processed_date?: string;
    admin_notes?: string;
    refund_reference?: string;
    user: string;
    invoice: string;
    user_subscription?: string;
    invoice_details?: {
        invoice_number: string;
        invoice_total: number;
        invoice_date: string;
        paid_date?: string;
    };
    subscription_details?: {
        plan_name: string;
        billing_cycle: string;
        subscription_start: string;
    };
    created_at: string;
    updated_at: string;
}
