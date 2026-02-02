# Documentation - Module Employees

## Vue d'ensemble

Le module **Employees** constitue le référentiel central des ressources humaines. Il assure la gestion de l'identité, du cycle de vie professionnel et des dossiers administratifs des collaborateurs. C'est le socle sur lequel reposent la paie, les congés et la gestion des talents.

## Fonctionnalités RH

### 1. Gestion de l'Identité
- Fiche signalétique complète et matricule unique.
- État civil, coordonnées et informations de contact.
- Liaison optionnelle avec un compte utilisateur pour l'accès au portail.

### 2. Cycle de Vie et Mouvements
- **Onboarding** : Accueil et enregistrement des nouveaux collaborateurs.
- **Mouvements** : Gestion des transitions de statut (période d'essai, actif, suspension).
- **Offboarding** : Sorties définitives (démission, fin de contrat, retraite).
- **Historique** : Traçabilité complète des changements de statut.

### 3. Dossier Administratif (Le "Vault")
- Archive numérique des documents légaux (Passeport, ID, Diplômes).
- Suivi des dates de validité et alertes d'expiration.
- Processus de vérification de la conformité des pièces.

### 4. Protection Sociale et Famille
- Déclaration des ayants droit (enfants à charge) pour les prestations sociales.
- Contacts d'urgence pour le "Duty of Care" (priorisation des appels).

### 5. Résidence et Mobilité
- Historique des domiciles avec distinction de l'adresse actuelle.

## Architecture Métier

### Modèles de Données

| Entité | Rôle Business |
| :--- | :--- |
| **Employee** | Profil central, identité et état du contrat. |
| **StatusHistory** | Chronologie des événements contractuels. |
| **EmployeeDocument** | Coffre-fort numérique des pièces justificatives. |
| **EmployeeAddress** | Historique de résidence et adresse fiscale. |
| **EmergencyContact** | Contacts à joindre en cas d'incident (priorisés). |
| **EmployeeChild** | Registre des enfants à charge pour les bénéfices. |
| **EmployeeEducation** | Parcours académique et qualifications. |
| **WorkSite** | Localisation physique du lieu de travail. |

## Guide de l'API

### Gestion du Personnel (`/employees`)
- `GET /` : Consulter l'annuaire de l'entreprise (filtres avancés).
- `POST /` : Lancer un processus d'onboarding.
- `GET /{id}` : Dossier RH complet (vue 360°).
- `PATCH /{id}/personal-info` : Mise à jour de l'état civil.
- `PATCH /{id}/assign-user/{user_id}` : Activer l'accès au portail.

### Cycle de Vie (`/employees/{id}/lifecycle`)
- `POST /transition` : Promouvoir ou changer le statut contractuel.
- `POST /suspend` : Verrouillage administratif immédiat.
- `POST /reactivate` : Retour en poste d'un collaborateur.
- `POST /offboard` : Enregistrer un départ définitif.

### Dossier et Famille
- `POST /employees/{id}/documents` : Versements au coffre-fort numérique.
- `POST /employees/{id}/family/children` : Déclarer un nouvel enfant à charge.
- `POST /employees/{id}/emergency-contacts` : Enregistrer un contact d'urgence.

## Règles de Gestion RH

1. **Unicité** : Le matricule est l'identifiant métier unique et immuable.
2. **Continuité des Adresses** : Une seule adresse peut être marquée comme "actuelle". Lors d'un déménagement, le système archive automatiquement l'ancienne.
3. **Priorité Sécurité** : Les contacts d'urgence sont séquencés de 1 à 10 pour garantir une chaîne de rappel efficace.
4. **Audit** : Toute modification sur le profil employé est tracée (Audit Log) avec l'auteur et la date de l'action.

## Bonnes Pratiques

- **Audit Trail** : Toujours utiliser les services dédiés pour les changements de statut afin de garantir l'intégrité de l'historique.
- **Vérification** : Ne marquer un document comme "Vérifié" qu'après confrontation avec l'original physique.
- **Archivage** : Le système privilégie la désactivation (`is_active=False`) à la suppression physique pour conserver l'historique légal.
