<script lang="ts">
  // Sub-components
  import MyCompanyHeader from "./MyCompanyHeader.svelte";
  import MyCompanyLegalBanner from "./MyCompanyLegalBanner.svelte";
  import CompanyInfoSection from "./sections/CompanyInfoSection.svelte";
  import WorkSitesSection from "./sections/WorkSitesSection.svelte";
</script>


<div class="pb-6">
  <div class="sticky top-0 z-10 bg-white">
    <MyCompanyHeader />
    <MyCompanyLegalBanner />
  </div>
  <div class="mt-6 space-y-6">
    <CompanyInfoSection />
    <WorkSitesSection />
  </div>
</div>

