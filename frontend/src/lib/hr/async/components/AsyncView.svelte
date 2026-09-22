<script lang="ts">
  import type { Snippet } from 'svelte';
  import type { ResourceAsync } from '../core/asyncState.svelte.js';
  import LoadingBar from '@/hr/components/layout/elements/LoadingBar.svelte';
  import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';
  import Empty from '@/hr/components/shared/containers/empty/Empty.svelte';
  import { Button } from '@/components/ui/button';
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { getFriendlyErrorMessage } from '@/hr/constants/errors';
  import { ERROR_MESSAGES } from '@/hr/constants/errors';

  let {
    state,
    emptyWhen,
    loadingText = 'Chargement...',
    errorTitle = 'Erreur de Connexion',
    emptyTitle = 'Aucun résultat',
    emptyDescription = 'Aucune donnée à afficher',
    children,
    emptySnippet
  }: {
    state: ResourceAsync<any>;
    emptyWhen?: (data: any) => boolean;
    loadingText?: string;
    errorTitle?: string;
    emptyTitle?: string;
    emptyDescription?: string;
    children: Snippet<[any]>;
    emptySnippet?: Snippet;
  } = $props();

  let isEmpty = $derived(state.data != null && emptyWhen ? emptyWhen(state.data) : false);
</script>

<LoadingBar loading={state.isFetching} />

{#if state.isLoading}
  <div class="flex justify-center items-center h-full">
    <AnimateSpin text={loadingText} />
  </div>
{:else if state.error && !state.data}
  <div class="flex justify-center items-center h-full">
    <Empty icon="alert-circle" title={errorTitle} description={getFriendlyErrorMessage(state.error) || ERROR_MESSAGES.NETWORK.UNKNOWN} iconClass="text-red-400" iconContainerClass="bg-red-50/30" iconSize={28} iconStrokeWidth={1.3}>
      <Button onclick={() => (state as any).refetch?.()} variant="outline" class="h-7 mt-2 rounded-lg"><AppIcon name="refresh-cw" /> Réessayer</Button>
    </Empty>
  </div>
{:else if isEmpty}
  <div class="flex justify-center items-center h-full">
    {#if emptySnippet}{@render emptySnippet()}{:else}<Empty icon="search" title={emptyTitle} description={emptyDescription} />{/if}
  </div>
{:else if state.data}
  {@render children(state.data)}
{/if}
