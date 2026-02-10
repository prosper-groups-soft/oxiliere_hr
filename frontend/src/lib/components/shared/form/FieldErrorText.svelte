<script lang="ts">
  import { CircleAlert } from '@lucide/svelte';

  interface Props {
    errors: string[] | Record<string, string> | any[];
    field?: string;
    showIcon?: boolean;
    class?: string;
  }

  const {
    errors,
    field,
    showIcon = true,
    class: className = ''
  }: Props = $props();

  // Function that extract the message error from the errors object
  function getErrorMessage(): string | null {
    if (!errors) return null;

    // If errors is an array
    if (Array.isArray(errors)) {
      if (errors.length === 0) return null;
      
      const firstError = errors[0];
      
      // If the error is an object with a message property
      if (typeof firstError === 'object' && firstError?.message) {
        return firstError.message;
      }
      
      // If the error is an object and we have a specific field
      if (typeof firstError === 'object' && field && firstError[field]) {
        return firstError[field];
      }
      
      // If the error is a string
      if (typeof firstError === 'string') {
        return firstError;
      }
    }

    // If errors is an object and we have a specific field
    // @ts-ignore
    if (typeof errors === 'object' && field && errors[field]) { // @ts-ignore
      return errors[field];
    }

    // If errors is a string directly
    if (typeof errors === 'string') {
      return errors;
    }

    return null;
  }

  const message = $derived(getErrorMessage());
</script>


{#if message}
  <div class="flex items-start gap-2 mt-2 {className}" role="alert">
    {#if showIcon}
      <CircleAlert class="w-4 h-4 text-red-600 mt-0.5 shrink-0" />
    {/if}
    <p class="text-sm text-red-600 leading-relaxed">
      {message}
    </p>
  </div>
{/if}

