<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { attendanceStore } from "../../../../stores/attendance.svelte";
  import { Button } from "@/components/ui/button";
  import { cn } from "@/utilities/common/css";
  import type { DayOfWeek, WorkPolicy, WorkPeriod } from "../../../../types/types";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Label } from "@/components/ui/label";
  import { Input } from "@/components/ui/input";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { DAYS, PERIOD_TYPES } from "../../../../constants/attendance.constants";
  import { useQueryClient } from "@tanstack/svelte-query";
  import { policyQueryKeys } from "../../../../queries/attendanceQueries";

  
  let { 
    open = $bindable(false),
    policy = $bindable<WorkPolicy | null>(null)
  } = $props<{ 
    open: boolean;
    policy: WorkPolicy | null;
  }>();

  let isSaving = $state(false);
  let saveError = $state<string | null>(null);

  const queryClient = useQueryClient();

  const activeDaysCount = $derived.by(() => {
    if (!policy) return 0;
    return DAYS.filter(d => {
      const p = policy.pattern[d.index];
      return p && !p.isOff;
    }).length;
  });

  async function savePolicy() {
    if (!policy || isSaving) return;

    isSaving = true;
    saveError = null;
    try {
      if (policy.id) {
        await attendanceStore.updatePolicy(policy.id, policy);
      } else {
        await attendanceStore.addPolicy(policy);
      }
      queryClient.invalidateQueries({ queryKey: policyQueryKeys.all });
      open = false;
    } catch (err) {
      saveError = 'Impossible d\'enregistrer le modèle. Veuillez réessayer.';
      console.error('[PolicySheet] save error:', err);
    } finally {
      isSaving = false;
    }
  }

  function toggleDayOff(dayIndex: DayOfWeek) {
    if (!policy) return;
    
    const currentPattern = policy.pattern[dayIndex];
    
    if (!currentPattern) {
      policy.pattern[dayIndex] = {
        isOff: false,
        periods: [
          { id: crypto.randomUUID(), startTime: "08:00", endTime: "12:00", type: "work", name: "Matin" },
          { id: crypto.randomUUID(), startTime: "12:00", endTime: "14:00", type: "break", name: "Pause déjeuner" },
          { id: crypto.randomUUID(), startTime: "14:00", endTime: "17:00", type: "work", name: "Après-midi" }
        ]
      };
    } else {
      policy.pattern[dayIndex].isOff = !currentPattern.isOff;
      if (policy.pattern[dayIndex].isOff) {
        policy.pattern[dayIndex].periods = [];
      } else {
        policy.pattern[dayIndex].periods = [
          { id: crypto.randomUUID(), startTime: "08:00", endTime: "12:00", type: "work", name: "Matin" },
          { id: crypto.randomUUID(), startTime: "12:00", endTime: "14:00", type: "break", name: "Pause déjeuner" },
          { id: crypto.randomUUID(), startTime: "14:00", endTime: "17:00", type: "work", name: "Après-midi" }
        ];
      }
    }
  }

  function addPeriod(dayIndex: DayOfWeek) {
    if (!policy) return;
    const dayPattern = policy.pattern[dayIndex];
    if (!dayPattern || dayPattern.isOff) return;
    
    dayPattern.periods.push({
      id: Date.now().toString(),
      startTime: "08:00",
      endTime: "17:00",
      type: "work",
      name: "Nouvelle période"
    });
  }

  function removePeriod(dayIndex: DayOfWeek, periodId: string) {
    if (!policy) return;
    const dayPattern = policy.pattern[dayIndex];
    if (!dayPattern) return;
    
    dayPattern.periods = dayPattern.periods.filter((p: WorkPeriod) => p.id !== periodId);
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl flex flex-col h-full overflow-hidden p-0">
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <Sheet.Title class="text-[1rem] text-bold">{policy?.id ? 'Modifier le modèle' : 'Définir un modèle'}</Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto px-6 py-6 space-y-8 custom-scrollbar">
      {#if policy}
        <div class="flex flex-col gap-y-4">
          <div class="space-y-1.5">
            <Label for="policyName">Nom du modèle</Label>
            <Input
              id="policyName"
              bind:value={policy.name}
              placeholder="ex: Bureau Standard"
              class="h-10 bg-white shadow-fine"
            />
          </div>
          <div class="space-y-1.5">
            <Label for="policyDesc">Description</Label>
            <Input
              id="policyDesc"
              bind:value={policy.description}
              placeholder="ex: 8h-17h, 5j/7"
              class="h-10 bg-white shadow-fine"
            />
          </div>
          <div class="space-y-1.5">
            <Label for="policyHours">Objectif hebdomadaire (heures)</Label>
            <Input
              id="policyHours"
              type="number"
              min="1"
              max="80"
              bind:value={policy.targetHours}
              placeholder="ex: 40"
              class="h-10 bg-white shadow-fine"
            />
          </div>
        </div>

        <div class="flex flex-col gap-4">
          <!-- Summary bar -->
          <div class="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-primary/5 border border-primary/10">
            <div class="flex items-center gap-2.5">
              <AppIcon name="calendar-days" size={16} class="text-primary/70" />
              <span class="text-[0.82rem] font-medium text-slate-700">
                <span class="font-bold text-primary text-[0.82rem]">{activeDaysCount}</span>/{DAYS.length} jours actifs
              </span>
            </div>
            <div class="flex-1 flex gap-1 px-3">
              {#each DAYS as day}
                {@const p = policy.pattern[day.index]}
                <div 
                  class={cn(
                    "h-2 flex-1 rounded-full transition-all duration-300",
                    p && !p.isOff 
                      ? "bg-primary/50" 
                      : "bg-slate-200"
                  )}
                  title={day.label}
                ></div>
              {/each}
            </div>
          </div>

          <!-- Day cards -->
          <div class="grid grid-cols-1 gap-3">
            {#each DAYS as day}
              {@const dayPattern = policy.pattern[day.index]}
              {@const isActive = dayPattern && !dayPattern.isOff}
              <div 
                class={cn(
                  "group relative flex flex-col rounded-xl border transition-all duration-200",
                  isActive 
                    ? "border-primary/15 bg-white shadow-[0_1px_3px_-1px_rgba(0,0,0,0.04)]" 
                    : "border-slate-100 bg-slate-50/40"
                )}
              >
                <!-- Left accent bar for active days -->
                {#if isActive}
                  <div class="absolute left-0 top-2 bottom-2 w-0.5 rounded-full bg-primary/40"></div>
                {/if}

                <!-- Day header -->
                <div class="flex items-center justify-between px-4 py-2.5">
                  <div class="flex items-center gap-3">
                    <div class={cn(
                      "flex items-center justify-center w-8 h-8 rounded-lg text-[0.75rem] font-bold transition-all",
                      isActive
                        ? "bg-primary/10 text-primary"
                        : "bg-slate-100 text-slate-400"
                    )}>
                      {day.short}
                    </div>
                    <span class="text-[0.82rem] font-medium text-slate-600 hidden sm:inline">{day.label}</span>
                    
                    <!-- Toggle switch -->
                    <button
                      onclick={() => toggleDayOff(day.index)}
                      class={cn(
                        "relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary/30 focus:ring-offset-1",
                        isActive ? "bg-primary" : "bg-slate-300"
                      )}
                      role="switch"
                      aria-checked={isActive}
                      aria-label={isActive ? `Désactiver ${day.label}` : `Activer ${day.label}`}
                    >
                      <span 
                        class={cn(
                          "pointer-events-none relative inline-block h-4 w-4 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out",
                          isActive ? "translate-x-4" : "translate-x-0"
                        )}
                      ></span>
                    </button>
                  </div>

                  <!-- Periods count badge + Add button -->
                  <div class="flex items-center gap-2">
                    {#if isActive}
                      <span class="text-[0.8rem] font-medium text-slate-500 tabular-nums">
                        {dayPattern.periods.length} période{dayPattern.periods.length > 1 ? 's' : ''}
                      </span>
                      <button
                        onclick={() => addPeriod(day.index)}
                        class="opacity-100 transition-opacity duration-150 flex items-center justify-center h-8 w-8 rounded-lg text-slate-700 hover:text-primary hover:bg-primary/5 cursor-pointer border"
                        title="Ajouter une période"
                      >
                        <AppIcon name="plus" size={18} />
                      </button>
                    {:else}
                      <span class="text-[0.82rem] font-medium text-slate-400">Repos</span>
                    {/if}
                  </div>
                </div>

                <!-- Periods list (only for active days) -->
                {#if isActive && dayPattern.periods.length > 0}
                  <div class="px-4 pb-3 pt-0 space-y-1.5">
                    {#each dayPattern.periods as period (period.id)}
                      <div class="group/period flex items-center gap-2 py-1.5 px-2.5 rounded-lg bg-slate-50/60 border border-slate-100/80 hover:border-slate-200 hover:bg-white transition-all duration-150">
                        <!-- Type chip -->
                        <div class={cn(
                          "shrink-0 flex items-center gap-1.5 px-2 py-1 rounded-md text-[0.7rem] font-semibold uppercase tracking-wider",
                          period.type === "work"
                            ? "bg-primary/8 text-primary"
                            : "bg-amber-50 text-amber-600 border border-amber-200/60"
                        )}>
                          <div class={cn(
                            "w-1.5 h-1.5 rounded-full",
                            period.type === "work" ? "bg-primary" : "bg-amber-400"
                          )}></div>
                          {PERIOD_TYPES.find(t => t.value === period.type)?.label}
                        </div>

                        <!-- Time inputs -->
                        <div class="flex items-center gap-1.5">
                          <input
                            type="time"
                            bind:value={period.startTime}
                            class="h-7 w-21 rounded-md border-0 bg-transparent px-1.5 text-[0.8rem] font-medium text-slate-700 focus:ring-2 focus:ring-primary/40 focus:outline-none cursor-pointer"
                          />
                          <span class="text-slate-300 text-[0.65rem] font-medium">→</span>
                          <input
                            type="time"
                            bind:value={period.endTime}
                            class="h-7 w-21 rounded-md border-0 bg-transparent px-1.5 text-[0.8rem] font-medium text-slate-800 focus:ring-2 focus:ring-primary/40 focus:outline-none cursor-pointer"
                          />
                        </div>

                        <!-- Name input -->
                        <input
                          type="text"
                          bind:value={period.name}
                          placeholder="Libellé"
                          class="h-7 flex-1 min-w-0 rounded-md border-0 bg-transparent px-1.5 text-[0.8rem] text-slate-800 placeholder:text-slate-300 focus:ring-2 focus:ring-primary/50 focus:outline-none"
                        />

                        <!-- Delete button -->
                        <button
                          onmousedown={(e) => e.preventDefault()}
                          onclick={(e) => { e.preventDefault(); e.stopPropagation(); (document.activeElement as HTMLElement)?.blur(); removePeriod(day.index, period.id); }}
                          class="transition-all duration-150 shrink-0 flex items-center justify-center h-7 w-7 rounded-md text-red-600 hover:text-red-700 hover:bg-red-50 cursor-pointer"
                          title="Supprimer cette période"
                        >
                          <AppIcon name="trash-2" size={18} />
                        </button>
                      </div>
                    {/each}
                  </div>
                {:else if isActive}
                  <!-- Empty state for active day with no periods -->
                  <div class="px-4 pb-3">
                    <button
                      onclick={() => addPeriod(day.index)}
                      class="w-full py-2 rounded-lg border-2 border-dashed border-slate-200 text-[0.75rem] font-medium text-slate-400 hover:border-primary/30 hover:text-primary hover:bg-primary/2 transition-all duration-150 flex items-center justify-center gap-1.5"
                    >
                      <AppIcon name="plus" size={12} />
                      Ajouter une période
                    </button>
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>

    <Sheet.Footer class="px-6 py-3 border-t bg-slate-50/50">
      {#if saveError}
        <div class="px-3 py-2 mb-2 rounded-lg bg-red-50 border border-red-100 text-[0.82rem] text-red-600 flex items-center gap-2">
          <AppIcon name="alert-circle" size={16} class="shrink-0 text-red-400" />
          {saveError}
        </div>
      {/if}
      <div class="flex gap-3">
        <Sheet.Close class="flex-1">
          <Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600 font-medium text-[0.88rem]">
            <AppIcon name="x" size={17} class="text-slate-400" />
            Annuler
          </Button>
        </Sheet.Close>
        <Button 
          onclick={savePolicy}
          disabled={!policy?.name || isSaving}
          class="flex-1 h-9 bg-primary! text-white font-medium shadow-fine text-[0.88rem] hover:opacity-90 transition-all disabled:opacity-50"
        >
          {#if isSaving}
            <AnimateSpin class="border-white size-3" text="" />
          {:else}
            <AppIcon name="check" size={17} />
          {/if}
          {policy?.id ? 'Enregistrer' : 'Créer le modèle'}
        </Button>
      </div>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>




