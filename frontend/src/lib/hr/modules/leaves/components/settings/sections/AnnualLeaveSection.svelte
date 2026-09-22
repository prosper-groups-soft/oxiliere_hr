<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import ValidationError from "@/hr/components/ui/validation-error";
  import TooltipWrapper from "@/hr/components/shared/containers/TooltipWrapper.svelte";
  import { leaveSettingsStore } from "../../../stores/leaveSettingsStore.svelte";
  import { cn } from "@/hr/utilities/common/css";
  import { preventNonNumeric } from "@/hr/utilities/common/number";

  
  const config = $derived(leaveSettingsStore.config);
  const validationErrors = $derived(leaveSettingsStore.validationErrors);
</script>


<div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
  <div class="flex items-start gap-4">
    <div class="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600 shrink-0">
      <AppIcon name="calendar" size={24} />
    </div>
    <div class="flex-1">
      <h5 class="font-medium text-slate-900 text-[0.95rem]">
        Forfait annuel
      </h5>
      <p class="text-[0.875rem] text-slate-500 mb-4">
        Nombre de jours de congés annuels accordés à chaque employé par an. 
        Le minimum légal en RDC est de <strong class="text-[0.875rem]">18 jours ouvrables</strong>.
      </p>
      
      <!-- Jours annuels -->
      <div class="flex items-center gap-6 flex-wrap">
        <div class="flex-1 min-w-[200px] max-w-[400px]">
          <Label class="text-[0.875rem] mb-1.5 block">Jours annuels</Label>
          <div class="flex items-center gap-2">
            <Input
              type="number"
              value={config.annualLeaveDays}
              onkeydown={preventNonNumeric}
              oninput={(e) => {
                const val = parseInt(e.currentTarget.value) || 0;
                leaveSettingsStore.setAnnualLeaveDays(val, e.currentTarget.value);
              }}
              class={cn("shadow-fine", validationErrors['annualLeaveDays'] && "border-red-500 focus:border-red-500 focus:ring-red-500")}
              min={18}
              max={60}
            />
            <span class="text-[0.875rem] text-slate-500">jours</span>
          </div>
          <ValidationError errors={validationErrors} field="annualLeaveDays" />
          <p class="text-[0.875rem] text-slate-400 mt-1.5">
            Plage: 18-60 jours. Valeur actuelle: <strong class="text-[0.875rem]">{config.annualLeaveDays} jours</strong>
          </p>
        </div>
      </div>

      <!-- Limites avancées -->
      <div class="mt-4 pt-4 border-t border-slate-100">
        <h6 class="text-[0.875rem] font-medium text-slate-700 mb-3 flex items-center gap-2">
          <AppIcon name="settings-2" size={15} class="text-slate-400" />
          Limites des demandes
        </h6>
        <div class="flex items-center gap-6 flex-wrap">
          <!-- Max consécutifs -->
          <div class="min-w-[180px]">
            <TooltipWrapper content="Nombre maximum de jours ouvrés consécutifs autorisés pour une seule demande de congé annuel. Dépasser cette valeur bloquera la soumission." contentClass="max-w-xs">
              {#snippet children(props)}
                <Label {...props} class="text-[0.875rem] mb-1.5 block text-left w-full">
                  Max jours consécutifs
                  <AppIcon name="info" size={13} class="inline-block text-slate-400 ml-1 -mt-0.5" />
                </Label>
              {/snippet}
            </TooltipWrapper>
            <div class="flex items-center gap-2">
              <Input
                type="number"
                value={config.maxConsecutiveDays}
                onkeydown={preventNonNumeric}
                oninput={(e) => {
                  const val = parseInt(e.currentTarget.value) || 0;
                  leaveSettingsStore.setMaxConsecutiveDays(val);
                }}
                class="w-20 text-center shadow-fine"
                min={1}
                max={60}
              />
              <span class="text-[0.875rem] text-slate-500">jours</span>
            </div>
            <p class="text-[0.82rem] text-slate-400 mt-1">
              Actuel: <strong class="text-[0.82rem] font-bold">{config.maxConsecutiveDays} jours</strong>
            </p>
          </div>

          <!-- Préavis -->
          <div class="min-w-[180px]">
            <TooltipWrapper content="Délai de préavis minimum entre la date de soumission et la date de début du congé. En dessous de ce délai, la soumission sera bloquée." contentClass="max-w-xs">
              {#snippet children(props)}
                <Label {...props} class="text-[0.875rem] mb-1.5 block text-left w-full">
                  Préavis requis
                  <AppIcon name="info" size={13} class="inline-block text-slate-400 ml-1 -mt-0.5" />
                </Label>
              {/snippet}
            </TooltipWrapper>
            <div class="flex items-center gap-2">
              <Input
                type="number"
                value={config.noticePeriodDays}
                onkeydown={preventNonNumeric}
                oninput={(e) => {
                  const val = parseInt(e.currentTarget.value) || 0;
                  leaveSettingsStore.setNoticePeriodDays(val);
                }}
                class="w-20 text-center shadow-fine"
                min={0}
                max={90}
              />
              <span class="text-[0.875rem] text-slate-500">jours</span>
            </div>
            <p class="text-[0.82rem] text-slate-400 mt-1">
              {#if config.noticePeriodDays > 0}
                Actuel: <strong class="text-[0.82rem] font-bold">{config.noticePeriodDays} jours</strong> avant le départ
              {:else}
                Aucun préavis requis
              {/if}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

