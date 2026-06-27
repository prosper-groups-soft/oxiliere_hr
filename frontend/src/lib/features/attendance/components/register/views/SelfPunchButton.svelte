<script lang="ts">
  import { useSelfPunchMutation } from "../../../queries/attendanceQueries";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";
  

  let { disabled = false } = $props<{ disabled?: boolean }>();

  const selfPunchMutation = useSelfPunchMutation();
  let isLocating = $state(false);
  let lastAction = $state<'in' | 'out' | null>(null);

  async function handleSelfPunch() {
    if (isLocating || $selfPunchMutation.isPending) return;

    isLocating = true;
    lastAction = null;

    try {
      // Get current timestamp, convert local time to ISO
      const now = new Date();
      // Adjust so the ISO string represents local time (not UTC)
      const localTimestamp = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString();

      // Try to get geolocation
      const position = await new Promise<GeolocationPosition | null>((resolve) => {
        if (!navigator.geolocation) {
          resolve(null);
          return;
        }
        navigator.geolocation.getCurrentPosition(
          (pos) => resolve(pos),
          () => resolve(null),
          { timeout: 5000, enableHighAccuracy: false }
        );
      });

      const payload: import('../../../api/attendance.endpoints').SelfPunchIn = {
        timestamp: localTimestamp,
        latitude: position?.coords.latitude ?? null,
        longitude: position?.coords.longitude ?? null,
      };

      $selfPunchMutation.mutate(payload, {
        onSuccess: (result) => {
          lastAction = result.action;
        },
      });
    } finally {
      isLocating = false;
    }
  }

  const buttonLabel = $derived(
    $selfPunchMutation.isPending ? "Pointage..." :
    isLocating ? "Localisation..." :
    "Pointer"
  );
</script>


<button
  onclick={handleSelfPunch}
  disabled={disabled || $selfPunchMutation.isPending || isLocating}
  class={cn(
    "flex items-center gap-2 h-7 px-4 rounded-md transition-all cursor-pointer border-none shadow-fine font-medium",
    disabled || $selfPunchMutation.isPending || isLocating
      ? "bg-slate-100 text-slate-400 cursor-not-allowed"
      : "bg-emerald-500 text-white hover:bg-emerald-600 active:scale-[0.97] hover:shadow-none"
  )}
>
  {#if $selfPunchMutation.isPending || isLocating}
    <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  {:else}
    <AppIcon name="clock" size={16} />
  {/if}
  <span class="text-[0.85rem]">{buttonLabel}</span>
</button>

