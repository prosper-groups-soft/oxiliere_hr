<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { attendanceStore } from "../../../../stores/attendance.svelte";
  import { Button } from "@/components/ui/button";
  import { cn } from "@/utilities/common/css";
  import type { DayOfWeek, WorkPolicy, WorkPeriod } from "../../../../types/types";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Label } from "@/components/ui/label";
  import { Input } from "@/components/ui/input";
  import * as Select from "@/components/ui/select";

  let { 
    open = $bindable(false),
    policy = $bindable<WorkPolicy | null>(null)
  } = $props<{ 
    open: boolean;
    policy: WorkPolicy | null;
  }>();

  const days: { label: string; index: DayOfWeek }[] = [
    { label: "Lun", index: 1 },
    { label: "Mar", index: 2 },
    { label: "Mer", index: 3 },
    { label: "Jeu", index: 4 },
    { label: "Ven", index: 5 },
    { label: "Sam", index: 6 },
    { label: "Dim", index: 0 },
  ];

  const periodTypes = [
    { value: "work", label: "Travail" },
    { value: "break", label: "Pause" }
  ];

  function savePolicy() {
    if (!policy) return;

    if (policy.id) {
      attendanceStore.updatePolicy(policy.id, policy);
    } else {
      attendanceStore.addPolicy(policy);
    }
    open = false;
  }

  function toggleDayOff(dayIndex: DayOfWeek) {
    if (!policy) return;
    
    const currentPattern = policy.pattern[dayIndex];
    
    if (!currentPattern) {
      policy.pattern[dayIndex] = {
        isOff: false,
        periods: [
          { id: Math.random().toString(36), startTime: "08:00", endTime: "12:00", type: "work", name: "Matin" },
          { id: Math.random().toString(36), startTime: "12:00", endTime: "14:00", type: "break", name: "Pause déjeuner" },
          { id: Math.random().toString(36), startTime: "14:00", endTime: "18:00", type: "work", name: "Après-midi" }
        ]
      };
    } else {
      policy.pattern[dayIndex].isOff = !currentPattern.isOff;
      if (policy.pattern[dayIndex].isOff) {
        policy.pattern[dayIndex].periods = [];
      } else {
        policy.pattern[dayIndex].periods = [
          { id: Math.random().toString(36), startTime: "08:00", endTime: "12:00", type: "work", name: "Matin" },
          { id: Math.random().toString(36), startTime: "14:00", endTime: "18:00", type: "work", name: "Après-midi" }
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
      startTime: "09:00",
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
    <Sheet.Header class="px-6 py-4 border-b bg-slate-50/50">
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
        </div>

        <div class="flex flex-col gap-4">
          <Label class="text-[0.875rem] text-slate-900 font-semibold">Configuration Hebdomadaire</Label>
          <div class="grid grid-cols-1 gap-4">
            {#each days as day}
              {@const dayPattern = policy.pattern[day.index]}
              <div class="flex flex-col gap-3 p-4 rounded-xl border border-slate-100 bg-slate-50/30">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                    <span class="text-[0.75rem] font-bold uppercase text-slate-500 w-8">{day.label}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onclick={() => toggleDayOff(day.index)}
                      class={cn(
                        "h-7 px-3 rounded-lg border text-[0.7rem] font-bold transition-all shadow-none",
                        (!dayPattern || dayPattern.isOff)
                          ? "border-slate-200 bg-white text-slate-400"
                          : "border-primary/20 bg-primary/10 text-primary hover:bg-primary/20"
                      )}
                    >
                      {(!dayPattern || dayPattern.isOff) ? 'OFF' : 'ACTIF'}
                    </Button>
                  </div>
                  
                  {#if dayPattern && !dayPattern.isOff}
                    <Button
                      variant="ghost"
                      size="sm"
                      onclick={() => addPeriod(day.index)}
                      class="h-7 px-2 text-slate-500 hover:text-primary transition-colors"
                    >
                      <AppIcon name="plus" size={14} class="mr-1" />
                      Période
                    </Button>
                  {/if}
                </div>
                
                {#if dayPattern && !dayPattern.isOff}
                  <div class="flex flex-col gap-2">
                    {#each dayPattern.periods as period (period.id)}
                      <div class="flex items-center gap-2 p-2 rounded-lg border border-slate-200 bg-white shadow-fine">
                        <Select.Root type="single" bind:value={period.type}>
                          <Select.Trigger class="h-8 w-24 bg-slate-50/50 border-none focus:ring-0 cursor-pointer">
                            <span class="text-[0.84rem] font-medium">
                              {periodTypes.find(t => t.value === period.type)?.label}
                            </span>
                          </Select.Trigger>
                          <Select.Content class="z-100">
                            {#each periodTypes as typeOption}
                              <Select.Item value={typeOption.value} class="text-[0.84rem]">{typeOption.label}</Select.Item>
                            {/each}
                          </Select.Content>
                        </Select.Root>
                        
                        <Input type="time" bind:value={period.startTime} class="h-8 w-22 text-[0.8rem] border-none bg-slate-50/50 cursor-pointer" />
                        <span class="text-slate-300 text-xs">-</span>
                        <Input type="time" bind:value={period.endTime} class="h-8 w-22 text-[0.8rem] border-none bg-slate-50/50 cursor-pointer" />
                        
                        <Input
                          type="text"
                          bind:value={period.name}
                          placeholder="Libellé"
                          class="h-8 flex-1 text-[0.8rem] border-none bg-slate-50/50 cursor-pointer"
                        />
                        
                        <Button
                          variant="ghost"
                          size="sm"
                          onclick={() => removePeriod(day.index, period.id)}
                          class="h-8 w-8 text-slate-400 hover:text-red-500 transition-colors"
                        >
                          <AppIcon name="trash" size={16} />
                        </Button>
                      </div>
                    {/each}
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>

    <Sheet.Footer class="px-6 py-4 border-t flex flex-row gap-3 bg-slate-50/50">
      <Button 
        onclick={savePolicy}
        class="flex-1 h-10 bg-primary text-white font-medium"
        disabled={!policy?.name}
      >
        <AppIcon name="check" size={18} />
        {policy?.id ? 'Enregistrer' : 'Créer le modèle'}
      </Button>
      <Sheet.Close class="flex-1">
        <Button variant="outline" class="w-full h-10">Annuler</Button>
      </Sheet.Close>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
</style>

