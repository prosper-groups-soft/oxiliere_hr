# Décisions Architecturales & Rétrospectives

> Ce document trace les décisions clés, ce qui a fonctionné, ce qui a échoué, et pourquoi.
> Il sert à éviter de répéter les mêmes erreurs et à capitaliser sur les bonnes pratiques.

---

## Principe

Une décision architecturale est documentée quand :
- Un choix important a été fait entre plusieurs options
- Un pattern a causé (ou évité) un problème récurrent
- Une approche a échoué et mérite d'être retenue comme leçon

---

## 1. Mode employee / manager

### Décision

**Option choisie** : Prop `mode` explicite (`'employee' | 'manager'`) passée par le parent.

| Option | Verdict | Raison |
|--------|---------|--------|
| A. Prop explicite `mode="manager"` | ✅ **Adopté** | Clair, prévisible, testable |
| B. Auto-détection via `review.status` | ❌ Rejeté | Trop implicite, cas spéciaux (admin, prévisualisation) impossibles |
| C. Les deux combinés | ❌ Rejeté | Complexité inutile, deux sources de vérité |

### Leçon

**Ne pas mélanger détection automatique et prop explicite.** Si le parent sait quel mode il veut, qu'il le passe. La détection automatique semble "magique" mais devient un cauchemar en debug.

---

## 2. Templates de campagne (snapshot vs référence)

### Décision

**Option choisie** : Template RH sur la campagne + **snapshot** copié dans chaque review à la création.

### Pourquoi snapshot plutôt que référence ?

- **Snapshot** = les données sont copiées dans la review au moment de sa création. Modifier le template après n'affecte pas les reviews existantes.
- **Référence** = la review pointe vers le template. Modifier le template change les reviews passées (régression historique).

### Règle

> Si une campagne peut être modifiée pendant qu'elle est active, le snapshot est indispensable. 
> 
> Chez nous, les campagnes ne sont modifiables qu'en **DRAFT**. Donc snapshot ou référence revient au même en pratique — mais le snapshot est plus sûr et plus prévisible.

### Ouvertures possibles

- L'employé peut **supprimer** des éléments du template qui ne s'appliquent pas
- L'employé peut **ajouter** ses propres objectifs en plus
- Le template sert de **socle**, pas de cage

### Leçon

**Snapshooter les templates au moment de l'instanciation.** C'est le pattern "value object" : une fois la review créée, elle est indépendante. Ça évite les effets de bord et préserve l'historique.

---

## 3. Un seul modèle d'évaluation (pas deux)

### Décision

Il n'y a **pas** deux évaluations séparées (employé vs manager). Il y a **une** évaluation avec deux jeux de champs :

```
PerformanceReview
├── goals              → Objectifs employé (remplis en mode employee)
├── goals_manager      → Objectifs manager (remplis en mode manager)
├── skills             → Compétences employé
├── skills_manager     → Compétences manager
├── employee_comment
├── manager_comment
└── overall_score      → Calculé automatiquement (fallback employé → manager)
```

### Leçon

**Un concept = une entité, même si plusieurs personnes contribuent.** La séparation est dans les colonnes, pas dans les lignes. C'est plus simple pour les requêtes, l'historique et l'UI.

---

## 4. Score calculé vs score calibré

### Décision

Le `overall_score` est **toujours calculé automatiquement** (formule mathématique). 
Le `calibrated_score` est saisi par RH et **remplace** l'`overall_score` dans l'affichage s'il est présent.

### Règle d'affichage

```typescript
displayScore = calibrated_score ?? overall_score
// ↑ Si calibré, on affiche le calibré. Sinon le calculé.
```

### Leçon

**Un score ne doit jamais être saisi manuellement comme valeur finale.** Le `manager_overall_score` est une "note indicative" distincte du score officiel. Ça permet au manager de donner son avis subjectif sans casser l'objectivité du calcul automatique.

---

## 5. Ce qui a échoué / Ce qui a marché

### ❌ A échoué

| Échec | Pourquoi | Leçon |
|-------|----------|-------|
| Auto-détection du mode via statut | Pas assez flexible pour les cas admin | ✅ Toujours passer une prop explicite |
| Tentative de deux modèles séparés (employee_review + manager_review) | Complexité inutile, duplication | ✅ Un seul modèle avec deux jeux de colonnes |
| Validation côté frontend seulement | Bugs silencieux quand le backend rejette | ✅ Toujours valider au backend aussi |

### ✅ A marché

| Succès | Pourquoi |
|--------|----------|
| `mode` prop explicite dans ReviewSheet | Simple, compréhensible, testable |
| Snapshot des templates | Pas de régression historique, flexible |
| `displayScore` virtuel | Centralise la logique d'affichage au lieu de la disperser |
| Goals + goals_manager avec fallback | Le manager peut reprendre ou ignorer l'auto-évaluation |
| Mode employee → manager → lecture seule | Cycle de vie clair, chaque étape a son mode |

---

## 6. Architecture des données

### Structure validée

```
Campaign
├── default_goals / default_skills  ← Template (optionnel, snapshot)
├── goal_weight / skill_weight       ← Poids pour le calcul du score
│
└── PerformanceReview (1 par employé)
    ├── goals / goals_manager        ← Objectifs (deux versions)
    ├── skills / skills_manager      ← Compétences (deux versions)
    ├── employee_comment / manager_comment
    ├── overall_score                ← Calculé automatiquement
    ├── calibrated_score             ← Ajusté par RH (prend le pas)
    ├── manager_overall_score        ← Note indicative du manager
    └── status                       ← Cycle de vie en 5 étapes
```

### Règles de nommage

- Les champs **employé** sont sans suffixe : `goals`, `skills`, `employee_comment`, `employee_rating`, `employee_level`
- Les champs **manager** ont le suffixe `_manager` : `goals_manager`, `skills_manager`, `manager_comment`, `manager_rating`, `manager_level`

---

## 7. Vocabulaire normalisé

| Terme | Signification | À ne pas confondre avec |
|-------|---------------|------------------------|
| **Mode** | Qui édite : `'employee'` ou `'manager'` | Le statut de l'évaluation |
| **Statut** | Où en est le cycle de vie : `EMPLOYEE_DRAFT → MANAGER_DRAFT → SUBMITTED → CALIBRATED → ACKNOWLEDGED` | Le mode d'édition |
| **Template** | Objectifs/compétences par défaut définis par RH sur la campagne | Les données réelles de la review |
| **Snapshot** | Copie indépendante du template au moment de la création | Une référence dynamique qui évoluerait avec le template |
| **Score** | Valeur numérique calculée ou calibrée | La note indicative du manager |

---

## Dernière mise à jour

- **Date** : Juillet 2026
- **Version** : 1.1
- **Responsable** : Développeur principal Oxilière HR

---

## 8. Conception d'interfaces "parlantes"

### Principe

Une interface "parlante" est une interface qui **communique avec l'utilisateur comme un humain**, pas comme une machine. Elle ne se contente pas d'afficher des données, elle **explique, guide et rassure**.

### Règles retenues

| Règle | Exemple concret |
|-------|----------------|
| **Pas d'états vides silencieux** | "Aucun objectif renseigné par l'employé" plutôt qu'une liste blanche |
| **Messages adaptés au contexte** | Si l'employé n'a pas encore rempli ses objectifs : "{prenom} n'a pas encore renseigné ses objectifs." |
| **Labels humains, pas techniques** | "Manager référent" plutôt que "Évaluateur (manager)" |
| **Verbes d'action plutôt que noms** | "Créer une évaluation" plutôt que "Nouvelle évaluation" |
| **Placeholders contextuels** | "Auto-évaluation..." / "Évaluation manager..." selon le mode |
| **Politesse et guidance** | "Veuillez choisir un employé" plutôt que "L'employé est requis" |
| **Séparateurs pour les actions destructives seulement** | Un seul séparateur avant "Supprimer" |

### Anti-patterns à éviter

- "est requis" → donne l'impression d'une erreur plutôt que d'un guidage
- Les libellés génériques comme "Soumettre la notation" → "Transmettre l'évaluation" est plus humain
- Les termes techniques sans contexte comme "Calibrer" → "Calibrer le score"
- Les états vides avec juste "Aucun" sans préciser *quoi*

### Leçon

> Le meilleur indicateur qu'une interface parle est celui-ci : **un utilisateur non formé doit pouvoir comprendre ce qui se passe et quoi faire sans lire la documentation.**
>
> Traduire chaque message en se demandant : "Est-ce que ma mère comprendrait ce que ça veut dire ?"
