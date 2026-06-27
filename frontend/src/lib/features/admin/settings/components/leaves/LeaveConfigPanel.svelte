<script lang="ts">
  import { leaveSettingsStore } from "../../stores/leaveSettingsStore.svelte";
  import { ui } from "@/stores/ui.svelte";
  import { slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import type { 
    useSaveLeaveSettingsMutation, 
    useInitializeDefaultsMutation 
  } from "../../queries/leaveQueries";

  // Sub-components
  import LeaveHeader from "./LeaveHeader.svelte";
  import LeaveLegalBanner from "./LeaveLegalBanner.svelte";
  import AnnualLeaveSection from "./sections/AnnualLeaveSection.svelte";
  import CarryOverSection from "./sections/CarryOverSection.svelte";
  import SenioritySection from "./sections/SenioritySection.svelte";
  import SpecialLeavesSection from "./sections/SpecialLeavesSection.svelte";

  interface Props {
    saveMutation: ReturnType<typeof useSaveLeaveSettingsMutation>;
    resetMutation: ReturnType<typeof useInitializeDefaultsMutation>;
    onSuccess?: () => void;
  }

  let { saveMutation, resetMutation, onSuccess }: Props = $props();

  const hasChanges = $derived(leaveSettingsStore.hasChanges);
  const validationErrors = $derived(leaveSettingsStore.validationErrors);
  const hasValidationErrors = $derived(Object.keys(validationErrors).length > 0);

  // Register status badges in global title bar
  $effect(() => {
    ui.addActions('leave-settings-header', saveStatusBadge);
    return () => ui.removeActions('leave-settings-header');
  });
</script>


{#snippet saveStatusBadge()}
  {#if hasChanges}
    {#if hasValidationErrors}
      <span class="flex items-center justify-center gap-1.5 text-[0.8rem] text-red-600 bg-red-50 px-2.5 py-1 rounded-full font-medium whitespace-nowrap w-44" transition:slide={{ duration: 300, easing: cubicOut, axis: 'y' }}>
        Erreurs de validation
      </span>
    {:else}
      <span class="flex items-center justify-center gap-1.5 text-[0.8rem] text-amber-600 bg-amber-50 px-2.5 py-1 rounded-full font-medium whitespace-nowrap w-44" transition:slide={{ duration: 300, easing: cubicOut, axis: 'y' }}>
        Non sauvegardé
      </span>
    {/if}
  {/if}
{/snippet}


<div class="sticky top-0 z-10 bg-white">
  <LeaveHeader {saveMutation} {resetMutation} {onSuccess} />
  <LeaveLegalBanner />
</div>

<div class="mt-6 space-y-6">
  <AnnualLeaveSection />
  <CarryOverSection />
  <SenioritySection />
  <SpecialLeavesSection />
</div>

