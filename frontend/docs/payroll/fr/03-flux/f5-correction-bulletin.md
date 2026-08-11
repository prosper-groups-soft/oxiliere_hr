# F5 — Correction de Bulletin

> **Écrans impliqués :** S4 (fiche de paie), S5 (saisie variables), S3 (run detail)

---

## Contexte

Un bulletin contient une erreur **après** que le calcul a été effectué. Le gestionnaire doit :

1. **Corriger** les données erronées
2. **Recalculer** le bulletin
3. **Conserver l'audit trail** de la correction
4. **Optionnellement** produire un bulletin rectificatif

Deux types de correction :
- **Correction simple** : modification puis recalcul dans le même cycle
- **Bulletin rectificatif** : correction sur un cycle clôturé (mois suivant)

---

## Diagramme de flux — Correction simple (même cycle)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              CORRECTION SIMPLE (cycle en cours, non PAYÉ)                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐
│ S4       │  Le gestionnaire consulte le bulletin de Jean Mbemba
│ CONSULT  │  → Détecte une erreur : absence non déduite
└─────┬────┘
      │
      ▼
┌──────────┐
│ S4       │  Clic sur [✏️ Corriger]
│ ACTION   │  
└─────┬────┘  → Le bulletin passe en CORRECTION
      │       → L'employé est déverrouillé pour modification
      │
      ▼
┌──────────┐
│ S5       │  Le gestionnaire est redirigé vers S5
│ MODIF    │  → Les champs sont ré-éditables
└─────┬────┘  → Correction du nombre de jours travaillés
      │       → [Sauvegarder]
      │
      ▼
┌──────────┐
│ S4 ou S3 │  Le bulletin est marqué DRAFT
│ RECALCUL │  
└─────┬────┘  → [Recalculer] (depuis S4 ou S3)
      │       → Le pipeline s'exécute pour cet employé uniquement
      │
      ▼
┌──────────┐
│ S4       │  ✅ Bulletin recalculé
│ RÉSULTAT │  → Statut : CORRECTED
└──────────┘  → La mention "Bulletin rectifié" apparaît en en-tête
```

---

## Diagramme de flux — Bulletin rectificatif (cycle clôturé)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│            BULLETIN RECTIFICATIF (cycle clôturé, statut PAID)              │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐
│ S3       │  Le gestionnaire consulte le run MAI 2026 (PAID)
│ HISTO    │  → Les bulletins sont en lecture seule
│ RIQUE    │  
└─────┬────┘
      │
      ▼
┌──────────┐
│ S4       │  Le gestionnaire voit le bulletin de Jean Mbemba (Mai 2026)
│ CONSULT  │  → Détecte une erreur sur la prime
│ LECTURE  │  → Le bouton "Corriger" est disponible via un menu contextuel
└─────┬────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚠️  Correction d'un bulletin clôturé                                       │
│  Le bulletin de Mai 2026 est verrouillé (PAID). La correction créera un     │
│  bulletin rectificatif qui sera inclus dans le prochain cycle (Juin 2026).  │
│                                                                               │
│  Conséquences :                                                              │
│  • Un bulletin rectificatif sera généré pour Juin 2026                      │
│  • La différence sera ajoutée/soustraite du net de Juin 2026                │
│  • Les déclarations CNSS/IPR seront ajustées au prochain cycle              │
│                                                                               │
│  [Annuler]    [Créer un bulletin rectificatif]                               │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────┐
│ S5       │  Un "ajustement" est créé pour l'employé dans le cycle en cours
│ AJUSTE   │  → Type : "Correction Mai 2026 - Prime"
│ MENT     │  → Montant : +50 000 CDF (régularisation)
└─────┬────┘  
      │
      ▼
┌──────────┐
│ S4       │  Le bulletin de Juin 2026 incluera :
│ BULLETIN │  → La ligne "Régularisation Mai 2026 : +50 000 CDF"
│ JUIN     │  → Le statut "Ce bulletin contient une régularisation"
└──────────┘  → Le bulletin original de Mai 2026 reste inchangé (sauf mention)
```

---

## Règles de correction

| # | Règle |
|---|-------|
| 1 | Une correction est toujours **horodatée et signée** |
| 2 | Le bulletin original est conservé dans l'audit trail (snapshot immuable) |
| 3 | La version corrigée est marquée `CORRECTED` avec le numéro de version |
| 4 | En mode rectificatif, le bulletin original n'est pas modifié |
| 5 | Une correction ne peut pas être annulée (mais une nouvelle correction est possible) |
| 6 | Les déclarations CNSS/IPR sont automatiquement ajustées |

---

## Affichage dans S4 (après correction)

Un bulletin corrigé affiche des éléments visuels supplémentaires :

- **En-tête** : bandeau jaune "🧾 Bulletin rectifié le 30/06/2026 par P. Kazadi"
- **Champs modifiés** : chaque ligne modifiée a une pastille 📝
- **Section** : "Modifications" en bas détaille les changements (valeur avant/après)
- **Bouton** : [📋 Voir l'original] pour basculer sur la version non corrigée
