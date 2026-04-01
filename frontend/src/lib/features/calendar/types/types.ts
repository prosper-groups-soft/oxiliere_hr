export type EventType = 'holiday' | 'closure' | 'training';


export interface CalendarEvent {
  id: string;
  title: string;
  defaultDate: string; // ISO string YYYY-MM-DD
  endDate?: string;
  type: EventType;
  scopeId?: string;
}


export interface DayClosure {
  date: string;
  reason: string;
  isHoliday: boolean;
}

