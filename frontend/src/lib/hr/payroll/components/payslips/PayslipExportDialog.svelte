<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Button } from '@/components/ui/button';
  import { Input } from '@/components/ui/input';
  import { Checkbox } from '@/components/ui/checkbox';
  import { Switch } from '@/components/ui/switch';
  import * as Dialog from '@/components/ui/dialog';
  import { payslipsStore } from '@/hr/payroll/stores/payslips/payslipsStore.svelte';
  import { payrollRunStore } from '@/hr/payroll/stores/runs/payrollRunStore.svelte';
  import { get_api_base_origin } from '@/utilities/http/urls';
  import { fetchPayslipsGlobal } from '@/hr/payroll/queries/payroll';

  let { open = $bindable(false) } = $props<{ open: boolean }>();

  let localSearch = $state('');
  let rows = $state<any[]>([]);
  let loading = $state(false);
  let selected = $state<Set<string>>(new Set());

  const runLabel = $derived.by(() => {
    if (!payslipsStore.runId) return 'Toutes les exécutions';
    const r = payrollRunStore.runList.find((x) => x.id === payslipsStore.runId);
    return r?.periodLabel ?? payslipsStore.runId.slice(0, 8);
  });

  const filtered = $derived.by(() => {
    const q = localSearch.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) => {
      const name = `${r.employee?.fullName ?? r.employee_name ?? ''} ${r.employee?.matricule ?? ''} ${r.employee_name ?? ''}`.toLowerCase();
      return name.includes(q);
    });
  });

  const allChecked = $derived(filtered.length > 0 && filtered.every((r) => selected.has(String(r.id))));
  const count = $derived(selected.size);

  async function load() {
    loading = true;
    try {
      const res = await fetchPayslipsGlobal({
        page: 1,
        pageSize: 200,
        runId: payslipsStore.runId || undefined,
        ordering: payslipsStore.ordering || undefined
      });
      rows = (res?.results as any[]) ?? [];
      // pré-cocher tout
      selected = new Set(rows.map((r) => String(r.id)));
    } catch {
      rows = [];
    } finally {
      loading = false;
    }
  }

  $effect(() => {
    if (open) {
      localSearch = '';
      load();
    }
  });

  function toggleAll() {
    if (allChecked) {
      // décocher seulement les visibles
      const next = new Set(selected);
      for (const r of filtered) next.delete(String(r.id));
      selected = next;
    } else {
      const next = new Set(selected);
      for (const r of filtered) next.add(String(r.id));
      selected = next;
    }
  }

  function toggleOne(id: string) {
    const next = new Set(selected);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    selected = next;
  }

  function doExport() {
    if (selected.size === 0) return;
    const ids = Array.from(selected).join(',');
    // GET ids= ; backend supporte aussi ?run_id= en repli
    const url = `${get_api_base_origin()}/api/payroll/payslips/export/zip/?ids=${encodeURIComponent(ids)}`;
    window.open(url, '_blank');
    open = false;
  }

  function fmt(v: any) {
    const n = Number(v);
    if (!Number.isFinite(n)) return '-';
    return n.toLocaleString('fr-FR');
  }
</script>

<Dialog.Root bind:open>
  <Dialog.Content class="sm:max-w-[680px] w-[92vw] p-0 gap-0 overflow-hidden max-h-[88vh] flex flex-col">
    <Dialog.Header class="px-6 pt-6 pb-3 text-left">
      <Dialog.Title class="text-[0.95rem] font-semibold flex items-center gap-2">
        <AppIcon name="download" size={16} class="text-slate-500" /> 
        Exporter bulletins
      </Dialog.Title>
      <Dialog.Description class="text-[0.82rem] text-slate-500">
        {#if payslipsStore.runId}
          Exécution : <span class="font-medium text-slate-700">{runLabel}</span> — {rows.length} bulletin{rows.length>1?'s':''}
        {:else}
          Toutes les exécutions — {rows.length} bulletin{rows.length>1?'s':''}
        {/if}
      </Dialog.Description>
    </Dialog.Header>

    <div class="px-6 pb-3 flex items-center gap-2">
      <div class="relative flex-1">
        <AppIcon name="search" size={16} class="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <Input bind:value={localSearch} placeholder="Rechercher (nom, matricule)…" class="h-8 pl-8 text-[0.85rem]" />
      </div>
      <label class="flex items-center gap-2 text-[0.82rem] text-slate-600 cursor-pointer select-none shrink-0">
        <Switch checked={allChecked} onCheckedChange={toggleAll} />
        Tout {filtered.length ? `(${filtered.length})` : ''}
      </label>
    </div>

    <div class="mx-6 border rounded-lg overflow-hidden flex-1 min-h-0">
      <div class="max-h-[52vh] min-h-[280px] overflow-y-auto divide-y divide-slate-100">
        {#if loading}
          <div class="py-10 text-center text-[0.82rem] text-slate-400">Chargement…</div>
        {:else if filtered.length === 0}
          <div class="py-10 text-center text-[0.82rem] text-slate-400">{rows.length===0 ? 'Aucun bulletin pour cette exécution' : 'Aucun résultat'}</div>
        {:else}
          {#each filtered as r (r.id)}
            {@const id = String(r.id)}
            {@const checked = selected.has(id)}
            {@const name = r.employee?.fullName ?? r.employee_name ?? '—'}
            {@const matricule = r.employee?.matricule ?? ''}
            <label class="flex items-center gap-3 px-3 py-2.5 hover:bg-slate-50 cursor-pointer">
              <Checkbox {checked} onCheckedChange={()=>toggleOne(id)} onclick={(e:Event)=>e.stopPropagation()} />
              <div class="min-w-0 flex-1">
                <div class="text-[0.84rem] font-medium text-slate-800 truncate">{name}</div>
                <div class="text-[0.78rem] text-slate-500 truncate">{matricule}{r.org_unit ? ` · ${r.org_unit}` : ''}{r.job_title ? ` · ${r.job_title}` : ''}</div>
              </div>
              <div class="text-right shrink-0">
                <div class="text-[0.82rem] font-semibold text-slate-800 tabular-nums">{fmt(r.net_amount ?? r.summary?.netPay)} CDF</div>
                <div class="text-[0.75rem] text-slate-400">Brut {fmt(r.gross_amount ?? r.summary?.grossSalary)}</div>
              </div>
            </label>
          {/each}
        {/if}
      </div>
    </div>

    <Dialog.Footer class="px-6 py-4 flex items-center justify-between">
      <span class="text-[0.82rem] text-slate-500">{count} sélectionné{count>1?'s':''}</span>
      <div class="flex gap-2">
        <Button variant="ghost" size="sm" class="h-8" onclick={()=> open=false}>
          <AppIcon name="x" size={16} class="mr-1.5 text-slate-300" /> 
          Annuler
        </Button>
        <Button size="sm" class="h-8" disabled={count===0} onclick={doExport}>
          <AppIcon name="download" size={16} class="mr-1.5" /> 
          Exporter ZIP
        </Button>
      </div>
    </Dialog.Footer>
  </Dialog.Content>
</Dialog.Root>

