<script lang="ts">
  import { cn } from "@/hr/utilities/common/css";
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import type { BankInstitution } from "../../types/types";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Badge } from "@/components/ui/badge";
  import { notification } from "@/hr/stores/notification.svelte";
  import { findCountry } from '@/hr/modules/employees/constants/countries';
  import CountryFlag from '@/hr/components/shared/country/CountryFlag.svelte';
  import { getMediaUrl } from "@/hr/utilities/common/media";


  let {
    institution,
    onEdit,
    onDelete,
  }: {
    institution: BankInstitution;
    onEdit?: (inst: BankInstitution) => void;
    onDelete?: (id: string) => void;
  } = $props();

  let countryInfo = $derived(findCountry(institution.country));
  let logoUrl = $derived(getMediaUrl(institution.logoUrl));

  function handleDelete(e: MouseEvent) {
    e.stopPropagation();
    notification.confirm({
      title: 'Confirmer la suppression',
      message: `Êtes-vous sûr de vouloir supprimer <strong>${institution.name}</strong> ?<br><br>Cette action est irréversible.`,
      type: 'danger',
      yesText: 'Supprimer',
      noText: 'Annuler',
      onYes: async () => {
        onDelete?.(institution.id);
      },
    });
  }
</script>


<div 
  class={cn(
    "group relative bg-white rounded-xl border p-4 transition-all duration-300 hover:shadow-xs shadow-fine hover:border-primary/20 flex items-start gap-2 cursor-pointer overflow-hidden",
    institution.isActive ? "border-slate-200" : "border-slate-100 bg-slate-50/40"
  )}
  onclick={() => onEdit?.(institution)}
  onkeydown={(e) => e.key === 'Enter' && onEdit?.(institution)}
  role="button"
  tabindex="0"
>
  {#if !institution.isActive}
    <div class="absolute inset-x-0 top-0 h-0.5 bg-slate-200"></div>
  {/if}

  <div class={cn(
    "h-16 w-16 rounded-xl flex items-center justify-center border overflow-hidden shrink-0 transition-all",
    institution.isActive
      ? "bg-white border-slate-100 group-hover:border-primary/20"
      : "bg-white border-slate-100"
  )}>
    {#if logoUrl}
      <img src={logoUrl} alt={institution.name} class="h-full w-full object-cover" />
    {:else}
      <AppIcon 
        name={institution.type === 'bank' ? 'bank' : 'app'} 
        size={26} 
        class={cn(
          "transition-colors",
          institution.isActive ? "text-slate-400 group-hover:text-primary/70" : "text-slate-300"
        )} 
      />
    {/if}
  </div>

  <div class="flex-1 min-w-0">
    <div class="flex items-start justify-between mb-2">
      <div class="min-w-0">
        <h4 class="text-[0.92rem] font-semibold text-slate-900 group-hover:text-primary truncate leading-tight transition-colors">
          {institution.name}
        </h4>
        <p class="text-[0.8rem] text-slate-400 mt-0.5">
          {institution.shortName}
          {#if institution.swiftCode}
            · {institution.swiftCode}
          {/if}
        </p>
      </div>
      <div class="flex items-center gap-1.5 shrink-0 mt-0.5">
        <Badge 
          variant="secondary" 
          class={cn(
            "text-[0.77rem] font-medium px-1.5 py-0.5 rounded-full border-0",
            institution.isActive
              ? "bg-emerald-50 text-emerald-600"
              : "bg-slate-100 text-slate-400"
          )}
        >
          {institution.isActive ? "Actif" : "Inactif"}
        </Badge>
        <Badge 
          variant="secondary" 
          class={cn(
            "text-[0.77rem] font-medium px-1.5 py-0.5 rounded-full border-0",
            institution.type === 'bank' ? "bg-blue-50 text-blue-600" : "bg-purple-50 text-purple-600"
          )}
        >
          {institution.type === 'bank' ? 'Banque' : 'M-Money'}
        </Badge>
      </div>
    </div>

    <div class="flex items-center gap-3 flex-wrap">
      {#if countryInfo}
        <span class="inline-flex items-center gap-1.5 text-[0.85rem] text-slate-500">
          <CountryFlag code={countryInfo.code} />
          <span class="text-[0.85rem]">{countryInfo.label}</span>
        </span>
      {:else}
        <span class="inline-flex items-center gap-1.5 text-[0.85rem] text-slate-500">
          <AppIcon name="map-pin" size={16} class="text-slate-400" />
          <span class="text-[0.85rem]">{institution.country}</span>
        </span>
      {/if}

      {#if institution.swiftCode}
        <span class="h-3 w-px bg-slate-200 shrink-0"></span>
        <span class="inline-flex items-center gap-1 text-[0.8rem] text-slate-400">
          <AppIcon name="globe" size={16} class="text-slate-300" />
          SWIFT: {institution.swiftCode}
        </span>
      {/if}
    </div>
  </div>

  <div class="flex items-center gap-0.5">
    {@render Menu()}
    <div class={cn(
      "h-8 w-8 rounded-lg flex items-center justify-center transition-all",
      institution.isActive
        ? "text-slate-300 hover:text-primary hover:bg-slate-50"
        : "text-slate-200"
    )}>
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
        class="flex items-center gap-2 px-2 py-1.5 text-slate-600 cursor-pointer rounded-md hover:bg-slate-50 transition-colors"
      >
        <AppIcon name="edit" size={15} class="text-slate-400" />
        <span class="text-sm">Modifier</span>
      </DropdownMenu.Item>
      <DropdownMenu.Separator class="bg-slate-50 my-1" />
      <DropdownMenu.Item 
        onclick={handleDelete}
        class="flex items-center gap-2 px-2 py-1.5 text-red-600 cursor-pointer rounded-md hover:bg-red-50/50! hover:text-red-600! transition-colors"
      >
        <AppIcon name="trash" size={15} class="text-red-600" />
        <span class="text-sm">Supprimer</span>
      </DropdownMenu.Item>
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}

