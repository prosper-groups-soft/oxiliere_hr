<script lang="ts">
  import PlaceholderPage from "@/components/layout/elements/PlaceholderPage.svelte";
  import { Network } from "@lucide/svelte";

  const features = [
    "Organigramme Interactif (Vue Arborescente, Zoomable)",
    "Référentiel des Carrières (Niveaux, Exigences)",
    "Gestion des Transitions (Promotions, Mobilité)",
    "Matrice de Compétences et Certifications",
    "Suivi des Postes Vacants (Vacancy Tracker)"
  ];
</script>

<PlaceholderPage 
  title="Postes & Organisation" 
  description="Structure hiérarchique et gestion des carrières."
  icon={Network}
  {features} 
/>



