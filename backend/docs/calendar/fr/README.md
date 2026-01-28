# Documentation - Module Calendar

## Vue d'ensemble

Le module **Calendar** gère le calendrier d'événements affectant les horaires de travail et la paie. Il inclut les jours fériés, les fermetures d'entreprise, les événements récurrents et les périodes spéciales qui impactent le calcul des salaires et absences.

## Fonctionnalités principales

### 1. Événements calendaires
- Jours fériés nationaux et locaux
- Fermetures d'entreprise
- Événements spéciaux (formation, conférence)
- Dates de validité (début, fin)
- Horaires optionnels pour événements partiels

### 2. Récurrence d'événements
- Événements uniques
- Récurrence annuelle (même date chaque année)
- Récurrence variable (ex: 2ème lundi de janvier)
- Gestion des exceptions

### 3. Périmètre géographique
- Événements globaux (toute l'entreprise)
- Événements par pays
- Événements par département
- Événements par site/bureau

### 4. Impact sur le travail
- Jour travaillable ou non
- Compensation requise ou non
- Prime spéciale associée
- Affichage du statut (Planifié, Confirmé, Annulé)

### 5. Intégration avec paie et présence
- Affecte le calcul des jours travaillés
- Déduction du solde de congés (si applicable)
- Impact sur les heures supplémentaires
- Ajustement des horaires de travail

## Architecture

### Modèles principaux

#### CalendarEvent
Événement sur le calendrier
- Nom de l'événement
- Code unique généré automatiquement
- Type (Jour férié, Fermeture, Événement, Congé collectif)
- Dates (début, fin)
- Horaires optionnels
- Récurrence (Aucune, Annuelle, Mensuelle, Hebdomadaire)
- Pays applicable (optionnel)
- Statut (En attente, Confirmé, Annulé)
- Description

### Énumérations

- **CalendarEventType** : PUBLIC_HOLIDAY, COMPANY_CLOSURE, COMPANY_EVENT, COLLECTIVE_LEAVE, SPECIAL_HOURS, OTHER
- **CalendarEventRecurrence** : NONE, DAILY, WEEKLY, MONTHLY, YEARLY
- **CalendarEventStatus** : PENDING, CONFIRMED, CANCELLED, RESCHEDULED
- **CountryCode** : ISO 2-letter codes

## Endpoints API

### Événements calendaires

```
GET    /api/v1/calendar/events                 - Lister tous les événements
POST   /api/v1/calendar/events                 - Créer un événement
GET    /api/v1/calendar/events/{id}            - Détail d'un événement
PUT    /api/v1/calendar/events/{id}            - Mettre à jour
DELETE /api/v1/calendar/events/{id}            - Supprimer
PATCH  /api/v1/calendar/events/{id}/confirm    - Confirmer
PATCH  /api/v1/calendar/events/{id}/cancel     - Annuler
```

### Filtrage par période

```
GET    /api/v1/calendar/events?start_date=2026-01-01&end_date=2026-12-31 - Par période
GET    /api/v1/calendar/events?country=CD     - Par pays
GET    /api/v1/calendar/events?type=PUBLIC_HOLIDAY - Par type
GET    /api/v1/calendar/events?status=CONFIRMED - Par statut
```

### Vues consolidées

```
GET    /api/v1/calendar/working-days/{year}    - Jours travaillés par année
GET    /api/v1/calendar/working-days/{year}/{month} - Par mois
GET    /api/v1/calendar/holidays/{year}/{country} - Jours fériés
GET    /api/v1/calendar/company-closures       - Fermetures d'entreprise
```

## Cas d'usage courants

### 1. Créer un jour férié national
```json
POST /api/v1/calendar/events
{
  "name": "Fête d'indépendance",
  "event_type": "PUBLIC_HOLIDAY",
  "country_code": "CD",
  "start_date": "2026-06-30",
  "is_workable": false,
  "recurrent": "YEARLY",
  "status": "CONFIRMED"
}
```

### 2. Créer une fermeture d'entreprise
```json
POST /api/v1/calendar/events
{
  "name": "Fermeture estivale",
  "event_type": "COMPANY_CLOSURE",
  "start_date": "2026-08-01",
  "end_date": "2026-08-15",
  "is_workable": false,
  "status": "PENDING"
}
```

### 3. Créer un événement ponctuel
```json
POST /api/v1/calendar/events
{
  "name": "Réunion générale annuelle",
  "event_type": "COMPANY_EVENT",
  "start_date": "2026-03-15",
  "start_time": "09:00:00",
  "end_time": "17:00:00",
  "is_workable": true,
  "status": "CONFIRMED"
}
```

### 4. Créer une récurrence spéciale (2ème lundi)
```json
POST /api/v1/calendar/events
{
  "name": "Jour férié local spécial",
  "event_type": "PUBLIC_HOLIDAY",
  "country_code": "CD",
  "start_date": "2026-01-01",
  "recurrent": "MONTHLY",
  "is_workable": false,
  "status": "CONFIRMED",
  "description": "Tous les 2èmes lundis du mois"
}
```

### 5. Consulter les jours travaillés du mois
```json
GET /api/v1/calendar/working-days/2026/01
Response:
{
  "month": 1,
  "year": 2026,
  "total_days": 31,
  "weekend_days": 8,
  "public_holidays": 2,
  "company_closures": 0,
  "working_days": 21,
  "half_days": 0
}
```

## Types d'événements et leurs impacts

### Jour férié (PUBLIC_HOLIDAY)
- **is_workable** : false
- **Impact paie** : Pas de déduction de congés (jour payé)
- **Effectif** : Compte comme jour travaillé pour paie
- **Récurrence** : Souvent annuelle

### Fermeture d'entreprise (COMPANY_CLOSURE)
- **is_workable** : false
- **Impact paie** : Peut être payé ou non selon politique
- **Effectif** : Tous les employés affectés
- **Récurrence** : Aucune (événement unique ou multi-jours)

### Événement spécial (COMPANY_EVENT)
- **is_workable** : true/false selon événement
- **Impact paie** : Aucun impact si travaillable
- **Effectif** : Peut être sélectif (certains employés)
- **Horaires** : Heures spéciales possibles

### Congé collectif (COLLECTIVE_LEAVE)
- **is_workable** : false
- **Impact paie** : Affecte le calcul des jours travaillés
- **Effectif** : Peut être par département ou global
- **Récurrence** : Aucune (événement unique)

## Calendrier de référence par pays

### RDC (Code CD)
```
- 1er janvier : Nouvel an (PUBLIC_HOLIDAY)
- 17 janvier : Assassinat de Laurent Désiré Kabila (PUBLIC_HOLIDAY)
- Lundi de Pâques : Easter Monday (PUBLIC_HOLIDAY)
- 1er mai : Fête du Travail (PUBLIC_HOLIDAY)
- 17 mai : Journée de la Libération (PUBLIC_HOLIDAY)
- 30 juin : Fête d'indépendance (PUBLIC_HOLIDAY)
- 1er août : Parents' Day (PUBLIC_HOLIDAY)
- 15 août : Assomption (PUBLIC_HOLIDAY)
- 25 décembre : Noël (PUBLIC_HOLIDAY)
```

## Intégrations

- **Module Payroll** : Affecte calcul des jours travaillés
- **Module Attendance** : Exclut les jours fériés du calcul
- **Module Leaves** : Détermine si absence = jour de congé
- **Module Jobs** : Horaires par département affectés
- **Rapports** : Effectifs, coûts de paie

## Processus de gestion des événements

1. **Création** : Créer l'événement avec détails
2. **Vérification** : Valider les dates et impacts
3. **Confirmation** : Approuver et confirmer
4. **Publication** : Diffuser aux employés
5. **Exécution** : Appliquer les règles à la date
6. **Clôture** : Archiver après période

## Bonnes pratiques

1. **Planification** : Ajouter les jours fériés au début de l'année
2. **Coordination** : Vérifier avec RH/Paie avant création
3. **Clarté** : Description claire de chaque événement
4. **Récurrence** : Utiliser les récurrences pour événements répétitifs
5. **Communication** : Notifier les employés des changements
6. **Révision** : Vérifier avant la date de l'événement

## Validation des données

- Dates cohérentes (fin ≥ début)
- Type d'événement valide
- Pays valide ou vide (global)
- Statut valide
- Récurrence compatible avec dates
- Si horaires : format heure valide, fin ≥ début

## Rapports disponibles

- **Calendrier annuel** : Vue complète année
- **Jours fériés** : Par pays et année
- **Jours travaillés** : Calcul des jours ouvrables
- **Fermetures planifiées** : Agenda des fermetures
- **Impact paie** : Analyse des jours sur salaire

## Support et dépannage

Pour toute question ou problème :
1. Vérifier la cohérence des dates
2. S'assurer que la récurrence est appropriée
3. Consulter l'impact sur autres modules
4. Valider la raison de l'événement
5. Contacter Paie/RH avant modification d'événements passés
