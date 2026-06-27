<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Switch } from "@/components/ui/switch";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import ValidationError from "@/components/ui/validation-error";
  import { taxSettingsStore } from "../../../stores/taxSettingsStore.svelte";
  import { cn } from "@/utilities/common/css";
  import { preventNonNumeric } from "@/utilities/common/number";

  const config = $derived(taxSettingsStore.config);
  const validationErrors = $derived(taxSettingsStore.validationErrors);
</script>


<div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
  <div class="flex items-start gap-4">
    <div class="w-12 h-12 rounded-xl bg-orange-50 flex items-center justify-center text-orange-600 shrink-0">
      <AppIcon name="calendar" size={24} />
    </div>
    <div class="flex-1">
      <div class="flex items-center justify-between mb-1">
        <h5 class="font-medium text-slate-900 text-[0.94rem]">Congés et Présence</h5>
      </div>
      <p class="text-[0.875rem] text-slate-500 mb-4">
        Paramètres de calcul des congés et gestion des présences
      </p>

      <div class="grid grid-cols-2 gap-4 mb-4">
        <div class="p-3 bg-slate-50 rounded-lg">
          <Label class="text-[0.87rem]">Heures par semaine</Label>
          <p class="text-[0.87rem] text-slate-400 mt-0.5 mb-2">Durée légale du travail (45h pour le code du travail RDC)</p>
          <div class="flex items-center gap-2">
            <Input
              type="number"
              value={config.workHoursPerWeek}
              onkeydown={preventNonNumeric}
              oninput={(e) => {
                const val = e.currentTarget.value;
                const num = val === '' ? NaN : parseInt(val);
                taxSettingsStore.updateConfig({ workHoursPerWeek: num });
              }}
              class={cn("w-full", validationErrors['workHoursPerWeek'] && "border-red-500 focus:border-red-500 focus:ring-red-500")}
              min={1}
              max={168}
              step={1}
            />
            <span class="text-[0.875rem]">h/semaine</span>
          </div>
          <ValidationError errors={validationErrors} field="workHoursPerWeek" />
          <div class="p-3 bg-slate-50 rounded-lg flex flex-col justify-center">
            <div class="flex items-center justify-start gap-2">
              <span class="text-[0.875rem] text-slate-500">Équivalent mensuel</span>
              <span class="text-[0.875rem] text-slate-400 mt-0.5">(Heures/semaine × 52 ÷ 12)</span>
            </div>
            <span class="text-[0.94rem] font-medium text-slate-700 mt-1">
              {Math.round((config.workHoursPerWeek ?? 45) * 52 / 12)} h/mois
            </span>
          </div>
        </div>

        <div class="p-3 bg-slate-50 rounded-lg">
          <Label class="text-[0.87rem]">Diviseur congés</Label>
          <p class="text-[0.87rem] text-slate-400 mt-0.5 mb-2">Jours pour calculer la valeur d'un jour de congé. Formule: Salaire ÷ Diviseur</p>
          <div class="flex items-center gap-2">
            <Input
              type="number"
              value={config.leaveDeductionDivisor}
              onkeydown={preventNonNumeric}
              oninput={(e) => {
                const val = e.currentTarget.value;
                const num = val === '' ? NaN : parseFloat(val);
                taxSettingsStore.updateConfig({ leaveDeductionDivisor: num });
              }}
              class={cn("w-full", validationErrors['leaveDeductionDivisor'] && "border-red-500 focus:border-red-500 focus:ring-red-500")}
              min={1}
              max={31}
              step={0.5}
            />
            <span class="text-[0.875rem]">j</span>
          </div>
          <ValidationError errors={validationErrors} field="leaveDeductionDivisor" />
        </div>
      </div>

      <!-- Switches for boolean options -->
      <div class="space-y-3">
        <div class="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
          <div>
            <span class="text-[0.88rem] font-medium text-slate-800">Intégration automatique à la paie</span>
            <div class="text-[0.875rem] text-slate-500">Calcule et déduit automatiquement les jours de congé pris du salaire mensuel</div>
          </div>
          <Switch
            checked={config.includeLeavesInPayroll ?? true}
            onCheckedChange={() => taxSettingsStore.updateConfig({ includeLeavesInPayroll: !(config.includeLeavesInPayroll ?? true) })}
            class="cursor-pointer"
          />
        </div>
        <div class="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
          <div>
            <span class="text-[0.88rem] font-medium text-slate-800">Calcul basé sur la présence réelle</span>
            <div class="text-[0.875rem] text-slate-500">Détermine les jours travaillés à partir des données de pointage/pointeuse au lieu d'une formule théorique</div>
          </div>
          <Switch
            checked={config.useTheoreticalDaysFromAttendance ?? false}
            onCheckedChange={() => taxSettingsStore.updateConfig({ useTheoreticalDaysFromAttendance: !(config.useTheoreticalDaysFromAttendance ?? false) })}
            class="cursor-pointer"
          />
        </div>
      </div>
    </div>
  </div>
</div>

