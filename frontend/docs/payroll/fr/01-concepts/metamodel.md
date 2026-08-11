# Métamodèle : Moteur de paie RDC

> **Les concepts fondamentaux du domaine de la paie en République Démocratique du Congo**

---

## Cartographie des concepts

```
                           ┌─────────────────────┐
                           │   PÉRIODE DE PAIE   │
                           └──────────┬──────────┘
                                      │ définit le contexte
                                      │ temporel pour
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
 ┌──────────────┐          ┌──────────────────┐          ┌──────────────────┐
 │   EMPLOYÉ    │◄────────►│CONTRAT DE TRAVAIL│          │ PARAMÈTRE LÉGAL  │
 └──────┬───────┘          └────────┬─────────┘          └──────────────────┘
        │                           │                            ▲
        │                           │ sert de base               │
        │                           ▼                            │
        │                   ┌───────────────┐                    │
        │◄─────────────────►│ÉLÉMENT DE PAIE│                    │
        │                   └───────┬───────┘                    │
        │                           │                            │
        │                           ▼                            │
        │                   ┌──────────────────┐                 │
        │                   │ BASE DE CALCUL   │                 │
        │                   └────────┬─────────┘                 │
        │                            │                           │
        │              ┌─────────────┼─────────────┐             │
        │              ▼             ▼             ▼             │
        │     ┌────────────┐ ┌────────────┐ ┌──────────────┐     │
        │     │ RETENUE    │ │  CHARGE    │ │  BULLETIN    │     │
        │     │(salariale) │ │ PATRONALE  │ │  DE PAIE     │     │
        │     └────────────┘ └────────────┘ └───────┬──────┘     │
        │                                           │            │
        └───────────────────────────────────────────┼────────────┘
                                                    │ fige tout
                                                    ▼
                                          ┌──────────────────┐
                                          │ PROCESSUS PAIE   │
                                          │ (8 étapes pipeline)│
                                          └──────────────────┘
```

### Concepts du métamodèle

| # | Concept | Nature | Dépendances |
|---|---------|--------|-------------|
| 1 | `Employé` | Entité du domaine RH | Aucune (donnée d'entrée) |
| 2 | `Contrat de travail` | Agrégat du domaine RH | `Employé` |
| 3 | `Période de paie` | Objet-valeur temporel | Aucune |
| 4 | `Élément de paie` | Structure universelle de gain | `Contrat de travail`, `Période` |
| 5 | `Paramètre légal` | Entité historisée | Aucune (donnée réglementaire) |
| 6 | `Base de calcul` | Accumulateur dynamique | `Élément de paie`, `Paramètre légal` |
| 7 | `Retenue` | Entité calculée | `Base de calcul`, `Paramètre légal` |
| 8 | `Charge patronale` | Entité calculée | `Base de calcul`, `Paramètre légal` |
| 9 | `Bulletin de paie` | Document-synthèse figé | Tous les concepts ci-dessus |

### Concept transversal : `Processus de paie`

Le processus de paie n'est pas une entité du métamodèle au sens des 9 concepts ci-dessus, mais un **concept opérationnel** qui orchestre le pipeline de calcul. 
Il est défini séparément en fin de document car il exprime la dynamique du système plutôt que sa structure statique.

---

## Concept : Employé

### Définition
Personne physique liée à l'organisation par un contrat de travail, dont les caractéristiques personnelles et professionnelles influencent le calcul de la paie.

> **Note** : L'`Employé` est un concept partagé avec le module `employees`. Le métamodèle payroll en définit les attributs pertinents pour la paie sans répliquer l'intégralité du modèle RH.

### Attributs

| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `identifiant_unique` | Identifiant | Oui | Référence unique de l'employé dans le système |
| `nom_complet` | Texte | Oui | Nom et prénom(s) tels qu'ils figurent sur le bulletin |
| `date_naissance` | Date | Oui | Utilisée pour vérifier l'âge légal de travail |
| `matricule_cnss` | Texte | Non | Numéro d'affiliation à la CNSS (obtenu après déclaration) |
| `numero_compte_bancaire` | Texte | Non | IBAN ou RIB pour le virement du net à payer |
| `personnes_a_charge` | Entier | Oui | Nombre de personnes à charge déclarées (0 par défaut) |
| `categorie_professionnelle` | Catégorie | Oui | Classe et échelon dans la grille salariale (ex: Classe 3, Échelon 2) |

### Relations

```
Employé ──1──>* Contrat de travail (un employé peut avoir plusieurs contrats successifs)
Employé ──1──>* Bulletin de paie (un employé reçoit un bulletin par période active)
```

### Cycle de vie

```
[Embauche] ──(déclaration CNSS)──> [Actif] ──(départ)──> [Sorti]
```

| Étape | Description | Événement déclencheur |
|-------|-------------|-----------------------|
| 1. Création | Saisie des informations personnelles et catégorielles | Embauche d'un nouveau travailleur |
| 2. Actif | Employé en période de travail, éligible à la paie | Périodes de paie successives |
| 3. Sorti | Employé ayant quitté l'organisation | Démission, licenciement, retraite, décès |

### Invariants

- **Règle 1** : Un employé ne peut avoir qu'un seul contrat actif à une date donnée.
- **Règle 2** : Le nombre de personnes à charge ne peut pas être négatif et ne peut pas dépasser 20 (maximum réaliste).
- **Règle 3** : Un employé avec un contrat actif est toujours éligible au calcul de la paie.

### Exemple concret

> Kiban M. est employé depuis le 1er mars 2020. Il est classé Classe 4, Échelon 3 sur la grille salariale. Il a déclaré 3 personnes à charge (conjoint + 2 enfants). Sa catégorie détermine le salaire de base applicable.

---

## Concept : Contrat de travail

### Définition
Convention juridique entre un employé et l'organisation qui établit les conditions de travail et la rémunération contractuelle de base.

### Attributs

| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `identifiant_contrat` | Identifiant | Oui | Référence unique du contrat |
| `employe_reference` | Référence | Oui | Référence vers l'employé contractant |
| `date_debut` | Date | Oui | Date d'effet du contrat |
| `date_fin` | Date | Non | Date de fin pour les CDD (null pour CDI) |
| `salaire_de_base` | Montant | Oui | Salaire brut mensuel contractuel (brut CDF) |
| `salaire_negocie_usd` | Montant (USD) | Non | Salaire net négocié en USD à l'embauche — c'est le montant que l'employé connaît comme « son salaire » ; converti en CDF au taux de la période pour donner le net à payer cible |
| `regime_travail` | Texte | Oui | Temps plein, temps partiel (avec taux d'activité), expatriation |
| `clauses_particulieres` | Texte | Non | Primes garanties, avantages contractuels spécifiques |

### Relations

```
Employé ──1──>* Contrat de travail
Contrat de travail ──1──>* Élément de paie (les éléments fixes du contrat, ex: salaire de base)
Contrat de travail ──*──1 Période de paie (le contrat est actif sur une ou plusieurs périodes)
```

### Cycle de vie

```
[Signature] ──(date d'effet)──> [Actif] ──(date de fin)──> [Expiré] / [Résilié]
```

| Étape | Description | Événement déclencheur |
|-------|-------------|-----------------------|
| 1. Signature | Création du contrat avec ses clauses | Embauche ou renouvellement |
| 2. Actif | Période d'exécution du contrat | Entrée en vigueur |
| 3. Expiré | Fin naturelle du terme (CDD) | Arrivée à échéance |
| 4. Résilié | Rupture anticipée | Démission, licenciement |

### Invariants

- **Règle 1** : Le salaire de base (brut) ne peut pas être inférieur au SMIG mensuel correspondant à la catégorie professionnelle.
- **Règle 2** : Un contrat CDI n'a pas de date de fin.
- **Règle 3** : La date de début doit être postérieure ou égale à la date de naissance + 16 ans (âge légal minimum).
- **Règle 4 — Prorata d'entrée/sortie** : Si la date de début du contrat ne coïncide pas avec le premier jour de la période de paie, le salaire de base est proratisé. La règle de prorata est définie dans la sémantique (prorata calendaire).
- **Règle 5** : `salaire_de_base` et `salaire_negocie_usd`, si tous deux renseignés, doivent être cohérents : `salaire_negocie_usd × taux_change_période ≈ salaire_de_base − retenues_estimées`. L'écart admissible est configurable (valeur par défaut : 5 %).

### Exemple concret

> Contrat signé le 1er mars 2020, CDI, temps plein. Salaire de base : 900 000 CDF. Classe 4, Échelon 3. Clause particulière : prime de performance trimestrielle équivalant à 1 mois de salaire.

---

## Concept : Période de paie

### Définition
Intervalle temporel pour lequel la paie est calculée. Définit le contexte conjoncturel du calcul (jours ouvrés, taux de change, indice d'inflation).

### Attributs

| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `identifiant_periode` | Identifiant | Oui | Référence unique (ex: 2026-01) |
| `date_debut` | Date | Oui | Premier jour de la période |
| `date_fin` | Date | Oui | Dernier jour de la période |
| `nombre_jours_ouvres` | Entier | Oui | Jours ouvrés réels dans la période |
| `nombre_jours_calendaires` | Entier | Oui | Jours calendaires dans la période |
| `taux_change_cdf_usd` | Taux (décimal) | Non | Taux de change CDF/USD pour la période (si applicable) |
| `source_taux_change` | Texte | Non | Source du taux (BCC, banque commerciale, config manuelle) |
| `indice_inflation` | Décimal | Non | Indice d'inflation du mois (si applicable) |
| `statut` | Énumération | Oui | Ouverte, En cours, Clôturée |

### Relations

```
Période de paie ──1──>* Bulletin de paie (une période produit un bulletin par employé)
Période de paie ──1──>* Élément de paie variable (heures sup, primes exceptionnelles)
```

### Cycle de vie

```
[Créée] ──(début période)──> [Ouverte] ──(calcul en cours)──> [En cours]
──>(clôture)──> [Clôturée]
```

| Étape | Description | Événement déclencheur |
|-------|-------------|-----------------------|
| 1. Créée | Période créée, pas encore active | Début d'année ou clôture de la période précédente |
| 2. Ouverte | Saisie des éléments variables possibles | Premier jour de la période |
| 3. En cours | Pipeline de calcul en exécution | Lancement du calcul par le gestionnaire |
| 4. Clôturée | Tous les bulletins générés et figés | Validation finale des bulletins |

### Invariants

- **Règle 1 — Unité de période** : Une période de paie est un **run unique** — tous les employés actifs sur cette période sont payés dans le même lancement du pipeline. Il n'existe pas de « paie exceptionnelle » individuelle en dehors du run.
- **Règle 2** : Une période ne peut être clôturée que si tous les employés actifs ont un bulletin généré.
- **Règle 3** : Les périodes ne peuvent pas se chevaucher.
- **Règle 4** : Le nombre de jours ouvrés est toujours inférieur ou égal au nombre de jours calendaires.
- **Règle 5** : Le prorata pour une entrée ou sortie en cours de période se calcule en jours calendaires (voir Semantique).

### Exemple concret

> Période janvier 2026 : du 1er au 31 janvier, 21 jours ouvrés (lundi-vendredi), 31 jours calendaires. Taux de change BCC : 2 850 CDF/USD.

---

## Concept : Élément de paie

### Définition
Structure universelle représentant tout type de gain ou d'avantage perçu par l'employé au cours d'une période de paie. L'élément de paie est l'unité atomique de composition du salaire.

### Attributs

| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `code` | Texte | Oui | Code unique et lisible (ex: SAL_BASE, PRIME_PERF, HS_30, IND_LOG) |
| `libelle` | Texte | Oui | Libellé lisible (ex: « Salaire de base », « Prime de performance ») |
| `montant_brut` | Montant | Oui | Montant nominal avant toute transformation |
| `mode_calcul` | Énumération | Oui | `fixe` (montant constant), `taux_horaire` (montant × heures), `journalier` (montant × jours), `formule` (calcul par règle métier) |
| `quantite` | Nombre | Non | Quantité associée au mode de calcul (heures pour taux_horaire, jours pour journalier) |
| `est_imposable` | Booléen | Oui | True si ce gain est soumis à l'IPR/IRPP |
| `soumis_cnss` | Booléen | Oui | True si ce gain est soumis à la cotisation CNSS |
| `soumis_inpp` | Booléen | Oui | True si ce gain est soumis à la cotisation INPP |
| `soumis_onem` | Booléen | Oui | True si ce gain est soumis à la cotisation ONEM |
| `est_exonere_logement` | Booléen | Oui | True si ce gain bénéficie de l'exonération logement |
| `est_exonere_transport` | Booléen | Oui | True si ce gain bénéficie de l'exonération transport |
| `categorie` | Énumération | Oui | `salaire_base`, `prime`, `heure_sup`, `indemnite`, `gratification`, `avantage_nature`, `autre` |

### Relations

```
Contrat de travail ──1──>* Élément de paie (les éléments fixes sont définis par le contrat)
Période de paie ──1──>* Élément de paie variable (saisis pour une période spécifique)
Élément de paie ──*──>* Base de calcul (un élément contribue à plusieurs bases selon ses flags)
```

### Cycle de vie

```
[Défini] ──(rattaché à un contrat)──> [Permanent]   (éléments fixes du contrat)
[Défini] ──(rattaché à une période)──> [Variable]   (saisi pour une période spécifique)
[Permanent|Variable] ──(calcul effectué)──> [Inclus dans le bulletin]
```

| Étape | Description | Événement déclencheur |
|-------|-------------|-----------------------|
| 1. Défini | Création de l'élément avec ses attributs | Paramétrage ou saisie |
| 2. Permanent | Élément récurrent lié au contrat | Engagé tant que le contrat est actif |
| 3. Variable | Élément saisi pour une période unique | Saisie mensuelle |
| 4. Inclus | Élément pris en compte dans le calcul | Exécution du pipeline |

### Invariants

- **Règle 1** : Le montant brut doit être positif ou nul (un élément négatif n'existe pas — les retenues sont modélisées séparément).
- **Règle 2** : Les codes d'élément sont uniques dans le catalogue.
- **Règle 3** : Les flags d'assujettissement (est_imposable, soumis_cnss, etc.) ne sont pas mutuellement exclusifs — un élément peut être soumis à plusieurs cotisations.
- **Règle 4** : Un élément `salaire_base` est toujours permanent et ne peut être saisi comme variable.

### Exemple concret

> **Salaire de base** : code `SAL_BASE`, montant 900 000 CDF, mode `fixe`, imposable: oui, CNSS: oui, INPP: oui, ONEM: oui, exonéré logement: non, exonéré transport: non, catégorie: `salaire_base`.
>
> **Indemnité de logement** : code `IND_LOG`, montant 270 000 CDF, mode `fixe`, imposable: oui, CNSS: oui, INPP: oui, ONEM: oui, exonéré logement: **oui**, exonéré transport: non, catégorie: `indemnite`.
>
> **Heure supplémentaire 30 %** : code `HS_30`, montant 5 250 CDF/h, mode `taux_horaire`, quantités: 4 heures, imposable: oui, CNSS: oui, INPP: oui, ONEM: oui, exonéré logement: non, exonéré transport: non, catégorie: `heure_sup`.

---

## Concept : Paramètre légal

### Définition
Valeur réglementaire fixée par l'État congolais (loi, décret, arrêté) utilisée comme constante dans une règle de calcul. Chaque paramètre est historisé pour permettre le calcul rétroactif conforme.

### Attributs

| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `code` | Texte | Oui | Code unique (ex: SMIG_2026, TAUX_CNSS_SAL, BAREME_IPR_2025) |
| `description` | Texte | Oui | Description de ce que ce paramètre représente |
| `type_parametre` | Énumération | Oui | `taux`, `montant_fixe`, `bareme_progressif`, `plafond`, `seuil`, `regle_arrondi`, `exoneration` |
| `valeur` | Dépend du type | Oui | Valeur du paramètre (montant, taux décimal, ou tableau de tranches) |
| `unite` | Texte | Non | Unité de la valeur (CDF, USD, %, jours) |
| `date_validite_debut` | Date | Oui | Première date à laquelle ce paramètre est applicable |
| `date_validite_fin` | Date | Non | Dernière date de validité (null si toujours en vigueur) |
| `reference_juridique` | Texte | Non | Texte de loi ou décret qui a fixé ce paramètre (ex: « Loi n° 23/053 ») |

### Relations

```
Paramètre légal ──*──1 Base de calcul (un paramètre peut influencer une base)
Paramètre légal ──*──1 Retenue (une retenue utilise un ou plusieurs paramètres)
Paramètre légal ──*──1 Charge patronale (une charge patronale utilise un ou plusieurs paramètres)
Paramètre légal ──*──1 Processus de paie (le pipeline utilise les paramètres applicables à la période)
```

> **Note** : Le paramètre légal est un concept référentiel — il n'a pas de cycle de vie au sens des autres concepts. Son existence est définie par une date de début et éventuellement une date de fin de validité. Il est créé ou mis à jour lors de la publication d'un nouveau texte réglementaire.

### Invariants

- **Règle 1** : À une date donnée, un paramètre de même code ne peut avoir qu'une seule version applicable.
- **Règle 2** : Un paramètre `bareme_progressif` doit contenir au moins une tranche.
- **Règle 3** : Les dates de validité de deux versions successives du même paramètre sont contiguës (la date_validite_debut de la nouvelle version = date_validite_fin de l'ancienne + 1 jour).

### Exemple concret

> **SMIG journalier** : code `SMIG_2026`, type `montant_fixe`, valeur 21 500 CDF, date_validite_debut: 2026-01-01, référence: « Décret n° 25/22 ».
>
> **Barème IRPP 2026** : code `BAREME_IRPP_2026`, type `bareme_progressif`, valeur : tableau de 10 tranches (cf. Guide §4.2), date_validite_debut: 2026-01-01, référence: « Loi n° 23/053 ».
>
> **Taux CNSS salarié** : code `TAUX_CNSS_SALARIAL`, type `taux`, valeur 0,05 (5 %), date_validite_debut: 2000-01-01 (indéfini).

---

## Concept : Base de calcul

### Définition
Assiette intermédiaire construite dynamiquement par filtrage et accumulation des éléments de paie selon leurs flags d'assujettissement. La base de calcul est le résultat d'une opération de sommation conditionnelle, pas une saisie.

### Attributs

| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `identifiant_base` | Identifiant | Oui | Référence unique de la base pour un bulletin donné |
| `type_base` | Énumération | Oui | `brut`, `cnss`, `imposable`, `inpp`, `onem`, `net` |
| `montant` | Montant | Oui | Résultat de l'accumulation |
| `elements_contribuant` | Liste de références | Oui | Références vers les éléments de paie qui composent cette base |
| `regle_filtrage` | Texte | Oui | Description de la règle de filtrage (ex: « somme des éléments où soumis_cnss = vrai ») |

### Relations

```
Élément de paie ──*──>* Base de calcul (plusieurs éléments contribuent à plusieurs bases)
Base de calcul ──1──1 Retenue (une base sert au calcul d'une retenue)
Base de calcul ──1──1 Charge patronale (une base sert au calcul d'une charge patronale)
Base de calcul ──1──1 Bulletin de paie (les bases sont figées dans le bulletin)
```

### Cycle de vie

```
[Construite] ──(étape 4 du pipeline)──> [Prête pour calcul]
```

| Étape | Description | Événement déclencheur |
|-------|-------------|-----------------------|
| 1. Construite | Filtrage et sommation des éléments selon les flags | Exécution de l'étape 4 du pipeline |
| 2. Prête pour calcul | Base disponible pour les étapes 5 et 6 | Validation de la construction |

Les bases de calcul ne sont jamais persistées indépendamment — elles sont **toujours figées dans le bulletin de paie** (concept 9). Leur durée de vie est celle de l'exécution du pipeline.

### Invariants

- **Règle 1** : Le montant d'une base de calcul est toujours égal à la somme des montants des éléments qui la composent.
- **Règle 2** : Une base de calcul ne peut pas être modifiée manuellement — elle est toujours le résultat d'un calcul.
- **Règle 3** : La base `brut` est la somme de **tous** les éléments de gain, sans exception.
- **Règle 4** : La base `net` = base `imposable` − retenues salariales (calcul final à l'étape 7).
- **Règle 5** : Les bases doivent respecter l'ordre de construction : brut → imposable/CNSS/INPP/ONEM → net.

### Exemple concret

> Pour Kiban M. en janvier 2026 :
> - **Base CNSS** = Salaire de base (900 000) + Indemnité logement (270 000) + Indemnité transport (30 000) + Heures sup (21 000) = **1 221 000 CDF**
>   (tous ces éléments ont `soumis_cnss = vrai`)
> - **Base imposable IRPP** = Base CNSS (1 221 000) − CNSS salariale (61 050) − exonération logement (270 000 plafonnée à 30 % du brut) − exonération transport (30 000) = **859 950 CDF**
>   (déduction des cotisations et exonérations réglementaires)

---

## Concept : Retenue

### Définition
Prélèvement obligatoire opéré sur la rémunération du travailleur pour le compte d'un organisme tiers ou de l'État.

### Attributs

| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `code` | Texte | Oui | Code unique (ex: CNSS_SAL, IPR, IRPP, SAISIE_ARRET) |
| `libelle` | Texte | Oui | Libellé lisible (ex: « Cotisation CNSS part salariale ») |
| `type_retenue` | Énumération | Oui | `cnss_salariale`, `impot_revenu`, `saisie_arret`, `avance`, `autre` |
| `montant` | Montant | Oui | Montant calculé de la retenue |
| `base_calcul_reference` | Référence | Oui | Référence vers la base de calcul utilisée |
| `taux_applicable` | Décimal | Oui | Taux effectif appliqué (taux fixe ou taux effectif du barème) |
| `parametres_utilises` | Liste de références | Oui | Paramètres légaux qui ont servi au calcul |

### Relations

```
Base de calcul ──1──* Retenue (une base peut servir à plusieurs retenues)
Retenue ──*──1 Bulletin de paie (une retenue est figée dans un bulletin)
Paramètre légal ──*──* Retenue (une retenue utilise plusieurs paramètres)
```

### Cycle de vie

```
[Calculée] ──(étape 5 du pipeline)──> [Intégrée au bulletin]
```

| Étape | Description | Événement déclencheur |
|-------|-------------|-----------------------|
| 1. Calculée | Application de la règle de calcul sur la base | Exécution de l'étape 5 du pipeline |
| 2. Intégrée au bulletin | Retenue figée dans le document final | Génération du bulletin (étape 8) |

### Invariants

- **Règle 1** : Le montant d'une retenue ne peut pas excéder le montant de la base de calcul qui l'alimente.
- **Règle 2** : CNSS salariale = base CNSS × 5 % (taux unique, sans plafond).
- **Règle 3** : IPR/IRPP = application du barème progressif sur la base imposable, puis plafonnement à 30 %, puis abattement familial.
- **Règle 4** : Le total des retenues salariales ne peut pas excéder le salaire brut (principe de non-insaisissabilité totale).
- **Règle 5** : Une retenue ne peut exister sans une base de calcul correspondante.

### Exemple concret

> **CNSS salariale** (Kiban M., janvier 2026) :
> - Base CNSS : 1 221 000 CDF
> - Taux : 5 %
> - **Montant** : 61 050 CDF
>
> **IRPP 2026** (Kiban M., janvier 2026) :
> - Base imposable : 859 950 CDF
> - Barème 10 tranches appliqué → impôt brut avant plafonnement : 172 738 CDF
> - Plafonnement 30 % : 859 950 × 30 % = 257 985 CDF → plafond non atteint
> - Abattement 3 personnes à charge : 172 738 × (1 − 0,06) = **162 373 CDF**

---

## Concept : Charge patronale

### Définition
Contribution financière due par l'employeur au titre de la protection sociale et de la formation professionnelle, calculée sur une base de rémunération et versée à un organisme collecteur.

### Attributs

| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `code` | Texte | Oui | Code unique (ex: CNSS_PAT, INPP, ONEM) |
| `libelle` | Texte | Oui | Libellé lisible (ex: « Cotisation CNSS part patronale ») |
| `type_charge` | Énumération | Oui | `cnss_patronale`, `inpp`, `onem`, `autre` |
| `montant` | Montant | Oui | Montant calculé de la charge |
| `base_calcul_reference` | Référence | Oui | Référence vers la base de calcul utilisée |
| `taux_applicable` | Décimal | Oui | Taux effectif appliqué |
| `parametres_utilises` | Liste de références | Oui | Paramètres légaux qui ont servi au calcul |

### Relations

```
Base de calcul ──1──* Charge patronale (une base peut servir à plusieurs charges)
Charge patronale ──*──1 Bulletin de paie (figée dans le bulletin)
Paramètre légal ──*──* Charge patronale (paramètres utilisés)
```

### Cycle de vie

```
[Calculée] ──(étape 6 du pipeline)──> [Intégrée au bulletin]
```

| Étape | Description | Événement déclencheur |
|-------|-------------|-----------------------|
| 1. Calculée | Application du taux sur la base | Exécution de l'étape 6 du pipeline |
| 2. Intégrée au bulletin | Charge figée dans le document final | Génération du bulletin (étape 8) |

### Invariants

- **Règle 1** : Les charges patronales n'affectent pas le net à payer — elles s'ajoutent au coût total employeur.
- **Règle 2** : CNSS patronale = base CNSS × 13 % (réparti en 3 branches : 5 % pensions + 1,5 % risques + 6,5 % familles).
- **Règle 3** : INPP = base INPP × taux selon effectif (1-50 : 3,5 %, 51-300 : 3 %, >300 : 2 %, public : 4 %).
- **Règle 4** : ONEM = base ONEM × 0,5 %.

### Exemple concret

> **CNSS patronale** (Kiban M., janvier 2026, entreprise de 50 salariés) :
> - Base CNSS : 1 221 000 CDF
> - Taux : 13 %
> - **Montant** : 158 730 CDF
>   - Pensions (5 %) : 61 050 CDF
>   - Risques professionnels (1,5 %) : 18 315 CDF
>   - Prestations familiales (6,5 %) : 79 365 CDF
>
> **INPP** (même entreprise : 1-50 salariés → 3,5 %) :
> - Base INPP : 1 221 000 CDF
> - **Montant** : 42 735 CDF

---

## Concept : Bulletin de paie

### Définition
Document de synthèse final et figé qui présente l'ensemble des gains, déductions et cotisations pour un employé donné sur une période de paie déterminée. Le bulletin est une photographie complète et horodatée du calcul.

### Attributs

| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `identifiant_bulletin` | Identifiant | Oui | Référence unique et séquentielle |
| `periode_reference` | Référence | Oui | Période de paie concernée |
| `employe_reference` | Référence | Oui | Employé concerné |
| `contrat_reference` | Référence | Oui | Contrat actif sur la période |
| `elements_de_paie` | Liste de références | Oui | Tous les éléments de gain inclus |
| `bases_de_calcul` | Liste d'objets | Oui | Snapshot de chaque base (type, montant, éléments contributeurs) |
| `retenues` | Liste d'objets | Oui | Snapshot de chaque retenue |
| `charges_patronales` | Liste d'objets | Oui | Snapshot de chaque charge patronale |
| `salaire_brut` | Montant | Oui | Total des gains |
| `total_retenues` | Montant | Oui | Somme des retenues salariales |
| `net_imposable` | Montant | Oui | Base imposable après exonérations et CNSS |
| `net_a_payer` | Montant | Oui | Salaire brut − total retenues |
| `cout_total_employeur` | Montant | Oui | Salaire brut + total charges patronales |
| `taux_change_utilise` | Décimal | Non | Taux de change effectif si applicable |
| `snapshot_parametres` | Objet | Oui | Copie de tous les paramètres légaux utilisés (version, valeur) |
| `date_generation` | Datetime | Oui | Date et heure de génération du bulletin |
| `signature_calcul` | Hash | Oui | Empreinte du calcul pour vérification d'intégrité |

### Relations

```
Employé ──1──* Bulletin de paie
Période de paie ──1──* Bulletin de paie
Bulletin de paie ──1──1 Snapshot paramètres (le bulletin fige les paramètres utilisés)
```

### Cycle de vie

```
[En cours] ──(étapes 1-7 du pipeline)──> [Calculé] ──(étape 8)──> [Généré]
──>(validation)──> [Validé]
```

| Étape | Description | Événement déclencheur |
|-------|-------------|-----------------------|
| 1. En cours | Bulletin en construction pendant l'exécution du pipeline | Lancement du processus de paie |
| 2. Calculé | Pipeline terminé, tous les montants sont connus | Fin de l'étape 7 |
| 3. Généré | Bulletin figé avec snapshot (étape 8) | Exécution de l'étape 8 |
| 4. Validé | Bulletin approuvé par le gestionnaire de paie | Validation manuelle |

### Invariants

- **Règle 1** : Le net à payer = salaire brut − total retenues (vérification comptable : toujours vrai).
- **Règle 2** : Le coût total employeur = salaire brut + total charges patronales.
- **Règle 3** : Un bulletin validé est immuable — aucune modification n'est possible sans créer une version corrigée.
- **Règle 4** : Le snapshot des paramètres doit contenir l'intégralité des paramètres qui ont influencé le calcul, pas seulement les références.
- **Règle 5** : Deux bulletins pour le même employé sur la même période ne peuvent pas coexister (unicité).

### Exemple concret

> Bulletin de Kiban M. — Janvier 2026 (Guide, cas pratique) :
> - Salaire brut : 1 221 000 CDF
> - Total retenues : 223 423 CDF (CNSS 61 050 + IRPP 162 373)
> - Net à payer : **997 577 CDF**
> - Charges patronales : 201 465 CDF (CNSS 158 730 + INPP 42 735)
> - Coût total employeur : **1 422 465 CDF**

---

## Concept transversal : Processus de paie (Pipeline)

### Définition
Orchestration en séquence immuable des huit étapes de calcul qui transforment les données brutes (employés, contrats, éléments de paie, paramètre légaux) en bulletins de paie.

### Structure du pipeline

```
Étape 1 : Vérification et validation de l'intégrité des données
    ↓
Étape 2 : Calcul individuel des gains et majorations d'heures
    ↓
Étape 3 : Détermination et validation du Salaire Brut
    ↓
Étape 4 : Construction des bases intermédiaires de calcul
    │
    ├── Base CNSS        (filtre : soumis_cnss = vrai)
    ├── Base Imposable   (filtre : est_imposable = vrai, déduction CNSS et exonérations)
    ├── Base INPP        (filtre : soumis_inpp = vrai)
    └── Base ONEM        (filtre : soumis_onem = vrai)
    ↓
Étape 5 : Calcul des retenues salariales
    ├── CNSS salariale   (base CNSS × 5 %)
    └── IPR / IRPP       (barème progressif → plafonnement 30 % → abattement familial)
    ↓
Étape 6 : Calcul des charges patronales
    ├── CNSS patronale   (base CNSS × 13 %, réparti 3 branches)
    ├── INPP             (base INPP × taux selon effectif)
    └── ONEM             (base ONEM × 0,5 %)
    ↓
Étape 7 : Calcul du Salaire Net et du Net à Payer
    ↓
Étape 8 : Génération du bulletin de paie et archivage d'audit
```

### Règles du pipeline

- **Immutabilité de l'ordre** : Les étapes s'exécutent toujours dans l'ordre 1→8. Aucune étape ne peut être sautée ou réordonnée.
- **Indépendance** : Chaque étape reçoit un état, applique sa logique et produit un nouvel état. Elle ne dépend que de l'état produit par l'étape précédente.
- **Stratégie interchangeable** : Les étapes 5 et 6 utilisent le Strategy Pattern pour permettre le remplacement d'une règle de calcul sans modifier l'étape elle-même (ex: IPR → IRPP).
- **Déterministe** : À paramètres identiques (employé, période, éléments, paramètres légaux), le pipeline produit exactement le même résultat.

### Événements du pipeline

| Étape | Événement déclencheur | Sortie produite |
|-------|----------------------|-----------------|
| 1 | Lancement du processus de paie | Données validées ou erreurs retournées |
| 2 | Validation des données | Éléments de gain avec montants calculés |
| 3 | Calcul des gains terminé | Salaire brut validé |
| 4 | Brut validé | Quatre bases de calcul construites |
| 5 | Bases construites | Retenues salariales calculées |
| 6 | Retenues calculées | Charges patronales calculées |
| 7 | Charges calculées | Net à payer et coût employeur déterminés |
| 8 | Net calculé | Bulletin de paie généré avec snapshot d'audit |

---

## Synthèse : Concepts et leur rôle dans le pipeline

| Concept | Étape du pipeline | Rôle |
|---------|-------------------|------|
| `Employé` | 1 (validation) | Vérifier que l'employé est actif et eligible |
| `Contrat de travail` | 2 (gains) | Fournir le salaire de base et les éléments fixes |
| `Période de paie` | 1, 8 (validation, génération) | Contexte temporel, taux de change, jours ouvrés |
| `Élément de paie` | 2, 3, 4 (gains, brut, bases) | Constituer le salaire brut et alimenter les bases |
| `Paramètre légal` | 4, 5, 6, 8 (bases, retenues, charges, génération) | Fournir les constantes réglementaires |
| `Base de calcul` | 4, 5, 6 (construction, retenues, charges) | Assiette intermédiaire pour les calculs |
| `Retenue` | 5, 8 (calcul, génération) | Montant déduit du salaire |
| `Charge patronale` | 6, 8 (calcul, génération) | Contribution employeur |
| `Bulletin de paie` | 8 (génération) | Document figé contenant tous les résultats |

---

## Invariants globaux du métamodèle

- **I1 — Intégrité référentielle** : Toute référence vers un concept doit correspondre à une instance existante de ce concept.
- **I2 — Cohérence temporelle** : Un bulletin de paie ne peut être généré que si le contrat de l'employé est actif sur la période concernée (date_debut_contrat ≤ date_fin_période ET date_fin_période ≤ date_fin_contrat ou contrat CDI).
- **I3 — Exactitude des sommes** : Salaire brut = Σ montants des éléments de paie inclus. Net à payer = Salaire brut − Σ retenues. Coût total employeur = Salaire brut + Σ charges patronales.
- **I4 — Immuabilité des paramètres** : Un paramètre légal ne peut pas être supprimé — seule une nouvelle version peut être créée avec une date de validité ultérieure.
- **I5 — Unicité du bulletin** : Il ne peut exister qu'un seul bulletin validé par (employé, période).
- **I6 — Non-régression des calculs** : L'ajout d'une nouvelle stratégie de calcul ne modifie pas le comportement des stratégies existantes.
- **I7 — Unité de période** : Tous les employés actifs sur une période sont calculés dans un seul run de paie. Il n'existe pas de paie individuelle déconnectée du run.
