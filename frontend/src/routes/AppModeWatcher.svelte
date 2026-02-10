<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
	import { appModeManager } from '@/hooks/is-organization.svelte';
	import { organizationQueryOptions } from '@/api/queries/organizations';
	import { current_organization_store } from '@/stores/auth';
	
  $effect(() => {
    if (appModeManager.isOrganizationMode){
      if ($current_organization_store && $current_organization_store.slug == appModeManager.orgSlug){
        return;
      }

      const currentOrgQuery = createQuery(organizationQueryOptions.detail(appModeManager.orgSlug as string));

      const unsub = currentOrgQuery.subscribe((value) => {
        if (value.isSuccess){
          current_organization_store.set(value.data)
        }
      });

      return () => {
        unsub();
      }
    } else {
      current_organization_store.set(null);
    }
  });
</script>

