import type { Readable, Writable } from 'svelte/store';
import { derived, writable } from 'svelte/store';

export const latest_notifications: Writable<any[]> = writable<any[]>([]);

export const notifications_stats: Writable<{ unread: number; read: number; total: number }> =
	writable({ unread: 0, read: 0, total: 0 });

export const unread_notifications_count: Readable<number> = derived(
	notifications_stats,
	($notifications_stats) => $notifications_stats?.unread || 0
);


export const show_notification_view: Writable<boolean> = writable(false);
