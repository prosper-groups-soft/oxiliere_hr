<script lang="ts">
  import * as Dialog from "@/components/ui/dialog";
  import { Button } from "@/components/ui/button";
  import { Switch } from "@/components/ui/switch";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/hr/components/layout/elements/AnimateSpin.svelte";
  import { getFriendlyErrorMessage } from "@/hr/constants/errors";
  import { bankingEndpoint } from "../../api/banking.endpoints";


  interface SeedInstitution {
    code: string;
    name: string;
    is_mobile_money: boolean;
    exists: boolean;
  }

  let {
    open = $bindable(false),
    onSeed,
  }: {
    open: boolean;
    onSeed?: (codes?: string[]) => Promise<void>;
  } = $props();

  let selected = $state<Set<string>>(new Set());
  let isSeeding = $state(false);
  let institutions = $state<SeedInstitution[]>([]);
  let isLoading = $state(false);
  let error = $state<string | null>(null);

  // Fetch the list when dialog opens
  $effect(() => {
    if (!open) return;

    isLoading = true;
    error = null;

    bankingEndpoint.listSeedableBanks()
      .then((data) => {
        institutions = data;
        selected = new Set(data.filter((i: SeedInstitution) => !i.exists).map((i: SeedInstitution) => i.code));
      })
      .catch((err: unknown) => {
        error = getFriendlyErrorMessage(err);
      })
      .finally(() => {
        isLoading = false;
      });
  });

  const banks = $derived(institutions.filter((i: SeedInstitution) => !i.is_mobile_money));
  const mobileMoney = $derived(institutions.filter((i: SeedInstitution) => i.is_mobile_money));

  function toggle(code: string) {
    const next = new Set(selected);
    if (next.has(code)) next.delete(code);
    else next.add(code);
    selected = next;
  }

  function selectAll() {
    selected = new Set(institutions.map((i: SeedInstitution) => i.code));
  }

  function deselectAll() {
    selected = new Set<string>();
  }

  async function handleSubmit() {
    if (selected.size === 0) return;
    isSeeding = true;
    try {
      const codes = selected.size === institutions.length ? undefined : [...selected];
      await onSeed?.(codes);
      open = false;
    } catch {
      // Toast already handled by mutation
    } finally {
      isSeeding = false;
    }
  }
</script>


<Dialog.Root bind:open>
  <Dialog.Content class="sm:max-w-xl p-0 overflow-hidden flex flex-col bg-white max-h-[90vh]">
    <Dialog.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <Dialog.Title class="text-[0.95rem] font-bold text-slate-900">
        Ajouter les institutions financières
      </Dialog.Title>
      <Dialog.Description class="text-[0.82rem] text-slate-500 mt-0.5">
        Sélectionnez les institutions à ajouter depuis la liste des banques agréées par la BCC
      </Dialog.Description>
    </Dialog.Header>

    {#if isLoading}
      <div class="flex items-center justify-center py-16">
        <AnimateSpin text="Chargement des institutions" />
      </div>
    {:else if error}
      <div class="flex flex-col items-center justify-center py-12 text-rose-500 text-[0.85rem] gap-2">
        <AppIcon name="alert-circle" size={18} class="mr-2" />
        <span>{error}</span>
      </div>
    {:else}
      <!-- Select / Deselect all toolbar -->
      <div class="flex items-center justify-between px-6 py-2 border-b border-slate-50 bg-white/60">
        <div class="flex items-center gap-3">
          <button
            onclick={selectAll}
            class="text-[0.78rem] font-medium text-primary hover:text-primary/80 transition-colors cursor-pointer"
          >
            Tout sélectionner
          </button>
          <span class="text-slate-200">|</span>
          <button
            onclick={deselectAll}
            class="text-[0.78rem] font-medium text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
          >
            Tout désélectionner
          </button>
        </div>
        <span class="text-[0.78rem] text-slate-400 tabular-nums">
          {selected.size}/{institutions.length}
        </span>
      </div>

      <!-- Scrollable list -->
      <div class="flex-1 overflow-y-auto p-4 space-y-3 scroll-smooth custom-scrollbar">
        <!-- Banks section -->
        <div>
          <div class="flex items-center gap-2 px-2 py-1.5 mb-1">
            <div class="p-1 rounded-md bg-blue-50 text-blue-500">
              <AppIcon name="bank" size={14} />
            </div>
            <span class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider">Banques</span>
            <span class="text-[0.7rem] text-slate-400">({banks.length})</span>
          </div>
          <div class="space-y-0.5">
            {#each banks as inst}
              {@const isExisting = inst.exists}
              <label
                class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-50 transition-colors cursor-pointer group {isExisting ? 'opacity-50 pointer-events-none' : ''}"
              >
                <Switch
                  checked={selected.has(inst.code)}
                  onCheckedChange={() => toggle(inst.code)}
                  disabled={isExisting}
                  class="cursor-pointer"
                />
                <div class="flex items-center gap-2 min-w-0 flex-1">
                  <span class="text-[0.7rem] font-mono font-medium text-slate-400 uppercase shrink-0 w-10">
                    {inst.code}
                  </span>
                  <span class="text-[0.85rem] text-slate-700 truncate">{inst.name}</span>
                  {#if isExisting}
                    <span class="ml-auto text-[0.7rem] font-medium text-emerald-500 shrink-0">Déjà présente</span>
                  {/if}
                </div>
              </label>
            {/each}
          </div>
        </div>

        <!-- Separator -->
        <div class="border-t border-slate-100 my-2"></div>

        <!-- Mobile Money section -->
        <div>
          <div class="flex items-center gap-2 px-2 py-1.5 mb-1">
            <div class="p-1 rounded-md bg-emerald-50 text-emerald-500">
              <AppIcon name="mobile" size={14} />
            </div>
            <span class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider">Mobile Money</span>
            <span class="text-[0.7rem] text-slate-400">({mobileMoney.length})</span>
          </div>
          <div class="space-y-0.5">
            {#each mobileMoney as inst}
              {@const isExisting = inst.exists}
              <label
                class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-50 transition-colors cursor-pointer group {isExisting ? 'opacity-50 pointer-events-none' : ''}"
              >
                <Switch
                  checked={selected.has(inst.code)}
                  onCheckedChange={() => toggle(inst.code)}
                  disabled={isExisting}
                  class="cursor-pointer"
                />
                <div class="flex items-center gap-2 min-w-0 flex-1">
                  <span class="text-[0.7rem] font-mono font-medium text-slate-400 uppercase shrink-0 w-10">
                    {inst.code}
                  </span>
                  <span class="text-[0.85rem] text-slate-700 truncate">{inst.name}</span>
                  {#if isExisting}
                    <span class="ml-auto text-[0.7rem] font-medium text-emerald-500 shrink-0">Déjà présente</span>
                  {/if}
                </div>
              </label>
            {/each}
          </div>
        </div>
      </div>

      <Dialog.Footer class="px-6 py-2.5 border-t flex flex-row gap-3 sm:justify-start bg-slate-50/50">
        <Dialog.Close>
          <Button variant="outline" class="h-9 rounded-md text-sm font-medium shadow-fine cursor-pointer">
            <AppIcon name="x" size={17} class="text-slate-300" />
            Annuler
          </Button>
        </Dialog.Close>
        <Button
          onclick={handleSubmit}
          disabled={selected.size === 0 || isSeeding}
          class="flex-1 h-9 rounded-md bg-primary text-white text-sm font-medium shadow-sm hover:shadow-md transition-all cursor-pointer gap-2"
        >
          {#if isSeeding}
            <AnimateSpin class="border-white size-3" text="" />
          {:else}
            <AppIcon name="plus" size={17} />
          {/if}
          Ajouter ({selected.size})
        </Button>
      </Dialog.Footer>
    {/if}
  </Dialog.Content>
</Dialog.Root>



