<script lang="ts">
  import SearchBar from "@/hr/components/shared/elements/SearchBar.svelte";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import { attendanceStore } from "../../stores/attendance.svelte";
  import { cn } from "@/hr/utilities/common/css";
  import SelfPunchButton from "./views/SelfPunchButton.svelte";


  let dateInput = $state<HTMLInputElement | null>(null);
  let dateBtnRefs = $state<Record<string, HTMLButtonElement | null>>({
    '-1': null,
    '0': null,
  });
  let dateIndicatorStyle = $state('');

  // Today's date string (YYYY-MM-DD) — used to block future navigation
  const todayStr = $derived(new Date().toISOString().split('T')[0]);

  const dateQuickActions = [
    { label: 'Hier', value: -1 },
    { label: "Aujourd'hui", value: 0 },
  ];

  // Whether the current store date is today or beyond
  const isFutureDisabled = $derived(attendanceStore.filters.dateRange.from >= todayStr);

  // Determine which quick-action date matches the current store date
  const activeDateKey = $derived.by(() => {
    const current = attendanceStore.filters.dateRange.from;
    for (const action of dateQuickActions) {
      const d = new Date();
      d.setDate(d.getDate() + action.value);
      const target = d.toISOString().split('T')[0];
      if (current === target) return String(action.value);
    }
    return null;
  });

  // Update sliding indicator position when active date changes
  $effect(() => {
    const btn = activeDateKey ? dateBtnRefs[activeDateKey] : null;
    if (btn) {
      dateIndicatorStyle = `left: ${btn.offsetLeft}px; width: ${btn.offsetWidth}px;`;
    } else {
      dateIndicatorStyle = 'left: 0; width: 0;';
    }
  });

  function handleQuickDate(offset: number) {
    const d = new Date();
    d.setDate(d.getDate() + offset);
    const target = d.toISOString().split('T')[0];
    if (target > todayStr) return;
    attendanceStore.filters.dateRange.from = target;
  }

  function handlePrevDay() {
    const d = new Date(attendanceStore.filters.dateRange.from);
    d.setDate(d.getDate() - 1);
    attendanceStore.filters.dateRange.from = d.toISOString().split('T')[0];
  }

  function handleNextDay() {
    if (isFutureDisabled) return;
    const d = new Date(attendanceStore.filters.dateRange.from);
    d.setDate(d.getDate() + 1);
    attendanceStore.filters.dateRange.from = d.toISOString().split('T')[0];
  }

  function handleDateChange(e: Event) {
    const val = (e.target as HTMLInputElement).value;
    if (val) {
      // Clamp to today — never allow a future date even if the picker bypasses max
      attendanceStore.filters.dateRange.from = val <= todayStr ? val : todayStr;
    }
  }

  const formattedDate = $derived.by(() => {
    const d = new Date(attendanceStore.filters.dateRange.from + 'T12:00:00');
    return d.toLocaleDateString('fr-FR', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  });
</script>


<div class="flex items-center justify-between pl-4 pr-10 py-2 bg-white border-b border-slate-100">
  <SearchBar 
    bind:value={attendanceStore.filters.search}
    placeholder="Rechercher un employé..."
    class="w-125"
    inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
    iconSize={22}
  />

  <div class="flex items-center gap-2">
    <SelfPunchButton />
    {@render DateNavigation()}
  </div>
</div>


{#snippet DateNavigation()}
  <!-- Date Navigation -->
  <div class="flex items-center bg-indigo-50 p-0.5 rounded-xl border border-slate-200/40">

    <!-- Current date label (white pill leftmost) -->
    <div class="flex items-center gap-1.5 pl-2 pr-2.5 py-0.5 bg-white rounded-lg shadow-fine mr-1">
      <AppIcon name="calendar" size={14} class="text-slate-400" />
      <span class="text-[0.82rem] text-slate-700 font-medium whitespace-nowrap">
        {formattedDate}
      </span>
    </div>

    <div class="w-px h-4 bg-indigo-200"></div>

    <!-- Quick actions : Hier / Aujourd'hui with sliding indicator -->
    <div class="relative flex items-center">
      <!-- Sliding indicator behind the active button -->
      <div
        class="absolute h-7 rounded-lg bg-white shadow-fine border border-slate-200/50 transition-all duration-250 ease-in-out z-10"
        style={dateIndicatorStyle}
      ></div>

      {#each dateQuickActions as action}
        <Button
          bind:ref={dateBtnRefs[String(action.value)]}
          variant="ghost"
          onclick={() => handleQuickDate(action.value)}
          class={cn(
            "relative h-7 px-2.5 rounded-lg transition-all z-20 flex items-center justify-center border-none shadow-none text-[0.84rem]",
            activeDateKey === String(action.value)
              ? "text-slate-900 font-medium cursor-pointer"
              : "text-slate-500 hover:text-slate-700 hover:bg-slate-200/50 cursor-pointer"
          )}
        >
          <span class="text-[0.84rem]">{action.label}</span>
        </Button>
      {/each}
    </div>

    <div class="w-px h-3.5 bg-indigo-200 mx-1"></div>

    <!-- Calendar picker -->
    <div class="relative h-7 w-7">
      <Button 
        variant="ghost" 
        size="icon" 
        onclick={() => dateInput?.showPicker()}
        class="h-7 w-7 rounded-lg hover:bg-white hover:shadow-sm"
      >
        <AppIcon name="calendar-days" size={15} class="text-slate-500" />
      </Button>
      <input 
        type="date"
        bind:this={dateInput}
        onchange={handleDateChange}
        value={attendanceStore.filters.dateRange.from}
        max={todayStr}
        class="absolute inset-0 opacity-0 pointer-events-none"
      />
    </div>

    <!-- Chevrons grouped together on the right -->
    <div class="flex items-center ml-1">
      <Button
        variant="ghost"
        size="icon"
        onclick={handlePrevDay}
        class="h-7 w-7 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-white transition-all"
      >
        <AppIcon name="chevron-left" size={15} />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        disabled={isFutureDisabled}
        onclick={handleNextDay}
        class={cn(
          "h-7 w-7 rounded-lg transition-all",
          isFutureDisabled
            ? "text-slate-300 cursor-not-allowed"
            : "text-slate-500 hover:text-slate-700 hover:bg-white"
        )}
      >
        <AppIcon name="chevron-right" size={15} />
      </Button>
    </div>
  </div>
{/snippet}

