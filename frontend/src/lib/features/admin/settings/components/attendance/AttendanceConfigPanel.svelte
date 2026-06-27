<script lang="ts">
  import { onMount } from 'svelte';
  import { attendanceSettingsStore } from "../../stores/attendanceSettingsStore.svelte";
  import AttendanceHeader from "./AttendanceHeader.svelte";
  import AttendanceLegalBanner from "./AttendanceLegalBanner.svelte";
  import AttendanceRulesSection from "./sections/AttendanceRulesSection.svelte";

  onMount(() => {
    attendanceSettingsStore.load();
  });
</script>


<div class="sticky top-0 z-10 bg-white">
  <AttendanceHeader />
  <AttendanceLegalBanner />
</div>

<div class="mt-6 space-y-6">
  <AttendanceRulesSection />
</div>
