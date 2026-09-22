<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Switch } from "@/components/ui/switch";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import ValidationError from "@/components/ui/validation-error";
  import { leaveSettingsStore } from "../../../stores/leaveSettingsStore.svelte";
  import { MONTHS } from "@/constants";
  import { cn } from "@/utilities/common/css";
  import { slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { preventNonNumeric } from "@/utilities/common/number";

  
  const config = $derived(leaveSettingsStore.config);
  const validationErrors = $derived(leaveSettingsStore.validationErrors);
</script>


<div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
  <div class="flex items-start gap-4">
    <div class="w-12 h-12 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600 shrink-0">
      <AppIcon name="refresh-cw" size={24} />
    </div>
    <div class="flex-1">
      <div class="flex items-center justify-between mb-1">
        <h5 class="font-medium text-slate-900 text-[0.94rem]">
          Report des congés
        </h5>
        <Switch 
          checked={config.allowsCarryOver} 
          onCheckedChange={(checked) => leaveSettingsStore.setAllowsCarryOver(checked)}
          class="data-[state=checked]:bg-emerald-600 cursor-pointer"
        />
      </div>
      
      <p class="text-[0.875rem] text-slate-500 mb-4">
        Autorise les employés à reporter les jours de congés non utilisés sur l'année suivante.
        Le Code du Travail RDC permet le report avec une limite temporelle.
      </p>
      
      {#if config.allowsCarryOver}
        <div class="grid grid-cols-2 gap-4" transition:slide={{ duration: 300, easing: cubicOut }}>
          <div class="p-3 bg-slate-50 rounded-lg">
            <Label class="text-[0.87rem] mb-1.5 block">Jours max reportables</Label>
            <p class="text-[0.87rem] text-slate-400 mb-2">
              Limite de jours pouvant être reportés (hors bonus d'ancienneté)
            </p>
            <div class="flex items-center gap-2">
              <Input
                type="number"
                value={config.maxCarryOverDays}
                onkeydown={preventNonNumeric}
                oninput={(e) => {
                  const val = parseInt(e.currentTarget.value) || 0;
                  leaveSettingsStore.setMaxCarryOverDays(val, e.currentTarget.value);
                }}
                class={cn("shadow-fine", validationErrors['maxCarryOverDays'] && "border-red-500 focus:border-red-500 focus:ring-red-500")}
                min={0}
                max={30}
              />
              <span class="text-[0.875rem] text-slate-500">j</span>
            </div>
            <ValidationError errors={validationErrors} field="maxCarryOverDays" />
          </div>
          
          <div class="p-3 bg-slate-50 rounded-lg">
            <Label class="text-[0.87rem] mb-1.5 block">Mois d'expiration</Label>
            <p class="text-[0.87rem] text-slate-400 mb-2">
              Les jours reportés expirent à la fin de ce mois
            </p>
            <div class="flex items-center gap-2">
              <Input
                type="number"
                value={config.carryOverExpirationMonth}
                onkeydown={preventNonNumeric}
                oninput={(e) => {
                  const val = parseInt(e.currentTarget.value) || 1;
                  leaveSettingsStore.setCarryOverExpirationMonth(val, e.currentTarget.value);
                }}
                class={cn("shadow-fine", validationErrors['carryOverExpirationMonth'] && "border-red-500 focus:border-red-500 focus:ring-red-500")}
                min={1}
                max={12}
              />
              <span class="text-[0.875rem] text-slate-500">/12</span>
            </div>
            <ValidationError errors={validationErrors} field="carryOverExpirationMonth" />
            <p class="text-[0.875rem] text-slate-400 mt-1.5">
              Expire en: <strong class="text-[0.875rem] font-medium">{MONTHS[config.carryOverExpirationMonth - 1]}</strong>
            </p>
          </div>
        </div>
      {:else}
        <p class="text-[0.84rem] text-slate-400" transition:slide={{ duration: 300, easing: cubicOut }}>
          Le report des congés est désactivé. Les jours non utilisés seront perdus en fin d'année.
        </p>
      {/if}
    </div>
  </div>
</div>

