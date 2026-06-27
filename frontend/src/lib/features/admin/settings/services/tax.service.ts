import {
	payrollConfigEndpoint,
	taxBracketsEndpoint,
	socialContributionsEndpoint,
	payrollInitEndpoint,
	legalAllowancesEndpoint,
	overtimeRulesEndpoint
} from '../api/tax.endpoints';
import type {
	PayrollConfigResponse,
	TaxBracketResponse,
	SocialContributionResponse,
	PayrollConfigUpdate,
	TaxBracketCreate,
	TaxBracketUpdate,
	SocialContributionCreate,
	SocialContributionUpdate
} from '../schemas/tax.schemas';

export { 
  type PayrollConfigResponse, 
  type TaxBracketResponse, 
  type SocialContributionResponse 
};


export const taxSettingsService = {
  // Tax Brackets
  async listTaxBrackets(): Promise<TaxBracketResponse[]> {
    return await taxBracketsEndpoint.list();
  },

  async createTaxBracket(
    data: TaxBracketCreate,
    silent = false
  ): Promise<TaxBracketResponse> {
    const response = await taxBracketsEndpoint.create(data);
    if (!silent) {
      console.log('Tax bracket created successfully');
    }
    return response;
  },

  async updateTaxBracket(
    bracketId: string, 
    data: TaxBracketUpdate,
    silent = false
  ): Promise<TaxBracketResponse> {
    const response = await taxBracketsEndpoint.update(bracketId, data);
    if (!silent) {
      console.log('Tax bracket updated successfully');
    }
    return response;
  },

  // Social Contributions (CNSS, etc.)
  async listContributions(): Promise<SocialContributionResponse[]> {
    const response = await socialContributionsEndpoint.list();
    return response.results || [];
  },

  async createContribution(
    data: SocialContributionCreate,
    silent = false
  ): Promise<SocialContributionResponse> {
    const response = await socialContributionsEndpoint.create(data);
    if (!silent) {
      console.log('Contribution rate created successfully');
    }
    return response;
  },

  async updateContribution(
    rateId: string,
    data: SocialContributionUpdate,
    silent = false
  ): Promise<SocialContributionResponse> {
    const response = await socialContributionsEndpoint.update(rateId, data);
    if (!silent) {
      console.log('Contribution rate updated successfully');
    }
    return response;
  },

  // Payroll Configuration (Global settings)
  async getConfiguration(): Promise<PayrollConfigResponse> {
    return await payrollConfigEndpoint.retrieve();
  },

  async updateConfiguration(
    data: PayrollConfigUpdate,
    silent = false
  ): Promise<PayrollConfigResponse> {
    const response = await payrollConfigEndpoint.update(data);
    if (!silent) {
      console.log('Payroll configuration updated successfully');
    }
    return response;
  },

  // Initialize defaults
  async initializeDefaults(): Promise<{ status: string; summary: Record<string, number> }> {
    return await payrollInitEndpoint.initializeDefaults();
  },

  // Legal Allowances
  async listLegalAllowances(): Promise<import('../types/tax.types').LegalAllowance[]> {
    return await legalAllowancesEndpoint.list();
  },

  async updateLegalAllowance(
    allowanceId: string,
    data: Partial<import('../types/tax.types').LegalAllowance>,
    silent = false
  ): Promise<import('../types/tax.types').LegalAllowance> {
    const response = await legalAllowancesEndpoint.update(allowanceId, data);
    if (!silent) {
      console.log('Legal allowance updated successfully');
    }
    return response;
  },

  // Overtime Rules
  async listOvertimeRules(): Promise<import('../types/tax.types').OvertimeRule[]> {
    return await overtimeRulesEndpoint.list();
  },

  async updateOvertimeRule(ruleId: string, data: Partial<import('../types/tax.types').OvertimeRule>): Promise<import('../types/tax.types').OvertimeRule> {
    return await overtimeRulesEndpoint.update(ruleId, data);
  },
};

