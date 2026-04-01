<script lang="ts">
  type Props = {
    label: string;
    count: number;
    totalNet: number;
  };

  let { label, count, totalNet }: Props = $props();
</script>


<div class="flex items-center gap-3">
  <span class="font-semibold text-slate-700 text-sm">{label}</span>
  <span class="text-slate-300 text-sm">|</span>
  <span class="text-slate-500 text-sm">{count} bulletin{count > 1 ? 's' : ''}</span>
  <span class="text-slate-300 text-sm">|</span>
  <span class="font-medium text-slate-700 text-sm">
    {totalNet.toLocaleString('fr-FR', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })}
  </span>
</div>

