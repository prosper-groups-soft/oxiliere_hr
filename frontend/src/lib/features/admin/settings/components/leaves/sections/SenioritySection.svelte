<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Switch } from "@/components/ui/switch";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import ValidationError from "@/components/ui/validation-error";
  import { leaveSettingsStore } from "../../../stores/leaveSettingsStore.svelte";
  import { cn } from "@/utilities/common/css";
  import { preventNonNumeric } from "@/utilities/common/number";
  import { slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';

  
  const config = $derived(leaveSettingsStore.config);
  const validationErrors = $derived(leaveSettingsStore.validationErrors);
</script>


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
        <Switch 
          checked={config.seniorityBonus.enabled} 
          onCheckedChange={() => leaveSettingsStore.toggleSeniorityBonus()}
          class="data-[state=checked]:bg-amber-500 cursor-pointer"
        />
      </div>
      
      <p class="text-[0.875rem] text-slate-500 mb-4">
        Octroi de jours supplémentaires basé sur l'ancienneté de l'employé dans l'entreprise.
        Récompense la fidélité selon la politique interne.
      </p>
      
      {#if config.seniorityBonus.enabled}
        <div transition:slide={{ duration: 300, easing: cubicOut }}>
          <div class="p-3 bg-amber-50/50 rounded-lg mb-4">
            <p class="text-[0.875rem] text-amber-800">
              <strong class="text-[0.875rem]">Règle:</strong> +{config.seniorityBonus.bonusDays} jour(s) de congé 
              par tranche de {config.seniorityBonus.yearsPerBonus} an(s) d'ancienneté
              {#if config.seniorityBonus.maxBonus}
                , jusqu'à un maximum de {config.seniorityBonus.maxBonus} jours.
              {/if}
            </p>
          </div>
          
          <div class="grid grid-cols-3 gap-3">
            <div class="space-y-1">
              <Label>Tranche (ans)</Label>
              <p class="text-[0.875rem] text-slate-400">Années par bonus</p>
              <Input 
                type="number"
                value={config.seniorityBonus.yearsPerBonus} 
                onkeydown={preventNonNumeric}
                oninput={(e) => {
                  const raw = e.currentTarget.value;
                  const val = parseInt(raw);
                  leaveSettingsStore.updateSeniorityBonus({ yearsPerBonus: val }, 'yearsPerBonus', raw);
                }}
                class={cn("shadow-fine", validationErrors['seniorityBonus.yearsPerBonus'] && "border-red-500 focus:border-red-500 focus:ring-red-500")}
                min={1} 
                max={10} 
              />
              <ValidationError errors={validationErrors} field="seniorityBonus.yearsPerBonus" />
            </div>
            
            <div class="space-y-1">
              <Label>Jours bonus</Label>
              <p class="text-[0.875rem] text-slate-400">Jours par tranche</p>
              <Input 
                type="number"
                value={config.seniorityBonus.bonusDays} 
                onkeydown={preventNonNumeric}
                oninput={(e) => {
                  const raw = e.currentTarget.value;
                  const val = parseInt(raw);
                  leaveSettingsStore.updateSeniorityBonus({ bonusDays: val }, 'bonusDays', raw);
                }}
                class={cn("shadow-fine", validationErrors['seniorityBonus.bonusDays'] && "border-red-500 focus:border-red-500 focus:ring-red-500")}
                min={1} 
                max={config.seniorityBonus.maxBonus || 20} 
              />
              <ValidationError errors={validationErrors} field="seniorityBonus.bonusDays" />
            </div>
            
            <div class="space-y-1">
              <Label>Maximum</Label>
              <p class="text-[0.875rem] text-slate-400">Plafond total</p>
              <Input 
                type="number"
                value={config.seniorityBonus.maxBonus || ''} 
                placeholder="∞" 
                onkeydown={preventNonNumeric}
                oninput={(e) => {
                  const newMax = e.currentTarget.value ? parseInt(e.currentTarget.value) : undefined;
                  leaveSettingsStore.updateSeniorityBonus({ maxBonus: newMax });
                  if (newMax && config.seniorityBonus.bonusDays > newMax) {
                    leaveSettingsStore.updateSeniorityBonus({ bonusDays: newMax });
                  }
                }} 
                class="shadow-fine"
                min={1} 
                max={30} 
              />
            </div>
          </div>
        </div>
      {:else}
        <p class="text-[0.875rem] text-slate-400" transition:slide={{ duration: 300, easing: cubicOut }}>
          Bonus d'ancienneté désactivé. Tous les employés recevront le même forfait annuel de base.
        </p>
      {/if}
    </div>
  </div>
</div>

