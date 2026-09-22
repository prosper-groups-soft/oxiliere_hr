import { registerType } from '@/hr/forms/core/typeRegistry.js';
import ScoringField from '../renderers/ScoringField.svelte';

export function registerScoringType() {
  registerType('scoring', {
    valueType: 'object',
    defaultRenderer: ScoringField
  });
}
