<script lang="ts">
  import * as Sheet from '@/components/ui/sheet';
  import { Button } from '@/components/ui/button';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { useQueryClient } from '@tanstack/svelte-query';
  import { useUpdateEmployeeMutation, useUpdateContractMutation, employeeQueryKeys } from '../../../../queries/employeeQueries';
  import { employeeStore } from '@/hr/employees/stores/employees.svelte';
  import type { EmployeeFullProfile } from '@/hr/employees/types/types';
  import { getEditConfig } from './editConfig';

  
  /**
   * EmployeeEditSheet — Sheet d'édition des informations employé (profil/contrat).
   * SRP : ce composant encapsule TOUTE la logique de sauvegarde
   * (mutations TanStack + rafraîchissement store + invalidation cache)
   * et le rendu dynamique du formulaire selon l'onglet actif.
   */

  let {
    employee,
    open = $bindable(),
    activeTabId,
    onOpenChange,
  }: {
    employee: EmployeeFullProfile;
    open: boolean;
    activeTabId: string;
    onOpenChange: (open: boolean) => void;
  } = $props();

  const queryClient = useQueryClient();
  const updateMutation = useUpdateEmployeeMutation();
  const updateContractMutation = useUpdateContractMutation();

  const isPending = $derived($updateMutation.isPending || $updateContractMutation.isPending);

  const currentConfig = $derived(getEditConfig(activeTabId));

  // Instance du formulaire dynamique — typée any car les formulaires exposent
  // des méthodes différentes (submit() pour les deux actuels).
  let formInstance = $state<any>(null);

  async function handleSave(data: any) {
    try {
      if (activeTabId === 'contract') {
        await $updateContractMutation.mutateAsync({
          employeeId: employee.id.toString(),
          data,
        });
      } else {
        await $updateMutation.mutateAsync({
          employeeId: employee.id.toString(),
          data,
        });
      }

      // Rafraîchir le store global pour mettre à jour l'UI (Layout, etc.)
      await employeeStore.getFullProfileById(employee.id.toString());

      // Invalider les queries pour le cache TanStack
      await queryClient.invalidateQueries({
        queryKey: employeeQueryKeys.detail(employee.id.toString()),
      });

      onOpenChange(false);
    } catch {
      // Error is handled by the mutation's onError (toast notification)
    }
  }

  function handleSubmitForm() {
    formInstance?.submit();
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content class="sm:max-w-175 bg-white p-0 flex flex-col h-full overflow-hidden">
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <Sheet.Title class="text-[1rem] text-slate-900 truncate font-bold">
        {currentConfig?.title ?? 'Modifier'}
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar px-3">
      {#if currentConfig}
        {@const DynamicForm = currentConfig.component}
        <DynamicForm
          {employee}
          onSave={handleSave}
          bind:this={formInstance}
        />
      {:else}
        <div class="flex flex-col items-center justify-center gap-3 p-8 text-center text-slate-500">
          <AppIcon name="circle-alert" size={28} class="text-slate-300" />
          <p class="text-[0.86rem]">
            Le formulaire pour « {activeTabId} » n'est pas encore disponible.
          </p>
        </div>
      {/if}
    </div>

    <!-- Footer -->
    <Sheet.Footer class="px-6 py-2.5 border-t bg-slate-50/50 flex flex-col gap-3">
      <div class="flex gap-3 w-full">
        <Sheet.Close class="flex-1">
          <Button
            onclick={() => onOpenChange(false)}
            variant="outline"
            class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600 font-medium text-[0.88rem]"
          >
            <AppIcon name="x" size={17} class="text-slate-300" />
            Annuler
          </Button>
        </Sheet.Close>

        {#if currentConfig}
          <Button
            type="button"
            onclick={handleSubmitForm}
            class="flex-1"
            disabled={isPending}
          >
            {#if isPending}
              <AnimateSpin text="" class="size-3 border-white" />
            {:else}
              <AppIcon name="check" size={17} class="text-white" />
            {/if}
            {currentConfig.saveLabel}
          </Button>
        {/if}
      </div>
    </Sheet.Footer>

  </Sheet.Content>
</Sheet.Root>

