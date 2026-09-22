import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
import { calendarService } from '../services/calendarService';
import { notification } from '@/hr/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/hr/constants/errors';
import type { CalendarEvent, EventType } from '../types/types';


// QUERY KEYS
export const calendarQueryKeys = {
  all: ['calendar'] as const,
  events: (startDate?: string, endDate?: string, eventType?: string, search?: string) =>
    [...calendarQueryKeys.all, 'events', startDate ?? '', endDate ?? '', eventType ?? '', search ?? ''] as const,
  detail: (id: string) => [...calendarQueryKeys.all, 'detail', id] as const,
};


/**
 * Query pour récupérer les événements du calendrier
 * Se recharge automatiquement quand les filtres changent
 */
export function useCalendarEventsQuery(
  startDate: () => string = () => '',
  endDate: () => string = () => '',
  eventType: () => string = () => '',
  search: () => string = () => ''
) {
  return createQuery({
    get queryKey() {
      return calendarQueryKeys.events(startDate(), endDate(), eventType(), search());
    },
    queryFn: () => calendarService.list({
      start_date: startDate() || undefined,
      end_date: endDate() || undefined,
      event_type: eventType() || undefined,
      search: search() || undefined,
    }),
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 10,   // 10 minutes
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  });
}


/**
 * Mutation pour créer un événement
 */
export function useCreateEventMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (data: {
      title: string;
      type: EventType;
      defaultDate: string;
      endDate?: string;
      description?: string;
      countryCode?: string;
    }) => calendarService.create(data),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: calendarQueryKeys.all
      });
      notification.toast.success('Événement créé avec succès');
    },

    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation pour mettre à jour un événement
 */
export function useUpdateEventMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({
      eventId,
      data,
    }: {
      eventId: string;
      data: {
        title?: string;
        type?: EventType;
        defaultDate?: string;
        endDate?: string;
        description?: string;
      };
    }) => calendarService.update(eventId, data),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: calendarQueryKeys.all
      });
      notification.toast.success('Événement mis à jour avec succès');
    },

    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation pour supprimer un événement
 */
export function useDeleteEventMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (eventId: string) => calendarService.delete(eventId),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: calendarQueryKeys.all
      });
      notification.toast.success('Événement supprimé');
    },

    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation pour initialiser les jours fériés par défaut
 */
export function useInitDefaultEventsMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: () => calendarService.importDefaultHolidays(),

    onSuccess: async (importedEvents) => {
      await queryClient.invalidateQueries({
        queryKey: calendarQueryKeys.all
      });

      const count = importedEvents?.length ?? 0;
      if (count > 0) {
        notification.toast.success(`${count} jours fériés importés avec succès`);
      } else {
        notification.toast.info('Aucun jour férié à importer');
      }
    },

    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}
