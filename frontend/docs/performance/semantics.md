# Sémantique : Performance

> Définitions précises des propriétés, états et événements du métamodèle.

---

## `Évaluation.status` — Les 5 états

### `EMPLOYEE_DRAFT`

**Définition** : L'évaluation a été créée par le système (automatiquement à l'activation de la campagne). L'employé peut modifier son auto-évaluation (objectifs, compétences, commentaire).

**Règles** :
- Seul l'employé concerné peut éditer
- Le manager peut voir en lecture seule (prévisualisation)
- L'employé peut soumettre → passe en `MANAGER_DRAFT`
- La soumission est irréversible

### `MANAGER_DRAFT`

**Définition** : L'employé a soumis son auto-évaluation. Le manager évalue les objectifs et compétences, ajoute son commentaire et peut ajuster la note.

**Règles** :
- Seul le manager peut éditer
- L'employé voit en lecture seule
- Le manager peut soumettre → passe en `SUBMITTED`
- Retour possible à `EMPLOYEE_DRAFT` si le manager demande une révision

### `SUBMITTED`

**Définition** : Le manager a soumis l'évaluation finale. En attente du calibrage RH.

**Règles** :
- Personne ne peut éditer (sauf RH en cas d'exception)
- RH peut calibrer → passe en `CALIBRATED`
- Calibrage automatique si pas d'action RH dans les 7 jours (copie du score brut)

### `CALIBRATED`

**Définition** : Le score a été calibré par RH. L'employé peut prendre connaissance.

**Règles** :
- L'employé peut voir l'évaluation complète avec le score calibré
- L'employé peut prendre connaissance → passe en `ACKNOWLEDGED`
- Si l'employé conteste, le statut reste `CALIBRATED` et un flag `disputed` est activé

### `ACKNOWLEDGED`

**Définition** : L'employé a pris connaissance et signé l'évaluation.

**Règles** :
- Immutable : aucune modification possible
- Visible par tous (employé, manager, RH) en lecture seule
- Clôture définitive du cycle d'évaluation pour cet employé

---

## `Évaluation.overall_score` — Score final

### Définition précise

Le score final est une **moyenne pondérée** automatique, jamais saisie manuellement :

```
overall_score = (score_objectifs × goal_weight) + (score_compétences × skill_weight)

Où `goal_weight` et `skill_weight` sont définis sur la campagne (défauts: 0.6 et 0.4).

La somme `goal_weight + skill_weight` doit être égale à 1 (normalisée automatiquement si ce n'est pas le cas).
```

### Calcul du score des objectifs

```
score_objectifs = Σ(manager_rating_i × weight_i) / Σ(weight_i)
```

- Les objectifs `CANCELLED` sont exclus
- Si `manager_rating` est absent, utiliser `employee_rating` (fallback)
- Si aucun objectif n'est noté, `score_objectifs = 0`

### Calcul du score des compétences

```
score_compétences = Σ(manager_level_i) / N
```

- Si `manager_level` est absent, utiliser `employee_level` (fallback)
- Si aucune compétence n'est évaluée, `score_compétences = 0`

### Valeurs limites

| Valeur | Signification |
|--------|--------------|
| `0` | Aucun objectif/compétence évalué |
| `1.0 - 1.9` | Insuffisant |
| `2.0 - 2.9` | En dessous des attentes |
| `3.0 - 3.9` | Satisfaisant |
| `4.0 - 4.5` | Dépassement des attentes |
| `4.6 - 5.0` | Exceptionnel |

---

## `Évaluation.manager_overall_score` — Note globale manager

### Définition

Note globale subjective saisie par le manager (1-5). Indépendante du calcul automatique. Sert de **référence** pour le calibrage.

### Différence avec `overall_score`

| Propriété | `overall_score` | `manager_overall_score` |
|-----------|----------------|------------------------|
| Calcul | Automatique | Manuel |
| Usage | Score officiel | Référence manager |
| Calibrage | Peut être ajusté | Non modifié |
| Visibilité | Tout le monde | Tout le monde |

---

## `Campagne.status` — Les 3 états

### `DRAFT`

**Définition** : La campagne est en cours de préparation par RH. Pas de visibilité pour les employés/managers.

**Règles** :
- Seul RH peut voir et modifier
- Les employés ne sont pas encore notifiés
- On peut ajouter/supprimer des participants

### `ACTIVE`

**Définition** : La campagne est en cours. Les évaluations sont visibles et éditables par les participants.

**Règles** :
- Les évaluations sont créées automatiquement pour chaque participant
- Les employés et managers peuvent accéder à leurs évaluations
- Impossible de revenir à `DRAFT`
- On peut encore ajouter des participants tardifs

### `CLOSED`

**Définition** : La campagne est terminée. Toutes les évaluations sont en lecture seule.

**Règles** :
- Aucune modification possible
- Les évaluations non soumises sont automatiquement verrouillées
- On peut rouvrir une campagne (cas exceptionnel)

---

## `Objectif.status` — Les 5 états

| État | Définition | Impact sur le score |
|------|-----------|-------------------|
| `PENDING` | Objectif en cours, pas encore évalué | Exclu du calcul |
| `ACHIEVED` | Objectif atteint | Inclus avec `rating` |
| `PARTIAL` | Objectif partiellement atteint | Inclus avec `rating` |
| `NOT_ACHIEVED` | Objectif non atteint | Inclus avec `rating` |
| `CANCELLED` | Objectif annulé (changement de priorité) | Exclu du calcul |

---

## `Objectif.weight` — Poids

### Règles

- Par défaut, tous les objectifs ont le même poids (1/N)
- La somme des poids doit être ≤ 1
- Si la somme est < 1, le poids restant est ignoré (pas de normalisation forcée)
- Le poids minimum est 0.1 (en dessous, considéré comme `CANCELLED` ? Non, simplement ignoré)

### Valeur par défaut

Si `weight` est absent ou null, on applique un poids équitable : `1 / nombre_objectifs_non_cancelled`.

---

## Calendrier et délais

### Règles temporelles

- `Campagne.start_date ≤ Campagne.end_date ≤ Campagne.submission_deadline`
- Une évaluation ne peut être soumise après `submission_deadline` (sauf exception RH)
- Le passage automatique `ACTIVE → CLOSED` se fait à `submission_deadline + 7 jours`
- Un rappel est envoyé aux employés/managers à J-7 et J-1 de la deadline

---

## Cas particuliers

### Employé sans manager

Si un employé n'a pas de manager attitré :
- L'étape `MANAGER_DRAFT` est automatiquement passée
- Le score manager est copié depuis l'auto-évaluation
- RH est notifié pour assigner un évaluateur

### Contestation

Si l'employé conteste son évaluation (statut `CALIBRATED`) :
- Un flag `disputed = true` est activé
- RH et manager sont notifiés
- Le statut reste `CALIBRATED` jusqu'à résolution
- RH peut modifier le `calibrated_score` et ajouter un commentaire
- Une fois résolu, l'employé peut `ACKNOWLEDGE`

### Évaluation multiple (co-managers)

Pas supporté en V1. L'évaluation est faite par le manager principal (N+1 direct). Les autres managers peuvent contribuer via le commentaire du manager (field `manager_comment` libre).
