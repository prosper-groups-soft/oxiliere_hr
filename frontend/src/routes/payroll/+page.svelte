<script lang="ts">
  import PlaceholderPage from "@/components/layout/elements/PlaceholderPage.svelte";
  import { Wallet } from "@lucide/svelte";

  const features = [
    "Stepper d'exécution de paie (Calcul -> Paiement)",
    "Bulletins de paie interactifs (Smart Payslip)",
    "Gestion des Avances sur salaire",
    "Configuration des taux et règles fiscales",
    "Visualisation de la masse salariale"
  ];
</script>

<PlaceholderPage 
  title="Paie" 
  description="Traitement de la paie et bulletins de salaire."
  icon={Wallet}
  {features} 
/>



