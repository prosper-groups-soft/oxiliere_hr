# Documentation - Module Présences

## Vue d'ensemble

Le module **Présences** assure le suivi du temps de travail, la gestion des horaires et la sécurisation des données pour la paie. Il automatise le calcul des heures effectives, des heures supplémentaires et des absences pour garantir une gestion RH précise et fluide.

## Valeur Métier

- **Précision de la Paie** : Calcul automatique des heures basé sur les pointages réels.
- **Contrôle des Coûts** : Suivi rigoureux des heures supplémentaires et des retards.
- **Conformité Légale** : Application systématique des politiques de repos et de durée de travail.
- **Sécurisation des Données** : Système de verrouillage des périodes pour figer les données avant la paie.

## Architecture RH

### Configuration & Calendriers
- **Politiques de Travail** : Modèles hebdomadaires définissant les horaires cibles et les pauses.
- **Détails de Shift** : Configuration précise de chaque journée (heures de début/fin, flexibilité).
- **Assignations & Rotations** : Attribution des cycles de travail aux employés avec gestion automatique des roulements.

### Suivi Opérationnel
- **Pointages (Punches)** : Enregistrement des entrées, sorties et pauses via badgeuse, mobile ou portail web.
- **Registre Journalier** : Vue consolidée de la présence sur un jour donné (taux d'absence, effectif attendu).
- **Feuilles de Temps (Timesheets)** : Synthèse individuelle validée par le système pour chaque journée de travail.

### Sécurité & Audit
- **Verrouillage de Période** : Mécanisme bloquant toute modification sur les données passées pour sécuriser la clôture RH.
- **Service de Validation** : Détection automatique des anomalies (pointages oubliés, chevauchements, durées excessives).

## Utilisation des API

### Services Principaux
- `/api/v1/attendance/punch` : Gestion des pointages en temps réel.
- `/api/v1/attendance/registry` : Accès aux journaux de présence et gestion des verrouillages.
- `/api/v1/attendance/scheduling` : Configuration des politiques de travail et des rotations.
- `/api/v1/attendance/maintenance` : Outils automatisés de fermeture des pointages et détection des absences.

## Bonnes Pratiques RH

1. **Vérification Quotidienne** : Utiliser le Registre Journalier pour identifier les anomalies dès qu'elles surviennent.
2. **Maintenance Automatisée** : Lancer régulièrement les tâches de clôture des pointages oubliés pour maintenir une base propre.
3. **Verrouillage Pré-Paie** : Toujours figer la période avant de générer les éléments de salaire pour éviter toute modification ultérieure.
4. **Audit de Cohérence** : Utiliser le service de validation sur les feuilles de temps critiques avant validation finale.
