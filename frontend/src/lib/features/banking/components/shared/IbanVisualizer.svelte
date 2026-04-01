<script lang="ts">
  import { cn } from "@/utilities/common/css";
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { toast } from "svelte-sonner";

  let { 
    label, 
    value, 
    class: className = "" 
  }: { 
    label: string; 
    value: string; 
    class?: string 
  } = $props();

  function copyToClipboard() {
    navigator.clipboard.writeText(value);
    toast.success(`${label} copié dans le presse-papier`);
  }
</script>

<div class={cn("flex flex-col gap-1", className)}>
  <span class="text-[0.65rem] font-semibold uppercase tracking-wider text-slate-400">
    {label}
  </span>
  <div class="flex items-center gap-2 group">
    <code class="text-[0.85rem] font-mono text-slate-700 bg-slate-50 px-2 py-0.5 rounded border border-slate-100 transition-colors group-hover:border-slate-200">
      {value}
    </code>
    <button 
      onclick={copyToClipboard}
      class="p-1.5 rounded-md text-slate-400 hover:text-primary hover:bg-primary/5 transition-all cursor-pointer"
      title={`Copier ${label}`}
    >
      <AppIcon name="copy" size={14} />
    </button>
  </div>
</div>

<style>
  code {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
  }
</style>
