# F1 — Cycle Mensuel Complet (flux principal)

> **Écrans impliqués :** S1 → S2 → S5 → S7 → S3 → S4 → S3 (clôture)

---

## Résumé

Flux principal du module paie. Il décrit le cycle mensuel typique du 1er au 5 du mois suivant, avec les étapes de création, 
saisie, validation, calcul, distribution et clôture.

---

## Diagramme de flux

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CYCLE MENSUEL DE PAIE (J +1 à J+30)                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌────────┐
│  S1    │  J+1 : Le gestionnaire arrive sur la Liste des exécutions
└───┬────┘
    │
    ▼
┌────────┐
│  S2    │  J+1 : Création du run
│  CRÉA  │  → Sélection période (Juin 2026)
│  TION  │  → Vérification doublon (pas de run existant)
└───┬────┘  → Sélection taux de change (BCC 2 850,00)
    │       → Aperçu employés (45 actifs)
    │       → Création → Run en DRAFT
    │
    ▼
┌────────┐
│  S5    │  J+1 à J+25 : Saisie des variables
│  SAISIE│  → Mode individuel : navigation employé par employé
│  VARIAB│  → Saisie HS, absences, primes exceptionnelles
└───┬────┘  → Mode groupé : lot de primes identiques
    │       → Cache local toutes les 30s
    │       → Sauvegarde régulière
    │
    ▼
┌────────┐
│  S7    │  J+25 : Validation
│  VALI  │  → Synthèse : totaux bruts, nets, charges
│  DATION│  → Revue des anomalies
└───┬────┘  → Si anomalies : correction retour S5
    │       → Si OK : lancement du calcul
    │
    ▼
┌────────┐  PROCESSING
│  CALCUL│  → Pipeline de calcul (5-30 secondes)
│  PIPELI│  → Étape 1 : Collecte (contrats, éléments, absences)
│  NE    │  → Étape 2 : Brut (base + primes + HS)
└───┬────┘  → Étape 3 : Charges (CNSS, ONEM, INPP)
    │       → Étape 4 : IPR (barème progressif)
    │       → Étape 5 : Net (brut - déductions - avances)
    │       → Génération des bulletins PDF
    │
    ▼
┌────────┐
│  S3    │  J+25 : Run COMPLETED
│  DÉTAIL│  → Statuts des bulletins : CALCULÉ
│  RUN   │  → Vérification rapide des résultats
└───┬────┘  → Téléchargement des bulletins en lot
    │       → Actions par employé : voir S4, corriger, etc.
    │
    ▼
┌────────┐
│  S4    │  J+25 à J+28 : Vérification individuelle
│  FICHE │  → Consultation des bulletins
│  PAIE  │  → Mode normal et audit
└───┬────┘  → Corrections si nécessaire (→ S5)
    │
    ▼
┌────────┐
│  PAIE  │  J+28 : Paiement (hors module)
│  MENT  │  → Export virement bancaire / chèques
└───┬────┘  → Distribution des bulletins papier
    │
    ▼
┌────────┐
│  S3    │  J+28 : Marquage PAYÉ
│  CLÔTU │  → Changement statut : COMPLETED → PAID
│  RE    │  → Run verrouillé (lecture seule)
└────────┘  → Archivage automatique
```

---

## Rôles impliqués

| Étape | Rôle | Actions |
|-------|------|---------|
| S2 Création | Gestionnaire paie | Paramètres du run |
| S5 Saisie | Gestionnaire paie | Saisie des variables |
| S7 Validation | Gestionnaire paie (ou N+1) | Revue + validation |
| S3 Détail | Gestionnaire paie | Vérification |
| S4 Bulletin | Gestionnaire paie, Employé | Consultation |
| Paiement | Comptabilité | Virement |
| Clôture | Gestionnaire paie | Archivage |

---

## Règles temporelles

| # | Règle | 
|---|-------|
| 1 | Le cycle débute le **1er du mois** (J+1) |
| 2 | La saisie des variables (S5) est ouverte jusqu'au **25 du mois** |
| 3 | La validation (S7) a lieu le **25-26** |
| 4 | Le calcul est lancé le **26** |
| 5 | La vérification (S4) se fait le **26-27** |
| 6 | Le paiement est effectué le **28** (ou dernier jour ouvré avant) |
| 7 | La clôture est automatique après marquage PAYÉ |

Ces dates sont configurables dans **S8 Configuration → Cycle**.

---

## Gestion des erreurs dans le flux

```
Étape S7 : Anomalies bloquantes
├── → Comportement normal : blocage du lancement
├── → Action : retour en S5 pour corrections
└── → Action alternative : forçage avec commentaire

Étape Pipeline : Échec de calcul
├── → Le run repasse en DRAFT
├── → Un message d'erreur est affiché avec la cause
└── → Les données S5 sont conservées

Étape S4 : Correction après calcul
├── → Le bulletin passe en CORRECTION
├── → Les variables sont modifiables (S5)
└── → Un recalcul partiel est nécessaire
```
