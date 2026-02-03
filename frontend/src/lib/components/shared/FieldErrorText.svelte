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

    // Fonction pour extraire le message d'erreur
    function getErrorMessage(): string | null {
        if (!errors) return null;

        // Si errors est un tableau
        if (Array.isArray(errors)) {
            if (errors.length === 0) return null;
            
            const firstError = errors[0];
            
            // Si l'erreur est un objet avec une propriété message
            if (typeof firstError === 'object' && firstError?.message) {
                return firstError.message;
            }
            
            // Si l'erreur est un objet et qu'on a un field spécifique
            if (typeof firstError === 'object' && field && firstError[field]) {
                return firstError[field];
            }
            
            // Si l'erreur est une string
            if (typeof firstError === 'string') {
                return firstError;
            }
        }

        // Si errors est un objet et qu'on a un field spécifique
        // @ts-ignore
        if (typeof errors === 'object' && field && errors[field]) { // @ts-ignore
            return errors[field];
        }

        // Si errors est une string directement
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
