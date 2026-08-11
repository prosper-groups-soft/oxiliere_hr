# Problèmes Connus et Travaux Futurs

> Inventaire des limitations identifiées, bugs reportés et améliorations à faire.
> Ce fichier sert à ne pas oublier ce qui a été repéré mais pas encore corrigé.

---

## 1. Sélection d'un autre employé (ReviewSheet création)

**Problème** : Dans la création d'évaluation (`ReviewSheet` en mode création), n'importe quel utilisateur peut sélectionner n'importe quel employé via le sélecteur, même si ce n'est pas lui.

**État** : 🔴 Non résolu

**Cause racine** : L'utilisateur Django authentifié (`request.user`) n'est pas lié à un modèle `Employee`. Il n'y a donc pas de mécanisme pour dire "cet employé s'auto-évalue" vs "un RH crée pour quelqu'un d'autre".

**Solution envisagée** :
1. Ajouter une relation `User ↔ Employee` (OneToOneField ou ForeignKey)
2. Quand un employé crée une évaluation, pré-sélectionner son propre profil et masquer le sélecteur
3. Quand un RH ou admin crée, garder le sélecteur avec tous les employés
4. Cela nécessite un système de rôles (permissions) pour distinguer les cas

**Priorité** : Moyenne (bloqué par la gestion des rôles)

---

## 2. Poids des objectifs en mode manager (GoalEditor)

**État** : ✅ Résolu

**Solution** : Slider (range 0-100%, pas de 5%) visible uniquement en mode `manager`. L'employé voit le poids en lecture seule avec label "(automatique)" — distribution équitable 1/N.

---

## 3. Affichage des poids de la campagne

**État** : ✅ Résolu

**Solution** : Les poids `goal_weight` / `skill_weight` définis sur la campagne sont affichés sous forme de badges "Poids : X%" au-dessus des éditeurs respectifs (GoalEditor, SkillEditor), aussi bien en création qu'en édition.

---

## 4. calibrated_score doit prendre le pas sur overall_score

**État** : ✅ Résolu

**Solution** : `displayScore = calibrated_score ?? overall_score` — le score calibré écrase le score calculé s'il existe. Implémenté dans `normalizeReview` et utilisé dans `ReviewCard` et `ReviewDetail`.

---

## 5. Template de campagne (snapshot)

**État** : ✅ Résolu

**Solution** : `default_goals` et `default_skills` sur `Campaign`. Copiés (snapshot) dans chaque review à la création via `create_review`, `activate_campaign`, et `add_participant`. L'employé peut ensuite modifier, supprimer ou ajouter librement.

---

## Dernière mise à jour

- **Date** : Juillet 2026
- **Version** : 1.0
