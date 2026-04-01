<script lang="ts">
  import { onboardingStore } from "../../../stores/onboarding.svelte";
  import type { Child } from "../../../types/types";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";

  interface Props {
    member: Child;
  }

  let { member }: Props = $props();

  function removeMember() {
    onboardingStore.removeChild(member.id as string);
  }
</script>


<div 
  class="flex items-center justify-between p-3.5 bg-white border border-slate-200 rounded-lg transition-all hover:border-slate-300 shadow-fine group"
>
  <div class="flex items-center gap-4">
    <div class="w-10 h-10 bg-slate-50 text-slate-500 rounded-md flex items-center justify-center border border-slate-100 shrink-0">
      <AppIcon name="user" size={20} />
    </div>
    <div>
      <p class="font-semibold text-slate-900 text-[0.85rem] tracking-tight">{member.name}</p>
      <div class="flex items-center gap-2 mt-0.5">
        <p class="text-[0.7rem] text-slate-500">{new Date(member.birthDate).toLocaleDateString()}</p>
      </div>
    </div>
  </div>
  <Button onclick={removeMember} size="icon" variant="ghost" class="h-8 w-8 text-red-400 hover:text-red-700 hover:bg-red-50">
    <AppIcon name="trash" size={19} />
  </Button>
</div>

