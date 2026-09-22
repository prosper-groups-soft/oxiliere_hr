<script lang="ts">
  import { hr } from '@/constants/features/navigation';
  import * as Card from "@/components/ui/card";
  import { Button } from "@/components/ui/button";
  import { Users, Briefcase, FileText, TrendingUp } from "@lucide/svelte";
</script>


<div class="space-y-6 space-x-7">
  <header>
    <h1 class="text-xl font-bold tracking-tight">
      Tableau de bord RH
    </h1>
    <p class="text-foreground text-sm">
      Bienvenue dans votre centre de gestion d'entreprise.
    </p>
  </header>

  <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
    <Card.Root>
      <Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
        <Card.Title class="text-sm font-medium">Total Employés</Card.Title>
        <Users class="h-4 w-4 text-muted-foreground" />
      </Card.Header>
      <Card.Content>
        <div class="text-2xl font-bold">1,284</div>
        <p class="text-xs text-muted-foreground">+4 ce mois-ci</p>
      </Card.Content>
    </Card.Root>

    <Card.Root>
      <Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
        <Card.Title class="text-sm font-medium">Recrutements</Card.Title>
        <Briefcase class="h-4 w-4 text-muted-foreground" />
      </Card.Header>
      <Card.Content>
        <div class="text-2xl font-bold">12</div>
        <p class="text-xs text-muted-foreground">Postes ouverts</p>
      </Card.Content>
    </Card.Root>

    <Card.Root>
      <Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
        <Card.Title class="text-sm font-medium">Congés en attente</Card.Title>
        <FileText class="h-4 w-4 text-muted-foreground" />
      </Card.Header>
      <Card.Content>
        <div class="text-2xl font-bold">28</div>
        <p class="text-xs text-amber-500 font-medium">À valider</p>
      </Card.Content>
    </Card.Root>

    <Card.Root>
      <Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
        <Card.Title class="text-sm font-medium">Masse Salariale</Card.Title>
        <TrendingUp class="h-4 w-4 text-muted-foreground" />
      </Card.Header>
      <Card.Content>
        <div class="text-2xl font-bold">425k $</div>
        <p class="text-xs text-muted-foreground">Mois en cours</p>
      </Card.Content>
    </Card.Root>
  </div>

  <div class="flex gap-4">
    <Button href={hr('/employees')}>Accéder à l'annuaire</Button>
    <Button variant="outline" href={hr('/recruitment')}>Gérer les offres</Button>
  </div>
</div>

