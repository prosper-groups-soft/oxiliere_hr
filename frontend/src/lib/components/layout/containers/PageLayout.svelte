<script lang="ts">
  import { page } from '$app/state';
  import { settings } from "@/stores/settings.svelte";
  import { ui } from "@/stores/ui.svelte";
  import { buildFullName } from "@/utilities/common/employee.utils";
  import { employeeStore } from '@/hr/employees/stores/employees.svelte';
  import { recruitmentStore } from '@/hr/recruitment/stores/recruitment.svelte';
  import { PAGE_LABELS } from '@/constants/features/navigation';
  import SideBar from "@/components/layout/shell/SideBar.svelte";
  import TopBar from "@/components/layout/shell/TopBar.svelte";
  import BreadCrumb from "@/components/layout/shell/BreadCrumb.svelte";
  import PageTitle from "@/components/layout/shell/title/PageTitle.svelte";
  import AnimateSpin from '../elements/AnimateSpin.svelte';

  
  let { children } = $props();

  // --- Regex patterns d'analyse de route ---
  /** Découpage robuste de l'URL (ignore les slashes multiples, superflus et trailing) */
  const PATH_SEGMENTS_REGEX = /[^/]+/g;
  /** Format UUID standard (v4/v7) */
  const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  /** Identifiants numériques purs (ex: /employees/42) */
  const NUMERIC_ID_REGEX = /^\d+$/;

  // --- Sidebar management ---
  const setExpanded = (val: boolean) => settings.update('sidebarExpanded', val);

  /**
   * Formatage texte propre depuis un slug (ex: "payroll-settings" -> "Payroll Settings")
   */
  function formatSlugLabel(slug: string): string {
    return slug
      .replace(/[-_]+/g, ' ')
      .replace(/\b\w/g, (char) => char.toUpperCase());
  }

  /**
   * getLabel : Résout le nom à afficher dans le Breadcrumb et le Titre
   */
  function getLabel(segment: string): string {
    // 1. Dictionnaire de labels statiques
    if (PAGE_LABELS[segment]) return PAGE_LABELS[segment];
    
    // 2. Détection des identifiants (UUID ou numérique)
    if (UUID_REGEX.test(segment) || NUMERIC_ID_REGEX.test(segment)) {
        // A. Vérifier dans la liste globale (si déjà chargée)
        const empFromList = employeeStore.getById(segment);
        if (empFromList) return empFromList.name;

        // B. Vérifier si c'est l'employé actuellement chargé dans 'current'
        if (employeeStore.current && String(employeeStore.current.id) === segment) {
            return buildFullName(employeeStore.current) || "Employé";
        }

        // C. Vérifier si c'est une campagne de recrutement
        if (recruitmentStore.activeCampaign?.id === segment) {
            return recruitmentStore.activeCampaign.title;
        }

        return "Chargement...";
    }

    // 3. Recherche Candidat
    const candidate = recruitmentStore.candidates.find(c => c.id === segment);
    if (candidate) return `${candidate.firstName} ${candidate.lastName}`;
    
    // 4. Fallback : Titrage propre via Regex
    return formatSlugLabel(segment);
  }

  /**
   * État dérivé pour la navigation
   * Se recalcule automatiquement dès que 'page.url.pathname' OU 'employeeStore.current' change.
   */
  const navigationData = $derived.by(() => {
    const segments = page.url.pathname.match(PATH_SEGMENTS_REGEX) || [];
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

