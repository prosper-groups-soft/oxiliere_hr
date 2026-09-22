<script lang="ts">
  import * as Sheet from '@/components/ui/sheet';
  import { Button } from '@/components/ui/button';
  import { Input } from '@/components/ui/input';
  import { Label } from '@/components/ui/label';
  import { Checkbox } from '@/components/ui/checkbox';
  import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger
  } from '@/components/ui/select';
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';
  import ValidationError from '@/hr/components/ui/validation-error';
  import type { Employee } from '@/hr/modules/employees/types/types';
  import { buildFullName } from "@/hr/utilities/common/employee.utils";
  import { cn } from "@/hr/utilities/common/css";
  import { fade } from "svelte/transition";
  import { 
    suspendEmployeeSchema, 
    reactivateEmployeeSchema, 
    offboardEmployeeSchema 
  } from '@/hr/modules/employees/schemas/employee.schemas';

  let { 
    open = $bindable(false),
    action,
    employee,
    onSave
  } = $props<{
    open: boolean;
    action: 'SUSPEND' | 'REACTIVATE' | 'OFFBOARD' | null;
    employee: Employee;
    onSave: (action: 'SUSPEND' | 'REACTIVATE' | 'OFFBOARD', data: any) => Promise<void>;
  }>();

  let isLoading = $state(false);
  let errors = $state<Record<string, string>>({});
  
  // Utiliser la date du jour par défaut
  const today = new Date().toISOString().split('T')[0];
  
  let suspendData = $state({ reason: '', effective_date: today });
  let reactivateData = $state({ reason: '', effective_date: today, is_active: true, can_connect: true });
  let offboardData = $state({ reason: '', end_date: today, departure_type: 'TERMINATED' as 'TERMINATED' | 'RESIGNED' | 'RETIRED' });

  const sheetTitle = $derived.by(() => {
    switch (action) {
      case 'SUSPEND': return 'Suspendre le contrat';
      case 'REACTIVATE': return 'Réactiver l\'employé';
      case 'OFFBOARD': return 'Lancer l\'offboarding';
      default: return '';
    }
  });

  const sheetDescription = $derived.by(() => {
    switch (action) {
      case 'SUSPEND': return `Vous êtes sur le point de suspendre le contrat de ${buildFullName(employee)}.`;
      case 'REACTIVATE': return `Réactivation de ${buildFullName(employee)}.`;
      case 'OFFBOARD': return `Lancement de la procédure de départ pour ${buildFullName(employee)}. Sélectionnez le type de départ, cette action clôturera son poste actuel.`;
      default: return '';
    }
  });

  function setErrors(fieldErrors: Record<string, string[] | undefined>) {
    errors = Object.fromEntries(
      Object.entries(fieldErrors).map(([key, val]) => [key, val?.[0] || ''])
    );
  }

  async function handleSubmit(e?: Event) {
    if (e) e.preventDefault();
    errors = {};
    isLoading = true;

    try {
      if (action === 'SUSPEND') {
        const result = suspendEmployeeSchema.safeParse(suspendData);
        if (!result.success) {
          setErrors(result.error.flatten().fieldErrors);
          return;
        }
        await onSave('SUSPEND', result.data);
      } else if (action === 'REACTIVATE') {
        const result = reactivateEmployeeSchema.safeParse(reactivateData);
        if (!result.success) {
          setErrors(result.error.flatten().fieldErrors);
          return;
        }
        await onSave('REACTIVATE', result.data);
      } else if (action === 'OFFBOARD') {
        const result = offboardEmployeeSchema.safeParse(offboardData);
        if (!result.success) {
          setErrors(result.error.flatten().fieldErrors);
          return;
        }
        await onSave('OFFBOARD', result.data);
      }
      open = false;
    } catch (err) {
      console.error("Erreur lors de l'enregistrement", err);
    } finally {
      isLoading = false;
    }
  }

  function clearError(field: string) {
    errors = { ...errors, [field]: '' };
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md bg-white p-0 flex flex-col h-full overflow-hidden">
    
    <!-- Header aligned with TransitionSheet -->
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <div class="flex items-center gap-3">
        <div class="space-y-0.5 min-w-0">
          <Sheet.Title class="text-[1rem] text-slate-900 truncate font-bold">
            {sheetTitle}
          </Sheet.Title>
          <Sheet.Description class="text-[0.8rem] text-slate-500">
            {sheetDescription}
          </Sheet.Description>
        </div>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-4 space-y-6" in:fade={{ duration: 200 }}>
        
        {#if action === 'SUSPEND'}
          <div class="space-y-2.5">
            <Label for="effective_date" class="text-slate-900">Date d'effet <span class="text-red-500">*</span></Label>
            <Input 
              id="effective_date" 
              type="date" 
              bind:value={suspendData.effective_date}
              oninput={() => clearError('effective_date')}
              class={cn(
                "h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine",
                errors.effective_date && "border-red-500 focus:ring-red-500"
              )}
            />
            <ValidationError {errors} field="effective_date" />
          </div>
          
          <div class="space-y-2.5">
            <Label for="reason" class="text-slate-900">Motif de la suspension <span class="text-red-500">*</span></Label>
            <textarea
              id="reason"
              bind:value={suspendData.reason}
              oninput={() => clearError('reason')}
              class={cn(
                "w-full h-28 rounded-lg border border-slate-200 px-3.5 py-3 text-[0.88rem] leading-relaxed focus:ring-4 focus:ring-primary/30 focus:border-primary focus:outline-none bg-white shadow-fine resize-none transition-all placeholder:text-slate-400",
                errors.reason && "border-red-500 focus:ring-red-500"
              )}
              placeholder="Décrivez la raison (mise à pied, congé sans solde prolongé...)"
            ></textarea>
            <ValidationError {errors} field="reason" />
          </div>
        {/if}

        {#if action === 'REACTIVATE'}
          <div class="space-y-2.5">
            <Label for="effective_date" class="text-slate-900">Date d'effet <span class="text-red-500">*</span></Label>
            <Input 
              id="effective_date" 
              type="date" 
              bind:value={reactivateData.effective_date}
              oninput={() => clearError('effective_date')}
              class={cn(
                "h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine",
                errors.effective_date && "border-red-500 focus:ring-red-500"
              )}
            />
            <ValidationError {errors} field="effective_date" />
          </div>
          
          <div class="space-y-2.5">
            <Label for="reason" class="text-slate-900">Motif / Commentaire (optionnel)</Label>
            <textarea
              id="reason"
              bind:value={reactivateData.reason}
              oninput={() => clearError('reason')}
              class={cn(
                "w-full h-28 rounded-lg border border-slate-200 px-3.5 py-3 text-[0.88rem] leading-relaxed focus:ring-4 focus:ring-primary/30 focus:border-primary focus:outline-none bg-white shadow-fine resize-none transition-all placeholder:text-slate-400",
                errors.reason && "border-red-500 focus:ring-red-500"
              )}
              placeholder="Ajouter un commentaire..."
            ></textarea>
            <ValidationError {errors} field="reason" />
          </div>
          
          <div class="flex items-center space-x-2 pt-2">
            <Checkbox id="is_active" bind:checked={reactivateData.is_active} />
            <Label for="is_active" class="cursor-pointer text-slate-800 text-[0.9rem]">Rendre l'employé actif</Label>
          </div>
          <div class="flex items-center space-x-2 pt-1">
            <Checkbox id="can_connect" bind:checked={reactivateData.can_connect} />
            <Label for="can_connect" class="cursor-pointer text-slate-800 text-[0.9rem]">Restaurer l'accès au portail</Label>
          </div>
        {/if}

        {#if action === 'OFFBOARD'}
          <div class="space-y-2.5">
            <Label for="end_date" class="text-slate-900">Date de départ <span class="text-red-500">*</span></Label>
            <Input 
              id="end_date" 
              type="date" 
              bind:value={offboardData.end_date}
              oninput={() => clearError('end_date')}
              class={cn(
                "h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine",
                errors.end_date && "border-red-500 focus:ring-red-500"
              )}
            />
            <ValidationError {errors} field="end_date" />
          </div>
          
          <div class="space-y-2.5">
            <Label for="departure_type" class="text-slate-900">Type de départ <span class="text-red-500">*</span></Label>
            <Select
              type="single"
              value={offboardData.departure_type}
              onValueChange={(v: string) => { offboardData.departure_type = v as 'TERMINATED' | 'RESIGNED' | 'RETIRED'; clearError('departure_type'); }}
            >
              <SelectTrigger id="departure_type" class={cn(
                "h-10 w-full bg-white border-slate-200 shadow-fine rounded-md cursor-pointer",
                errors.departure_type && "border-red-500"
              )}>
                <span class="truncate text-[0.87rem] font-medium">
                  {offboardData.departure_type === 'TERMINATED' ? 'Licenciement / Fin de contrat' : offboardData.departure_type === 'RESIGNED' ? 'Démission' : offboardData.departure_type === 'RETIRED' ? 'Retraite' : 'Sélectionnez le type de départ...'}
                </span>
              </SelectTrigger>
              <SelectContent class="z-9999">
                <SelectItem value="TERMINATED" class="text-[0.85rem]">Licenciement / Fin de contrat</SelectItem>
                <SelectItem value="RESIGNED" class="text-[0.85rem]">Démission</SelectItem>
                <SelectItem value="RETIRED" class="text-[0.85rem]">Retraite</SelectItem>
              </SelectContent>
            </Select>
            <ValidationError {errors} field="departure_type" />
          </div>
          
          <div class="space-y-2.5">
            <Label for="reason" class="text-slate-900">Motif du départ <span class="text-red-500">*</span></Label>
            <textarea
              id="reason"
              bind:value={offboardData.reason}
              oninput={() => clearError('reason')}
              class={cn(
                "w-full h-28 rounded-lg border border-slate-200 px-3.5 py-3 text-[0.88rem] leading-relaxed focus:ring-4 focus:ring-primary/30 focus:border-primary focus:outline-none bg-white shadow-fine resize-none transition-all placeholder:text-slate-400",
                errors.reason && "border-red-500 focus:ring-red-500"
              )}
              placeholder="Décrivez les raisons ou le contexte de ce départ..."
            ></textarea>
            <ValidationError {errors} field="reason" />
          </div>
        {/if}

      </div>
    </div>

    <!-- Footer aligned with TransitionSheet -->
    <Sheet.Footer class="px-6 py-2.5 border-t bg-slate-50/50 flex flex-col gap-3">
      <div class="flex gap-3 w-full">
        <Sheet.Close class="flex-1">
          <Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600 font-medium text-[0.88rem]">
            <AppIcon name="x" size={18} class="text-slate-300" />
            Annuler
          </Button>
        </Sheet.Close>
        
        <Button 
          onclick={() => handleSubmit()} 
          disabled={isLoading}
          class={cn(
            "flex-1 font-medium h-9 shadow-fine text-[0.88rem] hover:opacity-90 transition-all disabled:opacity-70",
            action === 'OFFBOARD' ? "bg-red-600 text-white hover:bg-red-700" : "bg-primary! text-white"
          )}
        >
          {#if isLoading}
            <AnimateSpin text="" class="size-3 border-white" />
          {:else}
            <AppIcon name="check" size={18} />
          {/if}
          {action === 'OFFBOARD' ? 'Confirmer le départ' : 'Enregistrer'}
        </Button>
      </div>
    </Sheet.Footer>

  </Sheet.Content>
</Sheet.Root>




