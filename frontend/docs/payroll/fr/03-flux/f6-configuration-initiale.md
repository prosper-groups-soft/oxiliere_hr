# F6 — Configuration Initiale

> **Écrans impliqués :** S8 (configuration), S10 (éléments contrat), `exchange-rates.md`, `catalogue.md`

---

## Contexte

Flux de **mise en place initiale** du module paie. Il est exécuté une fois (ou après une réinitialisation) 
pour configurer tous les paramètres avant le premier cycle.

---


## Diagramme de flux

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   CONFIGURATION INITIALE DU MODULE PAIE                     │
│    (Étape préalable au premier cycle de paie)                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌────────────────┐
│ ÉTAPE 1        │  Paramètres légaux (S8)
│ LÉGAL          │  → SMIG : 70 000 CDF
└───────┬────────┘  → CNSS : taux 4% employeur / 3,5% salarié / plafond 150 000
        │           → IPR : barème progressif (0% → 30%)
        │           → ONEM : 10 000 CDF / employé
        │           → INPP : 10 000 CDF / employé
        │           → [Sauvegarder]
        │
        ▼
┌────────────────┐
│ ÉTAPE 2        │  Taux de change (S8)
│ TAUX           │  → URL API BCC configurée
└───────┬────────┘  → Mode fallback défini
        │           → [Tester la connexion]
        │           → [Forcer la récupération] → 2 850,00 CDF/USD
        │           → [Sauvegarder]
        │
        ▼
┌────────────────┐
│ ÉTAPE 3        │  Catalogue des éléments de paie (S8)
│ CATALOGUE      │  → Vérifier les éléments par défaut (catalogue.md)
└───────┬────────┘  → Ajouter/modifier les éléments spécifiques à l'entreprise
        │           → Définir les règles d'imposition
        │           → [Sauvegarder]
        │
        ▼
┌────────────────┐
│ ÉTAPE 4        │  Paramètres du cycle (S8)
│ CYCLE          │  → Jour d'échéance : 5
└───────┬────────┘  → Méthode de paiement par défaut : virement
        │           → Jours de rappel : J-7, J-3, J-1
        │           → Validation obligatoire ? ✅
        │           → [Sauvegarder]
        │
        ▼
┌────────────────┐
│ ÉTAPE 5        │  Vérification des contrats existants
│ CONTRATS       │  → Liste des contrats actifs sans éléments de paie
└───────┬────────┘  → Pour chaque contrat, configurer éléments via S10
        │           → ⚠️ N contrats sans éléments de paie
        │
        ▼
┌────────────────┐
│ ÉTAPE 6        │  Test du premier cycle
│ TEST           │  → Créer un run test (S2)
└───────┬────────┘  → Lancer le calcul sur 1-2 employés (S7)
        │           → Vérifier les bulletins (S4)
        │           → Ajuster si nécessaire
        │
        ▼
┌────────────────┐
│ ✅ PRÊT        │  Le module est configuré et opérationnel
│ OPÉRATIONNEL   │  → Les cycles mensuels peuvent commencer
└────────────────┘
```

---

## Checklist de configuration

| # | Élément | Statut | Critère |
|---|---------|--------|---------|
| 1 | SMIG | ✅ | ≥ valeur légale (70 000 CDF) |
| 2 | CNSS paramètres | ✅ | Taux + plafond conformes |
| 3 | IPR barème | ✅ | Barème progressif à jour |
| 4 | ONEM / INPP | ✅ | Montants configurés |
| 5 | API BCC | ✅ | Connexion testée OK |
| 6 | Fallback taux | ✅ | Mode défini |
| 7 | Catalogue | ✅ | Éléments définis |
| 8 | Cycle params | ✅ | Jalon d'échéance configuré |
| 9 | Contrats | ⚠️ | 5 contrats sans éléments |

> Cette checklist est affichée dans S8 tant que la configuration n'est pas complète.

---

## Erreurs fréquentes

| Problème | Cause | Solution |
|----------|-------|----------|
| API BCC injoignable | URL incorrecte ou pas d'accès internet | Vérifier l'URL, configurer le fallback manuel |
| Aucun taux disponible | Pas de fetch BCC ni de taux manuel | Forcer le fetch ou saisir manuellement |
| Contrats sans éléments | Employés créés avant la config | Configurer S10 pour chaque contrat |
| Barème IPR incomplet | Tranches manquantes | Ajouter toutes les tranches (0 à 30 %) |
| CNSS plafond trop bas | Plafond < SMIG | Corriger le plafond (min 150 000 CDF) |
