<script lang="ts">
  import PlaceholderPage from "@/components/layout/elements/PlaceholderPage.svelte";
  import { UserPlus } from "@lucide/svelte";

  const features = [
    "Steppers d'enregistrement (Identité, Contrat, Documents)",
    "Checklist de Conformité automatique",
    "Collecte de documents et pièces d'identité",
    "Configuration de l'accès système initial"
  ];
</script>


<PlaceholderPage 
  title="Onboarding" 
  description="Assistant d'accueil pour les nouveaux collaborateurs."
  icon={UserPlus}
  {features} 
/>



