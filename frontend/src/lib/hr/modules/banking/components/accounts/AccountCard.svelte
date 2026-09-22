<script lang="ts">
  import { cn } from "@/hr/utilities/common/css";
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import type { BankAccount } from "../../types/types";
  import { 
    VERIFICATION_STATUS_COLORS, 
    VERIFICATION_STATUS_LABELS, 
    ACCOUNT_TYPE_LABELS
  } from "../../constants";
  import { bankingStore } from "../../stores/banking.svelte";
  import CurrencyChip from "../shared/CurrencyChip.svelte";
  import IbanVisualizer from "../shared/IbanVisualizer.svelte";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { getAvatarPalette } from "@/hr/utilities/common/func";
  import Badge from "@/components/ui/badge/badge.svelte";
  import { getInitials } from "@/hr/utilities/common/string";
  import { useDeleteAccountMutation } from "../../queries/bankingQueries";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getMediaUrl } from "@/hr/utilities/common/media";
  import { notification } from "@/hr/stores/notification.svelte";
  import TooltipWrapper from "@/hr/components/shared/containers/TooltipWrapper.svelte";


  let { account, onEdit }: { account: BankAccount, onEdit?: (acc: BankAccount) => void } = $props();
  
  const deleteMutation = useDeleteAccountMutation();
  const institution = $derived(bankingStore.getInstitutionById(account.institutionId));
  const statusColor = $derived(VERIFICATION_STATUS_COLORS[account.status]);
  const palette = $derived(getAvatarPalette(account.employeeName));
  const fullName = $derived(account.employeeName);
  const profilePhoto = $derived(getMediaUrl(account.employeePhoto));

  function handleDelete() {
    notification.confirm({
      title: 'Confirmer la suppression',
      message: `Êtes-vous sûr de vouloir supprimer le compte de ${account.employeeName} ?`,
      type: 'danger',
      yesText: 'Supprimer',
      onYes: () => {
        $deleteMutation.mutate(account.id);
      }
    });
  }
</script>


<div 
  id={`account-${account.id}`}
  class={cn(
    "group relative bg-white! rounded-xl border border-slate-50 p-5 transition-all duration-300 hover:shadow-xs hover:border-primary/20",
    account.isPrimary && "ring-1 ring-primary/30 border-primary/30 bg-primary/1"
  )}>
  <!-- Header: Bank Info & Status -->
  <div class="flex items-start justify-between mb-5">
    <div class="flex items-center gap-3">
      <div class="h-10 w-10 rounded-lg bg-slate-50 flex items-center justify-center border border-slate-100 group-hover:bg-white transition-colors">
        <AppIcon 
          name={institution?.type === 'bank' ? 'bank' : 'app'} 
          size={24} 
          class="text-slate-500" 
        />
      </div>
      <div>
        <h4 class="text-[0.88rem] font-medium text-slate-900 leading-tight">
          {institution?.name || account.institutionId}
        </h4>
        <p class="text-[0.82rem] text-slate-500 font-normal">
          {account.accountName}
        </p>
      </div>
    </div>

    <div class="flex items-start gap-2">
      <div class="flex flex-col items-end gap-1.5">
        <Badge 
          variant="secondary" 
          class={cn("text-[0.7rem] font-bold px-2 py-0.5", statusColor.bg, statusColor.text)}
        >
          <div class={cn("h-1.5 w-1.5 rounded-full mr-1.5", statusColor.dot)}></div>
          {VERIFICATION_STATUS_LABELS[account.status]}
        </Badge>
        {#if account.isPrimary}
          <Badge class="bg-primary/10 text-primary border-none text-[0.65rem] font-bold px-1.5 py-0 uppercase tracking-tighter">
            Primaire
          </Badge>
        {/if}
      </div>

      <!-- Actions -->
      <DropdownMenu.Root>
        <DropdownMenu.Trigger>
          {#snippet child({ props })}
            <button 
              {...props}
              class="h-7 w-7 rounded-lg text-slate-500 hover:text-primary hover:bg-slate-50 transition-colors flex items-center justify-center cursor-pointer"
            >
              <AppIcon name="more-horizontal" size={17} />
            </button>
          {/snippet}
        </DropdownMenu.Trigger>
        <DropdownMenu.Content align="end" class="w-40 p-1 bg-white shadow-fine border-slate-100 rounded-lg">
          <DropdownMenu.Item 
            onclick={() => onEdit?.(account)}
            class="flex items-center gap-2 px-2 py-1.5 text-[0.82rem] text-slate-600 cursor-pointer rounded-md hover:bg-slate-50 transition-colors"
          >
            <AppIcon name="edit" size={17} class="text-slate-400" />
            <span>Modifier</span>
          </DropdownMenu.Item>
          <DropdownMenu.Separator class="bg-slate-50 my-1" />
          <DropdownMenu.Item 
            onclick={handleDelete}
            class="flex items-center gap-2 px-2 py-1.5 text-[0.82rem] text-red-600 cursor-pointer rounded-md hover:bg-red-50/50! hover:text-red-600! transition-colors"
          >
            <AppIcon name="trash" size={17} class="text-red-600" />
            <span>Supprimer</span>
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Root>
    </div>
  </div>

  <!-- Account Details -->
  <div class="space-y-3">
    <!-- Row 1: N° Compte + Devises -->
    <div class="flex items-end justify-between">
      <IbanVisualizer label="Numéro de Compte" value={account.accountNumber} />
      <div class="flex items-center gap-1 mb-1">
        {#each account.currencies as cur}
          <CurrencyChip currency={cur} class={cur !== account.defaultCurrency ? "opacity-60" : ""} />
        {/each}
      </div>
    </div>
    
    <!-- Row 2: IBAN -->
    {#if account.iban}
      <IbanVisualizer label="IBAN" value={account.iban} />
    {/if}

    <!-- Row 3: Type + Devise par défaut -->
    <div class="flex items-center gap-4">
      <div class="flex items-center gap-1.5">
        <AppIcon name="layers" size={15} class="text-slate-400" />
        <span class="text-[0.82rem] text-slate-600">Type:</span>
        <span class="text-[0.82rem] font-medium text-slate-700">{ACCOUNT_TYPE_LABELS[account.type]}</span>
      </div>
      <div class="flex items-center gap-1.5">
        <AppIcon name="dollar-sign" size={15} class="text-slate-400" />
        <span class="text-[0.82rem] text-slate-600">Défaut:</span>
        <span class="text-[0.82rem] font-medium text-slate-700">{account.defaultCurrency}</span>
      </div>
    </div>

    <!-- Row 4: Branch Code + Swift -->
    <div class="flex items-center gap-4">
      {#if account.branchCode}
        <div class="flex items-center gap-1.5">
          <AppIcon name="building" size={15} class="text-slate-400" />
          <span class="text-[0.82rem] text-slate-600">Guichet:</span>
          <span class="text-[0.82rem] font-medium text-slate-700">{account.branchCode}</span>
        </div>
      {/if}
      {#if account.swift}
        <div class="flex items-center gap-1.5">
          <AppIcon name="globe" size={15} class="text-slate-400" />
          <span class="text-[0.82rem] text-slate-600">SWIFT:</span>
          <span class="text-[0.82rem] font-medium text-slate-700 uppercase">{account.swift}</span>
        </div>
      {/if}
    </div>

    <!-- Row 5: Dates -->
    <div class="flex items-center gap-4 pt-1">
      <span class="text-[0.8rem] text-slate-500">Créé le {new Date(account.createdAt).toLocaleDateString('fr-FR')}</span>
      {#if account.verifiedAt}
        <span class="text-[0.8rem] text-slate-500">• Vérifié le {new Date(account.verifiedAt).toLocaleDateString('fr-FR')}</span>
      {/if}
    </div>

    {#if account.notes}
      <div class="relative flex items-start gap-1.5 pt-1">
        <TooltipWrapper content={account.notes} side="bottom" asChild={true}>
          {#snippet children({ props })}
            <div {...props} class="flex items-start gap-1.5 cursor-help">
              <AppIcon name="file-text" size={14} class="text-slate-400 mt-0.5 shrink-0" />
              <span class="text-[0.8rem] text-slate-500 leading-snug line-clamp-2">
                {account.notes}
              </span>
            </div>
          {/snippet}
        </TooltipWrapper>
      </div>
    {/if}
  </div>

  <!-- Employee Footer -->
  <div class="mt-5 pt-3 border-t border-slate-100">
    <div class="flex items-center gap-3">
      <Avatar class="h-11 w-11 rounded-full border border-slate-200/50 shrink-0">
        <AvatarImage src={profilePhoto} alt={fullName} class="object-cover" />
        <AvatarFallback class={cn("font-bold text-[0.82rem]", palette.bg, palette.text)}>
          {getInitials(fullName)}
        </AvatarFallback>
      </Avatar>
      <div class="flex flex-col min-w-0">
        <span class="text-[0.82rem] font-medium text-slate-800 truncate leading-tight">
          {fullName}
        </span>
        <span class="text-[0.82rem] text-slate-500 truncate">
          Titulaire du compte
        </span>
      </div>
    </div>
  </div>
</div>

