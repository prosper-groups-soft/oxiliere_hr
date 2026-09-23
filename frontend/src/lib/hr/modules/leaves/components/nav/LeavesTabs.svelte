<script lang="ts">
  import NavTabs from "@/hr/navigation/components/NavTabs.svelte";
  import { hr } from "@/hr/constants/navigation/navigation";
  import { page } from "$app/state";
  import { useBalanceSummaryQuery, usePendingCountQuery } from "@/hr/modules/leaves/queries/leaveQueries";
  import { auth } from "@/hr/auth/stores/auth.svelte";
  import { fade } from "svelte/transition";
  import AnimateSpin from "@/hr/components/layout/elements/AnimateSpin.svelte";

  const currentEmployeeId = $derived(auth.currentUser?.id ?? '');
  const balanceQuery = $derived.by(() => useBalanceSummaryQuery('019e5513-31c0-736b-b2de-3cb3a6381e79'));
  const pendingQuery = usePendingCountQuery();
  const pendingCount = $derived($pendingQuery.data?.count ?? 0);
  const annualBalance = $derived(
    $balanceQuery?.data ? { allocated: $balanceQuery.data.allocated, remaining: $balanceQuery.data.totalAvailable, taken: $balanceQuery.data.deducted } : null
  );

  const baseTabs = [
    { id: 'requests', label: 'Mes Congés', icon: 'calendar-days', path: hr('/leaves/requests') },
    { id: 'team', label: 'Équipe', icon: 'users', path: hr('/leaves/team') },
    { id: 'settings', label: 'Configuration', icon: 'settings', path: hr('/leaves/settings') },
  ];
  const tabs = $derived(baseTabs.map(t => t.id === 'requests' && pendingCount > 0 ? { ...t, count: pendingCount } : t));

  const activeTabId = $derived.by(() => baseTabs.find(t => page.url.pathname.startsWith(t.path))?.id ?? 'requests');
</script>

<div class="border-b border-slate-100 px-4 flex items-center justify-between">
  <NavTabs {tabs} activeId={activeTabId} variant="underline" />
  {#if activeTabId === "requests"}
    <div in:fade={{ duration: 200 }} class="flex items-center gap-2 pr-6">
      {#if $balanceQuery?.isPending && !$balanceQuery?.isFetched && !!currentEmployeeId}
        <div class="flex items-center gap-2 px-3 py-1 text-[0.77rem] rounded-full border border-slate-100 bg-[#f5f6f7] text-slate-400">
          <AnimateSpin class="border-slate-400 size-2.5" text="Chargement" textPosition="right" />
        </div>
      {:else if annualBalance}
        <button class="group relative flex items-center gap-3 px-3 py-1.5 cursor-default text-[0.85rem] rounded-full border border-slate-100 shadow-fine bg-[#f5f6f7] text-slate-600 transition-all hover:shadow hover:border-slate-200 hover:bg-slate-100 leading-none" title="Solde annuel">
          <div class="flex items-center gap-2">
            <div class="h-1.5 w-1.5 rounded-full bg-blue-500"></div>
            <span class="text-slate-500 font-medium text-[0.85rem]">Annuel</span>
          </div>
          <div class="flex items-baseline gap-1.5">
            <span class="font-bold text-slate-800 text-[0.87rem] tabular-nums">{annualBalance.remaining}</span>
            <span class="text-slate-400 text-[0.85rem]">/ {annualBalance.allocated} j</span>
          </div>
          <div class="absolute bottom-0 left-2 right-2 h-0.5 rounded-full bg-slate-200 overflow-hidden">
            <div class="h-full rounded-full bg-blue-500 transition-all duration-300" style="width: {Math.min(100, (annualBalance.taken / annualBalance.allocated) * 100)}%"></div>
          </div>
        </button>
      {/if}
    </div>
  {/if}
</div>
