import { registerType } from '@/hr/forms/core/typeRegistry.js';
import GoalEditorField from '../renderers/GoalEditorField.svelte';
export function registerGoalEditorType() {
  registerType('goalEditor', { valueType: 'array', defaultRenderer: GoalEditorField });
}
