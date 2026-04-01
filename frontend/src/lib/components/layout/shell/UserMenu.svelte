<script lang="ts">
  /* --- IMPORTS --- */
  import { goto } from '$app/navigation';
  import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
  import { buttonVariants } from '@/components/ui/button';
  import * as DropdownMenu from '@/components/ui/dropdown-menu';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import AnimateSpin from '../elements/AnimateSpin.svelte';
  
  // Stores and Auth logic
  import { auth } from '@/features/auth/stores/auth.svelte';
  import { notification } from '@/stores/notification.svelte'; 
  
  // Queries and Utils
  import { organizationQueryOptions } from '@/api/queries/organizations';
  import { createQuery } from '@tanstack/svelte-query';
  import { cn } from '@/utilities/common/css';
  import { join_base_url } from '@/utilities/http/http';
  import { get_auth_base_url } from '@/utilities/http/urls';

  /* --- QUERIES --- */
  const queryOrg = createQuery({
    ...organizationQueryOptions.list({
      pageIndex: 0,
      pageSize: 20,
    }),
  });

  /* --- HANDLERS --- */
  
  function handleLogoutRequest() {
    notification.confirm({
      title: 'Déconnexion',
      message: 'Êtes-vous sûr.e de vouloir vous déconnecter de votre compte ?',
      type: 'danger',
      yesText: 'Se déconnecter',
      noText: 'Annuler',
      onYes: async () => {
        try {
          await auth.logout();
          goto('/login'); 
        } catch (error) {
          console.error('Logout failed:', error);
        }
      }
    });
  }

  function handleSwitchToEM() {
    console.log('Switch to EM');
  }

  function goto_my_accounts() {
    const url = join_base_url("/accounts", get_auth_base_url());
    goto(url);
  }

  function goto_home() {
    goto('/');
  }

  function goto_organization(slug: string) {
    goto('/o/' + slug);
  }
</script>


{#snippet renderAvatar(clickable: boolean)}
  <Avatar class={cn(clickable ? 'cursor-pointer hover:opacity-80 transition-opacity' : '')}>
    <AvatarImage src={auth.currentUser?.photo ?? ''} alt="Profil utilisateur" />
    {#if auth.currentUser}
      <AvatarFallback class="bg-slate-100 text-slate-700 font-bold uppercase">
        {(auth.currentUser.first_name?.[0] ?? '') + (auth.currentUser.last_name?.[0] ?? '')}
      </AvatarFallback>
    {:else}
      <AvatarFallback class="bg-slate-50 text-slate-400">Ox</AvatarFallback>
    {/if}
  </Avatar>
{/snippet}


{#snippet AppSelector()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger class={cn(buttonVariants({ variant: 'ghost', size: 'icon' }))}>
      <AppIcon name="grip" size={17} />
    </DropdownMenu.Trigger>
    <DropdownMenu.Content align="end">
      <DropdownMenu.Label class="text-[0.82rem]! font-semibold text-slate-500 px-2 py-1.5 uppercase">Applications</DropdownMenu.Label>
      <DropdownMenu.Group>
        <DropdownMenu.Item class="flex cursor-pointer flex-row gap-3 items-center py-2" onclick={handleSwitchToEM}>
          <span class="flex size-6.5 items-center justify-center rounded-md bg-[#6C6FF7] text-[10px] font-bold text-white shadow-sm">CT</span>
          <span>Comptabilité</span>
        </DropdownMenu.Item>

        <DropdownMenu.Item class="flex cursor-pointer flex-row gap-3 items-center py-2">
          <span class="flex size-6.5 items-center justify-center rounded-md bg-[#52AEA4] text-[10px] font-bold text-white shadow-sm">RH</span>
          <span>Ressources Humaines</span>
        </DropdownMenu.Item>
      </DropdownMenu.Group>
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}


{#snippet UserMenu()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger class="outline-none">
      {@render renderAvatar(true)}
    </DropdownMenu.Trigger>
    <DropdownMenu.Content class="p-1.5" align="end">
      
      <div class="flex items-center gap-3 px-3 py-3 mb-1">
        {@render renderAvatar(false)}
        <div class="flex flex-col min-w-0">
          <span class="truncate text-sm font-bold text-slate-900 leading-none mb-1">
            {auth.currentUser ? `${auth.currentUser.first_name} ${auth.currentUser.last_name}` : 'Utilisateur Anonyme'}
          </span>
          <span class="truncate text-xs text-slate-500 font-medium">
            {auth.currentUser?.email ?? 'Non connecté'}
          </span>
        </div>
      </div>

      <DropdownMenu.Separator />

      <DropdownMenu.Group class="py-1">
        <DropdownMenu.Item class="cursor-pointer py-2 hover:bg-slate-50" onclick={goto_home}>
          <AppIcon name="grid" size={18} class="mr-2.5 text-slate-500" />
          <span>Espace privé</span>
        </DropdownMenu.Item>

        <DropdownMenu.Item class="cursor-pointer py-2 hover:bg-slate-50" onclick={goto_my_accounts}>
          <AppIcon name="settings" size={18} class="mr-2.5 text-slate-500" />
          <span>Mon compte</span>
        </DropdownMenu.Item>
      </DropdownMenu.Group>

      <DropdownMenu.Group class="py-1">
        <DropdownMenu.Sub>
          <DropdownMenu.SubTrigger class="flex cursor-pointer items-center py-2">
            <AppIcon name="business" size={18} class="mr-2.5 text-slate-500" />
            <span class="truncate">
              {auth.currentOrganization?.name ?? 'Mes organisations'}
            </span>
          </DropdownMenu.SubTrigger>
          <DropdownMenu.SubContent class="max-h-64 min-w-60 rounded-xl p-1.5 shadow-xl" align="start" side="left">
            <DropdownMenu.Label class="text-[0.82rem]! font-bold text-slate-400 px-2 py-1.5 uppercase">Changer d'organisation</DropdownMenu.Label>
            
            {#if $queryOrg.isLoading}
              <DropdownMenu.Item class="gap-3 p-2 text-slate-800">
                <AnimateSpin text="Chargement..." />
              </DropdownMenu.Item>
            {:else if $queryOrg.isError}
               <DropdownMenu.Item class="gap-3 p-2 text-red-500">
                <AppIcon name="alert-circle" size={19} class="text-inherit" /> Erreur de chargement
              </DropdownMenu.Item>
            {:else if $queryOrg.isSuccess}
              {#each $queryOrg.data.results as org}
                <DropdownMenu.Item onSelect={() => goto_organization(org.slug)} class="gap-3 p-2 rounded-lg cursor-pointer">
                  <div class="flex size-7 items-center justify-center rounded-md border border-slate-100 bg-slate-50 text-slate-600">
                    <AppIcon name="business" size={18} />
                  </div>
                  <span class="font-medium">{org.name}</span>
                </DropdownMenu.Item>
              {/each}
            {/if}
          </DropdownMenu.SubContent>
        </DropdownMenu.Sub>
      </DropdownMenu.Group>

      <DropdownMenu.Separator />

      <DropdownMenu.Item 
        onclick={handleLogoutRequest} 
        class="cursor-pointer py-2 text-red-600 hover:text-red-700! hover:bg-red-50! rounded-lg group"
      >
        <AppIcon name="logout" size={19} class="mr-2 text-inherit transition-transform group-hover:translate-x-0.5" />
        <span>Se déconnecter</span>
      </DropdownMenu.Item>
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}


<div class="flex shrink-0 items-center gap-2 sm:gap-4 px-2">
  {@render AppSelector()}
  {@render UserMenu()}
</div>

