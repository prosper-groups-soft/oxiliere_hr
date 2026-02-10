<script lang="ts">
  import PlaceholderPage from "@/components/layout/elements/PlaceholderPage.svelte";
  import { Clock } from "@lucide/svelte";

  const features = [
    "Dashboard Opérationnel (Indicateurs temps réel)",
    "Registre Journalier (Grille haute performance)",
    "Timeline journalière visuelle par employé",
    "Configuration des Cycles et Rotations",
    "Command Palette pour pointage rapide"
  ];
</script>


<PlaceholderPage 
  title="Présences" 
  description="Gestion du temps et suivi des présences."
  icon={Clock}
  {features} 
/>




