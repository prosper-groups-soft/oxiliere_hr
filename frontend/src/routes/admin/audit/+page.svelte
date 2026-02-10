<script lang="ts">
  import PlaceholderPage from "@/components/layout/elements/PlaceholderPage.svelte";
  import { History } from "@lucide/svelte";

  const features = [
    "Journal d'activité système (System Logs)",
    "Traçabilité des actions utilisateurs",
    "Historique des modifications de données",
    "Filtres par utilisateur, date et type d'action",
    "Export des logs pour conformité"
  ];
</script>


<PlaceholderPage 
  title="Audit" 
  description="Traçabilité et historique des activités système."
  icon={History}
  {features} 
/>




