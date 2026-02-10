import { writable } from 'svelte/store';
// import ReconnectingWebSocket from 'reconnecting-websocket';
// import type { Options } from 'reconnecting-websocket';
import { latest_notifications, notifications_stats } from './notifications';


export const socket = writable< null>(null);

export const connectionStatus = writable<'connected' | 'disconnected' | 'connecting'>('disconnected');

let audio: HTMLAudioElement | undefined;

if (typeof window !== 'undefined') {
    audio = new Audio('/sounds/notification.wav');
}


const defaultSocketOptions: Options = {
  maxReconnectionDelay: 10000,
  minReconnectionDelay: 1000 + Math.random() * 4000,
  reconnectionDelayGrowFactor: 1.3,
  minUptime: 5000,
  connectionTimeout: 4000,
  maxRetries: 15,
  maxEnqueuedMessages: Infinity,
  startClosed: false,
  debug: false,
};


export function connect(customOptions: Partial<Options> = {}) {
  const socketOptions: Options = {
    ...defaultSocketOptions,
    ...customOptions
  };
    
  const wsUrl = `${location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/notify`;
  
  const ws = new ReconnectingWebSocket(wsUrl, [], socketOptions);
  
  ws.addEventListener('open', () => {
    connectionStatus.set('connected');
  });
    
  ws.addEventListener('close', () => {
    connectionStatus.set('disconnected');
  });
    
  connectionStatus.set('connecting');
  
  ws.addEventListener('error', () => {
    connectionStatus.set('connecting');
  });
    
  ws.addEventListener('message', (event: any) => {
    const data = JSON.parse(event.data);
    if (data.type === "notify" || data.type === "alert") {
      data.type = "notif";
      latest_notifications.update((n: any[]) => {
        return [data.payload, ...n];
      });
      notifications_stats.update((stats) => {
        stats.unread += 1;
        stats.total += 1;
        return stats;
      });
      audio?.play();
    }
  });
  
  socket.set(ws);
  
  return ws;
}


export function disconnect() {
  socket.update(ws => {
    if (ws) {
      ws.close();
    }
    return null;
  });
  connectionStatus.set('disconnected');
}


export function reconnect() {
  socket.update(ws => {
    if (ws) {
      ws.reconnect();
    }
    return ws;
  });
}


export function isConnected() {
  let connected = false;
  connectionStatus.subscribe(status => {
    connected = status === 'connected';
  })();
  return connected;
}

