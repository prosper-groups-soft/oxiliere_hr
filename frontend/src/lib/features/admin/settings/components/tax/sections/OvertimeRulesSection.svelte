<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Switch } from "@/components/ui/switch";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import ValidationError from "@/components/ui/validation-error";
  import { taxSettingsStore } from "../../../stores/taxSettingsStore.svelte";
  import { cn } from "@/utilities/common/css";
  import { preventNonNumeric } from "@/utilities/common/number";

  const validationErrors = $derived(taxSettingsStore.validationErrors);
  const overtimeRules = $derived(taxSettingsStore.overtimeRules);

  function translateOvertimeRuleType(type: string): string {
    const translations: Record<string, string> = {
      'FIRST_TWO_HOURS': 'Premières heures',
      'SUBSEQUENT_HOURS': 'Heures suivantes',
      'WEEKEND': 'Repos hebdomadaire',
      'HOLIDAY': 'Jour férié légal',
    };
    return translations[type] || type;
  }

  function getOvertimeRuleExplanation(type: string): string {
    const explanations: Record<string, string> = {
      'FIRST_TWO_HOURS': 'Majoration de 30% pour les 6 premières heures supplémentaires (46ème à 51ème heure par semaine)',
      'SUBSEQUENT_HOURS': 'Majoration de 60% pour les heures au-delà des 6 premières heures supplémentaires',
      'WEEKEND': 'Majoration de 100% (double) pour le travail effectué le dimanche ou jour de repos hebdomadaire',
      'HOLIDAY': 'Majoration de 100% (double) pour le travail effectué un jour férié légal (ex: 30 juin)',
    };
    return explanations[type] || '';
  }
</script>


<div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
  <div class="flex items-start gap-4">
    <div class="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center text-amber-600 shrink-0">
      <AppIcon name="clock" size={24} />
    </div>
    <div class="flex-1">
      <div class="flex items-center justify-start mb-1">
        <h5 class="font-medium text-slate-900 text-[0.94rem]">Heures supplémentaires</h5>
      </div>
      <p class="text-[0.875rem] text-slate-500 mb-4">
        Règles de calcul des heures supplémentaires fixées par la législation
      </p>
      {#if overtimeRules.length > 0}
        <div class="overflow-x-auto">
          <table class="w-full text-[0.85rem]">
            <thead>
              <tr class="border-b border-slate-200">
                <th class="text-left py-2 px-2 text-slate-600 font-medium text-[0.87rem]">Type</th>
                <th class="text-center py-2 px-2 text-slate-600 font-medium text-[0.87rem]">Actif</th>
                <th class="text-right py-2 px-2 text-slate-600 font-medium text-[0.87rem]">Multiplicateur</th>
                <th class="text-left py-2 px-2 text-slate-600 font-medium text-[0.87rem]">Description</th>
              </tr>
            </thead>
            <tbody>
              {#each overtimeRules as rule}
                <tr class="border-b border-slate-100 last:border-0">
                  <td class="py-2 px-2">
                    <ValidationError errors={validationErrors} field={`overtimeRule_${rule.id}_multiplier`} />
                    <div class="text-slate-800 text-[0.875rem] font-medium">{translateOvertimeRuleType(rule.rule_type)}</div>
                    <div class="text-slate-400 text-[0.875rem] mt-1">{getOvertimeRuleExplanation(rule.rule_type)}</div>
                  </td>
                  <td class="py-2 px-2">
                    <Switch 
                      checked={rule.is_active}
                      onCheckedChange={(checked) => taxSettingsStore.updateOvertimeRule(rule.id, { is_active: checked })}
                      class="data-[state=checked]:bg-orange-600 cursor-pointer"
                    />
                  </td>
                  <td class="py-2 px-2">
                    <div class="flex flex-col gap-1 items-end">
                      <div class="flex items-center gap-1">
                        <Input
                          type="number"
                          value={parseFloat(rule.multiplier)}
                          onkeydown={preventNonNumeric}
                          oninput={(e) => {
                            const val = e.currentTarget.value;
                            const num = val === '' ? 1 : parseFloat(val);
                            taxSettingsStore.updateOvertimeRule(rule.id, { multiplier: num.toFixed(2) });
                          }}
                          class={cn(
                            "w-20 text-right h-8 text-[0.875rem] shadow-fine",
                            validationErrors[`overtimeRule_${rule.id}_multiplier`] && "border-red-500 focus:border-red-500 focus:ring-red-500"
                          )}
                          min={1}
                          max={5}
                          step={0.01}
                        />
                        <span class="text-[0.87rem] text-slate-600">x</span>
                      </div>
                      <span class="text-[0.875rem] text-slate-400">(fixé par la loi)</span>
                    </div>
                  </td>
                  <td class="py-2 px-2 text-slate-500 text-[0.875rem]">{rule.description || '-'}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {:else}
        <AnimateSpin text="Chargement des règles" class="border-white size-3" />
      {/if}
    </div>
  </div>
</div>

