import type { CalendarEvent } from "../types/types";
import { STATUS_LABELS, RECURRENCE_LABELS, SHORT_MONTHS } from "./event.constants";


/**
 * Affiche une plage horaire HH:MM-HH:MM ou juste HH:MM
 */
export function formatTimeDisplay(event: CalendarEvent): string | null {
  if (!event.startTime) return null;
  if (!event.endTime) return event.startTime.slice(0, 5);
  return `${event.startTime.slice(0, 5)}-${event.endTime.slice(0, 5)}`;
}

/**
 * Affiche une plage de dates lisible (ex: 15 Août - 20 Août)
 */
export function formatDateRange(event: CalendarEvent): string {
  if (!event.endDate || event.endDate === event.defaultDate) return '';
  const start = event.defaultDate.slice(8); // DD
  const end = event.endDate.slice(8);       // DD
  // If different months, include month
  if (event.defaultDate.slice(5, 7) !== event.endDate.slice(5, 7)) {
    const startM = SHORT_MONTHS[parseInt(event.defaultDate.slice(5, 7)) - 1];
    const endM = SHORT_MONTHS[parseInt(event.endDate.slice(5, 7)) - 1];
    return `${parseInt(start)} ${startM} - ${parseInt(end)} ${endM}`;
  }
  return `${parseInt(start)}-${parseInt(end)}`;
}

/**
 * Construit un tooltip multi-lignes pour un événement
 */
export function buildTooltip(event: CalendarEvent): string {
  const lines: string[] = [event.title];
  if (event.description) lines.push(`— ${event.description}`);
  lines.push(`Type: ${event.type}`);
  lines.push(`Statut: ${STATUS_LABELS[event.status || 'APPROVED'] || event.status}`);

  let dateStr = event.defaultDate;
  if (event.endDate && event.endDate !== event.defaultDate) {
    dateStr += ` → ${event.endDate}`;
  }
  lines.push(`Date: ${dateStr}`);

  if (event.startTime) {
    let timeStr = event.startTime.slice(0, 5);
    if (event.endTime) timeStr += ` → ${event.endTime.slice(0, 5)}`;
    lines.push(`Horaire: ${timeStr}`);
  }
  if (event.recurrent && event.recurrent !== 'NONE') {
    lines.push(`Récurrence: ${RECURRENCE_LABELS[event.recurrent] || event.recurrent}`);
  }
  if (event.code) lines.push(`Code: ${event.code}`);
  if (event.isWorkable === false) lines.push('🚫 Jour non travaillé');
  return lines.join('\n');
}

