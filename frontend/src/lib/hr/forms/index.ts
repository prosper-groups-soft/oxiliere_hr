// Barrel — permet `import {...} from '@/hr/forms'` (chemins stables malgré les sous-dossiers).
export * from './core/types';
export * from './core/createForm.svelte';
export * from './core/typeRegistry';
export * from './core/behaviors';
export * from './core/dependencies';
export * from './data/resolveDataSource';
export * from './data/uploaders';
export * from './data/storeSnapshots';
export * from './validation/i18n';
export * from './validation/validators';
export * from './fields/primitives';
export * from './fields/business';
export * from './actions/actions';

// Composants Svelte (chemins stables) :
export { default as FormView } from './components/hosts/FormView.svelte';
export { default as FormHost } from './components/hosts/FormHost.svelte';
export { default as LayoutRenderer } from './components/layouts/LayoutRenderer.svelte';
export { default as FieldRenderer } from './components/renderers/FieldRenderer.svelte';
