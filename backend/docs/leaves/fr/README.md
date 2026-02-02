# Documentation - Gestion des Congés (Leaves)

## Vue d'ensemble
Le module **Leaves** automatise la gestion du cycle de vie des congés : configurations des droits, soumission des demandes, calcul des soldes et intégration avec la paie.

## Fonctionnalités Clés
- **Politiques Globales** : Définition des droits annuels par pays et règles de report.
- **Bonus d'Ancienneté** : Attribution automatique de jours supplémentaires selon les années de service.
- **Congés Spéciaux** : Gestion des événements familiaux (mariage, naissance, etc.) selon la législation.
- **Libre-Service** : Soumission et suivi des demandes par les employés.
- **Digitalisation des Approbations** : Workflow hiérarchique transparent.

## Architecture & Modèles

### Configuration
- **LeavePolicy** : Cadre légal annuel (ex: 18 jours pour la RDC, règles de report fin mars).
- **SeniorityRule** : Barème de jours bonus selon l'ancienneté.
- **CircumstanceLeaveRule** : Droits spécifiques pour les événements de vie.

### Opérations
- **LeaveBalance** : État actuel des droits d'un employé pour une année donnée.
- **LeaveRequest** : Dossier de demande de congé (Annuel ou Circonstanciel).
- **LeaveRecall** : Procédure de rappel d'un employé en congé pour nécessité de service.
- **LeaveTransaction** : Historique complet de chaque mouvement (attribution, prise, expiration).
- **LeaveCarryOver** : Suivi précis des jours reportés de l'année précédente.

## Endpoints API principales

### Configuration (Admin)
- `GET /config/policies` : Lister les politiques de congés.
- `POST /config/policies` : Créer une nouvelle politique.
- `GET /config/policies/{id}/seniority-rules` : Barème d'ancienneté.
- `GET /config/policies/{id}/circumstance-rules` : Règles de congés spéciaux.

### Gestion des Demandes
- `POST /leaves` : Soumettre une demande de congé.
- `GET /leaves/my-requests` : Historique personnel.
- `PATCH /leaves/{id}/approve` : Validation (Manager/RH).
- `PATCH /leaves/{id}/reject` : Refus avec motif.

### Administration & Soldes
- `GET /leaves/balances` : Consulter les soldes (Annuel + Reports).
- `POST /leaves/admin/adjust-balance/{emp_id}` : Correction manuelle de solde.
- `GET /leaves/transactions` : Audit trail des mouvements de jours.

## Intégrations
- **Employees** : Source des profils et de l'ancienneté.
- **Payroll** : Export des absences validées pour la paie.
- **Calendar** : Décompte des jours ouvrables uniquement.

## Rapports disponibles

- **Résumé des allocations** : Par employé et année
- **Demandes en attente** : À approuver
- **Utilisation par type** : Annuel, maladie, circonstanciel
- **Prévisions** : Congés planifiés futurs
- **Solde par département** : Vue managériale
- **Audit trail** : Historique complet des modifications

## Bonnes pratiques

1. **Planification** : Encourager la planification anticipée
2. **Communication** : Notifier manager et équipe des absences
3. **Conformité** : Respecter les minimums légaux par pays
4. **Documentation** : Exiger les justificatifs pour circonstanciels
5. **Transparence** : Afficher les soldes aux employés
6. **Audit** : Conserver l'historique complet

## Considérations légales

- Respect du code du travail RDC
- Minimum 18 jours par an (RDC)
- Interdiction du paiement en remplacement en cas de non-usage
- Conservation du droit aux congés pendant suspension contrat
- Calcul correct de l'indemnité en cas de résiliation
