<script lang="ts">
  import '@/css/app.css';
  import { browser } from '$app/environment';
  import { page } from '$app/state';
  import { ui } from '@/stores/ui.svelte';
  import { MENU_ITEMS, bottomMenuItems, MENU_ITEM_TYPE, type MenuItem } from "@/constants/features/navigation";
  import PageLayout from '@/components/layout/containers/PageLayout.svelte';
  import { Toaster } from '@/components/ui/sonner';
  import { QueryClient, QueryClientProvider } from '@tanstack/svelte-query';
  import type { Snippet } from 'svelte';
  import AppModeWatcher from './AppModeWatcher.svelte';
  import ConfirmDialog from '@/components/shared/modals/ConfirmDialog.svelte';

  
  let { children }: { children: Snippet } = $props();

  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        enabled: browser,
      },
    }
  });

  // --- Global Synchronization of Menu and Loading State ---
  $effect(() => {
    const pathname = page.url.pathname;
    let bestMatchId: string | null = pathname === '/hr' ? "home" : null;
    let maxMatchLength = -1;

    const checkMatch = (item: MenuItem) => {
      if ((item.type === MENU_ITEM_TYPE.router || !item.type) && item.path) {
        const itemPath = item.path;
        const isMatch = pathname === itemPath || 
                        (pathname.startsWith(itemPath) && 
                        (itemPath === '/' || pathname[itemPath.length] === '/'));
        
        if (isMatch && itemPath.length > maxMatchLength) {
          maxMatchLength = itemPath.length;
          bestMatchId = item.id;
        }
      }
    };

    // Scan menus to find the ID corresponding to the current URL
    MENU_ITEMS.forEach(group => group.items.forEach(checkMatch));
    bottomMenuItems.forEach(checkMatch);

    // Reactive update of the UI store
    ui.selectedMenuItem = bestMatchId;

    if (browser) {
      ui.initialLoading = false;
    }
  });
</script>


<QueryClientProvider client={queryClient}>
  <AppModeWatcher />
  <PageLayout>
    {@render children()}
  </PageLayout>
  <Toaster richColors class="pointer-events-auto" />
  <ConfirmDialog />
</QueryClientProvider>

