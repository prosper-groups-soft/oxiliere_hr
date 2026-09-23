<script lang="ts">
  import NavTabs from "@/hr/navigation/components/NavTabs.svelte";
  import { onboardingStore } from "../../../stores/onboarding.svelte";

  const tabs = $derived(onboardingStore.steps.map(s => ({ id: s.id, label: s.label, icon: s.icon, path: '' })));
  const activeId = $derived(onboardingStore.currentStep);
  function handleChange(id: string) { onboardingStore.setStep(id as any); }
</script>

<div class="bg-white border-b border-slate-100 mb-4 mt-1.5 pr-5 px-3.5">
  <div class="flex items-center justify-between">
    <NavTabs {tabs} activeId={activeId} variant="underline" onChange={handleChange} />
  </div>
</div>
