export type FilterMode = 'multi' | 'single' | 'date';

export interface FilterDef {
  key: string;
  label: string;
  icon?: string;
  mode: FilterMode;
  options: { value: string; label: string }[];
}

export interface SortDef {
  options: { value: string; label: string }[];
  value: string;
  order: 'asc' | 'desc';
}
