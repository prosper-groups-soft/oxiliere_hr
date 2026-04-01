<script lang="ts">
  import { cn } from "@/utilities/common/css";
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import type { BankInstitution } from "../../types/types";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Badge } from "@/components/ui/badge";
  import { toast } from "svelte-sonner";
  import { bankingStore } from "../../stores/banking.svelte";

  let { institution, onEdit }: { institution: BankInstitution, onEdit?: (inst: BankInstitution) => void } = $props();

  function handleDelete(e: MouseEvent) {
    e.stopPropagation();
    if (confirm(`Êtes-vous sûr de vouloir supprimer ${institution.name} ?`)) {
      bankingStore.deleteInstitution(institution.id);
      toast.success("Institution supprimée");
    }
  }
</script>


<div 
  class="group bg-white rounded-xl border border-slate-200 p-5 transition-all duration-300 hover:shadow-sm shadow-fine hover:border-primary/20 flex items-center gap-4 cursor-pointer"
  onclick={() => onEdit?.(institution)}
  onkeydown={(e) => e.key === 'Enter' && onEdit?.(institution)}
  role="button"
  tabindex="0"
>
  <div class="h-14 w-14 rounded-xl bg-slate-50 flex items-center justify-center border border-slate-100 group-hover:bg-white transition-colors overflow-hidden shrink-0">
    {#if institution.logoUrl}(c)
      <img src={institution.logoUrl} alt={institution.name} class="h-full w-full object-contain p-2" />
    {:else}
      <AppIcon 
        name={institution.type === 'bank' ? 'bank' : 'app'} 
        size={26} 
        class="text-slate-400 group-hover:text-primary/70 transition-colors" 
      />
    {/if}
  </div>

  <div class="flex-1 min-w-0">
    <div class="flex items-center justify-between gap-2 mb-1">
      <h4 class="text-[0.92rem] font-medium text-slate-900 truncate leading-tight">
        {institution.name}
      </h4>
      <Badge 
        variant="secondary" 
        class={cn(
          "text-[0.6rem] font-bold px-1.5 py-0 rounded uppercase tracking-wider",
          institution.type === 'bank' ? "bg-blue-50 text-blue-600" : "bg-purple-50 text-purple-600"
        )}
      >
        {institution.type === 'bank' ? 'Banque' : 'M-Money'}
      </Badge>
    </div>
    
    <div class="flex items-center gap-3">
      <p class="text-[0.75rem] text-slate-500 flex items-center gap-1.5 font-medium">
        <AppIcon name="map-pin" size={17} class="text-slate-400" />
        {institution.country}
      </p>
      {#if institution.swiftCode}
        <div class="h-3 w-px bg-slate-200"></div>
        <p class="text-[0.8rem] text-slate-400">
          {institution.swiftCode}
        </p>
      {/if}
    </div>
  </div>

  <div class="flex items-center gap-1">
    {@render Menu()}
    <div class="h-8 w-8 rounded-lg flex items-center justify-center text-slate-300 hover:text-primary hover:bg-slate-50 transition-all">
      <AppIcon name="chevron-right" size={20} />
    </div>
  </div>
</div>


{#snippet Menu()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      {#snippet child({ props })}
        <button 
          {...props}
          class="h-8 w-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-primary hover:bg-slate-50 transition-all cursor-pointer"
          onclick={(e) => e.stopPropagation()}
        >
          <AppIcon name="more-horizontal" size={19} />
        </button>
      {/snippet}
    </DropdownMenu.Trigger>
    <DropdownMenu.Content align="end" class="w-40 p-1 bg-white shadow-fine border-slate-100 rounded-lg">
      <DropdownMenu.Item 
        onclick={(e) => {
          e.stopPropagation();
          onEdit?.(institution);
        }}
        class="flex items-center gap-2 px-2 py-1.5 text-[0.82rem] text-slate-600 cursor-pointer rounded-md hover:bg-slate-50 transition-colors"
      >
        <AppIcon name="edit" size={15} class="text-slate-400" />
        <span>Modifier</span>
      </DropdownMenu.Item>
      <DropdownMenu.Separator class="bg-slate-50 my-1" />
      <DropdownMenu.Item 
        onclick={handleDelete}
        class="flex items-center gap-2 px-2 py-1.5 text-[0.82rem] text-red-600 cursor-pointer rounded-md hover:bg-red-50/50! hover:text-red-600! transition-colors"
      >
        <AppIcon name="trash" size={15} class="text-red-600" />
        <span>Supprimer</span>
      </DropdownMenu.Item>
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}

