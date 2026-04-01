# Composants Toast d'Erreur

Composants compacts pour afficher les erreurs dans des toasts avec `svelte-sonner`.

## Composants disponibles

- **NetworkErrorToast** - Erreurs de connexion réseau (code 600)
- **ValidationErrorToast** - Erreurs de validation (code 422)
- **NotFoundErrorToast** - Ressource introuvable (code 404)
- **ForbiddenErrorToast** - Accès refusé (code 403)
- **UnauthorizedErrorToast** - Non autorisé (code 401)
- **ServerErrorToast** - Erreurs serveur (codes 500-599)
- **UnknownErrorToast** - Erreurs inconnues

## Utilisation

### Méthode 1 : Fonction utilitaire (Recommandée)

```typescript
import { showError, showErrorToast } from '@/utilities/toast-error';
import OxilereError from '@/utilities/errors';

// Avec n'importe quelle erreur
try {
	await someApiCall();
} catch (error) {
	showError(error); // Détecte automatiquement le type d'erreur
}

// Avec une OxilereError spécifique
const error = OxilereError.parse(response);
showErrorToast(error, 7000); // Durée personnalisée: 7 secondes
```

### Méthode 2 : Utilisation directe avec svelte-sonner

```typescript
import { toast } from 'svelte-sonner';
import { ValidationErrorToast } from '@/components/shared/errors/toast';
import OxilereError from '@/utilities/errors';

const error = OxilereError.parse(response);

toast.error(ValidationErrorToast, {
	duration: 5000,
	dismissible: true,
	componentProps: { error }
});
```

### Exemple avec TanStack Query

```typescript
import { createMutation } from '@tanstack/svelte-query';
import { showError } from '@/utilities/toast-error';

const mutation = createMutation({
	mutationFn: updateUser,
	onError: (error) => {
		showError(error);
	}
});
```

## Caractéristiques

- **Compact** : Design minimaliste optimisé pour les toasts
- **Icônes** : Chaque type d'erreur a une icône distinctive
- **Détails** : Affiche les informations pertinentes de l'erreur
- **Validation** : Affiche jusqu'à 2 erreurs de champs + compteur
- **Personnalisable** : Durée d'affichage configurable

## Design

Tous les composants suivent la même structure :

- Icône colorée à gauche (5x5)
- Titre en gras (text-sm)
- Message descriptif (text-xs text-muted-foreground)
- Espacement compact pour s'adapter aux toasts
