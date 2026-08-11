<script lang="ts">
  import { page } from '$app/state';
  import { settings } from "@/stores/settings.svelte";
  import { ui } from "@/stores/ui.svelte";
  import { buildFullName } from "@/utilities/common/employee.utils";
  import { employeeStore } from '@/features/employees/stores/employees.svelte';
  import { recruitmentStore } from '@/features/recruitment/stores/recruitment.svelte';
  import { PAGE_LABELS } from '@/constants/features/navigation';
  import SideBar from "@/components/layout/shell/SideBar.svelte";
  import TopBar from "@/components/layout/shell/TopBar.svelte";
  import BreadCrumb from "@/components/layout/shell/BreadCrumb.svelte";
  import PageTitle from "@/components/layout/shell/title/PageTitle.svelte";
  import AnimateSpin from '../elements/AnimateSpin.svelte';

  
  let { children } = $props();

  // --- Sidebar management ---
  const setExpanded = (val: boolean) => settings.update('sidebarExpanded', val);

  /**
   * getLabel : Résout le nom à afficher dans le Breadcrumb et le Titre
   */
  function getLabel(segment: string) {
    // 1. Labels statiques
    if (PAGE_LABELS[segment]) return PAGE_LABELS[segment];
    
    const isUuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(segment);

    if (isUuid) {
        // A. Vérifier dans la liste globale (si déjà chargée)
        const empFromList = employeeStore.getById(segment);
        if (empFromList) return empFromList.name;

        // B. NOUVEAU : Vérifier si c'est l'employé actuellement chargé dans 'current'
        // On compare l'ID du segment avec l'ID de l'employé dans le store
        if (employeeStore.current && String(employeeStore.current.id) === segment) {
            return buildFullName(employeeStore.current);
        }

        // C. Vérifier si c'est une campagne de recrutement
        if (recruitmentStore.activeCampaign?.id === segment) {
            return recruitmentStore.activeCampaign.title;
        }

        return "Chargement...";
    }

    // 2. Recherche Candidat
    const candidate = recruitmentStore.candidates.find(c => c.id === segment);
    if (candidate) return `${candidate.firstName} ${candidate.lastName}`;
    

    // 4. Fallback formattage texte
    return segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ');
  }

  /**
   * État dérivé pour la navigation
   * Se recalcule automatiquement dès que 'page.url.pathname' OU 'employeeStore.current' change.
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
  <SideBar 
    expanded={settings.current.sidebarExpanded} 
    {setExpanded} 
  />

  <div class="flex flex-col flex-1 min-w-0 overflow-hidden bg-white">
    <header class="bg-white">
      <TopBar />
      <BreadCrumb items={navigationData.items} />
      <PageTitle title={navigationData.currentTitle || ''} />
    </header>
        
    <main class="flex-1 min-w-0 overflow-y-auto">
      {#if ui.initialLoading}
        <div class="text-sm h-full flex justify-center items-center bg-white">
          <AnimateSpin text="Initialisation" />
        </div>
      {:else}
        {@render children?.()}
      {/if}
    </main>
  </div>
</div>

