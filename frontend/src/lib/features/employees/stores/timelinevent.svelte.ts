import type { TimelineEvent } from "../types/types";


// Mock Data
const MOCK_TIMELINEVENT: TimelineEvent[] = [
  { 
    id: 1,
    date: '2024-01-15', 
    label: 'Promotion', 
    status: 'Senior Dev' 
  },
  { 
    id: 2,
    date: '2023-06-01', 
    label: 'Changement de département', 
    status: 'Engineering' 
  },
  { 
    id: 3,
    date: '2022-03-10', 
    label: 'Onboarding', 
    status: 'Junior Dev' 
  }
];


export class TimelineEventStore {

  getById(id: string | number): TimelineEvent | undefined {
    const numId = typeof id === 'string' ? parseInt(id, 10) : id;
    return MOCK_TIMELINEVENT.find(tlEvt => tlEvt.id === numId);
  }

  getTimelineEvents(): TimelineEvent[] {
    // Mock timeline data - in real app would fetch based on ID
    return MOCK_TIMELINEVENT;
  }
}


// Create a global instance if needed, 
// or instantiate in component context context
export const timelineEventStore = new TimelineEventStore();

