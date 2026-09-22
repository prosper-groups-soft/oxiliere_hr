import { registerType } from '@/hr/forms/core/typeRegistry.js';
import WorkingDaysTimeline from '../renderers/WorkingDaysTimeline.svelte';

export function registerTimelineType() {
  registerType('workingDaysTimeline', {
    valueType: 'object',
    defaultRenderer: WorkingDaysTimeline
  });
}
