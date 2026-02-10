<script lang="ts">
  import PlaceholderPage from "@/components/layout/elements/PlaceholderPage.svelte";
  import { Settings } from "@lucide/svelte";

  const features = [
    "Configuration générale de l'application",
    "Gestion des utilisateurs et permissions (RBAC)",
    "Paramètres de notifications et alertes",
    "Intégrations et API Keys",
    "Préférences régionales et devises"
  ];
</script>


<PlaceholderPage 
  title="Paramètres" 
  description="Configuration globale du système et des accès."
  icon={Settings}
  {features} 
/>




