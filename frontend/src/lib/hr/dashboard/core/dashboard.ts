export type DashboardRole = 'admin' | 'hr' | 'employee';

export type WidgetKind = 'kpi' | 'chart' | 'list';

export interface WidgetDef {
  id: string;
  kind?: WidgetKind;
  metric: string;
  period?: string;
  visibleIf?: (role: DashboardRole) => boolean;
  source: () => { queryKey: unknown[]; queryFn: () => Promise<any> };
  mapData: (raw: any) => any;
}

export interface DashboardConfig {
  role: DashboardRole;
  widgets: WidgetDef[];
  layout?: { type: 'grid'; columns: number };
  refresh?: { policy: 'poll'; interval: number };
}

export function createDashboard(config: DashboardConfig) {
  const visibleWidgets = config.widgets.filter(w => !w.visibleIf || w.visibleIf(config.role));
  return { ...config, visibleWidgets };
}

export function kpi(opts: Omit<WidgetDef, 'id'> & { id?: string }): WidgetDef {
  return { id: opts.metric, ...opts } as WidgetDef;
}
