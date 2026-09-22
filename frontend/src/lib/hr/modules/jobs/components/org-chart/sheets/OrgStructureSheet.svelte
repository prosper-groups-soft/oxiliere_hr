<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Button } from "@/components/ui/button";
  import * as Avatar from "@/components/ui/avatar";
  import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select";
  import { Badge } from "@/components/ui/badge";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import Empty from "@/hr/components/shared/containers/empty/Empty.svelte";
  import { jobsStore } from "../../../stores/jobs.svelte";
  import { useAllEmployees } from "@/hr/modules/employees/queries/employeeQueries";
  import { formatEmployeeName } from "@/hr/utilities/common/employee.utils";
  import { getInitials } from "@/hr/utilities/common/string";
  import { getAvatarPalette } from "@/hr/utilities/common/func";
  import { cn } from "@/hr/utilities/common/css";
  import { useCreateOrgUnitMutation, useUpdateOrgUnitMutation } from "../../../queries/orgQueries";
  import AnimateSpin from "@/hr/components/layout/elements/AnimateSpin.svelte";
  import ConfirmAction from "@/hr/components/shared/actions/ConfirmAction.svelte";
  import { notification } from "@/hr/stores/notification.svelte";
  import type { NodeType } from "../../../types/types";
  import type { OrgUnit, OrgUnitCreate, OrgUnitUpdate } from '../../../types/org.types';
  import type { Employee } from "@/hr/modules/employees/types/types";
  import { slide, fade } from 'svelte/transition';
  import { orgUnitSchema } from '../../../schemas/orgUnit.schema';
  import ValidationError from "@/hr/components/ui/validation-error";
  import { z } from 'zod';

  
  let { 
    open = $bindable(false),
    preselectedParentId = $bindable(null),
    editingOrgUnitId = $bindable(null)
  } = $props<{ 
    open: boolean, 
    preselectedParentId?: string | null,
    editingOrgUnitId?: string | null
  }>();

  // --- Form state (doit être déclaré avant les queries qui en dépendent) ---
  let isEditing = $state(false);
  let editingOrgUnit = $state<OrgUnit | null>(null);
  let formName = $state('');
  let formType = $state<NodeType>('DEPARTMENT');
  let formParentId = $state<string | null>(null);
  let formManagerId = $state<string | null>(null);
  let formAffointId = $state<string | null>(null);
  let formAuthorizedHeadcount = $state(0);

  // --- Queries ---
  const createOrgUnitMutation = useCreateOrgUnitMutation();
  const updateOrgUnitMutation = useUpdateOrgUnitMutation();
  
  // Requête pour la liste des employés (nécessaire pour les selects)
  const allEmployeesQuery = useAllEmployees();
  
  // Helper pour trouver un employé par ID dans la liste chargée
  function getEmployeeById(id: string | null) {
    if (!id) return undefined;
    const employees = $allEmployeesQuery.data;
    if (!employees) return undefined;
    return employees.find((e: { id: string | number }) => String(e.id) === id);
  }

  // Sync preselectedParentId when sheet opens
  $effect(() => {
    if (open && preselectedParentId) {
      editingOrgUnit = null;
      formName = '';
      formParentId = preselectedParentId;
      formManagerId = null;
      formAffointId = null;
      formAuthorizedHeadcount = 0;
      isEditing = true;
      preselectedParentId = null;
      clearValidationErrors();
    }
  });

  // Sync editingOrgUnitId when set from parent (via OrgNode)
  $effect(() => {
    if (editingOrgUnitId) {
      const orgUnit = jobsStore.getOrgUnitById(editingOrgUnitId);
      if (orgUnit) {
        openEdit(orgUnit);
        open = true;
      }
      editingOrgUnitId = null; // Reset after opening
    }
  });

  // --- Handlers ---
  function openAdd() {
    editingOrgUnit = null;
    formName = '';
    formType = 'DEPARTMENT';
    formParentId = null;
    formManagerId = null;
    formAffointId = null;
    formAuthorizedHeadcount = 0;
    isEditing = true;
    clearValidationErrors();
  }

  function openEdit(orgUnit: OrgUnit) {
    editingOrgUnit = orgUnit;
    formName = orgUnit.name;
    formType = orgUnit.type;
    formParentId = orgUnit.parentId;
    formManagerId = orgUnit.managerId;
    formAffointId = orgUnit.affointId ?? null;
    formAuthorizedHeadcount = orgUnit.authorizedHeadcount;
    isEditing = true;
    clearValidationErrors();
  }

  // Labels dérivés depuis allEmployeesQuery (utilisation de formatEmployeeName)
  const managerLabel = $derived(
    formManagerId
      ? formatEmployeeName(getEmployeeById(formManagerId))
      : '— Aucun'
  );
  
  const affointLabel = $derived(
    formAffointId
      ? formatEmployeeName(getEmployeeById(formAffointId))
      : '— Aucun'
  );

  function clearValidationErrors() {
    validationErrors = {};
  }

  function clearValidationError(field: string) {
    if (validationErrors[field]) {
      const { [field]: _, ...rest } = validationErrors;
      validationErrors = rest;
    }
  }

  function setValidationError(field: string, message: string) {
    validationErrors = { ...validationErrors, [field]: message };
  }

  async function handleSave() {
    clearValidationErrors();

    // Validation Zod
    const formData = {
      name: formName.trim(),
      type: formType,
      parentId: formParentId,
      managerId: formManagerId,
      affointId: formAffointId,
      authorizedHeadcount: formAuthorizedHeadcount,
    };

    const result = orgUnitSchema.safeParse(formData);
    if (!result.success) {
      result.error.issues.forEach((err: z.core.$ZodIssue) => {
        setValidationError(String(err.path[0]), err.message);
      });
      return;
    }

    try {
      if (editingOrgUnit) {
        // Mode édition : n'envoyer que les champs modifiés
        const changedData: Partial<OrgUnitUpdate> = {};
        const trimmedName = formName.trim();

        if (trimmedName !== editingOrgUnit.name) changedData.name = trimmedName;
        if (formType !== editingOrgUnit.type) changedData.type = formType;
        if (formParentId !== editingOrgUnit.parentId) changedData.parentId = formParentId;
        if (formManagerId !== editingOrgUnit.managerId) changedData.managerId = formManagerId;
        if (formAffointId !== (editingOrgUnit.affointId ?? null)) changedData.affointId = formAffointId;
        if (formAuthorizedHeadcount !== editingOrgUnit.authorizedHeadcount) {
          changedData.authorizedHeadcount = formAuthorizedHeadcount;
        }

        // N'envoyer que si au moins un champ a changé
        if (Object.keys(changedData).length > 0) {
          await $updateOrgUnitMutation.mutateAsync({ id: editingOrgUnit.id, data: changedData });
        }
      } else {
        // Mode création : envoyer tous les champs
        const data: OrgUnitCreate = {
          name: formName.trim(),
          type: formType,
          parentId: formParentId,
          managerId: formManagerId,
          affointId: formAffointId,
          authorizedHeadcount: formAuthorizedHeadcount,
        };
        await $createOrgUnitMutation.mutateAsync(data);
      }
      isEditing = false;
      clearValidationErrors();
    } catch (error) {
      // Error already handled by mutation onError
      console.error('Failed to save org unit:', error);
    }
  }
  
  // État de soumission
  const isSubmitting = $derived($createOrgUnitMutation.isPending || $updateOrgUnitMutation.isPending);
  
  // État de confirmation de suppression
  let deletingOrgUnitId = $state<string | null>(null);

  // État des erreurs de validation
  let validationErrors = $state<Record<string, string>>({});

  function requestDelete(orgUnit: OrgUnit) {
    const guardMessage = jobsStore.getDeleteOrgUnitGuard(orgUnit);
    if (guardMessage) {
      notification.toast.error(guardMessage);
      return;
    }

    deletingOrgUnitId = orgUnit.id;
  }

  async function confirmDelete(orgUnit: OrgUnit) {
    try {
      await jobsStore.deleteOrgUnit(orgUnit.id);
      notification.toast.success(`L'unite "${orgUnit.name}" a été supprimée.`);
    } catch {
      // Error toast is handled by the service.
    } finally {
      deletingOrgUnitId = null;
    }
  }

  const otherOrgUnits = $derived(
    editingOrgUnit
      ? jobsStore.orgUnits.filter(orgUnit => orgUnit.id !== editingOrgUnit!.id)
      : jobsStore.orgUnits
  );

  const parentLabel = $derived(
    formParentId 
      ? otherOrgUnits.find(orgUnit => orgUnit.id === formParentId)?.name ?? '— Aucun (Racine)'
      : '— Aucun (Racine)'
  );
  
  // Convert null to empty string for Select compatibility
  const selectParentId = $derived(formParentId ?? '');
  function handleParentChange(value: string) {
    formParentId = value || null;
  }

  const selectManagerId = $derived(formManagerId ?? '');

  function handleManagerChange(value: string) {
    formManagerId = value || null;
  }

  const selectAffointId = $derived(formAffointId ?? '');

  function handleAffointChange(value: string) {
    formAffointId = value || null;
  }

  // --- Node Type Options ---
  const nodeTypeItems = [
    { value: 'DEPARTMENT', label: 'Département', icon: 'business' },
    { value: 'DIVISION',   label: 'Division',    icon: 'corporate_fare' },
    { value: 'TEAM',       label: 'Équipe',      icon: 'team'     },
    { value: 'FUNCTION',   label: 'Fonction',    icon: 'settings' },
    { value: 'BRANCH',     label: 'Succursale',  icon: 'store'    },
    { value: 'PROJECT',    label: 'Projet',      icon: 'folder'   }
  ] satisfies { value: string; label: string; icon: string }[];

  const selectedNodeType = $derived(nodeTypeItems.find(i => i.value === formType));

  // --- Hierarchical Sorting ---
  interface FlatOrgUnit extends OrgUnit {
    level: number;
    childCount: number;
  }

  const hierarchicalOrgUnits = $derived.by(() => {
    const result: FlatOrgUnit[] = [];
    
    function traverse(orgUnitId: string | null, level: number) {
      const children = jobsStore.orgUnits.filter(orgUnit => orgUnit.parentId === orgUnitId);
      children.forEach(child => {
        const descendants = jobsStore.orgUnits.filter(orgUnit => orgUnit.parentId === child.id);
        result.push({ 
          ...child, 
          level,
          childCount: descendants.length
        });
        traverse(child.id, level + 1);
      });
    }

    traverse(null, 0);
    return result;
  });
</script>


{#snippet FormNumberInput(id: string, label: string, value: number, onChange: (v: number) => void)}
  <div class="space-y-2">
    <Label for={id}>{label}</Label>
    <Input {id} type="number" {value} onchange={(e) => onChange(Number(e.currentTarget.value))} class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
  </div>
{/snippet}


{#snippet FormInput(id: string, label: string, value: string, placeholder: string, required: boolean = false, type: string = 'text', onChange: (v: string) => void)}
  <div class="space-y-2">
    <Label for={id}>{label} {@html required ? '<span class="text-red-500">*</span>' : ''}</Label>
    <Input 
      {id} 
      {type}
      {value} 
      onchange={(e) => onChange(e.currentTarget.value)}
      {placeholder}
      class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine"
    />
  </div>
{/snippet}


{#snippet FormSelect(label: string, triggerLabel: string, items: { value: string, label: string }[], selectedValue: string, onChange: (v: string) => void)}
  <div class="space-y-2">
    <Label>{label}</Label>
    <Select type="single" value={selectedValue} onValueChange={onChange}>
      <SelectTrigger class="h-10 w-full shadow-fine">
        <span class="truncate text-sm">{triggerLabel}</span>
      </SelectTrigger>
      <SelectContent class="z-9999"> 
        {#each items as item}
          <SelectItem value={item.value}>{item.label}</SelectItem>
        {/each}
      </SelectContent>
    </Select>
  </div>
{/snippet}


{#snippet FormSelectWithIcons(label: string, triggerIcon: string, triggerLabel: string, items: { value: string, label: string, icon: string }[], selectedValue: string, onChange: (v: string) => void)}
  <div class="space-y-2">
    <Label>{label}</Label>
    <Select type="single" value={selectedValue} onValueChange={onChange}>
      <SelectTrigger class="h-10 w-full shadow-fine">
        <span class="flex items-center gap-2 truncate text-sm">
          <AppIcon name={triggerIcon} size={18} class="text-slate-500 shrink-0" />
          {triggerLabel}
        </span>
      </SelectTrigger>
      <SelectContent class="z-9999">
        {#each items as item}
          <SelectItem value={item.value}>
            <span class="flex items-center gap-2 text-[0.86rem]">
              <AppIcon name={item.icon} size={18} class="text-slate-500 shrink-0" />
              {item.label}
            </span>
          </SelectItem>
        {/each}
      </SelectContent>
    </Select>
  </div>
{/snippet}


{#snippet FormEmployeeSelect(label: string, triggerLabel: string, employees: Employee[], selectedValue: string, onChange: (v: string) => void)}
  {@const selectedEmployee = employees.find(e => String(e.id) === selectedValue)}
  {@const selectedPalette = selectedEmployee ? getAvatarPalette(selectedEmployee.name) : null}
  
  <div class="space-y-2">
    <Label>{label}</Label>
    <Select type="single" value={selectedValue} onValueChange={onChange}>
      <SelectTrigger class="h-10 w-full shadow-fine">
        <span class="flex items-center gap-2 truncate text-sm">
          {#if selectedEmployee}
            <Avatar.Root class="h-6 w-6 border border-slate-200 shrink-0">
              <Avatar.Image src={selectedEmployee.avatarUrl} alt={selectedEmployee.name} />
              <Avatar.Fallback class={cn("text-[0.85rem] font-medium", selectedPalette?.bg, selectedPalette?.text)}>
                {getInitials(...selectedEmployee.name.split(' '))}
              </Avatar.Fallback>
            </Avatar.Root>
            <span class="truncate text-[0.87rem]">{selectedEmployee.name}</span>
          {:else}
            <AppIcon name="circle-user" size={18} class="text-slate-400 shrink-0" />
            <span class="text-slate-500 text-[0.87rem]">{triggerLabel}</span>
          {/if}
        </span>
      </SelectTrigger>
      <SelectContent class="z-9999">
        <SelectItem value="">
          <span class="flex items-center gap-2 text-[0.87rem] text-slate-500">
            <AppIcon name="circle-user" size={18} class="shrink-0" />
            — Aucun
          </span>
        </SelectItem>
        {#each employees as employee}
          {@const palette = getAvatarPalette(employee.name)}
          <SelectItem value={String(employee.id)}>
            <span class="flex items-center gap-2 text-[0.86rem]">
              <Avatar.Root class="h-6 w-6 border border-slate-200 shrink-0">
                <Avatar.Image src={employee.avatarUrl} alt={employee.name} />
                <Avatar.Fallback class={cn("text-[0.6rem] font-medium", palette.bg, palette.text)}>
                  {getInitials(...employee.name.split(' '))}
                </Avatar.Fallback>
              </Avatar.Root>
              <span class="truncate text-[0.87rem]">{employee.name}</span>
            </span>
          </SelectItem>
        {/each}
      </SelectContent>
    </Select>
  </div>
{/snippet}


{#snippet FormHeader(title: string)}
  <header class="flex flex-col gap-9 mb-6">
     <Button variant="default" onclick={() => isEditing = false} class="h-7.5 text-[0.84rem] rounded-lg transition-colors self-start">
       <AppIcon name="arrow-left" size={18} />
       Retour
     </Button>
     <h3 class="font-bold text-slate-800">{title}</h3>
  </header>
{/snippet}


{#snippet OrgUnitListView()}
  <div class="flex flex-col flex-1 min-h-0">
    <!-- Header avec compteur et bouton -->
    <div class="px-6 py-4 pt-0 border-b border-slate-100 bg-white">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <AppIcon name="network" size={20} class="text-slate-500" />
          <span class="text-[0.875rem] font-medium text-slate-700">
            {hierarchicalOrgUnits.length} unité{hierarchicalOrgUnits.length > 1 ? 's' : ''}
          </span>
        </div>
        <Button 
          onclick={openAdd} 
          size="sm" 
          class="bg-primary text-white text-[0.84rem] h-8 px-3 shadow-fine transition-shadow"
        >
          <AppIcon name="plus" size={17} />
          Nouvelle unité
        </Button>
      </div>
    </div>

    <!-- Liste des unités -->
    <div class="flex flex-col flex-1 py-2">
      {#each hierarchicalOrgUnits as orgUnit, i}
        <div in:slide={{ duration: 250, delay: i * 30 }} out:fade={{ duration: 150 }}>
          {@render OrgUnitRow(orgUnit)}
        </div>
      {:else}
        <div class="flex-1 flex items-center justify-center px-6" in:fade={{ duration: 200 }}>
          <Empty 
            title="Aucune unité" 
            description="Commencez par créer votre première unité pour structurer votre organisation." 
            icon="network"
            iconClass="text-slate-300"
            iconSize={26}
            iconStrokeWidth={1}
          />
        </div>
      {/each}
    </div>
  </div>
{/snippet}


{#snippet OrgUnitFormView()}
  <div class="p-6 pt-0 h-full" in:fade={{ duration: 200 }}>
    {@render FormHeader(editingOrgUnit ? "Modifier l'unité" : "Nouveau unité")}

    <form id="org-unit-form-sheet" onsubmit={(e) => { e.preventDefault(); handleSave(); }} class="space-y-5">
      <div class="space-y-1">
        {@render FormInput('org-unit-name', 'Nom', formName, 'ex: Ressources Humaines', false, 'text', (v) => { formName = v; clearValidationError('name'); })}
        <ValidationError errors={validationErrors} field="name" />
      </div>

      {@render FormSelectWithIcons(
        'Type de noeud',
        selectedNodeType?.icon ?? 'business',
        selectedNodeType?.label ?? 'Unité',
        nodeTypeItems,
        formType,
        (v) => formType = v as NodeType
      )}

      {@render FormSelect(
        'Unité parent',
        parentLabel,
        [{ value: '', label: '— Aucun (Racine)' }, ...otherOrgUnits.map((orgUnit: OrgUnit) => ({ value: orgUnit.id, label: orgUnit.name }))],
        selectParentId,
        handleParentChange
      )}

      <div class="space-y-1">
        {@render FormEmployeeSelect(
          'Responsable (Manager)',
          managerLabel,
          ($allEmployeesQuery.data ?? []) as Employee[],
          selectManagerId,
          (v) => { handleManagerChange(v); clearValidationError('managerId'); }
        )}
        <ValidationError errors={validationErrors} field="managerId" />
      </div>

      {@render FormEmployeeSelect(
        'Adjoint',
        affointLabel,
        ($allEmployeesQuery.data ?? []) as Employee[],
        selectAffointId,
        handleAffointChange
      )}

      <div class="space-y-1">
        {@render FormNumberInput(
          'org-unit-authorized-headcount',
          'Effectif autorisé',
          formAuthorizedHeadcount,
          (v) => { formAuthorizedHeadcount = v; clearValidationError('authorizedHeadcount'); }
        )}
        <ValidationError errors={validationErrors} field="authorizedHeadcount" />
      </div>
    </form>
  </div>
{/snippet}


{#snippet OrgUnitFooterActions()}
  {#if isEditing}
    <div in:fade={{ duration: 150 }} class="flex flex-row gap-3 w-full">
      <Button variant="outline" onclick={() => isEditing = false} class="flex-1 h-9 shadow-fine">
        <AppIcon name="x" class="text-slate-300" size={16} />
        Annuler
      </Button>
      <Button 
        type="submit"
        form="org-unit-form-sheet"
        disabled={isSubmitting}
        class="flex-1 h-9 bg-primary text-white shadow-fine transition-all"
      >
        {#if isSubmitting}
          <AnimateSpin class="border-white size-3" text="" />
        {:else}
          <AppIcon name="check" size={16} />
        {/if}
        Enregistrer
      </Button>
    </div>
  {:else}
    <div in:fade={{ duration: 150 }} class="w-full">
      <Sheet.Close class="w-full">
        <Button variant="outline" class="w-full h-9 text-slate-900 border-slate-200 shadow-fine">
          <AppIcon name="x" class="text-slate-300" size={16} />
          Fermer
        </Button>
      </Sheet.Close>
    </div>
  {/if}
{/snippet}


{#snippet EmployeeChip(employee: import('../../../types/org.types').OrgChartEmployee | null | undefined, label: string)}
  {@const empName = employee ? formatEmployeeName(employee) : ''}
  {#if employee}
    {@const palette = getAvatarPalette(empName)}
    <div class="flex items-center gap-1.5 min-w-0" title={label}>
      <Avatar.Root class="h-7 w-7 border border-slate-200 rounded-full shrink-0">
        <Avatar.Image src={employee.photo || ''} alt={empName} />
        <Avatar.Fallback class={cn("text-[0.82rem] font-medium", palette.bg, palette.text)}>
          {getInitials(...empName.split(' '))}
        </Avatar.Fallback>
      </Avatar.Root>
      <span class="text-[0.86rem] text-slate-700 truncate">{empName}</span>
    </div>
  {:else}
    <span class="text-[0.83rem] text-slate-400 italic font-medium">{label}: —</span>
  {/if}
{/snippet}


{#snippet OrgUnitRow(orgUnit: FlatOrgUnit)}
  {@const typeColors: Record<string, string> = {
    'DEPARTMENT': 'bg-blue-100 text-blue-700 border-blue-200',
    'DIVISION': 'bg-purple-100 text-purple-700 border-purple-200',
    'TEAM': 'bg-orange-100 text-orange-700 border-orange-200',
    'FUNCTION': 'bg-slate-100 text-slate-700 border-slate-200',
    'BRANCH': 'bg-green-100 text-green-700 border-green-200',
    'PROJECT': 'bg-pink-100 text-pink-700 border-pink-200'
  }}
  {@const typeLabels: Record<string, string> = {
    'DEPARTMENT': 'Département',
    'DIVISION': 'Division',
    'TEAM': 'Équipe',
    'FUNCTION': 'Fonction',
    'BRANCH': 'Succursale',
    'PROJECT': 'Projet'
  }}
  <div
    class="mx-4 mb-2 p-3 bg-white rounded-lg border border-slate-200 shadow-fine hover:shadow-sm transition-shadow"
    style="margin-left: {1 + (orgUnit.level * 0.8)}rem"
  >
    <!-- Header avec nom, badge type et actions -->
    <div class="flex items-center justify-between mb-2">
      <div class="flex items-center gap-2 min-w-0">
        <span class="text-[0.82rem] px-2 py-0 rounded-full font-medium border {typeColors[orgUnit.type] || typeColors['DEPARTMENT']}">
          {typeLabels[orgUnit.type] || typeLabels['DEPARTMENT']}
        </span>
        <span class="text-[0.85rem] font-medium text-slate-900 truncate">{orgUnit.name}</span>
        {#if orgUnit.level === 0}
          <Badge variant="outline" class="text-[0.8rem] h-4 px-1.5 rounded-full bg-green-50 border-green-200 text-green-700">Racine</Badge>
        {/if}
      </div>

      <div class="flex items-center gap-0.5">
        <Button variant="ghost" size="icon" onclick={() => openEdit(orgUnit)} class="h-6 w-6 hover:bg-slate-100">
          <AppIcon name="edit" size={15} />
        </Button>
        <ConfirmAction
          isConfirming={deletingOrgUnitId === orgUnit.id}
          onRequest={() => requestDelete(orgUnit)}
          onConfirm={() => confirmDelete(orgUnit)}
          onCancel={() => deletingOrgUnitId = null}
          labels={{ action: '', confirm: 'Supprimer' }}
          icons={{ action: 'trash-2', confirm: 'check', cancel: 'x' }}
          variant="danger"
        />
      </div>
    </div>

    <!-- Ligne horizontale : Manager | Adjoint | Effectifs | Sous-unités -->
    <div class="flex items-center gap-3 mt-2 flex-wrap">
      {@render EmployeeChip(orgUnit.manager, "Manager")}
      <span class="text-slate-300">|</span>
      {@render EmployeeChip(orgUnit.affoint, "Adjoint")}
      <span class="text-slate-300">|</span>
      <span class="text-[0.8rem] text-slate-600 flex items-center gap-1">
        <AppIcon name="users" size={14} class="text-blue-500" />
        {orgUnit.employeeCount ?? 0}/{orgUnit.authorizedHeadcount}
      </span>
      <span class="text-slate-300">|</span>
      <span class="text-[0.8rem] text-slate-600 flex items-center gap-1">
        <AppIcon name="git-branch" size={14} class="text-purple-500" />
        {orgUnit.subUnitCount ?? 0}
      </span>
    </div>
  </div>
{/snippet}


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-170 flex flex-col h-full overflow-hidden p-0 bg-white">
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <div class="flex items-center justify-between">
        <Sheet.Title class="text-[1rem]">Structure organisationnelle</Sheet.Title>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar h-full relative flex flex-col">
      {#if isEditing}
        <div in:fade={{ duration: 200 }} class="flex flex-col flex-1">
          {@render OrgUnitFormView()}
        </div>
      {:else}
        <div in:fade={{ duration: 200 }} class="flex flex-col flex-1">
          {@render OrgUnitListView()}
        </div>
      {/if}
    </div>

    <Sheet.Footer class="px-6 py-2.5 border-t flex flex-row gap-3 sm:justify-start bg-slate-50/50">
      {@render OrgUnitFooterActions()}
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>




