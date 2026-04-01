<script lang="ts">
  import { 
    Avatar, 
    AvatarImage, 
    AvatarFallback 
  } from '@/components/ui/avatar';
  import { Badge } from '@/components/ui/badge';
  import { Button } from '@/components/ui/button';
  import * as Tabs from '@/components/ui/tabs';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { getInitials } from '@/utilities/common/string';
  import { getAvatarPalette } from '@/utilities/common/func';
  import { page } from '$app/state';
  import { cn } from '@/utilities/common/css'; 
  import { goto } from '$app/navigation';
  import AvatarGallery from '@/components/shared/media/AvatarGallery.svelte';
  import EmployeeLifecycleActions from './EmployeeLifecycleActions.svelte';
  import EmployeeActionSheet from '../sheets/EmployeeActionSheet.svelte';
  import EmployeeProfileForm from '../info/forms/EmployeeProfileForm.svelte';

  let { employee } = $props();
  let isEditSheetOpen = $state(false);

  function handleUpdateProfile(data: any) {
    isEditSheetOpen = false;
  }
  
  const TABS = [
    { id: 'profile', label: 'Infos Personnelles', icon: 'user' },
    { id: 'vault', label: 'Documents', count: 4, icon: 'files' },
    { id: 'family', label: 'Famille', icon: 'users' }
  ];

  const palette = $derived(getAvatarPalette(employee?.name || ''));

  /**
   * FIX: Changed from a function returning a string to a direct reactive value.
   * This prevents the infinite update loop by providing a stable primitive.
   */
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

  // --- Sliding Indicator Logic ---
  let tabElements = $state<Record<string, HTMLElement | null>>({
    profile: null,
    vault: null,
    family: null
  });
  let indicatorStyle = $state('');

  $effect(() => {
    const activeEl = tabElements[activeTabId];
    if (activeEl) {
      indicatorStyle = `left: ${activeEl.offsetLeft}px; width: ${activeEl.offsetWidth}px;`;
    }
  });
  
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
      // Base
      "relative flex items-center gap-2.5 bg-transparent shadow-none transition-all duration-300",
      "rounded-none border-none px-1 pb-2.5 outline-none focus-visible:ring-0",
      "font-bold group cursor-pointer text-slate-700",
      
      "data-[state=active]:text-primary data-[state=active]:bg-transparent",
      "data-[state=active]:hover:bg-transparent data-[state=active]:hover:text-primary",
      "data-[state=active]:focus:bg-transparent"
    )}
  >
    <AppIcon name={tab.icon} size={18} class="group-data-[state=active]:text-primary" />
    <span class="text-[0.879rem] tracking-tight">{tab.label}</span>  

    {#if tab.count}
      <span class="flex h-5 min-w-5 items-center justify-center rounded-full bg-slate-100 px-1.5 text-[0.7rem] font-black group-data-[state=active]:bg-primary group-data-[state=active]:text-white transition-colors">
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
            name={employee.name}
            src={employee.avatarUrl}
            class="h-full w-full rounded-2xl" 
            onUpload={(file) => console.log("Upload:", file)}
          >
            <Avatar class="h-full w-full rounded-2xl">
              <AvatarImage src={employee.avatarUrl} alt={employee.name} class="object-cover" />
              <AvatarFallback class={cn("font-bold text-[1.3rem] rounded-2xl", palette.bg, palette.text)}>
                {getInitials(...employee.name.split(' '))}
              </AvatarFallback>
            </Avatar>
          </AvatarGallery>
          
        </div>
        <div class="absolute -bottom-0.5 -right-1 bg-emerald-500 h-3.5 w-3.5 rounded-full shadow-fine" title="Employé actif"></div>
      </div>

      <div class="flex-1 space-y-1">
        <div>
          <div class="flex items-center gap-3">
            <h2 class="text-[1.05rem] font-bold text-slate-900">{employee.name}</h2>
            <Badge variant="outline" class="bg-slate-50 text-slate-500 border-slate-200 font-bold text-[0.65rem] uppercase tracking-widest">
              ID: {employee?.id ? String(employee.id).split('-')[0] : '...'}
            </Badge>
          </div>
          <p class="text-slate-500 text-[0.84rem]">Collaborateur Oxiliere</p>
        </div>
        
        <div class="flex flex-wrap gap-2">
          {@render InfoItem("circle-user", employee.role || 'Consultant')}
          {@render InfoItem("office", employee.department)}
        </div>
      </div>

      <div class="flex items-center gap-3 pb-1">
        <Button 
          onclick={() => isEditSheetOpen = true} 
          variant="outline" 
          size="sm" 
          class="shadow-fine rounded-lg border-slate-200 text-[0.85rem] h-7.5 px-3 hover:bg-slate-50"
        >
          <AppIcon name="edit-3" size={16} class="text-slate-600" />
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


<EmployeeActionSheet bind:open={isEditSheetOpen} title="Édition du profil">
  <EmployeeProfileForm {employee} onSave={handleUpdateProfile} />
  {#snippet footer()}
    <Button type="submit" form="profile-form" class="flex-1 bg-primary! shadow-fine h-9">
      <AppIcon name="check" size={16} />
      Mettre à jour le profil
    </Button>
  {/snippet}
</EmployeeActionSheet>

