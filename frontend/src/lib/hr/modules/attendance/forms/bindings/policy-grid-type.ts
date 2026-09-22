import { registerType } from '@/hr/forms/core/typeRegistry.js';
import PolicyGridField from '../renderers/PolicyGridField.svelte';

export function registerPolicyGridType() {
  registerType('policyGrid', {
    valueType: 'object',
    defaultRenderer: PolicyGridField
  });
}
