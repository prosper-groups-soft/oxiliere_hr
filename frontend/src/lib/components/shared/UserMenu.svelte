<script lang="ts">
	import { goto } from '$app/navigation';
	import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
	import { buttonVariants } from '@/components/ui/button';
	import * as DropdownMenu from '@/components/ui/dropdown-menu';
	import { 
    current_organization_store, 
    current_user_store 
  } from '@/stores/auth';
	import { logout } from '@/utilities/app/runtime';
	import { cn } from '@/utilities/common/css';
	import { organizationQueryOptions } from '@/api/queries/organizations';
	import type { SessionUser } from '@/types/users';
	import { createQuery } from '@tanstack/svelte-query';
	import AlertDialog from './modals/AlertDialog.svelte';
	import AppIcon from '@/components/layout/elements/AppIcon.svelte';
	import { join_base_url } from '@/utilities/http/http';
	import { get_auth_base_url } from '@/utilities/http/urls';

	const queryOrg = createQuery(
		{
		...organizationQueryOptions.list({
			pageIndex: 0,
			pageSize: 20,
		}),
	});

	const handleSwitchToEM = () => {
		console.log('Switch to EM');
	};

	let user: SessionUser | null = $state(null);
	let OpenLogout = $state(false);

	$effect(() => {
		const unsub_user = current_user_store.subscribe((_user) => {
			user = _user;
		});

		return () => {
			unsub_user();
		};
	});

	function openLogout() {
		OpenLogout = true;
	}

	function goto_my_accounts() {
		const url = join_base_url(
			"/accounts",
			get_auth_base_url()
		)
		goto(url);
	}

	function goto_home() {
		goto('/');
	}

	function goto_organization(slug: string) {
		goto('/o/' + slug);
	}
</script>


<AlertDialog
	bind:isOpen={OpenLogout}
	onYes={logout}
	title="Déconnexion"
	type="danger"
	message="Vous etes sûr.e de vouloir vous déconnecter ?"
></AlertDialog>


{#snippet renderAvatar(clickable: boolean)}
	<Avatar class={cn(clickable ? 'cursor-pointer' : '')}>
		<AvatarImage src={user?.photo ?? ''} />
		{#if user}
			<AvatarFallback>{user.first_name[0] + user.last_name[0]}</AvatarFallback>
		{:else}
			<AvatarFallback>Ox</AvatarFallback>
		{/if}
	</Avatar>
{/snippet}


{#snippet AppSelector()}
	<DropdownMenu.Root>
		<DropdownMenu.Trigger class={cn(buttonVariants({ variant: 'ghost', size: 'icon' }))}>
			<AppIcon name="grip" size={16} />
		</DropdownMenu.Trigger>
		<DropdownMenu.Content align="end">
			<DropdownMenu.Label>Applications</DropdownMenu.Label>

			<DropdownMenu.Group>
				<DropdownMenu.Item class="flex cursor-pointer flex-row gap-3" onclick={handleSwitchToEM}>
					<span
						class="flex size-6 items-center justify-center rounded-md bg-[#6C6FF7] text-[8px] font-medium text-white"
					>
						CPT
					</span>
					<span>Comptabilité</span>
				</DropdownMenu.Item>

				<DropdownMenu.Item class="flex cursor-pointer flex-row gap-3">
					<span
						class="flex size-6 items-center justify-center rounded-md bg-[#52AEA4] text-[8px] font-medium text-white"
					>
						RH
					</span>

					<span>Ressources Humaines</span>
				</DropdownMenu.Item>
			</DropdownMenu.Group>
		</DropdownMenu.Content>
	</DropdownMenu.Root>
{/snippet}


{#snippet UserMenu()}
	<DropdownMenu.Root>
		<DropdownMenu.Trigger>
			{#if user}
				{@render renderAvatar(true)}
			{:else}
				{@render renderAvatar(true)}
			{/if}
		</DropdownMenu.Trigger>
		<DropdownMenu.Content class="w-60" align="end">
			<div class="flex items-center gap-2 px-4 py-2">
				{#if user}
					{@render renderAvatar(true)}
				{:else}
					{@render renderAvatar(false)}
				{/if}
				{#if user}
					<span class="comet-body-s-accented text-secondary-foreground truncate text-[0.875rem]">
						{user.first_name}
						{user.last_name}
					</span>
				{:else}
					<span class="comet-body-s-accented text-secondary-foreground truncate text-[0.875rem]"> Anonyme </span>
				{/if}
			</div>
			<DropdownMenu.Separator />
			<DropdownMenu.Group>
				<DropdownMenu.Item class="cursor-pointer" onclick={goto_home}>
					<AppIcon name="grid" size={20} class="mr-2" />
					<span>Espace Privé</span>
				</DropdownMenu.Item>

				<DropdownMenu.Item class="cursor-pointer" onclick={goto_my_accounts}>
					<AppIcon name="settings" size={20} class="mr-2" />
					<span>Mon compte</span>
				</DropdownMenu.Item>
			</DropdownMenu.Group>
			<DropdownMenu.Group>
				<DropdownMenu.Sub>
					<DropdownMenu.SubTrigger class="flex cursor-pointer items-center">
						<AppIcon name="business" size={20} class="mr-2" />
						<span class="comet-body-s truncate">
							{#if $current_organization_store}
								{$current_organization_store.name}
							{:else}
								Mes Organisations
							{/if}
						</span>
					</DropdownMenu.SubTrigger>

					<DropdownMenu.SubContent
						class="w-(--bits-dropdown-menu-anchor-width) max-h-60 min-w-56 rounded-lg"
						align="start"
						side={'left'}
						sideOffset={4}
					>
						<DropdownMenu.Label class="text-muted-foreground text-xs"
							>Organisations</DropdownMenu.Label
						>
						{#if $queryOrg.isLoading}
							<DropdownMenu.Item class="gap-2 p-2">
								<div class="flex size-6 items-center justify-center rounded-md border">
									<AppIcon name="refresh" size={20} class="shrink-0 animate-spin" />
								</div>
								Chargement....
							</DropdownMenu.Item>
						{:else if $queryOrg.isError}
							<DropdownMenu.Item class="gap-2 p-2">
								<div class="flex size-6 items-center justify-center rounded-md border">
									<AppIcon name="refresh" size={20} class="shrink-0" />
								</div>
								Erreur de Chargement....
							</DropdownMenu.Item>
						{:else if $queryOrg.isSuccess}
							{#each $queryOrg.data.results as org, index}
								<DropdownMenu.Item onSelect={() => goto_organization(org.slug)} class="gap-2 p-2">
									<div class="flex size-6 items-center justify-center rounded-md border">
										<AppIcon name="business" size={20} class="shrink-0" />
									</div>
									{org.name}
								</DropdownMenu.Item>
							{/each}
						{/if}
					</DropdownMenu.SubContent>
				</DropdownMenu.Sub>
			</DropdownMenu.Group>

			<DropdownMenu.Separator />

			<DropdownMenu.Item onclick={openLogout} class="cursor-pointer">
				<AppIcon name="logout" size={20} class="mr-2" />
				<span>Se déconnecter</span>
			</DropdownMenu.Item>
		</DropdownMenu.Content>
	</DropdownMenu.Root>
{/snippet}


<div class="flex shrink-0 items-center gap-4">
	{@render AppSelector()}
	{@render UserMenu()}
</div>

