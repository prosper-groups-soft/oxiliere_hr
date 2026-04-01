<script lang="ts">
  import { attendanceStore } from "../../stores/attendance.svelte";
  import Sparkline from "@/components/shared/charts/Sparkline.svelte";

  const stats = $derived(attendanceStore.stats);
</script>


<div class="flex items-center gap-4 px-4 py-1.5 shadow-fine bg-white">
  
  <!-- Attendance Rate -->
  <div class="flex items-center gap-2">
    <div class="flex gap-1">
      <span class="text-[0.8rem] text-slate-900 font-medium">{stats.attendanceRate}%</span>
      <span class="text-[0.8rem] text-slate-500">Taux global</span>
      <div class="flex items-center gap-1">
        <div class="h-3 w-8 opacity-60">
          <Sparkline 
            data={[65, 78, 82, 75, 88, 92, stats.attendanceRate]} 
            color="#0f172a" 
            fillColor="rgba(15, 23, 42, 0.05)" 
            lineWidth={1.5}
          />
        </div>
      </div>
    </div>
  </div>

  <div class="h-8 w-px bg-slate-200/60"></div>

  <!-- Real-time metrics -->
  <div class="flex items-center gap-4.5">
    {#snippet Metric(label: string, value: number, color: string, icon: string)}
      <div class="flex items-center gap-2 group">
        <div class={`h-2 w-2 flex justify-center items-center rounded-full ${color}`}></div>
        <div class="flex gap-0.5">
          <span class="font-medium text-[0.8rem]">{value}</span>
          <span class="text-[0.8rem] text-slate-500">{label}</span>
        </div>
      </div>
    {/snippet}

    {@render Metric("Présents", stats.presentCount, "bg-emerald-500", "user-check")}
    {@render Metric("Retards", stats.lateCount, "bg-amber-500", "clock")}
    {@render Metric("Absents", stats.absentCount, "bg-rose-500", "user-x")}
  </div>
</div>

