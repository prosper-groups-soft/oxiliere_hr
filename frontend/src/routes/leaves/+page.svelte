<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
  import { monQueryOptions } from '$lib/api/queries/mon-query';

  // Use the configuration defined
  const query = createQuery(monQueryOptions.list());
</script>


<div class="p-8">
  <h1 class="text-2xl font-bold">Liste des Items</h1>

  {#if $query.isLoading}
    <p>Chargement des données depuis l'API...</p>
  {:else if $query.isError}
    <p class="text-red-500">Erreur : {$query.error.message}</p>
  {:else}
    <ul>
      {#each $query.data as item}
        <li>{item.name || 'Item sans nom'}</li>
      {/each}
    </ul>
  {/if}
</div>

