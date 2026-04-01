<script lang="ts">
  import { Separator } from "@/components/ui/separator";
  import UserMenu from "./UserMenu.svelte";
  import { auth } from "@/features/auth/stores/auth.svelte";
  import { OXILIERE_LABEL, ORGANIZATION_NAME } from '@/constants/app/base';
  import { NAV_CONFIG } from "@/constants/features/navigation";
</script>


<nav 
  class="bg-background flex w-full items-center justify-between gap-6 border-b px-5 sticky top-0 z-2"
  style="height: {NAV_CONFIG.topBarHeight}px;"
>
  <div class="min-w-0 flex-1">
    {#if auth.currentOrganization}
      <a 
        href="/o/{auth.currentOrganization.slug}" 
        class="flex items-center font-bold text-lg text-slate-900 gap-2 hover:text-primary transition-colors truncate"
      >
        <span class="truncate">{auth.currentOrganization.name}</span>
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

