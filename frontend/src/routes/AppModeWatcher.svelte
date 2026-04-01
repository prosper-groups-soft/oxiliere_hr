<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
	import { appModeManager } from '@/hooks/is-organization.svelte';
	import { organizationQueryOptions } from '@/api/queries/organizations';
  import { browser } from '$app/environment';
	import { auth } from '@/features/auth/stores/auth.svelte';
	
  $effect(() => {
    if (browser && appModeManager.isOrganizationMode){
      if (auth.currentOrganization && auth.currentOrganization.slug == appModeManager.orgSlug){
        return;
      }

      const currentOrgQuery = createQuery(organizationQueryOptions.detail(appModeManager.orgSlug as string));

      const unsub = currentOrgQuery.subscribe((value) => {
        if (value.isSuccess){
          auth.currentOrganization = value.data;
        }
      });

      return () => {
        unsub();
      }
    } else {
      auth.currentOrganization = null;
    }
  });
</script>

