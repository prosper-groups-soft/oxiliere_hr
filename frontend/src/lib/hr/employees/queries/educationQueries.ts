import { createMutation, useQueryClient } from '@tanstack/svelte-query';
import { employeesService } from '../services/employees.service';
import { employeeStore } from '../stores/employees.svelte';


const QUERY_KEY = 'employee_detail';


export function useAddEducationMutation(employeeId: string, onSuccess?: () => void) {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (data: any) => employeesService.addEducation(employeeId, data),
    onSuccess: async () => {
      await employeeStore.getFullProfileById(employeeId);
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, employeeId] });
      onSuccess?.();
    }
  });
}

export function useUpdateEducationMutation(employeeId: string, onSuccess?: () => void) {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({ educationId, data }: { educationId: string; data: any }) => 
      employeesService.updateEducation(educationId, data),
    onSuccess: async () => {
      await employeeStore.getFullProfileById(employeeId);
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, employeeId] });
      onSuccess?.();
    }
  });
}

export function useDeleteEducationMutation(employeeId: string) {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (educationId: string) => employeesService.removeEducation(educationId),
    onSuccess: async () => {
      await employeeStore.getFullProfileById(employeeId);
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, employeeId] });
    }
  });
}
