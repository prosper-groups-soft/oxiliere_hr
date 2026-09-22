<script lang="ts">
  import CompanyInfoSection from "./sections/CompanyInfoSection.svelte";
  import WorkSitesSection from "./sections/WorkSitesSection.svelte";
  import MyCompanyHeader from "./MyCompanyHeader.svelte";
</script>


<div class="pb-6">
  <MyCompanyHeader />
  <div class="space-y-6 mt-8.5">
    <CompanyInfoSection />
    <WorkSitesSection />
  </div>
</div>

