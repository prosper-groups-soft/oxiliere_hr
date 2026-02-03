// event-system.ts
export type EventHandler<T = any> = (payload: T) => void;
export type UnsubscribeFn = () => void;

class EventChannel<T= any> {
  private handlers = new Set<EventHandler<T>>();
  
  constructor(public readonly eventType: string) {}

  subscribe(handler: EventHandler<T>): UnsubscribeFn {
    this.handlers.add(handler);
    return () => this.unsubscribe(handler);
  }

  unsubscribe(handler: EventHandler<T>) {
    this.handlers.delete(handler);
  }

  publish(payload: T) {
    this.handlers.forEach(handler => handler(payload));
  }
}

export class EventSystem {
  private channels = new Map<string, EventChannel<any>>();

  channel<T>(eventType: string): EventChannel<T> {
    if (!this.channels.has(eventType)) {
      this.channels.set(eventType, new EventChannel<T>(eventType));
    }
    return this.channels.get(eventType) as EventChannel<T>;
  }

  destroyChannel(eventType: string) {
    this.channels.delete(eventType);
  }

  hasChannel(eventType: string) {
    return this.channels.has(eventType);
  }

  destroy() {
    this.channels.clear();
  }
}

// Instance globale
export const globalEventSystem = new EventSystem();


// event-factory.ts
export type EventDefinition<T> = {
    publish: (payload: T) => void;
    subscribe: (handler: (payload: T) => void) => UnsubscribeFn;
    getType: () => string;
};
  
export function createEvent<T = void>(type: string) {
    const channel = globalEventSystem.channel<T>(type);
  
    return {
      publish: (payload: T) => channel.publish(payload),
      subscribe: (handler: (payload: T) => void) => channel.subscribe(handler),
      getType: () => type
    };
}
