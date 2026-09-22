<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/hr/components/layout/elements/AnimateSpin.svelte";
  import { attendanceSettingsStore } from "../../../stores/attendanceSettingsStore.svelte";


  // Store bindings
  const isLoading = $derived(attendanceSettingsStore.isLoading);
  const fields = $derived(attendanceSettingsStore.formFields);

  // Actions
  function updateField<K extends keyof typeof fields>(key: K, value: number) {
    attendanceSettingsStore.formFields = {
      ...attendanceSettingsStore.formFields,
      [key]: value,
    };
  }
</script>


<div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
  <div class="flex items-start gap-4">
    <!-- Icon -->
    <div class="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center text-amber-600 shrink-0">
      <AppIcon name="clock" size={24} />
    </div>

    <div class="flex-1">
      <!-- Header -->
      <div class="flex items-center justify-between mb-1">
        <h5 class="font-medium text-slate-900 text-[0.95rem]">
          Configuration des règles
        </h5>
      </div>

      <!-- Description -->
      <p class="text-[0.875rem] text-slate-500 mb-4">
        Configurez les tolérances horaires et les seuils d'absence 
        pour le calcul des heures travaillées.
      </p>

      <!-- Loading state -->
      {#if isLoading}
        <div class="text-slate-400 h-40 flex items-center justify-center">
          <AnimateSpin text="Chargement" />
        </div>

      {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Période de grâce (retard) -->
          <div>
            <Label class="text-[0.875rem]">Période de grâce (retard)</Label>
            <div class="relative mt-1">
              <Input
                type="number"
                min={0}
                max={60}
                value={fields.late_grace_period}
                oninput={(e) => updateField('late_grace_period', parseInt(e.currentTarget.value) || 0)}
                class="shadow-fine pr-12"
              />
              <span class="absolute right-3 top-1/2 -translate-y-1/2 text-[0.8rem] text-slate-400 pointer-events-none">
                min
              </span>
            </div>
            <p class="text-[0.8rem] text-slate-400 mt-1">
              Tolérance après l'heure de début avant d'être marqué retard
            </p>
          </div>

          <!-- Seuil d'absence partielle -->
          <div>
            <Label class="text-[0.875rem]">Seuil d'absence partielle</Label>
            <div class="relative mt-1">
              <Input
                type="number"
                min={0}
                max={240}
                value={fields.partial_absence_threshold}
                oninput={(e) => updateField('partial_absence_threshold', parseInt(e.currentTarget.value) || 0)}
                class="shadow-fine pr-12"
              />
              <span class="absolute right-3 top-1/2 -translate-y-1/2 text-[0.8rem] text-slate-400 pointer-events-none">
                min
              </span>
            </div>
            <p class="text-[0.8rem] text-slate-400 mt-1">
              Temps manquant à partir duquel la journée est classée "présence partielle"
            </p>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>


<style>
  /* Empêcher les spinners sur les inputs number */
  :global(input[type="number"]::-webkit-inner-spin-button),
  :global(input[type="number"]::-webkit-outer-spin-button) {
    opacity: 1;
  }
</style>

