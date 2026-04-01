<script lang="ts">
  import { page } from '$app/state';
  import { settings } from "@/stores/settings.svelte";
  import { ui } from "@/stores/ui.svelte";
  import { employeeStore } from '@/features/employees/stores/employees.svelte';
  import { recruitmentStore } from '@/features/recruitment/stores/recruitment.svelte';
  import { PAGE_LABELS } from '@/constants/features/navigation';
  
  import SideBar from "@/components/layout/shell/SideBar.svelte";
  import TopBar from "@/components/layout/shell/TopBar.svelte";
  import BreadCrumb from "@/components/layout/shell/BreadCrumb.svelte";
  import PageTitle from "@/components/layout/shell/title/PageTitle.svelte";
  import AnimateSpin from '../elements/AnimateSpin.svelte';

  let { children } = $props();

  // --- Sidebar management via centralized settings store ---
  // We use the settings store to persist the user's preference
  const setExpanded = (val: boolean) => settings.update('sidebarExpanded', val);

  /**
   * Helper: Transforms a URL segment into a human-readable label
   * 1. Checks the static dictionary (PAGE_LABELS)
   * 2. Checks the employee database (for dynamic IDs)
   * 3. Checks the candidate database (for dynamic IDs)
   * 4. Falls back to raw text formatting
   */
  function getLabel(segment: string) {
    if (PAGE_LABELS[segment]) return PAGE_LABELS[segment];
    
    // Check if it's an employee ID
    const emp = employeeStore.getById(segment);
    if (emp) return emp.name;
    
    // Check if it's a candidate ID
    const candidate = recruitmentStore.candidates.find(c => c.id === segment);
    if (candidate) return `${candidate.firstName} ${candidate.lastName}`;
    
    // Check if it's a campaign ID
    const campaign = recruitmentStore.getCampaignById(segment);
    if (campaign) return campaign.title;
    
    return segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ');
  }

  /**
   * PURE DERIVED STATE: Computes navigation data (Breadcrumb & Title)
   * This is triggered automatically whenever 'page.url.pathname' changes.
   * Logic for 'ui.selectedMenuItem' is now handled exclusively by the Root Layout.
   */
  const navigationData = $derived.by(() => {
    const segments = page.url.pathname.split('/').filter(Boolean);
    let path = '';

    const items = segments.map((segment) => {
      path += `/${segment}`;
      return {
        label: getLabel(segment),
        href: path
      };
    });

    return {
      items,
      currentTitle: items.length > 0 
        ? items[items.length - 1].label 
        : 'Dashboard'
    };
  });
</script>


<div class="flex h-screen w-screen overflow-hidden">
  <!-- The SideBar state is driven by the global settings store -->
  <SideBar 
    expanded={settings.current.sidebarExpanded} 
    {setExpanded} 
  />

  <div class="flex flex-col flex-1 min-w-0 overflow-hidden bg-white">
    <header class="bg-white">
      <TopBar />
      <!-- Injecting computed breadcrumb and title into header components -->
      <BreadCrumb items={navigationData.items} />
      <PageTitle title={navigationData.currentTitle} />
    </header>
        
    <!-- bg-[#fdfdfe] -->
    <main class="flex-1 min-w-0 overflow-y-auto">
      {#if ui.initialLoading}
        <!-- Loading state feedback -->
        <div class="text-sm h-full flex justify-center items-center bg-white">
          <AnimateSpin 
            text="Chargement..."
          />
        </div>
      {:else}
      {@render children?.()}
      {/if}
      
    </main>
  </div>
</div>

