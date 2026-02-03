<script lang="ts">
	import { Rocket, Zap, Shield, Code2, ArrowRight, Github } from '@lucide/svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';

	const features = [
		{
			icon: Zap,
			title: 'Performance optimale',
			description: 'Architecture moderne et optimisée pour des performances exceptionnelles'
		},
		{
			icon: Shield,
			title: 'Sécurité renforcée',
			description: 'Authentification robuste et gestion des permissions intégrée'
		},
		{
			icon: Code2,
			title: 'Code réutilisable',
			description: 'Composants modulaires et API structurée pour tous vos services'
		}
	];
</script>

<div class="container mx-auto px-4 py-16 md:py-24">
	<div class="mx-auto max-w-6xl">
		<div class="mb-16 text-center">
			<div class="mb-6 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2 text-sm font-medium text-primary">
				<Rocket class="size-4" />
				Template de services
			</div>
			
			<h1 class="mb-6 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
				Créez vos services
				<span class="block text-primary">plus rapidement</span>
			</h1>
			
			<p class="mx-auto mb-8 max-w-2xl text-lg text-muted-foreground">
				Un template complet et moderne pour démarrer vos projets avec une architecture solide,
				des composants réutilisables et une API structurée.
			</p>
			
			<div class="flex flex-wrap items-center justify-center gap-4">
				<Button size="lg" class="gap-2">
					Commencer
					<ArrowRight class="size-4" />
				</Button>
			</div>
		</div>

		<div class="mb-16 grid gap-6 md:grid-cols-3">
			{#each features as feature}
				<Card.Root class="border-2 transition-all hover:border-primary/50 hover:shadow-lg">
					<Card.Header>
						<div class="mb-4 inline-flex size-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
							<svelte:component this={feature.icon} class="size-6" />
						</div>
						<Card.Title class="text-xl">{feature.title}</Card.Title>
					</Card.Header>
					<Card.Content>
						<p class="text-muted-foreground">{feature.description}</p>
					</Card.Content>
				</Card.Root>
			{/each}
		</div>

		<div class="rounded-2xl border-2 border-dashed border-gray-300 bg-gray-50/50 p-8 text-center">
			<h2 class="mb-3 text-2xl font-semibold text-gray-900">Prêt à démarrer ?</h2>
			<p class="mb-6 text-muted-foreground">
				Ce template inclut tout ce dont vous avez besoin : authentification, gestion des utilisateurs,
				API REST structurée, et composants UI modernes.
			</p>
			<div class="flex flex-wrap items-center justify-center gap-3">
				<code class="rounded-md bg-gray-900 px-4 py-2 text-sm text-gray-100">
					pnpm install
				</code>
				<code class="rounded-md bg-gray-900 px-4 py-2 text-sm text-gray-100">
					pnpm dev
				</code>
			</div>
		</div>
	</div>
</div>
