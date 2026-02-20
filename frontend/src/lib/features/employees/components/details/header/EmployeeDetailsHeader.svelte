<script lang="ts">
  import { crossfade } from 'svelte/transition';
  import { cubicInOut } from 'svelte/easing';
  import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
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
  import EmployeeActionSheet from '../ui/EmployeeActionSheet.svelte';
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

  const activeTabId = $derived(() => {
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

  const [send, receive] = crossfade({
    duration: 300,
    easing: cubicInOut
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
    class={cn(
      // Base
      "relative flex items-center gap-2.5 bg-transparent shadow-none transition-all duration-300",
      "rounded-none border-none px-2 pb-2 outline-none focus-visible:ring-0",
      "font-bold group cursor-pointer text-slate-700",
      
      "data-[state=active]:text-primary data-[state=active]:bg-transparent",
      "data-[state=active]:hover:bg-transparent data-[state=active]:hover:text-primary",
      "data-[state=active]:focus:bg-transparent"
    )}
  >
    <AppIcon name={tab.icon} size={18} class="group-data-[state=active]:text-primary" />
    <span class="text-[0.867rem] tracking-tight">{tab.label}</span>  

    {#if tab.count}
      <span class="flex h-5 min-w-5 items-center justify-center rounded-full bg-slate-100 px-1.5 text-[0.7rem] font-black group-data-[state=active]:bg-primary group-data-[state=active]:text-white transition-colors">
        {tab.count}
      </span>
    {/if}

    {#if activeTabId() === tab.id}
      <div 
        in:receive={{ key: 'active-bar' }}
        out:send={{ key: 'active-bar' }}
        class="absolute bottom-0 left-0 right-0 h-1 bg-primary rounded z-10"
      ></div>
    {/if}
  </Tabs.Trigger>
{/snippet}


<div class="bg-white border-b border-slate-100 sticky top-0">
  <div class="container">
    <div class="flex flex-col md:flex-row md:items-end gap-6 pb-3.5">
      <div class="relative group">
        <div class="h-21.5 w-21.5 rounded-3xl bg-white p-1 shadow-soft border border-slate-100 overflow-hidden group-hover:shadow-md transition-all duration-300">
          
          <AvatarGallery 
            name={employee.name}
            src={employee.avatarUrl}
            class="h-full w-full rounded-[1.25rem]" 
            onUpload={(file) => console.log("Upload:", file)}
          >
            <Avatar class="h-full w-full rounded-[1.2rem]">
              <AvatarImage src={employee.avatarUrl} alt={employee.name} class="object-cover" />
              <AvatarFallback class={cn("font-black text-[1.5rem] rounded-[1.2rem]", palette.bg, palette.text)}>
                {getInitials(...employee.name.split(' '))}
              </AvatarFallback>
            </Avatar>
          </AvatarGallery>
          
        </div>
        <div class="absolute -bottom-2 -right-2 bg-emerald-500 h-6 w-6 rounded-full border-4 border-white shadow-sm" title="Employé actif"></div>
      </div>

      <div class="flex-1 space-y-3">
        <div class="space-y-1">
          <div class="flex items-center gap-3">
            <h1 class="text-lg font-black tracking-tight text-slate-900">{employee.name}</h1>
            <Badge variant="outline" class="bg-slate-50 text-slate-500 border-slate-200 font-bold text-[0.65rem] uppercase tracking-widest">
              ID: {employee?.id ? String(employee.id).split('-')[0] : '...'}
            </Badge>
          </div>
          <p class="text-slate-500 text-[0.875rem]">Collaborateur Oxiliere</p>
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
          class="shadow-soft border-slate-200 font-medium text-[0.85rem] h-7.5 px-3 hover:bg-slate-50"
        >
          <AppIcon name="edit-3" size={18} class="text-slate-600" />
          Modifier
        </Button>
        <EmployeeLifecycleActions {employee} />
      </div>
    </div>

    <div class="mt-2">
      <Tabs.Root value={activeTabId()} onValueChange={handleTabChange} class="w-full">
        <Tabs.List class="relative bg-transparent w-full justify-start rounded-none h-auto p-0 gap-8 border-none">
          {#each TABS as tab}
            {@render TabTrigger(tab)}
          {/each}
        </Tabs.List>
      </Tabs.Root>
    </div>
  </div>
</div>


<EmployeeActionSheet bind:open={isEditSheetOpen} title="Édition du profil">
  <EmployeeProfileForm {employee} onSave={handleUpdateProfile} />
  {#snippet footer()}
    <Button type="submit" form="profile-form" class="flex-1 bg-primary! shadow-soft">
      Mettre à jour le profil
    </Button>
  {/snippet}
</EmployeeActionSheet>

