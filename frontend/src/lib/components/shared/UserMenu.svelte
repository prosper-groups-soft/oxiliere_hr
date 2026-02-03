<script lang="ts">
	import { goto } from '$app/navigation';
	import { Avatar, AvatarFallback, AvatarImage } from '$lib/components/ui/avatar';
	import { buttonVariants } from '$lib/components/ui/button';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { current_organization_store, current_user_store } from '$lib/stores/auth';
	import { logout } from '$lib/utilities/runtime';
	import { cn } from '$lib/utils';
	import { organizationQueryOptions } from '$lib/api/queries/organizations';
	import type { SessionUser } from '@/types/users';
	import {
		Building2,
		Grip,
		LayoutGrid,
		LogOut,
		RefreshCcw,
		Settings
	} from '@lucide/svelte';
	import { createQuery } from '@tanstack/svelte-query';
	import AlertDialog from './modals/AlertDialog.svelte';
	import { join_base_url } from '@/utilities/http';
	import { get_auth_base_url } from '@/utilities/urls';

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
			<Grip class="size-4" />
		</DropdownMenu.Trigger>
		<DropdownMenu.Content align="end">
			<DropdownMenu.Label>Applications</DropdownMenu.Label>

			<DropdownMenu.Group>
				<DropdownMenu.Item class="flex cursor-pointer flex-row gap-3" onclick={handleSwitchToEM}>
					<span
						class="flex size-6 items-center justify-center rounded-[6px] bg-[#6C6FF7] text-[8px] font-medium text-white"
					>
						CPT
					</span>
					<span>Comptabilité</span>
				</DropdownMenu.Item>

				<DropdownMenu.Item class="flex cursor-pointer flex-row gap-3">
					<span
						class="flex size-6 items-center justify-center rounded-[6px] bg-[#52AEA4] text-[8px] font-medium text-white"
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
				{@render renderAvatar(false)}
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
					<span class="comet-body-s-accented text-secondary-foreground truncate">
						{user.first_name}
						{user.last_name}
					</span>
				{:else}
					<span class="comet-body-s-accented text-secondary-foreground truncate"> Anonyme </span>
				{/if}
			</div>
			<DropdownMenu.Separator />
			<DropdownMenu.Group>
				<DropdownMenu.Item class="cursor-pointer" onclick={goto_home}>
					<LayoutGrid class="mr-2 size-4" />
					<span>Espace Privé</span>
				</DropdownMenu.Item>

				<DropdownMenu.Item class="cursor-pointer" onclick={goto_my_accounts}>
					<Settings class="mr-2 size-4" />
					<span>Mon compte</span>
				</DropdownMenu.Item>
			</DropdownMenu.Group>
			<DropdownMenu.Group>
				<DropdownMenu.Sub>
					<DropdownMenu.SubTrigger class="flex cursor-pointer items-center">
						<Building2 class="mr-2 size-4" />
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
									<RefreshCcw class="size-3.5 shrink-0" />
								</div>
								Chargement....
							</DropdownMenu.Item>
						{:else if $queryOrg.isError}
							<DropdownMenu.Item class="gap-2 p-2">
								<div class="flex size-6 items-center justify-center rounded-md border">
									<RefreshCcw class="size-3.5 shrink-0" />
								</div>
								Erreur de Chargement....
							</DropdownMenu.Item>
						{:else if $queryOrg.isSuccess}
							{#each $queryOrg.data.results as org, index}
								<DropdownMenu.Item onSelect={() => goto_organization(org.slug)} class="gap-2 p-2">
									<div class="flex size-6 items-center justify-center rounded-md border">
										<Building2 class="size-3.5 shrink-0" />
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
				<LogOut class="mr-2 size-4" />
				<span>Se déconnecter</span>
			</DropdownMenu.Item>
		</DropdownMenu.Content>
	</DropdownMenu.Root>
{/snippet}

<div class="flex shrink-0 items-center gap-4">
	{@render AppSelector()}
	{@render UserMenu()}
</div>
