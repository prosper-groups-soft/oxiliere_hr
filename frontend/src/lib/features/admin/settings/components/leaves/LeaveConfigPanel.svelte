<script lang="ts">
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import TooltipWrapper from "@/components/shared/containers/TooltipWrapper.svelte";
  import { leaveSettingsStore } from "../../stores/leaveSettingsStore.svelte";
  import { cn } from "@/utilities/common/css";

  const config = $derived(leaveSettingsStore.config);
  const isSaving = $derived(leaveSettingsStore.isSaving);
  const hasChanges = $derived(leaveSettingsStore.hasChanges);

  let showLegalBanner = $state(true);

  const leaveIcons: Record<string, string> = {
    heart: 'heart',
    baby: 'baby',
    'flower-2': 'star',
    stethoscope: 'activity'
  };

  const leaveIconColors: Record<string, string> = {
    heart: 'text-rose-500',
    baby: 'text-sky-500',
    'flower-2': 'text-violet-500',
    stethoscope: 'text-emerald-500'
  };

  function handleSave() {
    leaveSettingsStore.saveSettings();
  }

  function handleReset() {
    leaveSettingsStore.resetToDefaults();
  }
</script>


{#snippet Header()}
  <div class="bg-white flex items-center justify-between px-6 py-3 pr-8 border-b border-slate-100">
    <div class="flex items-center gap-3">
      <div>
        <h3 class="font-semibold text-slate-900 text-[0.96rem]">
          Configuration des congés
        </h3>
        <p class="text-[0.8rem] text-slate-500">
          Paramétrage selon le Code du Travail RDC
        </p>
      </div>
      {#if hasChanges}
        <span class="flex items-center gap-1.5 text-[0.8rem] text-amber-600 bg-amber-50 px-2.5 py-1 rounded-full">
          <AppIcon name="circle-alert" size={14} />
          Modifications non sauvegardées
        </span>
      {/if}
    </div>
    <div class="flex gap-2">
      {#if hasChanges}
        <Button variant="outline" onclick={handleReset} disabled={isSaving} class="h-7.5 shadow-fine">
          <AppIcon name="rotate-ccw" size={16} />
          Réinitialiser
        </Button>
        <Button onclick={handleSave} disabled={isSaving} class="bg-indigo-600 hover:bg-indigo-700 shadow-fine h-7.5">
          {#if isSaving}
            <AppIcon name="loader-2" size={17} class="animate-spin" />
          {:else}
            <AppIcon name="save" size={17} />
          {/if}
          Enregistrer
        </Button>
      {/if}
    </div>
  </div>
{/snippet}


{#snippet LegalInfoBanner()}
  {#if showLegalBanner}
    <div 
      class="bg-blue-50/80 border-b border-blue-100 px-6 pr-8 py-2.5 flex items-center justify-start gap-3"
    >
      <button
        aria-label="Fermer la bannière"
        onclick={() => showLegalBanner = false}
        class="shrink-0 p-1 text-blue-400 hover:text-blue-600 hover:bg-blue-100 rounded transition-all cursor-pointer"
      >
        <AppIcon name="x" size={17} />
      </button>
      <div class="flex items-center gap-3 flex-1 justify-start">
        <AppIcon name="scale" size={18} class="text-blue-500 shrink-0" />
        <span class="text-[0.82rem] text-blue-900 leading-relaxed">
          Les congés annuels sont régis par les articles 126 à 131 du Code du Travail de la RDC.
          La durée légale est fixée à <span class="font-semibold text-[0.82rem]">18 jours ouvrables</span> minimum.
        </span>
      </div>
    </div>
  {/if}
{/snippet}


{#snippet AnnualLeaveSection()}
  <div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
    <div class="flex items-start gap-4">
      <div class="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600 shrink-0">
        <AppIcon name="calendar" size={24} />
      </div>
      <div class="flex-1">
        <h5 class="font-medium text-slate-900 text-[0.95rem]">
          Forfait annuel
        </h5>
        <p class="text-[0.85rem] text-slate-500 mb-4">
          Nombre de jours de congé annuel selon le Code du Travail (18 jours minimum)
        </p>
        <div class="flex items-center gap-4">
          <div class="w-32">
            <Input
              type="number"
              value={config.annualLeaveDays}
              oninput={(e) => leaveSettingsStore.setAnnualLeaveDays(parseInt(e.currentTarget.value) || 18)}
              min={12}
              max={40}
              class="text-center shadow-fine"
            />
          </div>
          <div class="text-[0.85rem] text-slate-500">jours ouvrables</div>
        </div>
        <div class="flex gap-2 mt-3">
          {#each [{v: 18, l: '18 jours (légal RDC)'}, {v: 24, l: '24 jours (convention)'}] as preset}
            <button
              class={cn(
                "px-3 py-1.5 text-[0.82rem] rounded-full border transition-colors cursor-pointer",
                config.annualLeaveDays === preset.v
                  ? "bg-blue-50 border-blue-200 text-blue-700"
                  : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50"
              )}
              onclick={() => leaveSettingsStore.setAnnualLeaveDays(preset.v)}
            >
              {preset.l}
            </button>
          {/each}
        </div>
      </div>
    </div>
  </div>
{/snippet}


{#snippet SpecialLeavesSection()}
  <div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
    <h5 class="font-medium text-slate-900 mb-4 text-[0.94rem]">
      Congés de circonstances (Code du Travail RDC)
    </h5>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      {#each config.specialLeaves as leave (leave.type)}
        {@const isEditing = leaveSettingsStore.editingLeaveType === leave.type}
        <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
          <div class="w-10 h-10 rounded-lg bg-white flex items-center justify-center shrink-0">
            <AppIcon name={leaveIcons[leave.icon || ''] || 'calendar'} size={20} class={leaveIconColors[leave.icon || ''] || 'text-slate-600'} />
          </div>
          <div class="flex-1 min-w-0">
            <div class="font-medium text-slate-900 text-[0.875rem]">{leave.label}</div>
            <div class="text-[0.8rem] text-slate-500 truncate">{leave.description}</div>
          </div>
          
          {#if isEditing}
            <div class="flex items-center gap-2">
              <Input
                type="number"
                value={leaveSettingsStore.editForm.daysAllowed}
                oninput={(e) => leaveSettingsStore.editForm = { ...leaveSettingsStore.editForm, daysAllowed: parseInt(e.currentTarget.value) || 0 }}
                class="w-16 text-center h-8 text-[0.85rem] shadow-fine"
                min={0}
                max={30}
              />
              <button onclick={() => leaveSettingsStore.saveLeaveEdit()} class="w-7 h-7 rounded-md bg-green-100 text-green-600 flex items-center justify-center hover:bg-green-200 cursor-pointer">
                <AppIcon name="check" size={14} />
              </button>
              <button onclick={() => leaveSettingsStore.cancelLeaveEdit()} class="w-7 h-7 rounded-md bg-slate-200 text-slate-600 flex items-center justify-center hover:bg-slate-300 cursor-pointer">
                <AppIcon name="x" size={14} />
              </button>
            </div>
          {:else}
            <div class="flex items-center gap-2">
              <div>
                <TooltipWrapper content="Jours accordés">
                  {#snippet children(props)}
                    <span {...props} class="text-[0.875rem] font-semibold text-slate-700 px-2 cursor-pointer">
                      {leave.daysAllowed} jr{leave.daysAllowed > 1 ? 's' : ''}
                    </span>
                  {/snippet}
                </TooltipWrapper>
              </div>
              <button onclick={() => leaveSettingsStore.startEditingLeave(leave.type)} class="w-7 h-7 rounded-md hover:bg-slate-200 flex items-center justify-center text-slate-500 cursor-pointer">
                <AppIcon name="edit" size={14} />
              </button>
            </div>
          {/if}
        </div>
      {/each}
    </div>
    <p class="text-[0.84rem] text-slate-400 mt-2">
      * Valeurs conformes au Code du Travail RDC.
    </p>
  </div>
{/snippet}


{#snippet SenioritySection()}
  <div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
    <div class="flex items-start gap-4">
      <div class="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center text-amber-600 shrink-0">
        <AppIcon name="award" size={24} />
      </div>
      <div class="flex-1">
        <div class="flex items-center justify-between mb-1">
          <h5 class="font-medium text-slate-900 text-[0.94rem]">
            Bonus d'ancienneté
          </h5>
          <button
            aria-label={config.seniorityBonus.enabled ? "Désactiver le bonus d'ancienneté" : "Activer le bonus d'ancienneté"}
            class={cn("relative w-8 h-5 rounded-full transition-colors cursor-pointer", config.seniorityBonus.enabled ? "bg-indigo-500" : "bg-slate-300")}
            onclick={() => leaveSettingsStore.toggleSeniorityBonus()}
          >
            <span class={cn("absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow-sm transition-transform", config.seniorityBonus.enabled ? "translate-x-3" : "translate-x-0")}></span>
          </button>
        </div>
        <p class="text-[0.8rem] text-slate-500 mb-4">
          +1 jour par tranche de {config.seniorityBonus.yearsPerBonus} ans
        </p>
        {#if config.seniorityBonus.enabled}
          <div class="grid grid-cols-3 gap-3">
            <div class="space-y-1">
              <Label class="text-[0.75rem] text-slate-500">Tranche (ans)</Label>
              <Input type="number" value={config.seniorityBonus.yearsPerBonus} oninput={(e) => leaveSettingsStore.updateSeniorityBonus({ yearsPerBonus: parseInt(e.currentTarget.value) || 5 })} min={1} max={10} class="shadow-fine" />
            </div>
            <div class="space-y-1">
              <Label class="text-[0.75rem] text-slate-500">Jours bonus</Label>
              <Input type="number" value={config.seniorityBonus.bonusDays} oninput={(e) => leaveSettingsStore.updateSeniorityBonus({ bonusDays: parseInt(e.currentTarget.value) || 1 })} min={1} max={5} class="shadow-fine" />
            </div>
            <div class="space-y-1">
              <Label class="text-[0.75rem] text-slate-500">Maximum</Label>
              <Input type="number" value={config.seniorityBonus.maxBonus || ''} placeholder="∞" oninput={(e) => leaveSettingsStore.updateSeniorityBonus({ maxBonus: e.currentTarget.value ? parseInt(e.currentTarget.value) : undefined })} min={1} max={20} class="shadow-fine" />
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
{/snippet}    


{#snippet OptionToggle(label: string, desc: string, checked: boolean, toggle: () => void)}
  <div 
    class="flex items-center justify-between p-3 bg-slate-50 rounded-lg cursor-pointer hover:bg-slate-100 transition-colors"
    onclick={toggle}
    role="none"
  >
    <div class="flex-1">
      <div class="font-medium text-slate-900 text-[0.9rem]">{label}</div>
      <div class="text-[0.84rem] text-slate-500">{desc}</div>
    </div>
    <button
      aria-label={checked ? `Désactiver ${label}` : `Activer ${label}`}
      class={cn("relative w-8 h-5 rounded-full transition-colors cursor-pointer", checked ? "bg-indigo-500" : "bg-slate-300")}
      onclick={(e) => e.stopPropagation()}
    >
      <span class={cn("absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow-sm transition-transform", checked ? "translate-x-3" : "translate-x-0")}></span>
    </button>
  </div>
{/snippet}


{#snippet OptionsSection()}
  <div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
    <h5 class="font-medium text-slate-900 mb-4 text-[0.94rem]">
      Options complémentaires
    </h5>
    <div class="space-y-3">

      {@render OptionToggle("Autoriser les demi-journées", "Permettre les congés de 0.5 jour", config.allowHalfDays, () => leaveSettingsStore.setAllowHalfDays(!config.allowHalfDays))}
      {@render OptionToggle("Approbation requise", "Les congés nécessitent une validation", config.requireApproval, () => leaveSettingsStore.setRequireApproval(!config.requireApproval))}

      <div class="flex flex-col items-start gap-3 p-3 bg-slate-50 rounded-lg">
        <div class="flex-1">
          <div class="font-medium text-slate-900 text-[0.9rem]">Délai de préavis</div>
          <div class="text-[0.84rem] text-slate-500">Jours de préavis minimum</div>
        </div>
        <div class="flex items-center gap-2">
          <Input type="number" value={config.noticePeriodDays} oninput={(e) => leaveSettingsStore.setNoticePeriodDays(parseInt(e.currentTarget.value) || 15)} class="w-20 text-center shadow-fine" min={0} max={90} />
          <span class="text-[0.84rem] text-slate-500">jours</span>
        </div>
      </div>
    </div>
  </div>
{/snippet}


<div class="pb-6">
  <div class="sticky top-0 z-10 bg-white">
    {@render Header()}
    {@render LegalInfoBanner()}
  </div>
  <div class="mt-6 space-y-6">
    {@render AnnualLeaveSection()}
    {@render SpecialLeavesSection()}
    {@render SenioritySection()}
    {@render OptionsSection()}
  </div>
</div>

