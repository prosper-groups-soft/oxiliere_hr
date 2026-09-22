import { createMutation, useQueryClient } from '@tanstack/svelte-query';
import { employeesService } from '../services/employees.service';
import { employeeStore } from '../stores/employees.svelte';


const QUERY_KEY = 'employee_detail';


export function useAddDocumentMutation(employeeId: string, onSuccess?: () => void) {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (data: any) => employeesService.addDocument(employeeId, data),
    onSuccess: async () => {
      await employeeStore.getFullProfileById(employeeId);
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, employeeId] });
      onSuccess?.();
    }
  });
}

export function useUpdateDocumentMutation(employeeId: string, onSuccess?: () => void) {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({ documentId, data }: { documentId: string; data: any }) => 
      employeesService.updateDocument(documentId, data),
    onSuccess: async () => {
      await employeeStore.getFullProfileById(employeeId);
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, employeeId] });
      onSuccess?.();
    }
  });
}

export function useDeleteDocumentMutation(employeeId: string) {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (documentId: string) => employeesService.removeDocument(documentId),
    onSuccess: async () => {
      await employeeStore.getFullProfileById(employeeId);
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, employeeId] });
    }
  });
}export function useReplaceDocumentFileMutation(employeeId: string, onSuccess?: () => void) {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({ documentId, file }: { documentId: string; file: File }) => 
      employeesService.replaceDocumentFile(documentId, file),
    onSuccess: async () => {
      await employeeStore.getFullProfileById(employeeId);
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, employeeId] });
      onSuccess?.();
    }
  });
}
