<script lang="ts">
  import { cn } from "@/utilities/common/css";
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import type { BankAccount } from "../../types/types";
  import { 
    VERIFICATION_STATUS_COLORS, 
    VERIFICATION_STATUS_LABELS 
  } from "../../types/types";
  import { bankingStore } from "../../stores/banking.svelte";
  import CurrencyChip from "../shared/CurrencyChip.svelte";
  import IbanVisualizer from "../shared/IbanVisualizer.svelte";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { toast } from "svelte-sonner";
  import Badge from "@/components/ui/badge/badge.svelte";
  import { getInitials } from "@/utilities/common/string";

  let { account, onEdit }: { account: BankAccount, onEdit?: (acc: BankAccount) => void } = $props();
  
  const institution = $derived(bankingStore.getInstitutionById(account.institutionId));
  const statusColor = $derived(VERIFICATION_STATUS_COLORS[account.status]);
  const palette = $derived(getAvatarPalette(account.employeeName));

  function handleDelete() {
    if (confirm(`Êtes-vous sûr de vouloir supprimer le compte de ${account.employeeName} ?`)) {
      bankingStore.deleteAccount(account.id);
      toast.success("Compte supprimé avec succès");
    }
  }
</script>


<div class={cn(
  "group relative bg-white rounded-xl border border-slate-200 p-5 transition-all duration-300 hover:shadow-md hover:border-primary/20",
  account.isPrimary && "ring-1 ring-primary/30 border-primary/30 bg-primary/1"
)}>
  <!-- Header: Bank Info & Status -->
  <div class="flex items-start justify-between mb-6">
    <div class="flex items-center gap-3">
      <div class="h-10 w-10 rounded-lg bg-slate-50 flex items-center justify-center border border-slate-100 group-hover:bg-white transition-colors">
        <AppIcon 
          name={institution?.type === 'bank' ? 'bank' : 'app'} 
          size={22} 
          class="text-slate-500" 
        />
      </div>
      <div>
        <h4 class="text-[0.88rem] font-semibold text-slate-900 leading-tight">
          {institution?.name || account.institutionId}
        </h4>
        <p class="text-[0.75rem] text-slate-400 font-medium">
          {account.accountName}
        </p>
      </div>
    </div>

    <div class="flex flex-col items-end gap-2">
      <Badge 
        variant="secondary" 
        class={cn("text-[0.65rem] font-bold px-2 py-0.5", statusColor.bg, statusColor.text)}
      >
        <div class={cn("h-1.5 w-1.5 rounded-full mr-1.5", statusColor.dot)}></div>
        {VERIFICATION_STATUS_LABELS[account.status]}
      </Badge>
      {#if account.isPrimary}
        <Badge class="bg-primary/10 text-primary border-none text-[0.6rem] font-bold px-1.5 py-0 uppercase tracking-tighter">
          Primaire
        </Badge>
      {/if}
    </div>
  </div>

  <!-- Account Details -->
  <div class="space-y-4">
    <div class="flex items-end justify-between">
      <IbanVisualizer label="Numéro de Compte" value={account.accountNumber} />
      <CurrencyChip currency={account.currency} class="mb-1" />
    </div>

    {#if account.iban}
      <IbanVisualizer label="IBAN" value={account.iban} />
    {/if}
  </div>

  <!-- Employee Footer -->
  <div class="mt-6 pt-2 border-t border-slate-50 flex items-center justify-between">
    <div class="flex items-center gap-2 min-w-0">
      <div 
        class={cn("h-9 w-9 rounded-full flex items-center justify-center border border-slate-200/50 shrink-0", palette.bg, palette.text)}
      >
        <span class="text-[0.66rem] font-bold uppercase">
          {getInitials(account.employeeName)}
        </span>
      </div>
      <span class="text-[0.74rem] font-semibold text-slate-600 truncate">
        {account.employeeName}
      </span>
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
  </div>
</div>

