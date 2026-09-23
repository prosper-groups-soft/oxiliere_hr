export type DashboardRole = 'admin' | 'hr' | 'employee';

export interface WidgetDef {
  id: string;
  metric: string;
  period?: string;
  visibleIf?: (role: DashboardRole) => boolean;
  source: () => { queryKey: unknown[]; queryFn: () => Promise<any> };
  mapData: (raw: any) => { value: string; label: string; sublabel?: string; icon: string; color: string };
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
