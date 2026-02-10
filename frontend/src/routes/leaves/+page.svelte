<script lang="ts">
  import PlaceholderPage from "@/components/layout/elements/PlaceholderPage.svelte";
  import { CalendarDays } from "@lucide/svelte";

  const features = [
    "Compteur de solde personnel (Balance Wallet)",
    "File d'attente d'approbation manager",
    "Calendrier d'équipe (Team Planner)",
    "Détection automatique de conflits",
    "Moteur de règles d'acquisition de congés"
  ];
</script>

<PlaceholderPage 
  title="Congés" 
  description="Gestion des absences et demandes de congés."
  icon={CalendarDays}
  {features} 
/>



