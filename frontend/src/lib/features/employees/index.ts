// Export des types
export * from './types/types';

// Export du store
export { employeeStore, EmployeeStore } from './stores/employees.svelte';

// Export des queries
export {
  employeeQueryKeys,
  useEmployeesQuery,
  useEmployeeDetailQuery,
  useCreateEmployeeMutation,
  useUpdateEmployeeMutation,
  useAssignUserMutation,
  useRevokeUserMutation,
  useRefreshEmployees,
  syncEmployeesStore,
} from './queries/employeeQueries';


// Export des services
export { employeesService } from './services/employees.service';


// Export des endpoints
export { employeesEndpoint } from './api/employees.endpoints';


// Export des schémas de validation
export {
  createEmployeeSchema,
  updateEmployeeSchema,
  employeeAddressSchema,
  emergencyContactSchema,
  employeeChildSchema,
  employeeEducationSchema,
  type CreateEmployeeForm,
  type UpdateEmployeeForm,
  type EmployeeAddressForm,
  type EmergencyContactForm,
  type EmployeeChildForm,
  type EmployeeEducationForm,
} from './schemas/employee.schemas';

