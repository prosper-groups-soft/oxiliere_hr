<script lang="ts">
  import * as Card from "@/components/ui/card";
  import { Button } from "@/components/ui/button";
  import { Badge } from "@/components/ui/badge";
  import { ArrowLeft } from "@lucide/svelte";
  import type { Component } from "svelte";

  interface Props {
    title: string;
    description: string;
    features?: string[];
    icon: Component<any>; 
  }

  let {
    title,
    description,
    features = [],
    icon: Icon 
  }: Props = $props();
</script>


<div class="space-y-6">
  <header class="flex items-start justify-between">
    <div class="space-y-1">
      <div class="flex items-center gap-3">
        <div class="p-2 rounded-lg bg-primary/10">
          <Icon class="size-6 text-primary" />
        </div>
        <div>
          <h1 class="text-2xl font-bold tracking-tight">{title}</h1>
          <p class="text-sm text-muted-foreground">{description}</p>
        </div>
      </div>
    </div>
    <Badge variant="outline" class="bg-amber-50 text-amber-700 border-amber-200">
      En développement
    </Badge>
  </header>

  <Card.Root>
    <Card.Header>
      <Card.Title>Fonctionnalités Prévues</Card.Title>
      <Card.Description>
        Ce module est actuellement en cours de développement.
      </Card.Description>
    </Card.Header>
    <Card.Content>
      {#if features.length > 0}
        <ul class="space-y-2">
          {#each features as feature}
            <li class="flex items-start gap-2">
              <span class="text-primary mt-1">•</span>
              <span class="text-sm">{feature}</span>
            </li>
          {/each}
        </ul>
      {:else}
        <p class="text-sm text-muted-foreground">Les fonctionnalités seront définies prochainement.</p>
      {/if}
    </Card.Content>
    <Card.Footer>
      <Button variant="outline" href="/" class="gap-2">
        <ArrowLeft class="size-4" />
        Retour au tableau de bord
      </Button>
    </Card.Footer>
  </Card.Root>
</div>

