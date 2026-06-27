<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { taxSettingsStore } from "../../../stores/taxSettingsStore.svelte";

  const config = $derived(taxSettingsStore.config);

  // Calculate total CNSS rate
  const cnssTotalRate = $derived(
    config.cnss.employerRate + config.cnss.employeeRate
  );

  // Get first INPP rate (or 0 if empty)
  const inppRate = $derived(
    config.inpp.length > 0 ? config.inpp[0].rate : 0
  );
</script>


<div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
  <div class="flex items-start gap-4">
    <div class="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600 shrink-0">
      <AppIcon name="office" size={24} />
    </div>
    <div class="flex-1">
      <div class="flex items-center justify-between mb-1">
        <h5 class="font-medium text-slate-900 text-[0.94rem]">Cotisations sociales</h5>
      </div>
      <p class="text-[0.875rem] text-slate-500 mb-4">
        Taux de cotisation employeur et employé (CNSS, INPP, ONEM)
      </p>

      <div class="grid grid-cols-3 gap-4">
        <!-- CNSS -->
        <div class="p-3 bg-slate-50 rounded-lg">
          <div class="flex items-center justify-between mb-2">
            <span class="text-[0.88rem] font-medium text-slate-800">CNSS</span>
            <span class="text-[0.875rem] text-blue-600 font-medium">{(cnssTotalRate * 100).toFixed(1)}%</span>
          </div>
          <p class="text-[0.875rem] text-slate-500">
            Employeur: {(config.cnss.employerRate * 100).toFixed(1)}% · Employé: {(config.cnss.employeeRate * 100).toFixed(1)}%
          </p>
          {#if config.cnss.salaryCap}
            <p class="text-[0.875rem] text-slate-400 mt-1">
              Plafond: {taxSettingsStore.getDisplayValue(config.cnss.salaryCap).toFixed(0)} {config.currency}
            </p>
          {/if}
        </div>

        <!-- INPP -->
        <div class="p-3 bg-slate-50 rounded-lg">
          <div class="flex items-center justify-between mb-2">
            <span class="text-[0.88rem] font-medium text-slate-800">INPP</span>
            <span class="text-[0.875rem] text-blue-600 font-medium">{(inppRate * 100).toFixed(1)}%</span>
          </div>
          <p class="text-[0.875rem] text-slate-500">Institut National de Préparation Professionnelle</p>
        </div>

        <!-- ONEM -->
        <div class="p-3 bg-slate-50 rounded-lg">
          <div class="flex items-center justify-between mb-2">
            <span class="text-[0.88rem] font-medium text-slate-800">ONEM</span>
            <span class="text-[0.875rem] text-blue-600 font-medium">{(config.onem.rate * 100).toFixed(1)}%</span>
          </div>
          <p class="text-[0.875rem] text-slate-500">Office National de l'Emploi</p>
        </div>
      </div>
    </div>
  </div>
</div>

