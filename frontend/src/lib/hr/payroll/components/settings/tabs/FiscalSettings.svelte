<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { Badge } from '@/components/ui/badge';
  import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
  import type { TaxBracketConfig } from '@/hr/payroll/types/types';
  import SettingSection from '../SettingSection.svelte';


  let {
    brackets = [],
    isLoading = false,
  }: {
    brackets?: TaxBracketConfig[];
    isLoading?: boolean;
  } = $props();

  const formatAmount = (value: number | null | undefined): string => {
    if (value === null || value === undefined) return '∞';
    return value.toLocaleString('fr-FR');
  };

  const formatRate = (rate: number): string => `${rate}%`;
</script>


<SettingSection
  icon="receipt"
  title="Barème IRPP 2026"
  description="10 tranches progressives — Loi de finances 2026."
  iconClass="bg-purple-50"
>
  {#if isLoading && brackets.length === 0}
    <div class="flex items-center justify-center py-10 text-slate-500 text-[0.85rem]">
      <AnimateSpin text="Chargement du barème" textPosition="right" class="size-3" />
    </div>
  {:else if brackets.length === 0}
    <div class="py-10 text-center">
      <AppIcon name="receipt" size={28} class="text-slate-300 mx-auto mb-2" strokeWidth={1.3} />
      <p class="text-[0.9rem] text-slate-500">Aucune tranche fiscale configurée.</p>
    </div>
  {:else}
    <div class="overflow-hidden rounded-xl border border-slate-100">
      <Table>
        <TableHeader class="bg-slate-50">
          <TableRow>
            <TableHead class="text-[0.78rem] font-bold uppercase tracking-widest text-slate-500">Tranche</TableHead>
            <TableHead class="text-[0.78rem] font-bold uppercase tracking-widest text-slate-500">De (CDF/mois)</TableHead>
            <TableHead class="text-[0.78rem] font-bold uppercase tracking-widest text-slate-500">À (CDF/mois)</TableHead>
            <TableHead class="text-[0.78rem] font-bold uppercase tracking-widest text-slate-500 text-right">Taux</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {#each brackets as bracket}
            <TableRow class="hover:bg-slate-50/50 transition-colors">
              <TableCell class="py-2.5 text-[0.9rem] font-semibold text-slate-600">{bracket.label}</TableCell>
              <TableCell class="py-2.5 text-[0.9rem] text-slate-700 tabular-nums">{formatAmount(bracket.lower_limit)}</TableCell>
              <TableCell class="py-2.5 text-[0.9rem] text-slate-700 tabular-nums">
                {#if bracket.upper_limit === null}
                  <span class="text-slate-300">∞</span>
                {:else}
                  {formatAmount(bracket.upper_limit)}
                {/if}
              </TableCell>
              <TableCell class="py-2.5 text-right">
                <Badge
                  variant="outline"
                  class="text-[0.82rem] font-bold border-slate-200 bg-slate-50 text-slate-700 tabular-nums"
                >
                  {formatRate(bracket.rate_percentage)}
                </Badge>
              </TableCell>
            </TableRow>
          {/each}
        </TableBody>
      </Table>
    </div>
    <p class="text-[0.84rem] text-slate-500 mt-3 flex items-center gap-1">
      <AppIcon name="info" size={13} />
      Toutes les tranches sont chargées depuis le barème officiel ({brackets.length} tranches).
    </p>
  {/if}
</SettingSection>


