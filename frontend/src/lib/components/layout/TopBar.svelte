<script lang="ts">
    import UserMenu from "$lib/components/shared/UserMenu.svelte";
	import { current_organization_store } from "@/stores/auth";
	import { OXILIERE_LABEL } from '@/constants/base';
    
</script>

<nav class="comet-header-height bg-background flex w-full items-center justify-between gap-6 border-b pl-4 pr-6">
    <div class="min-w-1 flex-1">
        {#if $current_organization_store}
            <a href="/o/{$current_organization_store.slug}" class="flex items-center font-semibold text-xl text-foreground gap-2">
                {$current_organization_store.name}
            </a>
        {:else}
            <a href="/" class="flex items-center font-semibold text-xl text-foreground gap-2">
                {OXILIERE_LABEL}
            </a>
        {/if}
    </div>

    <UserMenu />
</nav>

