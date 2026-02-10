<script lang="ts">
  import PlaceholderPage from "@/components/shared/layout/elements/PlaceholderPage.svelte";
  import { Calendar } from "@lucide/svelte";

  const features = [
    "Timeline Master (Vue Année et Mois)",
    "Gestion des Jours Fériés et Fermetures",
    "Simulateur d'impact sur la paie",
    "Détection de conflits d'événements",
    "Import automatique des jours fériés par pays"
  ];
</script>


<PlaceholderPage 
  title="Calendrier" 
  description="Gestion des événements et jours non travaillés."
  icon={Calendar}
  {features} 
/>



