# F4 — Demande d'Avance par un Employé

> **Écrans impliqués :** S6 (avances), S5 (saisie variables), S3 (run en cours)

---

## Contexte

Un employé souhaite obtenir une **avance sur salaire**. Le flux décrit le processus complet :

1. **Demande** (faite par l'employé ou le gestionnaire pour lui)
2. **Approbation** (par N+1 ou RH selon le montant)
3. **Intégration** dans le cycle de paie via S5
4. **Remboursement** automatique sur les mois suivants

> **Note :** La demande par l'employé lui-même se ferait depuis le portail employé (module séparé). Ici on décrit le traitement côté RH.

---

## Diagramme de flux

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DEMANDE D'AVANCE SUR SALAIRE                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐
│ EMPLOYÉ  │  Jean Mbemba demande une avance de 500 000 CDF
│ DEMANDE  │  Motif : "Urgence familiale - frais médicaux"
└─────┬────┘  Via le portail employé (ou le gestionnaire via S6)
      │
      ▼
┌──────────┐
│ S6       │  Le gestionnaire (ou le système) reçoit la demande
│ LISTE    │  
└─────┬────┘  → La demande apparaît avec le statut PENDING
      │
      ▼
┌──────────┐
│ S6       │ 
│ APPROBA  │  **Si montant ≥ 200 000 CDF :**
│ TION     │  → Notification envoyée à N+1 / RH
└─────┬────┘  → N+1 se connecte → S6 → Détail avance → [Approuver] / [Rejeter]
      │
      ▼
┌──────────┐
│ S6       │  Décision :
│ RÉSULTAT │  
│          │  ✅ Approuvée → Plan de remboursement généré
│          │  ❌ Rejetée → Motif stocké, notification à l'employé
└─────┬────┘
      │
      ▼
┌──────────┐
│ S5       │  Si un cycle est en cours pour la période :
│ INTÉGRA  │  → L'échéance du mois apparaît automatiquement
│ TION     │  → Montant pré-rempli dans les déductions
└─────┬────┘  → Le gestionnaire peut ajuster si besoin
      │
      ▼
┌──────────┐
│ S3       │  Au moment du calcul :
│ CALCUL   │  → L'échéance est déduite du salaire net
│          │  → Le solde de l'avance est mis à jour
└──────────┘  → Prochaine échéance planifiée
```

---

## Règles d'approbation

| Montant | Approbation | Délai max |
|---------|-------------|-----------|
| < 200 000 CDF | Automatique | Immédiat |
| 200 000 → 1 000 000 CDF | N+1 | 48h |
| > 1 000 000 CDF | N+1 + RH | 72h |

---

## Notifications

| Événement | Destinataire | Canal |
|-----------|-------------|-------|
| Demande soumise | Gestionnaire RH | Notification in-app |
| Approbation requise | N+1 / RH | Notification in-app + email |
| Demande approuvée | Employé | Notification in-app |
| Demande rejetée | Employé | Notification in-app + motif |
| Échéance imminente | Gestionnaire RH (si S5 pas encore ouvert) | Notification in-app (J-2) |
| Défaut de paiement | Gestionnaire RH | Alerte dans S6 |

---

## Impact sur le cycle mensuel (F1)

| Étape | Impact |
|-------|--------|
| S2 Création | Aucun (l'avance est postérieure à la création) |
| S5 Saisie variables | Échéance pré-remplie dans la zone "Avances et Déductions" |
| S7 Validation | Aucune anomalie spécifique (sauf si avance > net) |
| S3 Détail | Solde de l'avance visible dans le détail du bulletin |
| S4 Bulletin | Ligne "Avance sur salaire" dans la section Déductions |
