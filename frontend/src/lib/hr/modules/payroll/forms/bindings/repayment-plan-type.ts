import { registerType } from '@/hr/forms/core/typeRegistry.js';
import RepaymentPlanField from '../renderers/RepaymentPlanField.svelte';
export function registerRepaymentPlanType() {
  registerType('repaymentPlan', { valueType: 'object', defaultRenderer: RepaymentPlanField });
}
