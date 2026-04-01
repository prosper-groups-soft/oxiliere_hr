<script lang="ts">
  import AlertDialog from '@/components/shared/modals/AlertDialog.svelte';
  import { notification } from '@/stores/notification.svelte';

  const req = $derived(notification.confirmRequest);

  let isOpen = $state(false);

  $effect(() => {
    isOpen = req !== null;
  });

  $effect(() => {
    if (!isOpen) {
      notification._close();
    }
  });
</script>


{#if req}
  <AlertDialog
    bind:isOpen
    title={req.title}
    message={req.message}
    type={req.type ?? 'danger'}
    yesText={req.yesText ?? 'Confirmer'}
    noText={req.noText ?? 'Annuler'}
    onYes={req.onYes}
    onNo={req.onNo}
  />
{/if}

