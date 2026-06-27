<script lang="ts">
  import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
  import { Badge } from '@/components/ui/badge';
  import { Button } from '@/components/ui/button';
  import * as Tabs from '@/components/ui/tabs';
  import * as Sheet from "@/components/ui/sheet";
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { getInitials } from '@/utilities/common/string';
  import { getAvatarPalette } from '@/utilities/common/func';
  import { page } from '$app/state';
  import { cn } from '@/utilities/common/css'; 
  import { buildFullName } from "@/utilities/common/employee.utils";
  import { goto } from '$app/navigation';
  import { getMediaUrl } from '@/utilities/common/media';
  import AvatarGallery from '@/components/shared/media/AvatarGallery.svelte';
  import EmployeeLifecycleActions from './EmployeeLifecycleActions.svelte';
  import EmployeeProfileForm from '../info/forms/EmployeeProfileForm.svelte';
  import EmployeeContractForm from '../contract/forms/EmployeeContractForm.svelte';
  import {  useUpdateEmployeeMutation, useUpdateContractMutation,
            useUploadProfilePhotoMutation, employeeQueryKeys 
  } from '../../../../queries/employeeQueries';
  import { useQueryClient } from '@tanstack/svelte-query';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { employeeStore } from '@/features/employees/stores/employees.svelte';
  import { getEmployeeStatusDotConfig } from "@/features/employees/constants/employeeStatus";


  let { employee } = $props();

  // --- LOGIQUE DÉRIVÉE ---

  const fullName = $derived(buildFullName(employee));

  /**
   * Récupère la photo de profil directement depuis employee.profile_photo,
   * sinon se rabat sur la photo du compte utilisateur.
   */
  const profilePhoto = $derived(
    getMediaUrl(employee.profile_photo || employee.user?.photo)
  );
  const TABS = $derived([
    { id: 'profile', label: 'Profil', icon: 'user' },
    { id: 'contract', label: 'Contrat', icon: 'briefcase' },
    { id: 'education', label: 'Éducation', count: employee?.educations?.length || 0, icon: 'graduation-cap' },
    { id: 'family', label: 'Famille', icon: 'users' },
    { id: 'account', label: 'Accès', icon: 'shield' },
    { id: 'documents', label: 'Documents', count: employee?.documents?.length || 0, icon: 'files' },
    { id: 'timeline', label: 'Parcours', icon: 'clock' }
  ]);

  const palette = $derived(getAvatarPalette(fullName || ''));

  const status = $derived(employee.current_status?.status);
  const statusDotConfig = $derived(getEmployeeStatusDotConfig(status));

  const activeTabId = $derived.by(() => {
    const path = page.url.pathname.replace(/\/$/, '');
    const segments = path.split('/');
    const lastSegment = segments[segments.length - 1];
    
    if (lastSegment === employee.id) return 'profile';
    
    const currentTab = TABS.find(t => lastSegment === t.id);
    return currentTab ? currentTab.id : 'profile';
  });

  const handleTabChange = (value: string) => {
    const baseUrl = `/employees/${employee.id}`;
    const targetUrl = value === 'profile' ? baseUrl : `${baseUrl}/${value}`;
    goto(targetUrl);
  };

  let tabElements = $state<Record<string, HTMLElement | null>>({
    profile: null,
    contract: null,
    education: null,
    family: null,
    account: null,
    documents: null,
    timeline: null
  });
  let indicatorStyle = $state('');

  $effect(() => {
    const activeEl = tabElements[activeTabId];
    if (activeEl) {
      indicatorStyle = `left: ${activeEl.offsetLeft}px; width: ${activeEl.offsetWidth}px;`;
    }
  });


  // 1. Définir une interface pour la config (pour TS)
  interface EditConfigItem {
    component: any;
    title: string;
    description: string;
    saveLabel: string;
    formId: string;
  }

  // 2. Typer l'objet avec Record pour permettre l'indexation par string
  const EDIT_CONFIG: Record<string, EditConfigItem> = {
    'profile': {
      component: EmployeeProfileForm,
      title: "Modifier le profil",
      description: "Mettez à jour les informations d'identité et de contact.",
      saveLabel: "Enregistrer",
      formId: "profile-form"
    },
    'contract': {
      component: EmployeeContractForm,
      title: "Modifier le contrat",
      description: "Modifiez les termes du contrat de l'employé.",
      saveLabel: "Mettre à jour le contrat",
      formId: "contract-form"
    }
  };

  const queryClient = useQueryClient();
  const updateMutation = useUpdateEmployeeMutation();
  const updateContractMutation = useUpdateContractMutation();
  const uploadPhotoMutation = useUploadProfilePhotoMutation();

  function handlePhotoUpload(file: File) {
    $uploadPhotoMutation.mutate({ employeeId: employee.id, file });
  }

  const isPending = $derived($updateMutation.isPending || $updateContractMutation.isPending);

  // 3. Sécuriser la récupération de la config
  const currentConfig = $derived(
    EDIT_CONFIG[activeTabId] || EDIT_CONFIG['profile']
  );
  
  let isEditDialogOpen = $state(false);
  let formInstance = $state<any>(null);

  async function handleSave(data: any) {
    try {
      console.log(`[EmployeeProfileHeader] Starting save for ${activeTabId}...`, data);
      
      // Call mutations using the $ prefix to access the store value, which contains mutateAsync
      if (activeTabId === 'contract') {
        await $updateContractMutation.mutateAsync({
          employeeId: employee.id.toString(),
          data: data
        });
      } else {
        await $updateMutation.mutateAsync({
          employeeId: employee.id.toString(),
          data: data
        });
      }
      
      console.log('[EmployeeProfileHeader] Save successful, refreshing store...');
      
      // Rafraîchir le store global pour mettre à jour l'UI (Layout, etc.)
      await employeeStore.getFullProfileById(employee.id.toString());
      
      // Invalider les queries pour le cache TanStack
      await queryClient.invalidateQueries({
        queryKey: employeeQueryKeys.detail(employee.id.toString())
      });

      console.log('[EmployeeProfileHeader] Closing editor dialog');
      isEditDialogOpen = false;
    } catch (error) {
      // Error is handled by the mutation's onError (toast notification)
      console.error('[EmployeeProfileHeader] Save failed:', error);
    }
  }

</script>


{#snippet InfoItem(icon: string, label: string)}
  <div class="flex items-center gap-2 text-[0.8rem] font-medium text-slate-500 bg-slate-50 px-3 py-0.5 rounded-full border border-slate-300/50">
    <AppIcon name={icon} size={16} class="text-slate-500" /> 
    {label}
  </div>
{/snippet}


{#snippet TabTrigger(tab: typeof TABS[0])}
  <Tabs.Trigger 
    value={tab.id} 
    bind:ref={tabElements[tab.id]}
    class={cn(
      "relative flex items-center gap-2.5 bg-transparent shadow-none transition-all duration-300",
      "rounded-none border-none px-1 pb-2.5 outline-none focus-visible:ring-0",
      "font-bold group cursor-pointer text-slate-800",
      "data-[state=active]:text-primary data-[state=active]:bg-transparent",
      "data-[state=active]:hover:bg-transparent data-[state=active]:hover:text-primary",
      "data-[state=active]:focus:bg-transparent"
    )}
  >
    <AppIcon name={tab.icon} size={18} class="text-slate-500 group-data-[state=active]:text-primary" />
    <span class="text-[0.879rem] tracking-tight">{tab.label}</span>  

    {#if tab.count}
      <span class="flex h-4.5 w-4.5 items-center justify-center rounded-full bg-slate-100 px-1.5 text-[0.7rem] font-bold group-data-[state=active]:bg-primary group-data-[state=active]:text-white transition-colors">
        {tab.count}
      </span>
    {/if}
  </Tabs.Trigger>
{/snippet}


<div class="bg-white border-b border-slate-100 sticky top-0 z-11 mb-0">
  <div class="container">
    <div class="flex flex-col md:flex-row md:items-end gap-6 py-3.5 px-4 pr-6">
      <div class="relative group">
        <div class="h-17 w-17 rounded-2xl bg-white shadow-none border border-slate-200 overflow-hidden group-hover:shadow-md transition-all duration-300">
          <AvatarGallery 
            name={fullName || ''}
            src={profilePhoto}
            class="h-full w-full rounded-2xl" 
            onUpload={handlePhotoUpload}
          >
            <Avatar class="h-full w-full rounded-2xl">
              <AvatarImage src={profilePhoto} alt={fullName} class="object-cover" />
              <AvatarFallback class={cn("font-bold text-[1.3rem] rounded-2xl", palette.bg, palette.text)}>
                {getInitials(employee.last_name, employee.middle_name, employee.first_name)}
              </AvatarFallback>
            </Avatar>
          </AvatarGallery>
        </div>
        <div class={cn('absolute -bottom-0.5 -right-1 h-3.5 w-3.5 rounded-full border border-white shadow-fine transition-colors duration-300', statusDotConfig.color)} title={statusDotConfig.title}></div>
      </div>

      <div class="flex-1 space-y-1">
        <div>
          <div class="flex items-center gap-3">
            <h2 class="text-[1.05rem] font-bold text-slate-900">{fullName}</h2>
            <Badge variant="outline" class="bg-slate-50 text-slate-500 border-slate-200 font-bold text-[0.65rem] uppercase tracking-widest hidden">
              ID: {employee?.id ? String(employee.id).split('-')[0] : '...'}
            </Badge>
          </div>
          <p class="text-slate-500 text-[0.84rem]">
            {employee.job_title || 'Poste non défini'}
            {#if employee.seniority_level}
              <span class="text-slate-400">•</span> {employee.seniority_level}
            {/if}
          </p>
        </div>
        
        <div class="flex flex-wrap gap-2">
          {@render InfoItem("circle-user", employee.matricule || 'N/A')}
          {@render InfoItem("mail", employee.email)}
        </div>
      </div>

      <div class="flex items-center gap-3 pb-1">
        <Button variant="outline" class="h-7.5" onclick={() => isEditDialogOpen = true}>
          <AppIcon name="edit" size={16} class="text-slate-700" />
          Modifier
        </Button>
        <EmployeeLifecycleActions {employee} />
      </div>
    </div>

    <div class="mt-0.5 px-3.5">
      <Tabs.Root value={activeTabId} onValueChange={handleTabChange} class="w-full">
        <Tabs.List class="relative bg-transparent w-full justify-start rounded-none h-auto p-0 gap-5 border-none">
          {#each TABS as tab}
            {@render TabTrigger(tab)}
          {/each}

          <!-- Sliding Indicator -->
          <div 
            class="absolute bottom-0 h-1 rounded-full bg-primary transition-all duration-300 ease-in-out z-10"
            style={indicatorStyle}
          ></div>
        </Tabs.List>
      </Tabs.Root>
    </div>
  </div>
</div>


<Sheet.Root bind:open={isEditDialogOpen}>
  <Sheet.Content class="sm:max-w-175 bg-white p-0 flex flex-col h-full overflow-hidden">
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <Sheet.Title class="text-[1rem] text-slate-900 truncate font-bold">
        {currentConfig.title}
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar px-3">
      {#if currentConfig.component}
        {@const DynamicForm = currentConfig.component}
        <DynamicForm 
          {employee} 
          onSave={handleSave} 
          bind:this={formInstance}
        />
      {:else}
        <div class="p-8 text-center text-slate-500">
          AppIcon
          Le formulaire pour "{activeTabId}" n'est pas encore disponible.
        </div>
      {/if}
    </div>

    <!-- Footer -->
    <Sheet.Footer class="px-6 py-2.5 border-t bg-slate-50/50 flex flex-col gap-3">
      <div class="flex gap-3 w-full">
        <Sheet.Close class="flex-1">
          <Button onclick={() => isEditDialogOpen = false} variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600 font-medium text-[0.88rem]">
            <AppIcon name="x" size={17} class="text-slate-300" />
            Annuler
          </Button>
        </Sheet.Close>

        <Button 
          type="button" 
          onclick={() => formInstance?.submit()}
          class="flex-1" 
          disabled={isPending}
        >
          {#if isPending}
            <AnimateSpin text="" class="size-3 border-white"/>
          {:else}
            <AppIcon name="check" size={17} class="text-white"/>
          {/if}
          {currentConfig.saveLabel}
        </Button>
      </div>
    </Sheet.Footer>

  </Sheet.Content>
</Sheet.Root>

