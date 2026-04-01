<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Button } from "@/components/ui/button";
  import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger
  } from "@/components/ui/select";
  import { Badge } from "@/components/ui/badge";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import { jobsStore } from "../../../stores/jobs.svelte";
  import { employeeStore } from "@/features/employees/stores/employees.svelte";
  import { notification } from "@/stores/notification.svelte";
  import type { Department, NodeType } from "../../../types/types";

  let { 
    open = $bindable(false),
    preselectedParentId = $bindable(null)
  } = $props<{ 
    open: boolean, 
    preselectedParentId?: string | null 
  }>();

  // --- Form state ---
  let isEditing = $state(false);
  let editingDept = $state<Department | null>(null);
  let formName = $state('');
  let formType = $state<NodeType>('DEPARTMENT');
  let formParentId = $state<string | null>(null);
  let formManagerId = $state<string | null>(null);
  let formAffointId = $state<string | null>(null);
  let formAuthorizedHeadcount = $state(0);

  // Sync preselectedParentId when sheet opens
  $effect(() => {
    if (open && preselectedParentId) {
      editingDept = null;
      formName = '';
      formParentId = preselectedParentId;
      formManagerId = null;
      formAffointId = null;
      formAuthorizedHeadcount = 0;
      isEditing = true;
      preselectedParentId = null;
    }
  });

  // --- Handlers ---
  function openAdd() {
    editingDept = null;
    formName = '';
    formType = 'DEPARTMENT';
    formParentId = null;
    formManagerId = null;
    formAffointId = null;
    formAuthorizedHeadcount = 0;
    isEditing = true;
  }

  function openEdit(dept: Department) {
    editingDept = dept;
    formName = dept.name;
    formType = dept.type;
    formParentId = dept.parentId;
    formManagerId = dept.managerId;
    formAffointId = dept.affointId ?? null;
    formAuthorizedHeadcount = dept.authorizedHeadcount;
    isEditing = true;
  }

  function handleSave() {
    const selectedManager = formManagerId
      ? employeeStore.getById(formManagerId)
      : undefined;
    const selectedAdjoint = formAffointId
      ? employeeStore.getById(formAffointId)
      : undefined;

    const data = {
      name: formName.trim(),
      type: formType,
      parentId: formParentId,
      managerId: formManagerId,
      managerName: selectedManager?.name ?? '',
      affointId: formAffointId,
      affointName: selectedAdjoint?.name ?? '',
      authorizedHeadcount: formAuthorizedHeadcount,
    };

    if (editingDept) {
      jobsStore.updateDepartment(editingDept.id, data);
    } else {
      jobsStore.addDepartment(data);
    }
    isEditing = false;
  }

  function handleDelete(dept: Department) {
    notification.confirm({
      title: 'Supprimer le département',
      message: `Voulez-vous vraiment supprimer "${dept.name}" ?`,
      type: 'danger',
      onYes: () => jobsStore.deleteDepartment(dept.id),
    });
  }

  const otherDepts = $derived(
    editingDept 
      ? jobsStore.departments.filter(d => d.id !== editingDept!.id)
      : jobsStore.departments
  );

  const parentLabel = $derived(
    formParentId 
      ? otherDepts.find(d => d.id === formParentId)?.name ?? '— Aucun (Racine)'
      : '— Aucun (Racine)'
  );
  
  // Convert null to empty string for Select compatibility
  const selectParentId = $derived(formParentId ?? '');
  function handleParentChange(value: string) {
    formParentId = value || null;
  }

  const selectManagerId = $derived(formManagerId ?? '');
  const managerLabel = $derived(
    formManagerId
      ? employeeStore.getById(formManagerId)?.name ?? '— Aucun'
      : '— Aucun'
  );

  function handleManagerChange(value: string) {
    formManagerId = value || null;
  }

  const selectAffointId = $derived(formAffointId ?? '');
  const affointLabel = $derived(
    formAffointId
      ? employeeStore.getById(formAffointId)?.name ?? '— Aucun'
      : '— Aucun'
  );

  function handleAffointChange(value: string) {
    formAffointId = value || null;
  }

  // --- Node Type Options ---
  const nodeTypeItems = [
    { value: 'DEPARTMENT', label: 'Département', icon: 'business' },
    { value: 'TEAM',       label: 'Équipe',      icon: 'team'     },
    { value: 'FUNCTION',   label: 'Fonction',    icon: 'settings' }
  ] satisfies { value: string; label: string; icon: string }[];

  const selectedNodeType = $derived(nodeTypeItems.find(i => i.value === formType));

  // --- Hierarchical Sorting ---
  interface FlatDept extends Department {
    level: number;
    childCount: number;
  }

  const hierarchicalDepts = $derived.by(() => {
    const result: FlatDept[] = [];
    
    function traverse(deptId: string | null, level: number) {
      const children = jobsStore.departments.filter(d => d.parentId === deptId);
      children.forEach(child => {
        const descendants = jobsStore.departments.filter(d => d.parentId === child.id);
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


{#snippet formNumberInput(id: string, label: string, value: number, onChange: (v: number) => void)}
  <div class="space-y-2">
    <Label for={id}>{label}</Label>
    <Input {id} type="number" {value} onchange={(e) => onChange(Number(e.currentTarget.value))} class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
  </div>
{/snippet}


{#snippet formInput(id: string, label: string, value: string, placeholder: string, required: boolean = false, type: string = 'text', onChange: (v: string) => void)}
  <div class="space-y-2">
    <Label for={id}>{label} {@html required ? '<span class="text-red-500">*</span>' : ''}</Label>
    <Input 
      {id} 
      {type}
      {value} 
      onchange={(e) => onChange(e.currentTarget.value)}
      {placeholder}
      class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine"
      {required}
    />
  </div>
{/snippet}


{#snippet formSelect(label: string, triggerLabel: string, items: { value: string, label: string }[], selectedValue: string, onChange: (v: string) => void)}
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

{#snippet formSelectWithIcons(label: string, triggerIcon: string, triggerLabel: string, items: { value: string, label: string, icon: string }[], selectedValue: string, onChange: (v: string) => void)}
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
            <span class="flex items-center gap-2 text-[0.82rem]">
              <AppIcon name={item.icon} size={18} class="text-slate-500 shrink-0" />
              {item.label}
            </span>
          </SelectItem>
        {/each}
      </SelectContent>
    </Select>
  </div>
{/snippet}


{#snippet formHeader(title: string)}
  <header class="flex flex-col gap-9 mb-6">
     <Button variant="default" onclick={() => isEditing = false} class="h-7.5 text-[0.84rem] rounded-lg transition-colors self-start">
       <AppIcon name="arrow-left" size={18} />
       Retour
     </Button>
     <h3 class="font-bold text-slate-800">{title}</h3>
  </header>
{/snippet}


{#snippet deptListView()}
  <div class="px-6 mb-3">
    <Button onclick={openAdd} size="sm" class="bg-primary text-white text-[0.84rem] h-7.5">
      <AppIcon name="plus" size={18} />Nouveau
    </Button>
  </div>
  <div class="divide-y divide-slate-100 border-b border-slate-100 h-full">
    {#each hierarchicalDepts as dept}
      {@render deptRow(dept)}
    {:else}
      <div class="h-full flex items-center justify-center">
        <Empty 
          title="Aucun département" 
          description="Commencez par créer votre premier département pour structurer votre organisation." 
          icon="network"
          iconClass="text-primary"
        />
      </div>
    {/each}
  </div>
{/snippet}


{#snippet deptFormView()}
  <div class="p-6 pt-0 animate-in fade-in slide-in-from-right-4 duration-300 h-full">
    {@render formHeader(editingDept ? 'Modifier le département' : 'Nouveau département')}

    <form id="dept-form-sheet" onsubmit={(e) => { e.preventDefault(); handleSave(); }} class="space-y-5">
      {@render formInput('dept-name', 'Nom', formName, 'ex: Ressources Humaines', true, 'text', (v) => formName = v)}
      
      {@render formSelectWithIcons(
        'Type de nœud',
        selectedNodeType?.icon ?? 'business',
        selectedNodeType?.label ?? 'Département',
        nodeTypeItems,
        formType,
        (v) => formType = v as NodeType
      )}
      
      {@render formSelect(
        'Département parent', 
        parentLabel, 
        [{ value: '', label: '— Aucun (Racine)' }, ...otherDepts.map(d => ({ value: d.id, label: d.name }))],
        selectParentId,
        handleParentChange
      )}
      
      {@render formSelect(
        'Responsable',
        managerLabel,
        [{ value: '', label: '— Aucun' }, ...employeeStore.employees.map(e => ({ value: String(e.id), label: e.name }))],
        selectManagerId,
        handleManagerChange
      )}
      
      {@render formSelect(
        'Adjoint',
        affointLabel,
        [{ value: '', label: '— Aucun' }, ...employeeStore.employees.map(e => ({ value: String(e.id), label: e.name }))],
        selectAffointId,
        handleAffointChange
      )}
      
      {@render formNumberInput('dept-authorized-headcount', 'Effectif autorisé', formAuthorizedHeadcount, (v) => formAuthorizedHeadcount = v)}
    </form>
  </div>
{/snippet}


{#snippet deptFooterActions()}
  {#if isEditing}
    <Button type="submit" form="dept-form-sheet" class="flex-1 bg-primary text-white shadow-fine transition-transform h-9">
      <AppIcon name="check" size={16} />
      Enregistrer
    </Button>
    <Button variant="outline" onclick={() => isEditing = false} class="flex-1 h-9 shadow-fine">
      Annuler
    </Button>
  {:else}
    <Sheet.Close class="w-full">
      <Button variant="outline" class="w-full h-9 text-slate-900 border-slate-200 shadow-fine">
        Fermer
      </Button>
    </Sheet.Close>
  {/if}
{/snippet}


{#snippet metadataItem(label: string, icon: string, value: string | number, align: 'left' | 'right' = 'left')}
  <div class="space-y-0.5 {align === 'right' ? 'text-right' : ''}">
    <span class="block text-[0.74rem] text-slate-600 uppercase tracking-wider">
      {label}
    </span>
    <div class="flex items-center gap-1.5 {align === 'right' ? 'justify-end' : ''}">
      {#if align === 'left'}
        <AppIcon name={icon} size={18} class="text-slate-500" />
      {/if}
      <span class="text-[0.76rem] font-medium text-slate-600 truncate">
        {value}
      </span>
      {#if align === 'right'}
        <AppIcon name={icon} size={18} class="text-slate-500" />
      {/if}
    </div>
  </div>
{/snippet}


{#snippet deptRow(dept: FlatDept)}
  {@const hoverColor = dept.level === 0 ? 'hover:bg-slate-50' : dept.level === 1 ? 'hover:bg-slate-100' : 'hover:bg-slate-200'}
  <div 
    class="group relative flex flex-col p-4 pt-0 {hoverColor} transition-colors"
    style="padding-left: {1.5 + (dept.level * 1.5)}rem"
  >
    <!-- Hierarchy Indicator Line -->
    {#if dept.level > 0}
      <div class="absolute left-0 top-0 bottom-0 w-px bg-slate-300" style="left: {dept.level * 1.7}rem"></div>
      <div class="absolute h-px bg-slate-300 top-1/2" style="left: {dept.level * 1.7}rem; width: 1rem"></div>
    {/if}

    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2 min-w-0">
        <span class="text-[0.855rem] font-medium text-slate-900 truncate">{dept.name}</span>
        {#if dept.level === 0}
          <Badge variant="outline" class="text-[0.65rem] h-4 px-1.5 bg-green-50 border-green-200 text-green-700 font-medium uppercase tracking-tighter">Racine</Badge>
        {/if}
      </div>

      <div class="flex items-center gap-1">
        <Button variant="ghost" onclick={() => openEdit(dept)} class="p-1! h-7.5 w-7.5 hover:bg-slate-200 hover:shadow-fine rounded border-none text-slate-600 hover:text-slate-700 transition-all">
          <AppIcon name="edit" size={16} />
        </Button>
        <Button variant="ghost" onclick={() => handleDelete(dept)} class="p-1! h-7.5 w-7.5 hover:bg-red-100 hover:shadow-fine rounded border-none text-slate-700 hover:text-red-800 transition-all">
          <AppIcon name="trash" size={16} class="text-red-400" />
        </Button>
      </div>
    </div>

    <div class="grid grid-cols-[1.8fr_1fr_1fr] gap-4">
      {@render metadataItem("Manager", "circle-user", dept.managerName || 'Non assigné')}
      {@render metadataItem("Autorisé", "users", dept.authorizedHeadcount)}
      {@render metadataItem("Divisions", "git-branch", dept.childCount, 'right')}
    </div>
  </div>
{/snippet}


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl flex flex-col h-full overflow-hidden p-0 bg-white">
    <Sheet.Header class="px-6 py-4 border-b bg-slate-50/50">
      <div class="flex items-center justify-between">
        <Sheet.Title class="text-[1rem]">Structure organisationnelle</Sheet.Title>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar h-full">
      {#if isEditing}
        {@render deptFormView()}
      {:else}
        {@render deptListView()}
      {/if}
    </div>

    <Sheet.Footer class="px-6 py-4 border-t flex flex-row gap-3 sm:justify-start bg-slate-50/50">
      {@render deptFooterActions()}
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>


<style>
  .custom-scrollbar::-webkit-scrollbar {
    width: 4px;
  }
  
  .custom-scrollbar::-webkit-scrollbar-thumb { 
    background: #e2e8f0; 
    border-radius: 10px; 
  }
</style>

