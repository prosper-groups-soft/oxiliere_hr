# Sémantique : Moteur de paie RDC

> **Signification précise de chaque propriété, état et événement du métamodèle**

---

Chaque section ci-dessous lève une ambiguïté identifiée du métamodèle. L'objectif est d'éliminer tout écart d'interprétation entre le document de conception et l'implémentation.

---

## Propriété : `est_imposable` (Élément de paie)

### Définition précise
L'attribut `est_imposable` indique si le montant brut de l'élément de paie doit être inclus dans l'assiette de calcul de l'impôt sur le revenu (IPR ou IRPP). C'est un indicateur **d'assujettissement fiscal**, pas un indicateur d'exonération.

> **Important** : `est_imposable = vrai` signifie que le gain entre **dans la base imposable avant déductions**. Il pourra ultérieurement être partiellement ou totalement exonéré par l'application des mécanismes d'exonération (logement, transport). Ces deux concepts ne sont pas en conflit : l'assujettissement détermine l'inclusion dans la base, l'exonération détermine la déduction après inclusion.

### Règles
- **Condition d'application** : Applicable à tout élément de catégorie `salaire_base`, `prime`, `heure_sup`, `gratification`, `indemnite` et `avantage_nature`.
- **Valeur par défaut** : `vrai` pour les catégories `salaire_base`, `prime`, `heure_sup`, `gratification`. `faux` pour `indemnite` si l'indemnité est déclarée comme remboursement de frais professionnels (transport, mission). `vrai` pour `avantage_nature` (sauf exceptions légales).
- **Précédence** : En cas de doute sur la qualification fiscale d'un élément, la valeur par défaut est `vrai`. Le gestionnaire de paie doit explicitement passer à `faux` sur la base d'un texte légal.

### Valeurs "limites"
- **Absent** : Non applicable — l'attribut est toujours présent (booléen).
- **Vide** : Non applicable — l'attribut est toujours renseigné.
- **Invalide** : Si la valeur n'est pas booléenne, l'élément est rejeté par l'étape 1 du pipeline (validation d'intégrité).

### Interactions

| Propriété | Interaction | Comportement résultant |
|-----------|-------------|------------------------|
| `est_exonere_logement = vrai` | `est_imposable = vrai` | Le gain est inclus dans la base imposable, puis une déduction pour exonération logement est appliquée (plafonnée à 30 % du brut imposable) |
| `est_exonere_transport = vrai` | `est_imposable = vrai` | Le gain est inclus dans la base imposable, puis une déduction pour frais professionnels est appliquée (plafonnée au coût réel de 4 courses/jour) |
| `soumis_cnss = vrai` | `est_imposable = vrai` | La CNSS salariale (5 %) est déduite de la base imposable (c'est une charge déductible du revenu imposable) |
| `est_imposable = faux` | `soumis_cnss = vrai` | Le gain est exclu de l'impôt mais reste soumis à la CNSS. Exemple typique : certaines indemnités de transport |

### Cas particuliers
- **Cas 1 — Indemnité de logement** : `est_imposable = vrai` (incluse dans la base avant exonération). L'exonération logement est une **déduction** après inclusion.
- **Cas 2 — Indemnité de transport justifiée** : `est_imposable = faux` si l'indemnité correspond exactement au coût réel des transports. Si l'indemnité dépasse le coût réel, la partie excédentaire doit être imposable.
- **Cas 3 — Avantage en nature (logement de fonction, véhicule)** : `est_imposable = vrai` — l'avantage en nature est évalué et intégré au brut imposable.

---

## Propriété : `soumis_cnss` (Élément de paie)

### Définition précise
Indique si le montant brut de l'élément de paie est soumis à la cotisation CNSS (Caisse Nationale de Sécurité Sociale). La CNSS est calculée sur **l'ensemble des rémunérations brutes perçues en contrepartie du travail**, sans plafond en RDC.

### Règles
- **Condition d'application** : Applicable à tout élément représentant une rémunération du travail (salaire, prime, commission, avantage en nature).
- **Valeur par défaut** : `vrai` pour toutes les catégories sauf `indemnite` lorsque l'indemnité est un remboursement de frais professionnels réels.
- **Précédence** : La pratique sociale établie en RDC soumet l'indemnité de logement à la CNSS. L'indemnité de transport, si elle est justifiée comme frais professionnel, n'est pas soumise.

### Valeurs "limites"
- **Absent / Vide** : Non applicable — toujours booléen.
- **Invalide** : Rejet à l'étape 1 du pipeline.

### Interactions

| Propriété | Interaction | Comportement résultant |
|-----------|-------------|------------------------|
| `est_exonere_logement = vrai` | `soumis_cnss = vrai` | L'indemnité logement est soumise à CNSS (conformément à la pratique sociale établie en RDC) |
| `soumis_cnss = faux` | `est_imposable = vrai` | Le gain est exclu de la base CNSS mais reste imposable. Rare, mais possible pour certaines indemnités non soumises |
| Base CNSS | Somme des éléments où `soumis_cnss = vrai` | La base CNSS sert au calcul de la retenue CNSS salariale (5 %) et de la charge patronale CNSS (13 %) |

### Cas particuliers
- **Cas 1 — Indemnité de logement** : `soumis_cnss = vrai` (pratique sociale établie en RDC).
- **Cas 2 — Indemnité de transport réelle** : `soumis_cnss = faux` si justifiée comme frais professionnel.
- **Cas 3 — Ticket-restaurant / prime de panier** : `soumis_cnss = vrai` (considéré comme rémunération).

---

## Relation : `montant_brut`, `mode_calcul` et `quantite` (Élément de paie)

### Définition précise
Ces trois attributs déterminent ensemble le montant effectif de l'élément de paie qui sera intégré au salaire brut.

Le **montant brut effectif** est déterminé ainsi :

| `mode_calcul` | Formule | Exemple |
|--------------|---------|---------|
| `fixe` | `montant_effectif = montant_brut` (quantité ignorée) | Salaire de base : 900 000 CDF |
| `taux_horaire` | `montant_effectif = montant_brut × quantite` | HS 30 % : 5 250 CDF/h × 4 h = 21 000 CDF |
| `journalier` | `montant_effectif = montant_brut × quantite` | Indemnité mission : 15 000 CDF/j × 5 j = 75 000 CDF |
| `formule` | `montant_effectif = evaluation(montant_brut, contexte)` | Prime annuelle : formule basée sur le salaire de base × coefficient |

### Règles
- **Condition d'application** : Applicable à tout élément de paie.
- **Valeur par défaut** : `mode_calcul = "fixe"`, `quantite = 1` si non spécifié pour `taux_horaire` ou `journalier`.
- **Précédence** : Le `mode_calcul` détermine la règle d'interprétation. Si `mode_calcul = fixe`, la `quantite` est ignorée même si elle est renseignée.

### Valeurs "limites"
- **Montant brut = 0** : L'élément est inclus dans la liste mais n'a pas d'impact sur le salaire brut (élément déclaratif ou nul).
- **Quantité absente avec mode_calcul = taux_horaire ou journalier** : L'élément est invalide — rejet à l'étape 1.
- **Quantité = 0** : L'élément est présent mais son montant effectif est nul.
- **Mode_calcul = formule sans règle de formule associée** : Invalide — rejet.

### Cas particuliers
- **Cas 1 — Heures supplémentaires** : Le montant brut est le taux horaire de base × coefficient de majoration (1,3 pour les 2 premières heures, 1,6 pour les suivantes). La quantité est le nombre d'heures effectuées.
- **Cas 2 — Primes forfaitaires mensuelles** : Mode = `fixe`, montant = valeur mensuelle. Exemple : prime de transport forfaitaire 30 000 CDF.
- **Cas 3 — Avance sur salaire** : Ce n'est PAS un élément de paie de gain. C'est une retenue (type `avance`) qui sera déduite du salaire.

---

## Mécanisme : Exonération de l'indemnité de logement

### Définition précise
L'indemnité de logement versée à l'employé est exonérée d'impôt (mais pas de CNSS — voir ci-dessus) à hauteur d'un plafond maximal de **30 % du traitement brut imposable**.

### Règles
- **Le traitement brut imposable** est défini comme la somme des éléments où `est_imposable = vrai`, **avant** déduction de l'exonération logement et **avant** déduction de la CNSS.
  - Formule : `brut_imposable_avant_exoneration = Σ(gains avec est_imposable = vrai)`
  - *Note* : Certaines pratiques incluent ou excluent l'indemnité logement elle-même de cette assiette. La règle retenue est **l'indemnité logement est incluse dans le brut imposable servant au calcul du plafond**.
- **Montant exonéré** = `min(montant_indemnite_logement, brut_imposable_avant_exoneration × 30 %)`
- **Fraction réintégrée** = `montant_indemnite_logement − montant_exonere` (cette fraction est soumise à l'impôt et à la CNSS)
- **La CNSS** reste due sur la totalité de l'indemnité logement, y compris la partie exonérée d'impôt (conformément à la pratique sociale).

### Algorithme

```
Étape 1 : Calculer le brut imposable avant exonération
          = Σ(gains avec est_imposable = vrai)
          (cela inclut l'indemnité de logement)

Étape 2 : Calculer le plafond d'exonération
          plafond_logement = brut_imposable_avant_exoneration × 30 %

Étape 3 : Déterminer le montant exonéré
          exoneration_logement = min(montant_indemnite_logement, plafond_logement)

Étape 4 : La base imposable devient
          base_imposable_apres_logement = brut_imposable_avant_exoneration - exoneration_logement
```

### Valeurs "limites"
- **Aucune indemnité logement** : exonération_logement = 0, sans impact.
- **Indemnité logement > plafond 30 %** : exonération plafonnée à 30 % du brut imposable, le surplus est réintégré.
- **Entreprise ne verse pas d'indemnité logement distincte** (logement de fonction) : L'avantage en nature logement est évalué et soumis aux mêmes règles.

### Cas particuliers
- **Cas 1** : Brut imposable = 1 221 000 CDF. Indemnité logement = 270 000 CDF. Plafond = 1 221 000 × 30 % = 366 300 CDF. L'indemnité (270 000) < plafond (366 300) → exonération totale de l'indemnité logement.
- **Cas 2** : Brut imposable = 800 000 CDF. Indemnité logement = 350 000 CDF. Plafond = 800 000 × 30 % = 240 000 CDF. Exonération = 240 000 CDF. Fraction réintégrée = 110 000 CDF.

---

## Mécanisme : Exonération de l'indemnité de transport

### Définition précise
L'indemnité de transport constitue un remboursement de frais professionnels et est exonérée d'impôt (et de CNSS si justifiée) à condition de ne pas présenter un caractère exagéré.

### Règles
- **Plafond d'exonération** : Coût de 4 courses de taxi par jour pour les cadres, 4 courses de bus par jour pour le personnel d'exécution.
- **Évaluation** : Le coût est déterminé par le marché local du transport (ex: Kinshasa). Il est stocké comme paramètre légal (ex: `COURSE_TAXI_KINSHASA`, `COURSE_BUS_KINSHASA`).
- **Montant exonéré** = `min(montant_indemnite_transport, plafond_courses × nombre_jours_ouvres)`
- **Fraction exagérée** = `montant_indemnite_transport − montant_exonere` → réintégrée à la base imposable et à la base CNSS.

### Algorithme

```
Étape 1 : Déterminer le plafond journalier selon la catégorie
          si catégorie = cadre → plafond_journalier = COURSE_TAXI × 4
          si catégorie = execution → plafond_journalier = COURSE_BUS × 4

Étape 2 : Calculer le plafond mensuel
          plafond_mensuel = plafond_journalier × nombre_jours_ouvres

Étape 3 : Déterminer l'exonération
          exoneration_transport = min(montant_indemnite_transport, plafond_mensuel)
```

### Valeurs "limites"
- **Aucune indemnité transport** : exonération = 0.
- **Catégorie non déterminée** : Par défaut, appliquer le plafond "exécution" (plus conservateur).
- **Indemnité transport > plafond mensuel** : Fraction réintégrée imposable et soumise à CNSS.

### Cas particuliers
- **Cas 1** : Cadre, 21 jours ouvrés. Indemnité transport = 100 000 CDF. Course taxi = 1 200 CDF. Plafond = (1 200 × 4) × 21 = 100 800 CDF. Exonération totale = 100 000 CDF.
- **Cas 2** : Exécution, 21 jours ouvrés. Indemnité transport = 80 000 CDF. Course bus = 500 CDF. Plafond = (500 × 4) × 21 = 42 000 CDF. Exonération = 42 000 CDF. Fraction réintégrée = 38 000 CDF.

---

## Mécanisme : Plafonnement de l'impôt à 30 %

### Définition précise
Quel que soit le barème utilisé (IPR ou IRPP), l'impôt théorique calculé ne peut pas excéder 30 % du revenu net imposable (base de l'impôt après exonérations et déduction de la CNSS).

### Règles
- **Étape 1** : Calculer l'impôt théorique via le barème (IPR ou IRPP) sur la base imposable (après exonérations logement/transport et déduction CNSS).
- **Étape 2** : Calculer le plafond = `base_imposable × 30 %`.
- **Étape 3** : L'impôt à retenir = `min(impôt_théorique, plafond)`.

### Algorithme détaillé

```
base_imposable_nette = base_imposable_apres_exonerations − cnss_salariale
impot_theorique = appliquer_bareme(base_imposable_nette)  // IPR ou IRPP
plafond_30 = base_imposable_nette × 0,30
impot_apres_plafonnement = min(impot_theorique, plafond_30)
```

### Valeurs "limites"
- **Impôt théorique < plafond** : L'impôt théorique est retenu (cas général pour les bas salaires).
- **Impôt théorique > plafond** : Le plafond s'applique. C'est le cas pour les hauts revenus où le barème progressif produirait un impôt > 30 % du net imposable.
- **Plafond non atteint** : Aucun ajustement nécessaire.

### Cas particuliers
- **Cas 1 (cas pratique du Guide)** : Base imposable nette = 859 950 CDF. Impôt IRPP théorique = 172 738 CDF. Plafond = 859 950 × 30 % = 257 985 CDF. Plafond non atteint → impôt retenu = 172 738 CDF.
- **Cas 2 (haut revenu)** : Base imposable nette = 10 000 000 CDF. Impôt théorique IRPP ≈ 3 800 000 CDF (≈ 38 %). Plafond = 3 000 000 CDF. Impôt retenu = 3 000 000 CDF.

---

## Mécanisme : Abattement pour charges de famille

### Définition précise
L'impôt après plafonnement bénéficie d'une réduction de 2 % par personne à charge déclarée, dans la limite de 9 personnes (abattement maximal de 18 %).

### Règles
- **Personne à charge** : Épouse(ou mari) et enfants légitimes ou adoptifs à charge, au sens de la législation fiscale congolaise.
- **Taux unitaire** : 2 % par personne à charge.
- **Plafond** : 9 personnes maximum → 18 % maximum.
- **Application** : Pourcentage appliqué à l'impôt **après plafonnement**.
  - `impôt_après_abattement = impôt_après_plafonnement × (1 − min(nombre_charges × 0,02, 0,18))`
- **Arrondi** : Le résultat est arrondi selon la règle d'arrondi configurée.

### Valeurs "limites"
- **0 personne à charge** : Aucun abattement. `impôt_après_abattement = impôt_après_plafonnement`.
- **1-9 personnes** : Abattement proportionnel (2 % à 18 %).
- **10+ personnes** : Abattement plafonné à 18 %.

### Cas particuliers
- **Cas 1 (Guide)** : 3 personnes à charge. Abattement = 6 %. Impôt après plafonnement = 172 738 CDF. Impôt final = 172 738 × 0,94 = **162 373 CDF**.
- **Cas 2** : 9 personnes à charge. Abattement = 18 %. Impôt après plafonnement = 200 000 CDF. Impôt final = 200 000 × 0,82 = **164 000 CDF**.
- **Cas 3** : Divorce ou séparation — l'épouse n'est plus à charge. Mise à jour nécessaire du nombre de personnes à charge avant le calcul.

---

## Propriété : Règles d'arrondi

### Définition précise
Les montants calculés à chaque étape du pipeline sont soumis à une règle d'arrondi configurable. La règle s'applique aux montants intermédiaires et finaux.

### Règles
- **Valeur par défaut** : Arrondi arithmétique à l'unité de franc congolais la plus proche (arrondi standard : 0,5 → supérieur).
  - `round(montant) = floor(montant + 0,5)`
- **Stratégies alternatives possibles** :
  - `arrondi_superieur` : Toujours arrondir à l'unité supérieure (ceil).
  - `arrondi_inferieur` : Toujours arrondir à l'unité inférieure (floor).
  - `aucun` : Conservation des décimales (pour calculs intermédiaires internes).
- **Quand arrondir ?** :
  - Chaque base de calcul (étape 4) : arrondi à l'unité.
  - Chaque retenue (étape 5) : arrondi à l'unité.
  - Chaque charge patronale (étape 6) : arrondi à l'unité.
  - Net à payer (étape 7) : arrondi à l'unité.
  - Coût total employeur (étape 7) : arrondi à l'unité.
- **Où stocker la règle ?** : Dans les paramètres légaux, code `REGLE_ARRONDI`.

### Valeurs "limites"
- **Arrondi non configuré** : Arrondi arithmétique standard (défaut).
- **Montant négatif** : L'arrondi s'applique symétriquement (ex: −61,5 → −61 pour l'arrondi arithmétique, ou −62 pour l'arrondi supérieur).

### Cas particuliers
- **Calculs multi-étapes** : Appliquer l'arrondi à **chaque étape**, pas seulement au résultat final. Exemple : CNSS = arrondi(base CNSS × 5 %). Impôt = arrondi(arrondi(impôt théorique) × (1 − abattement)). Chaque arrondi intermédiaire préserve la traçabilité.

---

## Propriété : Taux de change (Période de paie)

### Définition précise
Le taux de change CDF/USD est une donnée d'entrée du processus de paie qui permet de convertir les éléments libellés en USD vers le CDF, monnaie de référence du calcul de paie en RDC.

### Règles
- **Statut** : Propriété de la Période de paie (concept D3 validé).
- **Source** : Définie au lancement du processus de paie, typiquement depuis le taux BCC (Banque Centrale du Congo) du dernier jour ouvré de la période.
- **Application** : Tout élément de paie exprimé en USD est converti en CDF avant intégration dans le pipeline :
  - `montant_cdf = montant_usd × taux_change`
- **Snapshot** : Le taux utilisé est figé dans le bulletin de paie (attribut `taux_change_utilise`).

### Valeurs "limites"
- **Taux absent** : Si aucun taux n'est fourni et qu'aucun élément n'est libellé en USD, le taux est ignoré. Si des éléments USD existent sans taux → erreur (étape 1).
- **Taux = 0** : Invalide — rejet à l'étape 1.
- **Plusieurs taux concurrents** : Un seul taux par période est retenu. Le taux BCC prime, avec fallback possible sur un taux configuré manuellement.

### Cas particuliers
- **Opérations en double devise** : Certaines entreprises fixent une partie du salaire en USD. Ces éléments sont convertis en CDF au taux de la période avant intégration dans le pipeline.
- **Variation intra-période** : Le taux retenu est unique pour toute la période. On utilise le taux moyen ou le taux de clôture (à définir dans la politique de l'entreprise).

---

## Mécanisme : Proratisation des entrées et sorties

### Définition précise
Lorsqu'un employé commence ou termine son contrat en cours de période, son salaire de base est réduit proportionnellement au nombre de jours calendaires effectivement travaillés dans la période.

### Règles

- **Unité de prorata** : Jours calendaires (pas jours ouvrés). C'est le standard en RDC.
- **Formule** : `salaire_proratisé = salaire_de_base × (nb_jours_travaillés / nb_jours_calendaires_période)`
- **Décompte des jours travaillés** :
  - Pour une **embauche** : du `max(date_embauche, date_debut_période)` à `date_fin_période`, inclus
  - Pour une **sortie** : de `date_debut_période` à `min(date_sortie, date_fin_période)`, inclus
  - Les week-ends et jours fériés ne sont pas déduits — c'est un prorata strictement calendaire
- **Périmètre** : Seul le salaire de base est proratisé. Les indemnités fixes et primes mensuelles restent calculées en mois complet, sauf clause contractuelle contraire. Les heures supplémentaires sont toujours calculées sur les heures réellement effectuées (pas de prorata).

### Algorithme

```
Étape 1 : Déterminer la période d'activité dans le mois
          date_debut_activite = max(date_debut_contrat, date_debut_periode)
          date_fin_activite   = min(date_fin_contrat ?? date_fin_periode, date_fin_periode)

Étape 2 : Calculer le nombre de jours calendaires travaillés
          nb_jours_travailles = date_fin_activite - date_debut_activite + 1

Étape 3 : Appliquer le prorata
          salaire_proratise = salaire_de_base × nb_jours_travailles / nb_jours_calendaires_periode

Étape 4 : Arrondir à l'unité (arrondi arithmétique)
```

### Valeurs « limites »

| Situation | nb_jours_travaillés | Effet |
|-----------|---------------------|-------|
| Embauche le 1er jour du mois | = nb_jours_calendaires | Pas de prorata |
| Embauche le dernier jour du mois | 1 | Salaire = 1/nb_jours_calendaires × base |
| Sortie le 1er jour du mois | 1 | Même règle |
| Employé présent tout le mois | = nb_jours_calendaires | Pas de prorata |
| Embauche et sortie dans le même mois | nb_jours effectifs | Prorata sur la période réelle |

### Interaction avec les autres mécanismes

- **Exonération logement** : Calculée sur le salaire proratisé (le plafond de 30 % s'applique au brut imposable proratisé).
- **Abattement familial** : Calculé sur l'impôt (inchangé — l'abattement dépend des personnes à charge, pas du temps de présence).
- **CNSS** : Calculée sur la base CNSS complète (incluant tous les éléments du mois). Seul le salaire de base est proratisé, mais les autres éléments (logement, prime) restent intacts.
- **Arrondi** : Appliqué après prorata (étape 4 de l'algorithme), avant intégration dans le pipeline.

---

## Concept : Construction des bases de calcul

### Définition précise
Les bases de calcul sont construites à l'étape 4 du pipeline par filtrage et accumulation des éléments de paie selon leurs indicateurs d'assujettissement. Ce n'est pas une saisie — c'est un calcul automatique et déterministe.

### Règles

#### Ordre de construction (important pour les dépendances)

```
1. Base BRUT        = Σ tous les éléments de gain (sans exception)
                       → pas de filtre, c'est la somme totale

2. Base CNSS        = Σ éléments où soumis_cnss = vrai
                       → inclut l'indemnité logement (pratique sociale)
                       → exclut l'indemnité transport réelle (frais professionnels)
                       → PAS DE PLAFOND en RDC

3. Base INPP        = Σ éléments où soumis_inpp = vrai
                       → généralement identique à la base CNSS

4. Base ONEM        = Σ éléments où soumis_onem = vrai
                       → généralement identique à la base CNSS

5. Base IMPOSABLE   = (Σ éléments où est_imposable = vrai)
                       − exonération logement (plafonnée 30%)
                       − exonération transport (frais professionnels)
                       − CNSS salariale (5% de la base CNSS)
```

### Interactions entre bases et retenues/charges

| Base | Utilisée pour | Formule de retenue/charge |
|------|--------------|---------------------------|
| Base CNSS | Retenue CNSS salariale | `base_CNSS × 5 %` |
| Base CNSS | Charge patronale CNSS | `base_CNSS × 13 %` (3 branches) |
| Base IMPOSABLE | Retenue IPR/IRPP | Barème progressif → plafonnement → abattement |
| Base INPP | Charge patronale INPP | `base_INPP × taux_INPP_selon_effectif` |
| Base ONEM | Charge patronale ONEM | `base_ONEM × 0,5 %` |

### Valeurs "limites"
- **Base vide (0 CDF)** : Si aucun élément ne correspond au filtre, la base est égale à 0 CDF. La retenue associée est nulle. C'est légal (aucun impôt, aucune cotisation si pas de rémunération).
- **Base négative** : Impossible — les montants sont toujours positifs et la somme de positifs est positive. Si une base négative apparaît, c'est une erreur de calcul.

### Cas particuliers
- **Base CNSS sans plafond** : Contrairement à certains pays, la RDC n'applique aucun plafond à la base CNSS. L'intégralité du brut est soumise.
- **Différence entre base INPP et base ONEM** : En pratique, ces bases sont identiques à la base CNSS. Mais le métamodèle prévoit des indicateurs distincts pour permettre des évolutions réglementaires futures.
- **Base imposable = 0 ou négative** : Si exonérations + CNSS > brut imposable, la base imposable devient nulle (zéro, pas négative). L'impôt est nul.

---

## État : Cycle de vie du Bulletin de paie

### Définition précise
Le bulletin de paie passe par quatre états au cours de sa vie. Seul l'état `Validé` est définitif.

| État | Signification | Actions possibles |
|------|---------------|-------------------|
| `En cours` | Le pipeline est en exécution, les valeurs ne sont pas stabilisées | Aucune (état interne au pipeline) |
| `Calculé` | Le pipeline a terminé, tous les montants sont connus | Consultation, re-calcul si besoin |
| `Généré` | Le bulletin est figé avec son snapshot d'audit | Consultation, export |
| `Validé` | Le bulletin est approuvé par le gestionnaire | Aucune modification possible |

### Règles de transition

```
[En cours] ──(pipeline terminé)──> [Calculé]
[Calculé] ──(snapshot généré)──> [Généré]
[Généré] ──(validation manuelle)──> [Validé]
[Calculé] ──(re-lancement pipeline)──> [En cours]  (boucle possible avant validation)
```

- **Transition interdite** : `Validé → En cours` (immuable).
- **Correction après validation** : Un nouveau bulletin doit être créé pour la même période avec une version incrémentée.

### Valeurs "limites"
- **Bulletin bloqué en Calculé** : Si le snapshot n'est pas généré, le bulletin reste calculé mais pas figé. C'est un état temporaire.
- **Validation automatique** : En option si le gestionnaire active la validation automatique (à utiliser avec précaution).

---

## Interaction : Ordre de calcul des retenues

### Définition précise
L'ordre dans lequel les retenues salariales sont calculées est important car la CNSS salariale (5 %) est déductible de la base imposable.

### Ordre impératif

```
1. Calculer la CNSS salariale        (base CNSS × 5 %)
2. Calculer la base imposable nette  (base IMPOSABLE − CNSS salariale)
3. Calculer l'impôt (IPR/IRPP)      (barème sur base imposable nette)
4. Autres retenues éventuelles       (saisie-arrêt, avance, cotisation mutuelle)
```

### Règle d'interaction

La CNSS salariale **réduit** la base imposable. C'est une charge fiscalement déductible. L'ordre de calcul est donc critique :

```
base_imposable_nette = base_imposable_apres_exonerations − cnss_salariale
```

### Cas particulier
- **CNSS salariale calculée mais impôt nul** : Si après déduction de la CNSS, la base imposable devient nulle ou négative, l'impôt est nul. La CNSS reste due (elle est calculée sur la base CNSS, pas sur la base imposable).
- **Absence de retenue CNSS (travailleur non affilié)** : La CNSS salariale = 0. La base imposable n'est pas réduite de ce montant.

---

## Événement : Lancement du processus de paie

### Définition précise
Action déclenchée par le gestionnaire de paie qui initie l'exécution du pipeline de calcul pour un ensemble d'employés sur une période donnée.

### Règles
- **Déclencheur** : Action manuelle (gestionnaire) ou programmée (cron).
- **Entrées requises** :
  - Période de paie (avec taux de change si applicable)
  - Liste des employés actifs sur la période
  - Contrats actifs pour chaque employé
  - Éléments de paie fixes (issus des contrats)
  - Éléments de paie variables (saisis pour la période)
  - Paramètres légaux applicables à la période
- **Sortie** : Un bulletin de paie par employé (état `Calculé` → `Généré`).

### Conditions préalables
- La période ne doit pas être déjà clôturée.
- Toutes les données variables doivent être saisies (temps de travail, primes exceptionnelles, etc.).
- Les paramètres légaux doivent être définis pour la période.

### Cas particuliers
- **Nouvel employé en cours de période** : Le calcul est proratisé (au prorata des jours ouvrés restants ou des jours calendaires — à définir dans la politique).
- **Employé sorti en cours de période** : Calcul proratisé jusqu'à la date de sortie.
- **Absence non rémunérée** : L'absence doit être traduite en réduction des éléments variables avant le lancement.

---

## Événement : Snapshot d'audit (étape 8)

### Définition précise
À la génération du bulletin, une copie complète et horodatée de tous les paramètres légaux utilisés est jointe au bulletin. Cette copie est un **snapshot** — elle ne change pas même si les paramètres légaux sont modifiés ultérieurement.

### Contenu du snapshot

```
{
  "date_generation": "2026-01-31T18:00:00Z",
  "regle_arrondi": "arithmetique",
  "taux_change": { "valeur": 2850, "source": "BCC" },
  "parametres_legaux": {
    "SMIG_2026": { "valeur": 21500, "unite": "CDF/jour" },
    "TAUX_CNSS_SALARIAL": { "valeur": 0.05 },
    "TAUX_CNSS_PATRONAL": { "valeur": 0.13 },
    "BAREME_IRPP_2026": { "tranches": [ ... ] },
    "TAUX_INPP": { "valeur": 0.035, "condition": "effectif_1_50" },
    "TAUX_ONEM": { "valeur": 0.005 },
    ...
  },
  "formules_appliquees": {
    "cnss_salariale": "base_cnss × 0.05",
    "irpp": "bareme_10_tranches(base_imposable) → plafonnement(30%) → abattement_familial(2%×charge)",
    ...
  }
}
```

### Règle
- Intégrité : Le snapshot est signé par un hash (SHA-256) qui permet de vérifier qu'il n'a pas été modifié après génération.
- Immuabilité : Le snapshot est en lecture seule après génération.
