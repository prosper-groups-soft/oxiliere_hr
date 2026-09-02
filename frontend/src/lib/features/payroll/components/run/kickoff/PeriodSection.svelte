<script lang="ts">
  import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
  import { Label } from "@/components/ui/label";
  import { Input } from "@/components/ui/input";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { formatDate } from "@/utilities/common/date";


  interface Props {
    periodStart: string;
    periodEnd: string;
    onPeriodStartChange: (value: string) => void;
    onPeriodEndChange: (value: string) => void;
  }

  let {
    periodStart,
    periodEnd,
    onPeriodStartChange,
    onPeriodEndChange
  }: Props = $props();

  function periodDays(): number {
    if (!periodStart || !periodEnd) return 0;
    const s = new Date(periodStart);
    const e = new Date(periodEnd);
    return Math.round((e.getTime() - s.getTime()) / 86400000) + 1;
  }
</script>


<Card class="border-slate-200 shadow-sm rounded-2xl">
  <CardHeader class="px-5! pt-2! pb-0!">
    <CardTitle class="text-[0.98rem] font-bold text-slate-900 tracking-tight">
      Période de paie
    </CardTitle>
    <CardDescription class="text-[0.875rem]">
      Définissez la période couverte par cette exécution.
    </CardDescription>
  </CardHeader>
  <CardContent class="px-5! py-5! pt-1! space-y-4">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
      <div class="space-y-1.5">
        <Label for="period-start" class="text-[0.85rem] text-slate-900 font-medium">
          Date début *
        </Label>
        <Input
          id="period-start"
          type="date"
          value={periodStart}
          oninput={(e) => onPeriodStartChange((e.currentTarget as HTMLInputElement).value)}
          class="h-9 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine"
        />
      </div>
      <div class="space-y-1.5">
        <Label for="period-end" class="text-[0.85rem] text-slate-900 font-medium">
          Date fin *
        </Label>
        <Input
          id="period-end"
          type="date"
          value={periodEnd}
          oninput={(e) => onPeriodEndChange((e.currentTarget as HTMLInputElement).value)}
          class="h-9 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine"
        />
      </div>
    </div>

    {#if periodDays() > 0}
      <div class="flex items-center gap-2.5 px-3.5 py-2.5 bg-slate-50 rounded-lg border border-slate-100">
        <AppIcon name="calendar-range" size={15} class="text-slate-400 shrink-0" />
        <span class="text-[0.85rem] text-slate-600">
          {periodDays()} jours calendaires
          <span class="text-slate-300 mx-1.5">·</span>
          {formatDate(periodStart)} → {formatDate(periodEnd)}
        </span>
      </div>
    {/if}
  </CardContent>
</Card>

