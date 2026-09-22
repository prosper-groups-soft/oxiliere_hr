<script lang="ts">
  import { page } from '$app/state';
  import CandidateProfile from "@/hr/recruitment/components/profile/CandidateProfile.svelte";


  let candidateId = $derived(page.params.candidateId as string);
</script>


<div class="h-full overflow-y-auto">
  <CandidateProfile {candidateId} />
</div>

