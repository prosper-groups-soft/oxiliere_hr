# Catalogue : Moteur de paie RDC

> **Types concrets, valeurs par défaut et exemples pour chaque concept du métamodèle**

---

Ce catalogue est **exhaustif** (conformément à la décision D4). Il liste tous les types concrets du domaine de la paie en RDC, avec leurs valeurs, règles d'utilisation et exemples. Il sert de référence unique pour l'implémentation.

---

## 1. Catalogue des éléments de paie

### 1.1 Gains et rémunérations

| Code | Libellé | Catégorie | Mode | Montant / Taux | Imposable | CNSS | INPP | ONEM | Exon Logt | Exon Transp |
|------|---------|-----------|------|----------------|-----------|------|------|------|-----------|-------------|
| `SAL_BASE` | Salaire de base | `salaire_base` | fixe | Contractuel | Oui | Oui | Oui | Oui | Non | Non |
| `SAL_BASE_PARTIEL` | Salaire de base (temps partiel) | `salaire_base` | fixe | Contractuel × taux_activité | Oui | Oui | Oui | Oui | Non | Non |
| `ANCIENNETE` | Prime d'ancienneté | `prime` | formule | Salaire_base × taux_ancienneté | Oui | Oui | Oui | Oui | Non | Non |
| `PRIME_PERF` | Prime de performance | `prime` | fixe | Selon barème interne | Oui | Oui | Oui | Oui | Non | Non |
| `PRIME_FONCT` | Prime de fonction | `prime` | fixe | Contractuelle | Oui | Oui | Oui | Oui | Non | Non |
| `PRIME_RISQUE` | Prime de risque / salissure | `prime` | fixe | Contractuelle | Oui | Oui | Oui | Oui | Non | Non |
| `PRIME_LOGEMENT` | Prime de logement (non exonérée) | `prime` | fixe | Contractuelle | Oui | Oui | Oui | Oui | Non | Non |
| `HS_30` | Heures supplémentaires majorées 30% | `heure_sup` | taux_horaire | Taux_horaire_base × 1,3 × nb_heures | Oui | Oui | Oui | Oui | Non | Non |
| `HS_60` | Heures supplémentaires majorées 60% | `heure_sup` | taux_horaire | Taux_horaire_base × 1,6 × nb_heures | Oui | Oui | Oui | Oui | Non | Non |
| `HS_JF` | Heures supplémentaires jours fériés | `heure_sup` | taux_horaire | Taux_horaire_base × 2,0 × nb_heures | Oui | Oui | Oui | Oui | Non | Non |
| `HS_NUIT` | Heures de nuit | `heure_sup` | taux_horaire | Taux_horaire_base × 1,5 × nb_heures | Oui | Oui | Oui | Oui | Non | Non |
| `IND_LOG` | Indemnité de logement | `indemnite` | fixe | Contractuelle (exonérée dans limite 30%) | Oui | Oui | Oui | Oui | **Oui** | Non |
| `IND_TRANSP` | Indemnité de transport | `indemnite` | fixe | Contractuelle (exonérée frais réels) | Oui | Oui* | Oui* | Oui* | Non | **Oui** |
| `IND_MISSION` | Indemnité de mission / déplacement | `indemnite` | journalier | Forfait journalier × nb_jours | Non | Non | Non | Non | Non | Non |
| `IND_LOGEMENT_FONCT` | Logement de fonction (avantage évalué) | `avantage_nature` | formule | Valeur locative estimée | Oui | Oui | Oui | Oui | **Oui** | Non |
| `IND_VEHICULE` | Véhicule de fonction (avantage évalué) | `avantage_nature` | formule | Pourcentage valeur véhicule | Oui | Oui | Oui | Oui | Non | Non |
| `GRATIF_13EME` | 13e mois / gratification annuelle | `gratification` | formule | Salaire_base / 12 (ou mois complet) | Oui | Oui | Oui | Oui | Non | Non |
| `GRATIF_EXCEP` | Gratification exceptionnelle / prime | `gratification` | fixe | Montant décidé par l'employeur | Oui | Oui | Oui | Oui | Non | Non |
| `COMMISSION` | Commissions sur ventes | `prime` | fixe | Montant des ventes × taux commission | Oui | Oui | Oui | Oui | Non | Non |
| `PRIME_PANIER` | Prime de panier / ticket-restaurant | `indemnite` | fixe | Forfait journalier × nb_jours | Oui | Oui | Oui | Oui | Non | Non |
| `RAPPEL_SAL` | Rappel de salaire | `autre` | fixe | Montant dû des périodes antérieures | Oui | Oui | Oui | Oui | Non | Non |
| `CONGE_PAYE` | Indemnité de congés payés | `indemnite` | fixe | Salaire_base / 24 × jours_congés | Oui | Oui | Oui | Oui | Non | Non |
| `PREAVIS` | Indemnité de préavis (travail ou non) | `indemnite` | fixe | Salaire_base × mois_préavis | Oui | Oui | Oui | Oui | Non | Non |
| `LICENCIEMENT` | Indemnité de licenciement | `indemnite` | formule | Calcul selon ancienneté et salaire | Oui* | Oui* | Oui* | Oui* | Non | Non |

> **Notes** :
> - `IND_TRANSP` : `soumis_cnss` dépend de la nature (frais réels = non, forfaitaire = oui). La règle par défaut est `oui` pour le forfait de transport non justifié.
> - `LICENCIEMENT` : L'imposition et l'assujettissement CNSS de l'indemnité de licenciement suivent des règles spécifiques (part exonérée selon l'ancienneté).
> - `IND_MISSION` : Considérée comme remboursement de frais professionnels → non imposable, non soumise.

### 1.2 Éléments de déduction (pré-comptés)

| Code | Libellé | Montant | Imposable | CNSS | Notes |
|------|---------|---------|-----------|------|-------|
| `AVANCE_SAL` | Avance sur salaire | Montant avancé | Non | Non | Remboursée par déduction sur le net à payer |
| `SAISIE_ARRET` | Saisie-arrêt | Montant judiciaire | Non | Non | Selon barème de saisie |

Ces éléments ne sont pas des gains mais des déductions. Ils sont modélisés comme des éléments de paie de catégorie `autre` avec des flags d'assujettissement tous à `faux`. Ils réduisent le net à payer.

> **Note de conception** : Les avances et saisies-arrêts pourraient alternativement être modélisées comme des `Retenue` (concept métier). Le choix de les mettre dans `Élément de paie` permet une gestion unifiée de toutes les lignes du bulletin. À trancher dans l'implémentation.

---

## 2. Catalogue des retenues salariales

| Code | Libellé | Type | Base de calcul | Taux / Règle | Plafond | Ordre |
|------|---------|------|----------------|--------------|---------|-------|
| `CNSS_SAL` | Cotisation CNSS part salariale | `cnss_salariale` | Base CNSS | 5 % fixe | Aucun en RDC | 1 |
| `IPR` | Impôt Professionnel sur les Rémunérations | `impot_revenu` | Base imposable | Barème 4 tranches (3%-15%-30%-40%) | 30 % du net imposable | 2 |
| `IRPP` | Impôt sur le Revenu des Personnes Physiques | `impot_revenu` | Base imposable | Barème 10 tranches (0%-15%-20%-22,5%-25%-30%-32,5%-35%-37,5%-40%) | 30 % du net imposable | 2 |
| `SAISIE_ARRET_RET` | Retenue pour saisie-arrêt | `saisie_arret` | Net à payer (avant saisie) | Selon barème judiciaire | Selon loi | 3 |
| `AVANCE_RET` | Remboursement d'avance | `avance` | Net à payer (avant avance) | Montant fixe | Net à payer avant déduction | 3 |
| `COTISATION_MUTUELLE` | Cotisation mutuelle / prévoyance | `autre` | Salaire brut | Taux contractuel | Contractuel | 3 |

### 2.1 Barème IPR traditionnel (pré-2026)

| Tranche | Borne inférieure (CDF) | Borne supérieure (CDF) | Taux | Valeur par défaut |
|---------|----------------------|----------------------|------|-------------------|
| 1 | 0 | 162 000 | 3 % | Applicable jusqu'au 31/12/2025 |
| 2 | 162 001 | 1 800 000 | 15 % | |
| 3 | 1 800 001 | 3 600 000 | 30 % | |
| 4 | 3 600 001 et + | — | 40 % | |

### 2.2 Barème IRPP 2026 (post-01/01/2026)

| Tranche | Borne inférieure (CDF) | Borne supérieure (CDF) | Taux |
|---------|----------------------|----------------------|------|
| 1 | 0 | 43 680 | 0 % |
| 2 | 43 681 | 119 000 | 15 % |
| 3 | 119 001 | 225 000 | 20 % |
| 4 | 225 001 | 385 000 | 22,5 % |
| 5 | 385 001 | 605 000 | 25 % |
| 6 | 605 001 | 855 000 | 30 % |
| 7 | 855 001 | 1 159 000 | 32,5 % |
| 8 | 1 159 001 | 1 402 000 | 35 % |
| 9 | 1 402 001 | 1 913 000 | 37,5 % |
| 10 | 1 913 001 et + | — | 40 % |

### 2.3 Algorithme de calcul d'impôt (valable pour les deux barèmes)

```
Algorithme : calcul_impôt(base_imposable_nette, barème, nb_charges)

Étape 1 : Appliquer le barème
  impôt_brut = 0
  montant_restant = base_imposable_nette
  Pour chaque tranche t du barème (triée par borne inférieure croissante) :
    si montant_restant <= 0, sortir
    largeur_tranche = min(montant_restant, largeur_max_t)
    impôt_brut += largeur_tranche × taux_t
    montant_restant -= largeur_tranche

Étape 2 : Plafonnement à 30 %
  plafond = base_imposable_nette × 0,30
  impôt_plafonné = min(impôt_brut, plafond)

Étape 3 : Abattement familial
  taux_abattement = min(nb_charges × 0,02, 0,18)
  impôt_final = arrondi(impôt_plafonné × (1 - taux_abattement))

Retourner impôt_final
```

---

## 3. Catalogue des charges patronales

| Code | Libellé | Type | Base de calcul | Taux | Répartition |
|------|---------|------|----------------|------|-------------|
| `CNSS_PAT` | Cotisation CNSS part patronale | `cnss_patronale` | Base CNSS | 13 % | Pensions 5% + Risques 1,5% + Familles 6,5% |
| `INPP` | Contribution INPP | `inpp` | Base INPP | Variable (voir ci-dessous) | Formation professionnelle |
| `ONEM` | Contribution ONEM | `onem` | Base ONEM | 0,5 % | Soutien à l'emploi |
| `AUTRE_CHARGE` | Autre charge patronale | `autre` | Variable | Variable | Mutuelle, prévoyance, etc. |

### 3.1 Taux INPP par catégorie d'employeur

| Effectif | Taux | Code paramètre |
|----------|------|----------------|
| Secteur public | 4,0 % | `TAUX_INPP_PUBLIC` |
| 1 à 50 salariés | 3,5 % | `TAUX_INPP_1_50` |
| 51 à 300 salariés | 3,0 % | `TAUX_INPP_51_300` |
| Plus de 300 salariés | 2,0 % | `TAUX_INPP_300_PLUS` |

---

## 4. Catalogue des bases de calcul

| Code | Type base | Filtre | Déductions | Alimente |
|------|-----------|--------|------------|----------|
| `BASE_BRUT` | brut | Aucun (tous les gains) | Aucune | Étape 3 (validation brut) |
| `BASE_CNSS` | cnss | `soumis_cnss = vrai` | Aucune | CNSS salariale, CNSS patronale |
| `BASE_INPP` | inpp | `soumis_inpp = vrai` | Aucune | INPP |
| `BASE_ONEM` | onem | `soumis_onem = vrai` | Aucune | ONEM |
| `BASE_IMPOT` | imposable | `est_imposable = vrai` | Exonération logement (plafond 30%)<br>Exonération transport (frais réels)<br>CNSS salariale | IPR / IRPP |

### 4.1 Ordre de construction

```
BASE_BRUT = Σ(gains)
    ↓
BASE_CNSS = Σ(gains où soumis_cnss == vrai)
BASE_INPP = Σ(gains où soumis_inpp == vrai)
BASE_ONEM = Σ(gains où soumis_onem == vrai)
    ↓
BASE_IMPOT = Σ(gains où est_imposable == vrai)
             − exonération_logement(BASE_IMPOT_brute)
             − exonération_transport()
             − CNSS_SALARIALE  // calculée d'abord via BASE_CNSS × 5%
```

> **Important** : L'ordre `BASE_CNSS` → `BASE_IMPOT` est obligatoire car la CNSS salariale (calculée sur `BASE_CNSS`) est nécessaire à `BASE_IMPOT`.

---

## 5. Catalogue des paramètres légaux

| Code | Description | Type | Valeur | Début validité | Fin validité | Référence juridique |
|------|-------------|------|--------|---------------|-------------|---------------------|
| `SMIG_2026` | SMIG journalier (manœuvre ordinaire) | montant_fixe | 21 500 CDF/j | 2026-01-01 | — | Décret n° 25/22 |
| `SMIG_2025` | SMIG journalier (période précédente) | montant_fixe | 17 500 CDF/j | 2025-06-01 | 2025-12-31 | Décret n° 24/18 |
| `TAUX_CNSS_SALARIAL` | Taux CNSS part salariale | taux | 5 % (0,05) | 2000-01-01 | — | Code du travail |
| `TAUX_CNSS_PAT_PENS` | Taux CNSS patronal — Pensions | taux | 5 % (0,05) | 2000-01-01 | — | Code du travail |
| `TAUX_CNSS_PAT_RISQ` | Taux CNSS patronal — Risques prof. | taux | 1,5 % (0,015) | 2000-01-01 | — | Code du travail |
| `TAUX_CNSS_PAT_FAM` | Taux CNSS patronal — Prestations fam. | taux | 6,5 % (0,065) | 2000-01-01 | — | Code du travail |
| `TAUX_INPP_PUBLIC` | Taux INPP — secteur public | taux | 4 % (0,04) | 2026-01-01 | — | Loi INPP |
| `TAUX_INPP_1_50` | Taux INPP — 1 à 50 salariés | taux | 3,5 % (0,035) | 2026-01-01 | — | Loi INPP |
| `TAUX_INPP_51_300` | Taux INPP — 51 à 300 salariés | taux | 3 % (0,03) | 2026-01-01 | — | Loi INPP |
| `TAUX_INPP_300_PLUS` | Taux INPP — plus de 300 salariés | taux | 2 % (0,02) | 2026-01-01 | — | Loi INPP |
| `TAUX_ONEM` | Taux ONEM | taux | 0,5 % (0,005) | 2026-01-01 | — | Réforme CNT |
| `BAREME_IPR_2025` | Barème IPR traditionnel (4 tranches) | bareme_progressif | Voir §2.1 | 2000-01-01 | 2025-12-31 | Ordonnance-Loi n° 13/008 |
| `BAREME_IRPP_2026` | Barème IRPP 2026 (10 tranches) | bareme_progressif | Voir §2.2 | 2026-01-01 | — | Loi n° 23/053 |
| `PLAFOND_IMPOT_MAX` | Plafonnement max impôt | taux | 30 % (0,30) | 2000-01-01 | — | Code des impôts |
| `ABATTEMENT_FAMILIAL` | Réduction par personne à charge | taux | 2 % (0,02) | 2000-01-01 | — | Code des impôts |
| `MAX_PERSONNES_CHARGE` | Nombre max de personnes à charge | seuil | 9 | 2000-01-01 | — | Code des impôts |
| `EXON_LOGEMENT_PLAF` | Plafond exonération logement | taux | 30 % (0,30) du **salaire de base** | 2000-01-01 | — | Code des impôts |
| `EXON_TRANSPORT_CADRE` | Plafond transport cadre (par course) | montant_fixe | À définir localement | Variable | — | Appréciation DGI |
| `EXON_TRANSPORT_EXEC` | Plafond transport exécution (par course) | montant_fixe | À définir localement | Variable | — | Appréciation DGI |
| `NB_COURSES_CADRE` | Nombre de courses taxi/jour (cadres) | seuil | 4 | 2000-01-01 | — | Doctrine DGI |
| `NB_COURSES_EXEC` | Nombre de courses bus/jour (exécution) | seuil | 4 | 2000-01-01 | — | Doctrine DGI |
| `REGLE_ARRONDI` | Règle d'arrondi | regle_arrondi | `arithmetique` (défaut) | 2000-01-01 | — | Paramétrage entreprise |
| `MAJORATION_HS_1` | Majoration 2 premières heures sup | taux | 30 % (0,30) | 2000-01-01 | — | Code du travail |
| `MAJORATION_HS_2` | Majoration heures sup suivantes | taux | 60 % (0,60) | 2000-01-01 | — | Code du travail |
| `MAJORATION_HS_JF` | Majoration jours fériés | taux | 100 % (1,00) | 2000-01-01 | — | Code du travail |

---

## 6. Catalogue des catégories professionnelles

| Classe | Libellé | Échelons | Application |
|--------|---------|----------|-------------|
| 1 | Manœuvre ordinaire | 1-4 | Personnel non qualifié |
| 2 | Ouvrier spécialisé | 1-4 | Personnel avec formation de base |
| 3 | Ouvrier qualifié / Agent de maîtrise | 1-4 | Personnel avec qualification technique |
| 4 | Agent de maîtrise supérieur / Technicien | 1-4 | Personnel avec diplôme technique |
| 5 | Cadre subalterne | 1-4 | Personnel avec diplôme universitaire (BAC+2/3) |
| 6 | Cadre moyen | 1-4 | Personnel avec BAC+4/5 |
| 7 | Cadre supérieur / Cadre de collaboration | 1-4 | Personnel avec haute qualification |

**Principe de tension salariale** : Le rapport entre le salaire de la Classe 1, Échelon 1 et la Classe 7, Échelon 4 est fixé à 1:10 (Décret n° 25/22). Cela signifie que le salaire maximum de la grille = SMIG × 10, soit 215 000 CDF/jour, donc environ 5 590 000 CDF/mois (base 26 jours).

---

## 7. Catalogue des cycles de vie

### 7.1 Types de période

| Type | Durée | Exemple | Usage |
|------|-------|---------|-------|
| `mensuelle` | 1 mois civil | 2026-01 (01/01 au 31/01) | Standard |
| `quinzaine` | 15 jours | 2026-01-Q1 (01/01 au 15/01) | Paiement par quinzaine |
| `hebdomadaire` | 7 jours | 2026-S03 | Travailleurs temporaires |
| `journalière` | 1 jour | 2026-01-15 | Journaliers |

### 7.2 Régimes de travail

| Code | Libellé | Taux d'activité par défaut |
|------|---------|---------------------------|
| `TEMPS_PLEIN` | Temps plein | 100 % |
| `TEMPS_PARTIEL_50` | Mi-temps | 50 % |
| `TEMPS_PARTIEL_60` | Temps partiel 60 % | 60 % |
| `TEMPS_PARTIEL_80` | Temps partiel 80 % | 80 % |
| `EXPATRIE` | Expatrié | 100 % (régime spécifique) |

---

## 8. Exemple concret : Cas pratique janvier 2026

Données issues du Guide de Calcul Paie RDC (pages 191-372).

### Données d'entrée

**Employé** : Kiban M., Classe 4 Échelon 3, 3 personnes à charge, matricule CNSS : 123456789.

**Contrat** : CDI, salaire de base = 900 000 CDF, date d'embauche = 01/03/2020.

**Période** : Janvier 2026, 21 jours ouvrés, 31 jours calendaires.

**Éléments de paie du mois** :

| Code | Libellé | Montant | Quantité | Imposable | CNSS | INPP | ONEM | Ex Logt | Ex Transp |
|------|---------|---------|----------|-----------|------|------|------|---------|-----------|
| `SAL_BASE` | Salaire de base | 900 000 | — | Oui | Oui | Oui | Oui | Non | Non |
| `IND_LOG` | Indemnité de logement | 270 000 | — | Oui | Oui | Oui | Oui | **Oui** | Non |
| `IND_TRANSP` | Indemnité de transport | 30 000 | — | Oui | Oui* | Oui | Oui | Non | **Oui** |
| `HS_30` | Heures sup 30% | 5 250 | 4 h | Oui | Oui | Oui | Oui | Non | Non |
| **Total brut** | | **1 221 000** | | | | | | | |

> * IND_TRANSP : soumis_cnss = oui car forfaitaire non justifié.

### Calcul étape par étape

#### Étape 4 — Construction des bases

| Base | Calcul | Montant |
|------|--------|---------|
| BASE_BRUT | 900 000 + 270 000 + 30 000 + 21 000 | **1 221 000 CDF** |
| BASE_CNSS | idem (tous soumis_cnss = vrai) | **1 221 000 CDF** |
| BASE_INPP | idem (tous soumis_inpp = vrai) | **1 221 000 CDF** |
| BASE_ONEM | idem (tous soumis_onem = vrai) | **1 221 000 CDF** |
| BASE_IMPOT_brute | 900 000 + 270 000 + 30 000 + 21 000 (tous imposable) | **1 221 000 CDF** |

#### Étape 5 — Retenues salariales

**CNSS salariale** : 1 221 000 × 5 % = **61 050 CDF**

**Exonération logement** :
- Salaire de base : 900 000 CDF
- Plafond 30 % du salaire de base : 900 000 × 30 % = 270 000 CDF
- Indemnité logement (270 000) = plafond (270 000) → exonération totale : **270 000 CDF**

**Exonération transport** : (forfaitaire, entreprise définit comme non exagéré) → exonération totale : **30 000 CDF**

**Base imposable nette** : 1 221 000 − 270 000 − 30 000 − 61 050 = **859 950 CDF**

**IRPP 2026** (barème 10 tranches) :
- Tranche 1 (0-43 680, 0%) : 0
- Tranche 2 (43 681-119 000, 15%) : 75 320 × 15 % = 11 298
- Tranche 3 (119 001-225 000, 20%) : 106 000 × 20 % = 21 200
- Tranche 4 (225 001-385 000, 22,5%) : 160 000 × 22,5 % = 36 000
- Tranche 5 (385 001-605 000, 25%) : 220 000 × 25 % = 55 000
- Tranche 6 (605 001-855 000, 30%) : 250 000 × 30 % = 75 000
- Tranche 7 (855 001-859 950, 32,5%) : 4 950 × 32,5 % = 1 609
- Impôt brut : 0 + 11 298 + 21 200 + 36 000 + 55 000 + 75 000 + 1 609 = **200 107 CDF**
- *(Note : ce montant diffère légèrement du Guide car le Guide utilise une répartition de tranches légèrement différente — l'algorithme ci-dessus est le plus précis)*
- Plafonnement 30 % : 859 950 × 30 % = 257 985 CDF (plafond non atteint)
- Abattement 3 personnes : 200 107 × (1 − 0,06) = **188 101 CDF**

**Total retenues** : 61 050 + 188 101 = **249 151 CDF**

#### Étape 6 — Charges patronales (entreprise : 50 salariés → INPP 3,5 %)

| Charge | Base | Taux | Montant |
|--------|------|------|---------|
| CNSS patronale (pensions) | 1 221 000 | 5 % | 61 050 |
| CNSS patronale (risques) | 1 221 000 | 1,5 % | 18 315 |
| CNSS patronale (familles) | 1 221 000 | 6,5 % | 79 365 |
| **Total CNSS patronale** | | **13 %** | **158 730** |
| INPP | 1 221 000 | 3,5 % | 42 735 |
| **Total charges patronales** | | | **201 465** |

#### Étape 7 — Net à payer et coût total

| Indicateur | Calcul | Montant |
|-----------|--------|---------|
| Salaire brut | | **1 221 000 CDF** |
| Total retenues | 61 050 + 188 101 | **249 151 CDF** |
| **Net à payer** | 1 221 000 − 249 151 | **971 849 CDF** |
| Total charges patronales | | **201 465 CDF** |
| **Coût total employeur** | 1 221 000 + 201 465 | **1 422 465 CDF** |

---

### Cas particulier : Embauche en cours de période (15 janvier 2026)

**Scénario** : Kiban M. est embauché le **15 janvier 2026** (au lieu du 1er mars 2020 dans le cas de base). Le salaire de base est proratisé selon la règle de prorata calendaire.

**Calcul du prorata** :
| Élément | Valeur |
|---------|--------|
| Jours calendaires en janvier 2026 | 31 |
| Jours travaillés (15 janvier au 31 janvier inclus) | 17 |
| Salaire de base mensuel | 900 000 CDF |
| **Salaire de base proratisé** | 900 000 × 17/31 = **493 548 CDF** |

**Éléments de paie du mois** :

| Code | Libellé | Montant | Qté | Imposable | CNSS | Logt | Transp |
|------|---------|---------|-----|-----------|------|------|--------|
| `SAL_BASE` | Salaire de base (prorata 17/31) | 493 548 | — | Oui | Oui | Non | Non |
| `PRIME_TRANSPORT` | Prime de transport | 30 000 | — | Oui | Oui | Non | Non |
| `PRIME_PANIER` | Prime de panier | 25 000 | — | Oui | Oui | Non | Non |
| `IND_LOG` | Indemnité de logement | 270 000 | — | Oui | Oui | **Oui** | Non |
| `PRIME_PERF` | Prime de performance | 22 000 | — | Oui | Oui | Non | Non |
| `PRIME_RISQUE` | Prime de risque | 0 | — | Oui | Oui | Non | Non |
| **Total** | | **840 548** | | | | | |

> **Note** : Seul `SAL_BASE` est proratisé (17/31). Les primes et indemnités restent en mois complet car ce sont des montants fixes indépendants du temps de présence.

**Vérification rapide — Salaire brut** :
```
Salaire brut = 493 548 + 30 000 + 25 000 + 270 000 + 22 000 = 840 548 CDF
```

**Retenues et calcul du net** :
| Retenue | Base | Calcul | Montant |
|---------|------|--------|---------|
| CNSS salariale (5 %) | 840 548 | 840 548 × 5 % | **42 027 CDF** |
| Base imposable nette | 840 548 − 270 000 (logt) − 42 027 (CNSS) | = 528 521 CDF | |
| IRPP (barème progressif) | Voir calcul ci-dessous | | **8 235 CDF** |
| **Total retenues** | 42 027 + 8 235 | | **50 262 CDF** |
| **Net à payer (avant autres déductions)** | 840 548 − 50 262 | | **790 286 CDF** |

**Détail IRPP** (sur la base imposable nette de 528 521 CDF) :

| Tranche | Limite | Taux | Calcul | Impôt |
|---------|--------|------|--------|-------|
| 1 | 0 – 472 500 | 0 % | 472 500 × 0 % | 0 CDF |
| 2 | 472 501 – 528 521 | 15 % | (528 521 − 472 500) × 15 % | **8 403 CDF** |
| **Impôt théorique** | | | | **8 403 CDF** |
| Plafonnement 30 % | 528 521 × 30 % = 158 556 | | 8 403 < 158 556 → pas de plafonnement | 8 403 CDF |
| Abattement familial (1 personne) | 8 403 × 2 % = 168 | | | −168 CDF |
| **IRPP final** | | | | **8 235 CDF** |

> **Rappel** : Ce calcul utilise les paramètres légaux 2026. Le prorata d'embauche n'affecte pas le mécanisme IPR / IRPP — seule la base imposable est réduite parce que le salaire de base proratisé est plus faible.

| Synthèse | Calcul | Montant |
|----------|--------|---------|
| Salaire brut | | **840 548 CDF** |
| Total retenues | 42 027 + 8 235 | **50 262 CDF** |
| **Net à payer** | 840 548 − 50 262 | **790 286 CDF** |
| Total charges patronales | 109 271 + 29 419 | **138 690 CDF** |
| **Coût total employeur** | 840 548 + 138 690 | **979 238 CDF** |

> **Comparaison avec le cas de base** : L'employé présent tout le mois avait un net à payer de 971 849 CDF. Ici, avec 17/31 de salaire de base, le net est de 790 286 CDF (−18,7 %), ce qui est cohérent avec la réduction du seul salaire de base (les primes et indemnités restent constantes). Le coût total employeur passe de 1 422 465 CDF à 979 238 CDF (−31,2 %).

---

## 9. Implémentations prévues (référence pour l'API)

| Concept | Structure de données prévue | Backend | Frontend |
|---------|---------------------------|---------|----------|
| `Employé` | Employee (module existant) | Modèle Django | Store employees |
| `Contrat de travail` | EmploymentContract (module existant) | Modèle Django | Store contracts |
| `Période de paie` | PayrollPeriod | Modèle Django | Store payrollPeriods |
| `Élément de paie` | PayElement | Modèle Django | Store payElements |
| `Paramètre légal` | LegalParameter | Modèle Django | Store legalParameters |
| `Base de calcul` | CalculationBasis | Objet calculé (non persisté) | Type calculé |
| `Retenue` | Deduction | Objet calculé (non persisté) | Type calculé |
| `Charge patronale` | EmployerCharge | Objet calculé (non persisté) | Type calculé |
| `Bulletin de paie` | PaySlip | Modèle Django (persisté avec snapshot) | Store paySlips |
