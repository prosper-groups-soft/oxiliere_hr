# Documentation - Module Calendar

## Vue d'ensemble

Le module **Calendar** centralise la gestion des dates impactant le temps de travail et la paie. Il permet de définir les jours fériés, les fermetures exceptionnelles et les événements d'entreprise afin d'assurer l'exactitude des calculs de salaires et de présences.

## Fonctionnalités clés

- **Jours Fériés** : Configuration des fêtes nationales et locales avec récurrence annuelle.
- **Fermetures Entreprise** : Planification des arrêts collectifs (ex: congés techniques, ponts).
- **Événements Spéciaux** : Gestion des dates importantes (ex: réunions générales, formations).
- **Impact Travail** : Désignation explicite des jours chômés (non travaillables) pour automatiser la paie.
- **Périmètre Géographique** : Possibilité de définir des événements par pays ou pour l'ensemble du groupe.

## Architecture & Données

### Événements (CalendarEvent)
Chaque entrée représente une période spécifique. Les champs clés incluent :
- **Type** : Catégorie (Férié, Fermeture, Événement).
- **Statut travaillable** : Si désactivé, le jour est considéré comme non travaillé pour tout le personnel concerné.
- **Récurrence** : Permet de reconduire automatiquement un jour férié chaque année.

## Utilisation API

### Gestion des Événements
- `GET /events` : Liste chronologique des événements (filtrable par date et type).
- `POST /events` : Enregistrer un nouvel événement ou jour férié.
- `PUT /events/{id}` : Modifier les détails d'un événement existant.
- `DELETE /events/{id}` : Supprimer un événement du calendrier.

## Intégrations

Le module Calendar est une source de vérité critique pour :
- **Paie** : Calcul des jours ouvrés et détection des absences sur jours fériés.
- **Présence** : Validation automatique des pointages et des horaires.
- **Congés** : Détermination des jours à déduire du solde lors d'une demande d'absence.

## Bonnes Pratiques

1. **Anticipation** : Enregistrez tous les jours fériés nationaux dès le début de l'année civile.
2. **Précision** : Utilisez le champ "Description" pour expliquer l'origine d'une fermeture exceptionnelle.
3. **Récurrence** : Privilégiez la récurrence "Annuelle" pour les fêtes à date fixe afin de réduire la maintenance.
4. **Vidé de Cache** : Les changements sur le calendrier sont répercutés automatiquement, mais une vérification des calculs de paie est recommandée après une modification majeure.
