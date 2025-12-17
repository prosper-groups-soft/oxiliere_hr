Parfait. Je vais procéder **comme un architecte métier**, pas comme un simple relecteur Django.

Objectif : **lister exhaustivement toutes les règles métier** qui **doivent quitter les modèles** et **vivre dans les services**, *strictement dérivées de ce que tes modèles expriment déjà* (sans invention gratuite).

Je structure par **domain**, avec :

* 🎯 **Responsabilité métier**
* 📜 **Règles explicites**
* ⚠️ **Cas limites**
* 🧱 **Service cible recommandé**

---

# 1. Salary / Contract Domain

## 🎯 Responsabilité

Gestion du **cycle de vie d’un contrat de rémunération**.

---

## 📜 Règles métier

### Création / activation de contrat

1. Un employé **ne peut avoir qu’un seul contrat actif** à la fois.
2. À la création :

   * `code` est généré automatiquement selon une séquence métier.
   * Le contrat est `is_active=True` par défaut.
3. Un contrat **CDI** :

   * N’a pas de `end_date`.
4. Un contrat **non CDI** :

   * DOIT avoir une `end_date`.
   * `start_date < end_date`.
5. La durée minimale dépend du `payment_period` :

   * MONTHLY → ≥ 30 jours
   * DAILY / PER_TASK → ≥ 1 jour
6. Un contrat ne peut pas chevaucher un autre contrat actif du même employé.
7. Les champs financiers doivent être cohérents :

   * FIXED → `base_salary` requis
   * HOURLY → `hourly_rate` requis
8. Un contrat horaire ne peut pas être MONTHLY sans règle explicite.

---

### Clôture / désactivation

9. Un contrat peut être clôturé manuellement.
10. À la clôture :

    * `is_active=False`
    * `end_date` est définie si absente.
11. Un contrat clôturé ne peut plus générer de paiement.
12. La clôture déclenche :

    * Notification RH
    * Mise à jour du `PaymentState`

---

### Notification

13. Création de contrat → notification interne.
14. Fin de contrat → notification interne.

---

### 🧱 Service cible

```text
SalaryContractService
 ├─ create_contract()
 ├─ validate_contract()
 ├─ close_contract()
 ├─ activate_contract()
 └─ notify_events()
```

---

# 2. Payment State Domain

## 🎯 Responsabilité

Planification et **orchestration temporelle des paiements**.

---

## 📜 Règles métier

15. Un contrat actif DOIT avoir un `PaymentState`.
16. `next_payment_date` est calculée à partir de :

    * `salary.start_date`
    * `payment_period`
17. Après chaque paiement :

    * `payment_cycles += 1`
    * `last_period` est mis à jour
    * `next_payment_date` est recalculée
18. Si contrat non CDI :

    * `has_next=False` lorsque `next_payment_date >= end_date`
19. Un contrat inactif → `has_next=False`.

---

### 🧱 Service cible

```text
PaymentScheduleService
 ├─ initialize()
 ├─ compute_next_date()
 ├─ advance_cycle()
 └─ stop()
```

---

# 3. Payslip (Payroll Run) Domain

## 🎯 Responsabilité

Exécuter **une période de paie**.

---

## 📜 Règles métier

### Sélection des employés

20. Seuls les employés ayant :

    * un contrat actif
    * un `payment_period` correspondant
21. Un employé ne peut apparaître qu’une fois par période.
22. Les contrats expirés avant `start_date` sont exclus.

---

### Workflow de fiche de paie

23. États possibles :

    * REVIEW → CONFIRMED → PAID
    * REVIEW → CANCELED
24. Interdictions :

    * PAID → REVIEW ❌
    * PAID → CANCELED ❌
25. CONFIRMED verrouille la liste des employés.
26. PAID verrouille définitivement les SalaryLogs.

---

### Confirmation

27. CONFIRMED :

    * Génère les `SalaryLog`
    * Lance le calcul des montants
    * Vérifie que le total global > 0
    * (Optionnel) crée la transaction comptable

---

### Paiement

28. PAID :

    * Marque tous les `SalaryLog` comme payés
    * Enregistre `paid_at`
    * Envoie notifications

---

### 🧱 Service cible

```text
PayslipWorkflowService
 ├─ create()
 ├─ select_employees()
 ├─ confirm()
 ├─ pay()
 └─ cancel()
```

---

# 4. Salary Computation Domain

## 🎯 Responsabilité

Calcul **strictement déterministe** d’un bulletin.

---

## 📜 Règles métier

### Temps de travail

29. Le temps de travail dépend :

    * des paramètres Attendance
30. Si `pay_overtime=True` :

    * calcul overtime / undertime
31. Sinon :

    * overtime ignoré

---

### Calcul brut

32. FIXED → base_salary
33. HOURLY → hourly_rate × heures travaillées
34. Heures nulles → montant = 0

---

### Heures supplémentaires

35. Si FIXED + pay_overtime :

    * overtime rémunéré au taux horaire

---

### Avances

36. Une seule avance non remboursée par employé.
37. Le remboursement :

    * ne dépasse jamais le solde restant
    * ne dépasse jamais le salaire courant
38. Le remboursement génère un `RepaymentLog`.
39. Une avance soldée est marquée `is_repaid=True`.

---

### Cotisations

40. Cotisation applicable si :

    * employee concerné OU everyone=True
    * dans la période
41. Calcul :

    * montant fixe OU pourcentage
42. Cotisation appliquée une seule fois par bulletin.

---

### Bonus

43. Bonus applicable si :

    * employee concerné OU everyone=True
    * actif
44. Bonus ajouté au brut.

---

### Résultat final

45. Ordre de calcul :

    * Brut
    * − avances
    * − cotisations
    * * bonus
46. Total ≥ 0 sinon rejet.

---

### 🧱 Service cible

```text
SalaryComputationService
 ├─ compute_time()
 ├─ compute_gross()
 ├─ apply_advances()
 ├─ apply_contributions()
 ├─ apply_bonus()
 └─ finalize()
```

---

# 5. Bonus Domain

## 🎯 Responsabilité

Attribution conditionnelle d’avantages.

---

## 📜 Règles métier

47. Un bonus peut être :

    * global (`everyone=True`)
    * ciblé
48. Si `everyone=True` :

    * aucune affectation manuelle possible.
49. Un bonus peut être :

    * temporaire (start/end)
    * permanent
50. Bonus inactif → ignoré.

---

### 🧱 Service cible

```text
BonusAssignmentService
 ├─ assign()
 ├─ unassign()
 ├─ reset()
 └─ resolve_applicable()
```

---

# 6. Social Contribution Domain

## 🎯 Responsabilité

Déductions légales.

---

## 📜 Règles métier

51. Une cotisation doit définir :

    * montant OU pourcentage (exclusif)
52. Applicabilité identique aux bonus.
53. Cotisation inactive → ignorée.
54. Cotisation calculée sur le brut courant.

---

### 🧱 Service cible

```text
ContributionService
 ├─ validate()
 ├─ assign()
 ├─ compute()
```

---

# 7. Advance / Repayment Domain

## 🎯 Responsabilité

Gestion du crédit salarié.

---

## 📜 Règles métier

55. Un employé ne peut avoir qu’une avance active.
56. Le remboursement est progressif.
57. Le pourcentage est calculé sur le montant initial.
58. Le remboursement ne crée jamais un salaire négatif.
59. Chaque remboursement est tracé.

---

### 🧱 Service cible

```text
AdvanceRepaymentService
 ├─ request()
 ├─ compute_repayment()
 ├─ apply()
```

---

# 8. Notifications Domain

## 📜 Règles métier

60. Notification lors de :

    * création de contrat
    * fin de contrat
    * paiement effectué
61. Notifications **asynchrones**.

---

### 🧱 Service cible

```text
NotificationService
 ├─ contract_created()
 ├─ contract_closed()
 ├─ salary_paid()
```

---

# Synthèse finale

Tu as **~60 règles métier explicites** déjà présentes dans tes modèles.
Ce que tu as fait est **conceptuellement très bon**, mais elles sont **au mauvais endroit**.

👉 Prochaine étape logique :

1. Je te propose **l’arborescence exacte `services/`**
2. Puis on refactorise **un domaine complet** (ex : SalaryComputation) en clean architecture

Dis-moi :
**quel domaine tu veux extraire en premier ?**
