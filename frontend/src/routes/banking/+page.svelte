<script lang="ts">
  import PlaceholderPage from "@/components/layout/elements/PlaceholderPage.svelte";
  import { Landmark } from "@lucide/svelte";

  const features = [
    "Vault des coordonnées bancaires employés",
    "Répertoire des institutions financières",
    "Centre de vérification et conformité",
    "Génération des fichiers de virement SEPA/SWIFT",
    "Rapports de paiement"
  ];
</script>


<PlaceholderPage 
  title="Comptes Bancaires" 
  description="Gestion des coordonnées bancaires et paiements."
  icon={Landmark}
  {features} 
/>




