import { createMutation, useQueryClient } from '@tanstack/svelte-query';
import { employeesService } from '../services/employees.service';
import { employeeStore } from '../stores/employees.svelte';
import type { 
  EmployeeChild, 
  EmployeeEmergencyContact 
} from '../types/types';


const QUERY_KEY = 'employee_detail';


// ==========================================
// CHILDREN MUTATIONS
// ==========================================

export function useAddChildMutation(employeeId: string, onSuccess?: () => void) {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (data: Omit<EmployeeChild, 'id'>) => employeesService.addChild(employeeId, data),
    onSuccess: async () => {
      await employeeStore.getFullProfileById(employeeId);
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, employeeId] });
      onSuccess?.();
    }
  });
}


export function useUpdateChildMutation(employeeId: string, onSuccess?: () => void) {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({ childId, data }: { childId: string; data: Partial<EmployeeChild> }) => 
      employeesService.updateChild(childId, data),
    onSuccess: async () => {
      await employeeStore.getFullProfileById(employeeId);
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, employeeId] });
      onSuccess?.();
    }
  });
}


export function useDeleteChildMutation(employeeId: string) {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (childId: string) => employeesService.removeChild(childId),
    onSuccess: async () => {
      await employeeStore.getFullProfileById(employeeId);
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, employeeId] });
    }
  });
}


// ==========================================
// EMERGENCY CONTACTS MUTATIONS
// ==========================================

export function useAddEmergencyContactMutation(employeeId: string, onSuccess?: () => void) {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (data: Omit<EmployeeEmergencyContact, 'id'>) => employeesService.addEmergencyContact(employeeId, data),
    onSuccess: async () => {
      await employeeStore.getFullProfileById(employeeId);
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, employeeId] });
      onSuccess?.();
    }
  });
}


export function useUpdateEmergencyContactMutation(employeeId: string, onSuccess?: () => void) {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({ contactId, data }: { contactId: string; data: Partial<EmployeeEmergencyContact> }) => 
      employeesService.updateEmergencyContact(contactId, data),
    onSuccess: async () => {
      await employeeStore.getFullProfileById(employeeId);
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, employeeId] });
      onSuccess?.();
    }
  });
}


export function useDeleteEmergencyContactMutation(employeeId: string) {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (contactId: string) => employeesService.removeEmergencyContact(contactId),
    onSuccess: async () => {
      await employeeStore.getFullProfileById(employeeId);
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, employeeId] });
    }
  });
}

