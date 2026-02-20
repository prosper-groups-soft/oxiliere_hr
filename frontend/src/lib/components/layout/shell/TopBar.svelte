<script lang="ts">
  import { Separator } from "@/components/ui/separator";
  import UserMenu from "$lib/components/shared/UserMenu.svelte";
  import { current_organization_store } from "@/stores/auth";
  import { OXILIERE_LABEL, ORGANIZATION_NAME } from '@/constants/app/base';
  import { NAV_CONFIG } from "@/constants/features/navigation";
</script>


<nav 
  class="bg-background flex w-full items-center justify-between gap-6 border-b px-5 sticky top-0 z-2"
  style="height: {NAV_CONFIG.topBarHeight}px;"
>
  <div class="min-w-0 flex-1">
    {#if $current_organization_store}
      <a 
        href="/o/{$current_organization_store.slug}" 
        class="flex items-center font-bold text-lg text-slate-900 gap-2 hover:text-primary transition-colors truncate"
      >
        <span class="truncate">{$current_organization_store.name}</span>
      </a>
    {:else}
      <div class="flex items-center font-bold text-lg text-slate-900 gap-2">
        <span class="text-primary">{OXILIERE_LABEL}</span>
      <Separator orientation="vertical" class="data-[orientation=vertical]:h-4 bg-gray-400" />
        <span class="text-slate-600 font-medium text-[0.95rem]">{ORGANIZATION_NAME}</span>
      </div>
    {/if}
  </div>

  <div class="flex items-center gap-4">
    <UserMenu />
  </div>
</nav>

