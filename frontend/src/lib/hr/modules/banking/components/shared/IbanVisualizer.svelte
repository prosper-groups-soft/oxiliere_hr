<script lang="ts">
  import { cn } from "@/hr/utilities/common/css";
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { notification } from "@/hr/stores/notification.svelte";


  let { 
    label, 
    value, 
    class: className = "" 
  }: { 
    label: string; 
    value: string; 
    class?: string 
  } = $props();

  let copied = $state(false);
  let timeoutId: ReturnType<typeof setTimeout> | undefined;

  function copyToClipboard() {
    navigator.clipboard.writeText(value);
    notification.toast.success(`${label} copié dans le presse-papier`);
    
    copied = true;
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      copied = false;
    }, 1500);
  }
</script>


<div class={cn("flex flex-col gap-1", className)}>
  <span class="text-[0.75rem] font-semibold uppercase tracking-wider text-slate-400">
    {label}
  </span>
  <div class="flex items-center gap-2 group">
    <code class="text-[0.85rem] text-slate-700 bg-slate-50 px-2 py-0.5 rounded border border-slate-100 transition-colors group-hover:border-slate-200">
      {value}
    </code>
    <button 
      onclick={copyToClipboard}
      class="p-1.5 rounded-md text-slate-400 hover:text-primary hover:bg-primary/5 transition-all cursor-pointer"
      title={`Copier ${label}`}
    >
      <AppIcon name={copied ? "check" : "copy"} size={16} class={copied ? "text-green-500" : ""} />
    </button>
  </div>
</div>

