<script lang="ts">
  import { goto } from "$app/navigation";

  // Redirect to users page by default
  $effect(() => {
    goto("/admin/settings/access");
  });
</script>

