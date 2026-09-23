export type NavVariant = 'underline' | 'pill' | 'crossfade';

export interface TabDef {
  id: string;
  label: string;
  icon: string;
  path?: string;
  count?: number;
}
