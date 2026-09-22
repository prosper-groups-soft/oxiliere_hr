<script lang="ts">
  import { fade } from 'svelte/transition';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import DataPagination from '@/components/layout/elements/DataPagination.svelte';
  import LoadingBar from '@/components/layout/elements/LoadingBar.svelte';
  import SearchBar from '@/components/shared/elements/SearchBar.svelte';
  import FilterChips from '@/components/shared/elements/FilterChips.svelte';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import PayslipGroupList from '@/hr/payroll/components/payslips/PayslipGroupList.svelte';
  import PayslipDetailSheet from '@/hr/payroll/components/payslips/sheets/PayslipDetailSheet.svelte';
  import PayslipsActions from '@/hr/payroll/components/payslips/PayslipsActions.svelte';
  import { payslipsStore } from '@/hr/payroll/stores/payslips/payslipsStore.svelte';
  import { payrollRunStore } from '@/hr/payroll/stores/runs/payrollRunStore.svelte';
  import type { Payslip } from '@/hr/payroll/types/types';
  import { ui } from '@/stores/ui.svelte';
  import { Button } from '@/components/ui/button';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';


  type PayslipGroup = { period: string; label: string; payslips: Payslip[]; count: number; totalNet: number; };
  
  function formatPeriodLabel(period: string) {
    const d = new Date(`${period}-01`); if (Number.isNaN(d.getTime())) return period;
    return new Intl.DateTimeFormat('fr-FR', { month:'long', year:'numeric' }).format(d);
  }
  
  function getPayslipGroups(payslips: Payslip[]): PayslipGroup[] {
    const m = new Map<string,Payslip[]>();
    for (const p of payslips) {
      const k = (p as any).payroll_run ? new Date((p as any).payroll_run_start || (p as any).created_at).toISOString().slice(0,7) : ((p.period as any)?.start ?? '').substring(0,7) || '—';
      const key = k || '—';
      if (!m.has(key)) m.set(key, []); m.get(key)!.push(p);
    }
    return Array.from(m.entries()).sort(([a],[b])=>b.localeCompare(a)).map(([period, items])=>({
      period, label: period==='—' ? 'Bulletins' : formatPeriodLabel(period),
      payslips: [...items].sort((a,b)=>(a.employee?.fullName??'').localeCompare(b.employee?.fullName??'')),
      count: items.length, totalNet: items.reduce((s,p)=>s+((p.summary?.netPay?? (p as any).net_amount ?? 0)),0)
    }));
  }

  let sheetOpen = $state(false);
  let selectedPayslip = $state<Payslip | null>(null);
  
    function openDetail(id: string) {
    const p = payslipsStore.payslips.find(x=>x.id===id);
    if (p) { selectedPayslip = p; sheetOpen = true; }
  }

  let viewState: 'loading'|'success'|'error'|'offline' = $state('loading');
  let hasLoadedOnce = $state(false);
  let refreshing = false;
  
  async function refresh() {
    if (refreshing) return; refreshing=true;
    try { await payslipsStore.fetchPayslips(); hasLoadedOnce=true; viewState='success'; }
    catch (e:any) { viewState = e?.message==='offline' ? 'offline' : 'error'; }
    finally { refreshing=false; }
  }
  
  // assure runs chargés pour filtre par exécution
  $effect(()=>{ if(!payrollRunStore.runList.length) payrollRunStore.fetchRunList().catch(()=>{}); });

  $effect(()=>{
    const sig = [payslipsStore.search, payslipsStore.orgUnit, payslipsStore.runId, payslipsStore.ordering, payslipsStore.currentPage, payslipsStore.perPage].join('|');
    void sig; const t=setTimeout(()=>{refresh();}, 350); return ()=>clearTimeout(t);
  });

  $effect(()=>{ ui.addActions('payroll-payslips-list', PayslipsActionsSnippet); return ()=>ui.removeActions('payroll-payslips-list'); });

  const filtersWithSearch = $derived.by(()=>{
    const f: Record<string,string[]>={};
    if(payslipsStore.runId) { const r=payrollRunStore.runList.find(x=>x.id===payslipsStore.runId); f.run=[r?.periodLabel ?? payslipsStore.runId.slice(0,8)]; }
    if(payslipsStore.orgUnit) f.orgUnit=[payslipsStore.orgUnit];
    if(payslipsStore.search) f.search=[payslipsStore.search];
    return f;
  });

  const activeFiltersWithSearch = $derived((payslipsStore.orgUnit?1:0)+(payslipsStore.runId?1:0)+(payslipsStore.search?1:0));
  function handleFilterRemove(k:string){ if(k==='search') payslipsStore.setSearch(''); else if(k==='orgUnit') payslipsStore.setOrgUnit(''); else if(k==='run') payslipsStore.setRunId(''); }
  function handleResetFilters(){ payslipsStore.resetFilters(); }
  function handleClearSearch(){ payslipsStore.setSearch(''); }

  const totalCount = $derived(payslipsStore.totalCount);
  const pageItems = $derived(payslipsStore.paginatedPayslips);
</script>


<svelte:head>
  <title>Oxiliere HR - Bulletins de paie</title>
</svelte:head>


{#snippet PayslipsActionsSnippet()}
  <PayslipsActions />
{/snippet}


{#snippet QuickStats()}
  <div class="flex items-center gap-5 px-4 py-1">
    <div class="flex items-center gap-2">
      <AppIcon name="file-text" size={17} class="text-slate-500" />
      <span class="text-sm font-semibold text-slate-800 tabular-nums">{totalCount}</span>
      <span class="text-sm text-slate-400">bulletins</span>
    </div>
    {#if payslipsStore.runId}
    <div class="flex items-center gap-2">
      <AppIcon name="layers" size={17} class="text-blue-500" />
      <span class="text-sm font-semibold text-blue-600 tabular-nums">1</span>
      <span class="text-sm text-slate-400">exécution</span>
    </div>
    {/if}
  </div>
{/snippet}


{#snippet Header()}
  <header class="flex items-center justify-between pb-2.5 border-b border-slate-100 pt-2.5 px-4 pr-8">
    <div class="flex-1 ml-0.5">
      <SearchBar bind:value={payslipsStore.search} placeholder="Rechercher un bulletin (nom, matricule)..." class="w-125" inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]" iconSize={22} onClear={handleClearSearch} />
    </div>
    {@render QuickStats()}
  </header>
{/snippet}


<div class="flex h-full flex-col overflow-hidden min-h-0">
  {@render Header()}

  <FilterChips filters={filtersWithSearch} activeFiltersCount={activeFiltersWithSearch} getDisplayLabel={(k,v)=>k==='search'?`Recherche: "${v}"`:k==='run'?`Exécution: ${v}`:`Unité: ${v}`} onRemove={handleFilterRemove} onReset={handleResetFilters} class="py-1 pb-1.5 px-6 border-b border-slate-50" />
  <LoadingBar loading={payslipsStore.isFetching} />
  
  <main class="flex flex-1 flex-col overflow-hidden min-h-0">
    {#key viewState==='loading' ? 'loading' : viewState==='success' && pageItems.length>0 ? 'table' : 'empty'}
      <div class="flex flex-1 flex-col overflow-hidden min-h-0" in:fade={{duration:160}}>
        {#if viewState==='loading'}
          <div class="flex-1 min-h-0 flex items-center justify-center"><AnimateSpin text="Chargement des bulletins" /></div>
        {:else if viewState==='error' || viewState==='offline' || pageItems.length===0}
          {@const isOffline = viewState==='offline'}
          {@const isError = viewState==='error'}
          {@const isEmpty = !isOffline && !isError}
          {@const isFilteredEmpty = isEmpty && activeFiltersWithSearch>0}
          <div class="flex-1 min-h-0 flex items-center justify-center px-6 py-12">
            <Empty icon={isOffline?'wifi-off':isError?'alert-triangle':isFilteredEmpty?'search-x':'file-text'} title={isOffline?'Hors connexion':isError?'Une erreur est survenue':isFilteredEmpty?'Aucun bulletin trouvé':'Aucun bulletin'} description={isOffline?'Impossible de charger les bulletins. Vérifiez votre connexion.':isError?'Une erreur est survenue lors du chargement.':isFilteredEmpty?'Aucun bulletin ne correspond à vos critères.':'Aucun bulletin n\'a été généré pour cette période.'} iconContainerClass={isOffline?'bg-amber-50':isError?'bg-rose-50':'bg-slate-50'} iconClass={isEmpty?'text-slate-300':undefined} iconSize={isEmpty?30:32} iconStrokeWidth={1.5}>
              {#if isOffline || isError}<Button onclick={()=>refresh()} variant="outline" class="h-7 mt-2 rounded-lg"><AppIcon name="refresh-cw" />Réessayer</Button>
              {:else if isFilteredEmpty}<Button variant="ghost" onclick={handleResetFilters} class="h-7 bg-slate-50"><AppIcon name="x" size={16} class="text-slate-400" />Réinitialiser les filtres</Button>
              {:else}<Button variant="outline" onclick={()=>payslipsStore.downloadZip()} class="h-7"><AppIcon name="download" size={16} />Exporter ZIP</Button>{/if}
            </Empty>
          </div>
        {:else}
          <div class="flex-1 min-h-0 overflow-y-auto"><PayslipGroupList groups={getPayslipGroups(pageItems)} onSelect={openDetail} /></div>
          <footer class="px-4 bg-slate-50/80 border-t border-[#e9eaea] pr-10">
            <DataPagination currentCount={pageItems.length} totalCount={totalCount} currentPage={payslipsStore.currentPage} totalPages={payslipsStore.totalPages} perPage={payslipsStore.perPage} onPageChange={(p)=>payslipsStore.setPage(p)} onPerPageChange={(s)=>payslipsStore.setPerPage(s)} onNext={()=>payslipsStore.nextPage()} onPrev={()=>payslipsStore.prevPage()} unitLabel="bulletins" />
          </footer>
        {/if}
      </div>
    {/key}
  </main>
</div>

<PayslipDetailSheet bind:open={sheetOpen} payslip={selectedPayslip} />

