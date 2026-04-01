<script lang="ts">
  import { crossfade } from 'svelte/transition';
  import { cubicInOut } from 'svelte/easing';
  import * as Tabs from '@/components/ui/tabs';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { cn } from '@/utilities/common/css'; 
  import { onboardingStore } from "../../../stores/onboarding.svelte";
  import { Button } from '@/components/ui/button';
  import { notification } from '@/stores/notification.svelte';

  const { steps } = onboardingStore;

  const [send, receive] = crossfade({
    duration: 300,
    easing: cubicInOut
  });

  function handleStartFresh() {
    onboardingStore.reset();
    onboardingStore.clearDraft();
    onboardingStore.isAutoSaveEnabled = true;
    notification.toast.info("Nouveau dossier commencé.");
  }
</script>


<div class="bg-white border-b border-slate-100 mb-4 mt-1.5 pr-5 px-3.5">
  <div class="flex items-center justify-between">
    <Tabs.Root value={onboardingStore.currentStep} onValueChange={(v) => onboardingStore.setStep(v as any)} class="w-full">
      <Tabs.List class="relative bg-transparent w-full justify-start rounded-none h-auto p-0 gap-2 border-none">
        {#each steps as step}
          {@render TabTrigger(step)}
        {/each}
      </Tabs.List>
    </Tabs.Root>

    {@render AutoSyncIndicator()}

  </div>
</div>


{#snippet TabTrigger(tab: typeof steps[0])}
  <Tabs.Trigger 
    value={tab.id} 
    class={cn(
      "relative flex items-center gap-2.5 bg-transparent shadow-none transition-all duration-300",
      "rounded-none border-none px-4 outline-none focus-visible:ring-0",
      "font-bold group cursor-pointer text-slate-700",
      "data-[state=active]:text-primary data-[state=active]:bg-transparent",
      "data-[state=active]:hover:bg-transparent data-[state=active]:hover:text-primary",
      "data-[state=active]:focus:bg-transparent"
    )}
  >
    <AppIcon name={tab.icon} size={18} class="group-data-[state=active]:text-primary" />
    <span class="text-[0.879rem] tracking-tight">{tab.label}</span>  

    {#if onboardingStore.currentStep === tab.id}
      <div 
        in:receive={{ key: 'active-bar' }}
        out:send={{ key: 'active-bar' }}
        class="absolute bottom-0 left-0 right-0 h-1 bg-primary rounded-full z-10"
      ></div>
    {/if}
  </Tabs.Trigger>
{/snippet}


{#snippet AutoSyncIndicator()}
  <div class="flex items-center gap-2.5 text-slate-500 select-none pr-2">
    {#if onboardingStore.isSyncing}
      <div class="h-2 w-2 rounded-full bg-blue-500 animate-pulse"></div>
      <span class="text-[0.72rem] font-medium">Enregistrement...</span>
    {:else if onboardingStore.isRestoredDraft}
      <div class="flex items-center gap-2">
        <div class="h-2 w-2 rounded-full bg-green-400"></div>
        <span class="text-[0.72rem] font-medium tracking-tight text-green-600 whitespace-nowrap">Brouillon restauré</span>
        <Button 
          variant="ghost" 
          size="sm" 
          onclick={handleStartFresh}
          class="h-5.5 px-2 text-[0.72rem] text-slate-400 hover:text-slate-600 font-medium"
        >
          Recommencer
        </Button>
      </div>
    {:else if onboardingStore.lastSaved}
      <div class="h-2 w-2 rounded-full bg-emerald-500/80"></div>
      <span class="text-[0.72rem] font-medium tracking-tight whitespace-nowrap">Enregistré à {onboardingStore.lastSaved}</span>
    {/if}
  </div>
{/snippet}

