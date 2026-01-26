# Gestion de la Paie en RDC

## Vue d'ensemble

C'est une excellente observation et c'est tout le défi d'un logiciel de paie en RDC. Vous touchez du doigt la différence entre :

- **Salaire Net à Payer** : Ce que l'employé reçoit effectivement
- **Coût Total Employeur** : Ce que l'entreprise dépense réellement

Effectivement, en RDC, la majorité des contrats sont négociés **en Net** (ex: "Je te paie 500 USD net"). Cependant, la loi oblige l'employeur à faire apparaître tous les détails sur la fiche de paie.

Voici comment votre logiciel doit gérer cette "transparence" et cette réalité.

---

## 1. Le mécanisme du "Gross-Up" (Calcul à l'envers)

Puisque l'employé veut **500 USD dans sa poche**, votre logiciel doit être capable de calculer quel doit être le **Salaire Brut** pour qu'après avoir déduit :

- L'**IPR** (impôt)
- La **CNSS** (5 %)

L'employé reçoive exactement 500 USD.

### Visibilité des différentes parties

- **L'employé** ne voit que les 500 USD
- **L'État** voit le Brut, l'IPR, la CNSS, l'INPP et l'ONEM

---

## 2. Ce que l'employé ignore (mais que l'entreprise paie)

Il y a deux types de valeurs "invisibles" pour l'employé mais gérées par vos fixtures :

### A. Les charges patronales

**INPP, ONEM, CNSS employeur** :
- L'employé ne les voit souvent même pas sur sa fiche de paie (ou juste pour information)
- C'est un coût supplémentaire pour l'entreprise : **environ 11 % à 13 % en plus du brut**

### B. Les avantages légaux inclus

Dans les 500 USD, l'employeur "cache" souvent l'allocation de logement et de transport pour optimiser les impôts.

**Exemple** :
Sur les 500 USD, l'employeur peut déclarer que :
- **100 USD** sont pour le logement (exonéré d'impôt)
- **400 USD** sont le salaire de base

L'employé reçoit toujours ses 500 USD, mais l'entreprise paie moins d'impôts.

---

## 3. Pourquoi les fixtures sont indispensables

Même si l'employé s'en moque, votre logiciel doit utiliser vos fixtures pour :

### Générer le bulletin de paie légal
- En cas de contrôle de l'Inspection du Travail ou de la DGI, la fiche de paie doit détailler la CNSS, l'IPR, etc.

### Déclarer les impôts
- L'entreprise doit savoir exactement combien verser à la DGI (IPR) et à la CNSS chaque mois

### Protéger l'entreprise
- Si vous ne calculez pas bien la part CNSS, l'entreprise risque de lourdes amendes, même si elle paie bien l'employé

---

## En résumé

### Pour l'employé
Votre logiciel doit afficher une interface simple : **"Salaire Net : 500 USD"**

### En arrière-plan (le moteur de paie)
Le logiciel utilise toutes les fixtures créées pour transformer ce "Net" en une comptabilité légale :
- Barème IPR
- Taux CNSS
- SMIG (Salaire Minimum)
- Allocations légales
- Charges patronales
