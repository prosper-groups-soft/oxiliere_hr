<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { jobsStore } from "$lib/features/jobs/stores/jobs.svelte";
  import { employeeStore } from "$lib/features/employees/stores/employees.svelte";
  import type { Transition } from "../../../types/types";
  import { cn } from "@/utilities/common/css";
  import { fly } from "svelte/transition";
  import { cubicOut } from "svelte/easing";

  let { 
    transition,
    onEdit
  } = $props<{ 
    transition: Transition,
    onEdit: (trans: Transition) => void
  }>();

  function getEmployeeName(id: string | number) {
    return employeeStore.employees.find(e => String(e.id) === String(id))?.name || "Employé inconnu";
  }

  function getPositionTitle(id: string | undefined | null) {
    if (!id) return null;
    return jobsStore.positions.find(p => p.id === id)?.title || "Poste inconnu";
  }

  function getDeptName(id: string | undefined | null) {
    if (!id) return null;
    return jobsStore.getDepartmentById(id)?.name || null;
  }

  const typeConfig: Record<string, { label: string, icon: string, class: string }> = {
    PROMOTION: { label: 'Promotion', icon: 'trending-up', class: "bg-emerald-50 text-emerald-600 border-emerald-100" },
    TRANSFER:  { label: 'Mutation',  icon: 'refresh-cw',  class: "bg-blue-50 text-blue-600 border-blue-100" },
    HIRE:      { label: 'Embauche',  icon: 'plus-circle', class: "bg-purple-50 text-purple-600 border-purple-100" },
    OFFBOARD:  { label: 'Départ',    icon: 'user-minus',  class: "bg-red-50 text-red-600 border-red-100" }
  };

  const isHire = $derived(transition.type === 'HIRE');
  const isOffboard = $derived(transition.type === 'OFFBOARD');

  const employeeName = $derived(getEmployeeName(transition.employeeId));
  const employeeInitial = $derived(employeeName.charAt(0).toUpperCase());
  const cfg = $derived(typeConfig[transition.type] ?? typeConfig.TRANSFER);
</script>


{#snippet ItemActions()}
  <div onclick={(e) => e.stopPropagation()} role="none">
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        {#snippet child({ props })}
          <button 
            {...props}
            class="p-1.5 hover:bg-slate-100 rounded-md transition-colors text-slate-400 hover:text-slate-700 cursor-pointer outline-none"
          >
            <AppIcon name="more-vertical" size={19} />
          </button>
        {/snippet}
      </DropdownMenu.Trigger>

      <DropdownMenu.Content align="end" class="p-1 rounded-lg shadow-fine bg-white border-slate-100 min-w-40">
        <DropdownMenu.Item onclick={() => onEdit(transition)} class="cursor-pointer gap-2 py-2 text-[0.85rem]!">
          <AppIcon name="edit" size={16} class="text-slate-500" />
          Modifier
        </DropdownMenu.Item>
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  </div>
{/snippet}


<div 
  in:fly={{ y: 10, duration: 300, easing: cubicOut }}
  onclick={() => onEdit(transition)}
  role="button"
  tabindex="0"
  onkeydown={(e) => e.key === 'Enter' && onEdit(transition)}
  class="group/row relative flex items-center w-full h-20 shrink-0 px-0 bg-white border-b border-slate-100 hover:bg-hover transition-colors duration-150 cursor-pointer overflow-hidden"
>
  <!-- Employee Info -->
  <div class="flex items-center w-[28%] shrink-0 pl-4 min-w-0 gap-4">
    <div class="h-10 w-10 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-center text-primary font-bold text-base shrink-0 group-hover/row:bg-primary group-hover/row:text-white group-hover/row:border-primary transition-all">
      {employeeInitial}
    </div>
    <div class="flex flex-col min-w-0">
      <span class="font-semibold text-[0.88rem] text-slate-900 truncate leading-tight group-hover/row:text-primary transition-colors">
        {employeeName}
      </span>
      <Badge variant="outline" class={cn("mt-1 w-fit h-5 px-2 text-[0.6rem] font-bold uppercase tracking-widest border-none", cfg.class)}>
        <AppIcon name={cfg.icon} size={10} class="mr-1" />
        {cfg.label}
      </Badge>
    </div>
  </div>

  <!-- Movement Flow -->
  <div class="flex items-center flex-1 min-w-0 px-6 gap-3 overflow-hidden">
    <!-- From -->
    <div class="flex flex-col min-w-0 text-left">
      <span class="text-[0.62rem] font-bold text-slate-400 uppercase tracking-widest mb-0.5">
        {isHire ? 'Origine' : 'De'}
      </span>
      {#if isHire}
        <span class="text-[0.82rem] text-slate-400 italic truncate">Recrutement externe</span>
      {:else}
        <span class="text-[0.82rem] font-medium text-slate-600 truncate">{getPositionTitle(transition.fromPositionId) ?? 'N/A'}</span>
        {#if getDeptName(transition.fromDepartmentId)}
          <span class="text-[0.7rem] text-slate-400 truncate">{getDeptName(transition.fromDepartmentId)}</span>
        {/if}
      {/if}
    </div>

    <!-- Arrow -->
    <div class="flex shrink-0 items-center text-slate-300">
      <AppIcon name="arrow-right" size={16} />
    </div>

    <!-- To -->
    <div class="flex flex-col min-w-0 text-left">
      <span class="text-[0.62rem] font-bold text-slate-400 uppercase tracking-widest mb-0.5">
        {isOffboard ? 'Statut final' : 'Vers'}
      </span>
      {#if isOffboard}
        <span class="text-[0.82rem] text-red-400 truncate">Fin de contrat</span>
      {:else}
        <span class="text-[0.82rem] font-semibold text-primary truncate">{getPositionTitle(transition.toPositionId) ?? 'N/A'}</span>
        {#if getDeptName(transition.toDepartmentId)}
          <span class="text-[0.7rem] text-primary/60 truncate">{getDeptName(transition.toDepartmentId)}</span>
        {/if}
      {/if}
    </div>
  </div>

  <!-- Reason (Motif) -->
  {#if transition.reason}
    <div class="flex flex-col min-w-0 w-[18%] shrink-0 px-3 border-l border-slate-100">
      <span class="text-[0.62rem] font-bold text-slate-400 uppercase tracking-widest mb-0.5">Motif</span>
      <div class="flex items-start gap-1.5 min-w-0">
        <AppIcon name="quote" size={14} class="text-slate-400 shrink-0 mt-0.5" />
        <span class="text-[0.78rem] text-slate-600 truncate leading-tight">{transition.reason}</span>
      </div>
    </div>
  {/if}

  <!-- Date -->
  <div class="flex flex-col items-end shrink-0 w-[14%] pr-3 text-right">
    <span class="text-[0.62rem] font-bold text-slate-400 uppercase tracking-widest mb-0.5">Date</span>
    <span class="text-[0.8rem] font-medium text-slate-600">
      {new Date(transition.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })}
    </span>
  </div>

  <!-- Actions -->
  <div class="flex items-center pr-2">
    {@render ItemActions()}
  </div>
</div>

