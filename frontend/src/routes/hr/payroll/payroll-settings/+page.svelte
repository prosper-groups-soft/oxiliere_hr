<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import EmptyState from '@/components/shared/containers/empty/EmptyState.svelte';
  import { ui } from '@/stores/ui.svelte';
  import { payrollStore } from '@/hr/payroll/stores/payroll.svelte';
  import { payrollSettingsStore } from '@/hr/payroll/stores/configuration/payrollSettingsStore.svelte';

  import GeneralSettings from '@/hr/payroll/components/settings/tabs/GeneralSettings.svelte';
  import LegalSettings from '@/hr/payroll/components/settings/tabs/LegalSettings.svelte';
  import FiscalSettings from '@/hr/payroll/components/settings/tabs/FiscalSettings.svelte';
  import CatalogSettings from '@/hr/payroll/components/settings/tabs/CatalogSettings.svelte';
  import SettingsTabs from '@/hr/payroll/components/settings/SettingsTabs.svelte';
  import SettingsFooter from '@/hr/payroll/components/settings/SettingsFooter.svelte';


  $effect(() => {
    ui.addActions('payroll-settings', ActionsSnippet);
    return () => ui.removeActions('payroll-settings');
  });

  $effect(() => {
    payrollSettingsStore.load();
  });
</script>


{#snippet ActionsSnippet()}
  <!-- Actions go here -->
{/snippet}


<svelte:head>
  <title>Oxiliere HR - Configuration de la paie</title>
</svelte:head>


<div class="flex h-full flex-col overflow-hidden min-h-0">
  {#if payrollSettingsStore.viewState === 'loading'}
    <EmptyState variant="loading" class="h-full" title="Chargement des paramétrages" />

  {:else if payrollSettingsStore.viewState === 'error' || payrollSettingsStore.viewState === 'offline'}
    <EmptyState
      variant={payrollSettingsStore.viewState === 'offline' ? 'offline' : 'error'}
      class="h-full"
      title="Erreur lors du chargement des paramétrages"
      onRetry={() => payrollSettingsStore.load()}
    />

  {:else}
    <!-- Tabs — hors du flux de scroll, collés -->
    <div class="shrink-0 sticky top-0 z-10 bg-white/95 backdrop-blur supports-backdrop-filter:bg-white/80 border-b border-slate-100">
      <div class="max-w-4xl mx-auto px-6 pt-3">
        <SettingsTabs
          tabs={payrollSettingsStore.tabs}
          activeTab={payrollSettingsStore.activeTab}
          onTabChange={(value) => payrollSettingsStore.setTab(value)}
        />
      </div>
    </div>

    <main class="flex-1 overflow-y-auto min-h-0">
      <div class="max-w-4xl mx-auto px-6 py-3">

        {#if payrollSettingsStore.activeTab === 'general'}
          <GeneralSettings
            config={payrollSettingsStore.draftConfig}
            onChange={(field, value) => payrollSettingsStore.updateDraft(field, value)}
          />

        {:else if payrollSettingsStore.activeTab === 'legal'}
          <LegalSettings
            config={payrollSettingsStore.draftConfig}
            smig={payrollSettingsStore.activeSMIG}
            overtimeRules={payrollStore.overtimeRules}
            legalAllowances={payrollStore.legalAllowances}
            socialContributions={payrollStore.socialContributions}
            onChange={(field, value) => payrollSettingsStore.updateDraft(field, value)}
            onOvertimeChange={(ruleId, data) => payrollSettingsStore.updateOvertimeRule(ruleId, data)}
            onAllowanceChange={(allowanceId, data) => payrollSettingsStore.updateAllowance(allowanceId, data)}
            onResetAllowances={() => payrollSettingsStore.resetAllowances()}
          />

        {:else if payrollSettingsStore.activeTab === 'fiscal'}
          <FiscalSettings brackets={payrollStore.taxBrackets} isLoading={false} />
          
        {:else if payrollSettingsStore.activeTab === 'catalog'}
          <CatalogSettings
            adjustments={payrollStore.adjustments}
            isLoading={false}
            onToggle={(adj, isActive) => payrollSettingsStore.toggleAdjustment(adj, isActive)}
            onCreate={(data) => payrollSettingsStore.createAdjustment(data)}
            onUpdate={(id, data) => payrollSettingsStore.updateAdjustment(id, data)}
            onDelete={(id) => payrollSettingsStore.deleteAdjustment(id)}
            onReset={() => payrollSettingsStore.resetAdjustments()}
          />
        {/if}

        <!-- Erreur de sauvegarde -->
        {#if payrollSettingsStore.saveError}
          <div class="mt-4 flex items-center gap-2 p-3 bg-rose-50 border border-rose-100 rounded-lg text-[0.82rem] text-rose-700">
            <AppIcon name="alert-circle" size={16} class="shrink-0" />
            {payrollSettingsStore.saveError}
          </div>
        {/if}
      </div>
    </main>

    <SettingsFooter
      isSaving={payrollSettingsStore.isSaving}
      canSave={!!payrollSettingsStore.draftConfig}
      onSave={() => payrollSettingsStore.save()}
      onCancel={() => payrollSettingsStore.cancel()}
    />
  {/if}
</div>

