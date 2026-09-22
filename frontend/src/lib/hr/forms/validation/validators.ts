// Helpers de validation exacts api §6. Le moteur interne (createForm)
// utilise zod sans l'exposer — l'API publique reste ces helpers.
import type { ValidationContext, ValidationResult, ValidatorConfig } from '../core/types.js';


export const validators = {
	required: (message?: string): ValidatorConfig => ({ type: 'required', message }),
	email: (message?: string): ValidatorConfig => ({ type: 'email', message }),
	url: (message?: string): ValidatorConfig => ({ type: 'url', message }),
	phone: (message?: string): ValidatorConfig => ({ type: 'phone', message }),
	integer: (message?: string): ValidatorConfig => ({ type: 'integer', message }),
	min: (value: number, message?: string): ValidatorConfig => ({
		type: 'min',
		params: { value },
		message
	}),
	max: (value: number, message?: string): ValidatorConfig => ({
		type: 'max',
		params: { value },
		message
	}),
	minLength: (value: number, message?: string): ValidatorConfig => ({
		type: 'minLength',
		params: { value },
		message
	}),
	maxLength: (value: number, message?: string): ValidatorConfig => ({
		type: 'maxLength',
		params: { value },
		message
	}),
	regex: (pattern: RegExp, message?: string): ValidatorConfig => ({
		type: 'regex',
		params: { pattern },
		message
	}),
	oneOf: (values: any[], message?: string): ValidatorConfig => ({
		type: 'oneOf',
		params: { values },
		message
	}),
	equalTo: (other: string, message?: string): ValidatorConfig => ({
		type: 'equalTo',
		params: { other },
		message
	}),
	minDate: (value: string, message?: string): ValidatorConfig => ({
		type: 'minDate',
		params: { value },
		message
	}),
	maxDate: (value: string, message?: string): ValidatorConfig => ({
		type: 'maxDate',
		params: { value },
		message
	}),
	minItems: (value: number, message?: string): ValidatorConfig => ({
		type: 'minItems',
		params: { value },
		message
	}),
	maxItems: (value: number, message?: string): ValidatorConfig => ({
		type: 'maxItems',
		params: { value },
		message
	}),
	unique: (params?: Record<string, any>, message?: string): ValidatorConfig => ({
		type: 'unique',
		params,
		message,
		async: true
	}),
	exists: (params?: Record<string, any>, message?: string): ValidatorConfig => ({
		type: 'exists',
		params,
		message,
		async: true
	}),
	custom: (
		fn: (value: any, ctx: ValidationContext) => boolean | Promise<boolean>,
		message?: string
	): ValidatorConfig => ({
		type: 'custom',
		params: { fn },
		message,
		async: fn.constructor.name === 'AsyncFunction'
	})
};

/**
 * Invariant inter-champs (api §6) : reçoit `values` complet.
 * En cas d'échec l'erreur est globale, sauf `{ valid:false, field }`
 * qui la rattache au champ fautif.
 */
export function invariant(
	check: (
		values: Record<string, any>
	) => boolean | Promise<boolean> | { valid: boolean; field?: string } | Promise<{ valid: boolean; field?: string }>,
	message: string
): { name: string; validate: (values: Record<string, any>) => Promise<ValidationResult> } {
	return {
		name: `invariant:${message.slice(0, 32)}`,
		validate: async (values) => {
			const r = await check(values);
			if (typeof r === 'boolean') return r ? { valid: true } : { valid: false, message };
			return r.valid ? { valid: true } : { valid: false, message, field: r.field };
		}
	};
}
