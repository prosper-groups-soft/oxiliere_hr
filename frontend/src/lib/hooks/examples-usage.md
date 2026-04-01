# Utilisation des hooks de détection de mode (Svelte 5)

## Hooks disponibles

### `detectMode(pathname: string): AppMode`

Fonction utilitaire pour détecter le mode depuis un pathname.

### `extractOrgSlug(pathname: string): string | null`

Fonction utilitaire pour extraire le slug d'organisation depuis un pathname.

### `useAppMode`

Rune `$derived` qui retourne le mode actuel ('user' | 'organization').

### `useOrgSlug`

Rune `$derived` qui retourne le slug de l'organisation ou null.

### `useIsOrganizationMode`

Rune `$derived` qui retourne true si on est en mode organisation.

### `useModeInfo`

Rune `$derived.by()` qui retourne toutes les informations du mode.

## Exemples d'utilisation

### Dans un composant Svelte 5

```svelte
<script lang="ts">
    import { useAppMode, useOrgSlug, useIsOrganizationMode, useModeInfo } from '$lib/hooks/is-organization.svelte';

    // Utilisation simple du mode (pas besoin de $ avec les runes)
    $effect(() => {
        console.log('Mode actuel:', useAppMode); // 'user' ou 'organization'
    });

    // Utilisation du slug d'organisation
    $effect(() => {
        if (useOrgSlug) {
            console.log('Organisation slug:', useOrgSlug);
        }
    });

    // Vérification si on est en mode organisation
    $effect(() => {
        if (useIsOrganizationMode) {
            console.log('En mode organisation');
        }
    });

    // Utilisation complète
    $effect(() => {
        console.log('Info complète:', useModeInfo);
        /*
        {
            mode: 'organization',
            isOrganization: true,
            isUser: false,
            orgSlug: 'mon-org',
            pathname: '/o/mon-org/applications'
        }
        */
    });
</script>

{#if useIsOrganizationMode}
    <h1>Mode Organisation: {useOrgSlug}</h1>
    <!-- Interface organisation -->
{:else}
    <h1>Mode Utilisateur</h1>
    <!-- Interface utilisateur -->
{/if}
```

### Navigation conditionnelle (Svelte 5)

```svelte
<script lang="ts">
    import { useIsOrganizationMode, useOrgSlug } from '$lib/hooks/is-organization.svelte';
    import { goto } from '$app/navigation';

    function navigateToApplications() {
        if (useIsOrganizationMode && useOrgSlug) {
            goto(`/o/${useOrgSlug}/applications`);
        } else {
            goto('/applications');
        }
    }

    function navigateToSettings() {
        if (useIsOrganizationMode && useOrgSlug) {
            goto(`/o/${useOrgSlug}/settings`);
        } else {
            goto('/settings');
        }
    }
</script>
```

### Composant adaptatif (Svelte 5)

```svelte
<script lang="ts">
    import { useModeInfo } from '$lib/hooks/is-organization.svelte';

    // Titre adaptatif avec $derived
    const pageTitle = $derived(
        useModeInfo.isOrganization
            ? `Organisation ${useModeInfo.orgSlug}`
            : 'Mon compte'
    );

    // URL d'API adaptative avec $derived
    const apiBaseUrl = $derived(
        useModeInfo.isOrganization
            ? `/api/organizations/${useModeInfo.orgSlug}`
            : '/api/user'
    );
</script>

<h1>{pageTitle}</h1>
```

### Middleware/Guard (Svelte 5)

```svelte
<script lang="ts">
    import { useIsOrganizationMode, useOrgSlug } from '$lib/hooks/is-organization.svelte';
    import { goto } from '$app/navigation';

    // Redirection si pas d'organisation en mode org
    $effect(() => {
        if (useIsOrganizationMode && !useOrgSlug) {
            goto('/o'); // Rediriger vers le sélecteur d'organisation
        }
    });
</script>
```

### Variables dérivées personnalisées (Svelte 5)

```typescript
// utils/context.svelte.ts
import { useModeInfo } from '$lib/hooks/is-organization.svelte';

export const contextualApiUrl = $derived.by(() => {
	const baseUrl = '/api';

	if (useModeInfo.isOrganization && useModeInfo.orgSlug) {
		return `${baseUrl}/organizations/${useModeInfo.orgSlug}`;
	}

	return `${baseUrl}/user`;
});

export const contextualTitle = $derived.by(() => {
	if (useModeInfo.isOrganization && useModeInfo.orgSlug) {
		return `Organisation ${useModeInfo.orgSlug}`;
	}

	return 'Mon compte personnel';
});
```

## Patterns d'URL supportés

### Mode utilisateur

- `/` → Mode utilisateur
- `/applications` → Mode utilisateur
- `/settings` → Mode utilisateur
- `/profile` → Mode utilisateur

### Mode organisation

- `/o/mon-org` → Mode organisation, slug: "mon-org"
- `/o/mon-org/applications` → Mode organisation, slug: "mon-org"
- `/o/mon-org/settings` → Mode organisation, slug: "mon-org"
- `/o/autre-org/members` → Mode organisation, slug: "autre-org"
