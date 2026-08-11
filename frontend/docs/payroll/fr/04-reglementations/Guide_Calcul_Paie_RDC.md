# **Rapport d'architecture et de spécifications fonctionnelles : Conception d'un moteur de paie évolutif pour la République Démocratique du Congo**

La gestion de la paie en République Démocratique du Congo (RDC) exige des organisations une adaptation constante face aux réformes du droit du travail, de la fiscalité et de la sécurité sociale1. Dans ce contexte instable, le développement d'un logiciel 
de paie ne peut se limiter à une approche monolithique où les règles de calcul seraient figées dans le code applicatif. Afin de prémunir les organisations contre les régressions réglementaires et de garantir l'évolutivité de l'outil, il est indispensable 
de concevoir un moteur de paie hautement modulaire, découplé et entièrement paramétrable.
L'analyse technique détaillée ci-dessous décrit l'architecture, la modélisation métier et le pipeline de calcul d'un moteur de paie conforme à la législation congolaise en vigueur, intégrant la transition fiscale majeure applicable au 1er janvier 20261.

## **Modélisation Domain-Driven Design et découplage structurel des responsabilités**

Pour concevoir un moteur capable d'absorber les évolutions de la législation congolaise sans modification de son code source, l'architecture logicielle s'appuie sur les principes du *Domain-Driven Design* (DDD) . Le domaine de la paie est décomposé 
en contextes délimités (*Bounded Contexts*) au sein desquels neuf entités fondamentales assument des responsabilités uniques et étanches :

> * **Employé** : Cette entité représente la dimension humaine et administrative du travailleur. Elle encapsule ses caractéristiques d'état civil, sa classification catégorielle (échelon et classe au sein de la grille salariale nationale) et ses variables sociales personnelles, notamment le nombre de personnes à charge, élément indispensable au calcul des abattements fiscaux2.  
> * **Contrat de travail** : Cet agrégat régit la relation contractuelle entre l'employé et l'employeur. Il stocke la date d'embauche (pour le calcul automatique de l'ancienneté), le salaire de base brut contractuel, les clauses spécifiques (avantages contractuels, primes garanties) et le régime de travail (temps plein, temps partiel, expatriation)4.  
> * **Période de paie** : Cette entité temporelle définit l'intervalle d'exécution des calculs (généralement le mois civil). Elle contrôle les variables conjoncturelles comme le nombre de jours ouvrés réels, le taux de change de référence pour les entreprises opérant en double devise (USD/CDF) et l'indice d'inflation applicable5.  
> * **Élément de paie** : Structure universelle modélisant toutes les rubriques financières du bulletin, qu'il s'agisse de gains (salaire de base, primes, heures supplémentaires, indemnités) ou de retenues (avances sur salaire, saisies-arrêts) .
 
> * **Paramètre légal** : Cette entité gère l'ensemble des constantes réglementaires fournies par l'État congolais (taux de cotisation, plafonds de calcul, barèmes progressifs, valeur journalière du SMIG). Chaque paramètre est historisé avec une date de début et une date de fin de validité pour permettre le recalcul conforme d'une paie passée.  
> * **Base de calcul** : Il s'agit d'accumulateurs de données construits de manière dynamique à partir des éléments de paie pour alimenter les calculs intermédiaires d'assiettes de cotisations et d'impôts.  
> * **Retenue** : Elle modélise les prélèvements obligatoires opérés sur la rémunération du travailleur pour le compte d'organismes tiers (cotisation salariale CNSS, impôt sur le revenu).  
> * **Charge patronale** : Cette entité quantifie les contributions financières dues par l'employeur au titre de la protection sociale (CNSS patronale) et de l'effort de formation ou d'emploi (INPP, ONEM).  
> * **Bulletin de paie** : Document de synthèse final qui fige l'ensemble des calculs, des bases de calcul, des retenues et des charges patronales associés à un employé pour une période donnée. Il garantit la traçabilité comptable et légale de chaque montant généré.

### **Le Strategy Pattern pour l'isolation des règles de calcul**

La flexibilité réglementaire du moteur repose sur l'implémentation du patron de conception *Strategy*. Chaque règle de calcul (cotisation CNSS, calcul de l'impôt sur le revenu, majoration des heures supplémentaires) est isolée dans une classe de stratégie spécifique implémentant une interface commune :

                        ┌───────────────────────────────┐  
                        │       <<interface>>           │  
                        │   ICalculationStrategy        │  
                        └───────────────┬───────────────┘  
                                        │  
             ┌──────────────────────────┼──────────────────────────┐  
             ▼                          ▼                          ▼  
┌──────────────────────────┐ ┌──────────────────────────┐ ┌──────────────────────────┐  
│ CNSSCalculationStrategy  │ │   IPRCalculationStrategy │ │   OTCalculationStrategy  │  
└──────────────────────────┘ └──────────────────────────┘ └──────────────────────────┘

Cette structure permet au moteur de paie de substituer dynamiquement, au moment de l'exécution, la formule de calcul requise en fonction de la période temporelle traitée ou de la législation applicable.  
L'illustration parfaite de cette flexibilité se manifeste dans la transition fiscale du 1er janvier 2026, marquée par l'unification de l'Impôt Professionnel sur les Rémunérations (IPR) au sein du nouvel Impôt sur le Revenu des Personnes Physiques (IRPP).
Le moteur peut basculer d'une stratégie IPRTraditionalCalculationStrategy à une stratégie IRPP2026CalculationStrategy sans modifier le noyau du système.

### **Les tables de décision pour les barèmes progressifs**

Pour éviter le codage en dur des grilles d'imposition progressives (qu'il s'agisse de l'ancien IPR à quatre tranches ou de l'IRPP 2026 à dix tranches), le moteur exploite des tables de décision stockées en base de données. L'application interroge ces structures 
tabulaires pour segmenter la matière imposable et appliquer le taux adéquat, assurant une conformité immédiate dès la publication d'un nouveau texte de loi fiscale.

## **Modélisation universelle des éléments de paie et construction dynamique des bases**

L'un des défis majeurs d'un logiciel de paie en RDC réside dans la gestion des rubriques de rémunération, dont la liste ne doit jamais être figée. Le moteur modélise chaque gain sous une structure universelle caractérisée par un montant, 
un mode de calcul (fixe, basé sur un taux horaire, ou indexé sur le nombre de jours) et un ensemble d'indicateurs d'assujettissement (*flags*) :

Structure de l'Élément de Paie :  
 ├── ID / Code unique (ex. PR_PERF, LOG_COMP)  
 ├── Libellé (ex. Prime de performance, Indemnité de logement)  
 ├── Montant brut nominal  
 ├── Mode de calcul (Constante, Formule, Taux horaire, Journalier)  
 ├── Indicateurs d'assujettissement (Flags) :  
 │    ├── est_imposable (IPR / IRPP)  
 │    ├── soumis_cnss (Sécurité Sociale)  
 │    ├── soumis_inpp (Formation Professionnelle)  
 │    ├── soumis_onem (Contribution à l'Emploi)  
 │    └── soumis_autres (Mutuelle, Prévoyance)

Grâce à ces indicateurs d'assujettissement, le moteur applique à chaque étape du pipeline une logique de filtrage et d'accumulation pour construire dynamiquement les bases de calcul. Cette méthode garantit l'indépendance de l'assiette de calcul de chaque retenue et charge patronale, conformément à la réglementation fiscale et sociale congolaise.

> * **Salaire Brut** : Somme de tous les éléments de gain (salaire de base, primes, indemnités de logement et transport, gratifications, heures supplémentaires).
> * **Base CNSS** : Somme des gains dont l'attribut soumis_cnss est vrai. Elle comprend l'ensemble des rémunérations brutes perçues en contrepartie du travail, y compris l'indemnité de logement (pratique sociale établie), à l'exclusion des indemnités justifiées représentatives de frais professionnels (comme le transport réel).  
> * **Base Imposable IPR / IRPP** : ![][image1] des gains dont l'attribut est_imposable est vrai, déduction faite de la cotisation salariale CNSS (5 %) et des fractions exonérées de logement et de transport5.  
> * **Base INPP** : ![][image1] des gains dont l'attribut soumis_inpp est vrai, équivalant généralement à la rémunération brute globale telle que définie par les règlements de l'INPP3.  
> * **Base ONEM** : ![][image1] des gains dont l'attribut soumis_onem est vrai, basée sur la rémunération mensuelle brute des salariés nationaux et expatriés10.

## **Le pipeline de calcul en huit étapes obligatoires**

Le moteur de paie fonctionne comme un pipeline à sens unique, exécutant les étapes de calcul dans un ordre immuable. Cette linéarité empêche les dépendances circulaires et assure la reproductibilité de chaque calcul.

┌────────────────────────────────────────────────────────┐  
│1. Vérification et validation de l'intégrité des données│  
└───────────────────────────┬────────────────────────────┘  
                            ▼  
┌────────────────────────────────────────────────────────┐  
│2. Calcul individuel des gains et majorations d'heures  │  
└───────────────────────────┬────────────────────────────┘  
                            ▼  
┌────────────────────────────────────────────────────────┐  
│ 3. Détermination et validation du Salaire Brut         │  
└───────────────────────────┬────────────────────────────┘  
                            ▼  
┌────────────────────────────────────────────────────────┐  
│ 4. Construction des bases intermédiaires de calcul     │  
└───────────────────────────┬────────────────────────────┘  
                            ▼  
┌────────────────────────────────────────────────────────┐  
│ 5. Calcul des retenues salariales (CNSS, IPR / IRPP)   │  
└───────────────────────────┬────────────────────────────┘  
                            ▼  
┌────────────────────────────────────────────────────────┐  
│ 6. Calcul des charges patronales (CNSS, INPP, ONEM)    │  
└───────────────────────────┬────────────────────────────┘  
                            ▼  
┌────────────────────────────────────────────────────────┐  
│ 7. Calcul du Salaire Net et du Net à Payer             │  
└───────────────────────────┬────────────────────────────┘  
                            ▼  
┌────────────────────────────────────────────────────────┐  
│ 8. Génération du bulletin de paie et archivage d'audit │  
└────────────────────────────────────────────────────────┘

Chaque étape du pipeline opère de manière indépendante, ignorant les traitements de l'étape précédente ou suivante. Elle reçoit un état du bulletin de paie, applique sa logique de domaine et passe le bulletin enrichi à l'étape suivante.

## **Paramètres légaux et évolutions du cadre réglementaire congolais (2026)**

L'évolutivité du moteur exige que l'ensemble des constantes légales soient stockées sous forme de paramètres temporels paramétrables.

### **SMIG et tension salariale (Décret n° 25/22)**

Le décret n° 25/22 du 30 mai 2025 fixe le montant cible du Salaire Minimum Interprofessionnel Garanti (SMIG) journalier à **21 500 CDF** pour un manœuvre ordinaire à compter du 1er janvier 20262. Le décret maintient le principe légal 
d'une tension salariale de 1 à 10 entre le manœuvre ordinaire et le cadre de collaboration au dernier échelon (classe 7, échelon 4), revalorisant mécaniquement l'ensemble de la grille salariale de l'entreprise2. La valeur mensuelle minimale obligatoire d'une catégorie professionnelle s'obtient 
en multipliant le taux journalier légal par 262.

### **Heures supplémentaires et majorations**

Conformément au Code du travail, les heures accomplies au-delà de la durée légale du travail font l'objet d'un calcul de majoration horaire progressive, paramétré par stratégie13 :

> * Les deux premières heures de dépassement hebdomadaire : majoration de **30 %**13.  
> * Les heures suivantes : majoration de **60 %**13.  
> * Les heures accomplies les jours fériés ou de repos hebdomadaire : taux de majoration conventionnels plus élevés (généralement 100 %)13.

> * **Qu'est-ce qu'une majoration ?** *Majorer* signifie multiplier le taux horaire par un coefficient. C'est la **compensation légale** pour un travail effectué en dehors des heures normales.
>   * **130 % (×1.30)** : pour 1 heure de HS, l'employé est payé **1.3 × son taux horaire** pour cette heure. La majoration est de **+30 %**.
>   * **200 % (×2.00)** : pour 1 heure de travail le dimanche, il est payé **2 × son taux** — majoration de **+100 %** (le salaire est doublé).
>
> **Pourquoi ?** Le Code du travail RDC (Loi n° 15/2002) impose ces majorations pour :
> 1. **Compenser la pénibilité** (nuit, dimanche, férié) ;
> 2. **Dissuader l'employeur d'abuser des HS** (ça coûte plus cher) ;
> 3. **Indemniser le salarié** de son temps de repos perdu.

### **Cotisations sociales (CNSS)**

La Caisse Nationale de Sécurité Sociale (CNSS) structure ses cotisations obligatoires sur une assiette brute globale sans aucun plafond en RDC8 :

> * **Part salariale** : Retenue de **5 %** assise sur le brut CNSS, affectée à la branche des pensions8.  
> * **Part patronale** : Contribution globale de **13 %**8 répartie comme suit :  
  * Branche des pensions : **5 %**14.  
  * Branche des risques professionnels : **1,5 %**14.  
  * Branche des prestations aux familles : **6,5 %**14.

### **Évolutions fiscales : Barèmes IPR traditionnel vs. IRPP 2026**

Le moteur doit être capable d'exécuter des rétro-calculs de paie sur d'anciennes périodes en utilisant l'ancien barème progressif de l'IPR (établi à 4 tranches d'imposition) ou le nouveau barème de l'IRPP unifié à 10 tranches applicable au 1er janvier 20261.

#### **Barème IPR traditionnel (Ordonnance-Loi n° 13/008)**

L'ancien système calculait l'IPR mensuel sur la base d'un barème à quatre tranches, avec un taux allant de 3 % à 40 %, caractérisé par l'absence d'une tranche d'exonération totale substantielle5 :

| Tranche | Borne Inférieure (CDF) | Borne Supérieure (CDF) | Largeur de Tranche (CDF) | Taux de la Tranche |
| :---- | :---- | :---- | :---- | :---- |
| **1** | 0 | 162 000 | 162 000 | 3 % |
| **2** | 162 001 | 1 800 000 | 1 638 000 | 15 % |
| **3** | 1 800 001 | 3 600 000 | 1 800 000 | 30 % |
| **4** | 3 600 001 et plus | – | – | 40 % |

#### **Barème IRPP 2026 (Loi n° 23/053)**

La réforme introduit un barème plus progressif composé de 10 tranches d'imposition, intégrant une première tranche totalement exonérée (taux de 0 %)6 :

| Tranche | Borne Inférieure (CDF) | Borne Supérieure (CDF) | Largeur de Tranche (CDF) | Taux de la Tranche |
| :---- | :---- | :---- | :---- | :---- |
| **1** | 0 | 43 680 | 43 680 | 0 % |
| **2** | 43 681 | 119 000 | 75 320 | 15 % |
| **3** | 119 001 | 225 000 | 106 000 | 20 % |
| **4** | 225 001 | 385 000 | 160 000 | 22,5 % |
| **5** | 385 001 | 605 000 | 220 000 | 25 % |
| **6** | 605 001 | 855 000 | 250 000 | 30 % |
| **7** | 855 001 | 1 159 000 | 304 000 | 32,5 % |
| **8** | 1 159 001 | 1 402 000 | 243 000 | 35 % |
| **9** | 1 402 001 | 1 913 000 | 511 000 | 37,5 % |
| **10** | 1 913 001 et plus | – | – | 40 % |

#### **Règles d'écrêtement et d'abattements**

Quel que soit le barème utilisé, l'impôt brut calculé est soumis à deux mécanismes de personnalisation fiscale :

> * **Plafonnement des 30 %** : Le montant total théorique de l'impôt brut ne peut jamais excéder 30 % du salaire net imposable (base de l'impôt)5. Si le calcul du barème dépasse ce plafond de 30 %, il est automatiquement réduit pour égaler exactement ![][image2]17.  
> * **Réduction pour charges de famille** : L'impôt après plafonnement fait l'objet d'une réduction de **2 % par personne à charge** (épouse, enfants légitimes ou adoptifs à charge), dans la limite stricte de 9 personnes (soit un abattement maximal de 18 %)5.

### **Cotisations patronales : INPP et ONEM**

L'employeur supporte deux taxes parafiscales calculées sur la masse salariale brute des rémunérations versées, sans déduction possible du salaire net de l'employé \[cite: user query, 44\] :

> * **INPP** : Institut National de Préparation Professionnelle5. Le taux dépend de la taille et de la nature de la structure pour l'exercice 20263 :  
  * Secteur public : **4 %**3.  
  * Secteur privé de 1 à 50 salariés : **3,5 %**3.  
  * Secteur privé de 51 à 300 salariés : **3 %**3.  
  * Secteur privé de plus de 300 salariés : **2 %**3.  
> * **ONEM** : Office National de l'Emploi5. À la suite de la réforme validée au Conseil National du Travail, la contribution patronale mensuelle est de **0,5 %** de la rémunération mensuelle globale brute de tous les salariés11.

### **Règles d'exonération des indemnités de logement et de transport**

Pour encourager l'accès au logement et compenser l'absence de transports publics fiables dans les centres urbains comme Kinshasa ou Lubumbashi, la loi congolaise accorde des exonérations d'impôt et de sécurité sociale sous des conditions strictes de seuils22 :

> * **Indemnité de logement** : Elle est exonérée à hauteur d'un plafond maximal de **30 % du traitement brut imposable** (défini comme l'ensemble des gains et primes du mois, à l'exception des avantages en nature et des allocations à caractère purement social)23. Tout centime d'indemnité versé au-delà de cette limite de 30 % est réintégré à l'assiette imposable et soumise à cotisation CNSS23.  
> * **Indemnité de transport** : Elle constitue un remboursement de frais professionnels et est totalement exonérée à condition de ne pas présenter un caractère exagéré9. La DGI apprécie l'exagération sur la base de la valeur de **4 courses de taxi par jour pour les cadres** et de **4 courses de bus par jour pour le personnel d'exécution**9. L'excédent au-delà de ces montants réels du marché local est réintégré à la base imposable9.

### **Règles d'arrondi**

Le moteur doit pouvoir configurer des règles d'arrondi applicables aux calculs intermédiaires et finaux (ex. arrondi arithmétique à l'unité de franc congolais la plus proche ou arrondi supérieur), stockées sous forme de clés de paramétrage légal.

## **Cas pratique d'exécution complète et validation numérique (Janvier 2026\)**

Pour démontrer la conformité et la rigueur algorithmique du moteur de paie, ce cas pratique compare l'exécution du calcul d'un bulletin selon deux configurations réglementaires distinctes (le système IPR traditionnel et le nouveau système IRPP 2026), appliquées au même travailleur pour le mois de janvier 20261.

### **Variables d'entrée du domaine**

> * **Travailleur** : Cadre de collaboration (Catégorie 7, Échelon 1).  
> * **Salaire de base journalier (obéissant au SMIG 2026\)** : 139 965,00 CDF2.  
> * **Régime horaire mensuel** : 26 jours de prestation accomplis2.  
> * **Salaire de base brut mensuel contractuel** : ![][image3]2.  
> * **Prime de performance mensuelle** : 500 000,00 CDF.  
> * **Indemnité de logement allouée** : 900 000,00 CDF.  
> * **Indemnité de transport allouée** : 260 000,00 CDF (Kinshasa, jugée raisonnable et validée sous la limite des 4 courses de taxi/jour par la DGI)9.  
> * **Personnes à charge déclarées** : 5 personnes (épouse et 4 enfants légitimes)25.  
> * **Profil Employeur** : PME privée comptant 45 employés (taux INPP de 3,5 % applicable)3.

### **Exécution du pipeline de calcul**

#### **Étape 1 : Vérification des données (Validation)**

Le moteur interroge le référentiel des paramètres légaux à la date du 1er janvier 2026 :

> * Le SMIG de la catégorie professionnelle 7-1 est de 139 965,00 CDF par jour2.  
> * Le salaire de base contractuel journalier déclaré (139 965,00 CDF) respecte exactement le SMIG de référence2. La règle de conformité minimale est validée.  
> * Le nombre de personnes à charge (5) est valide (![][image4] maximum)5.

#### **Étape 2 : Calcul des gains individuels**

Les rubriques du bulletin sont calculées individuellement :


#### **Étape 3 : Calcul du salaire brut**

![][image9]  
![][image10]

#### **Étape 4 : Construction des bases de calcul intermédiaires**

##### **Évaluation de l'exemption logement**

Le traitement brut imposable servant de base de calcul pour l'exonération logement est composé uniquement du salaire de base et de la prime de performance23 :  
![][image11]  
![][image12]  
L'indemnité de logement effectivement allouée de ![][image13] est inférieure au plafond d'exonération de ![][image14]23. Elle est donc **entièrement exonérée**23. Le montant réintégré au brut imposable est de ![][image15]25.

##### **Évaluation de l'exemption transport**

L'indemnité de transport allouée de ![][image16] respecte les grilles réelles et n'excède pas les quotités journalières raisonnables pour un cadre9. Elle est donc **entièrement exonérée**9. Le montant réintégré au brut imposable est de ![][image15]25.

##### **Détermination de la base de cotisation CNSS**

La base de calcul CNSS est construite à partir des gains soumis :  
![][image17]  
![][image18]  
Aucun plafond d'assiette ne s'appliquant aux cotisations CNSS en RDC, la base CNSS finale retenue est de **4 139 090,00 CDF**8.

##### **Détermination des bases INPP et ONEM**

Conformément à la réglementation sur l'assiette brute, les bases de calcul de l'INPP et de l'ONEM correspondent à la rémunération brute globale du travailleur3 :  
![][image19]

#### **Étape 5 : Calcul des retenues du travailleur (CNSS et Impôt)**

##### **1\. Cotisation Salariale CNSS (5 %)**

![][image20]  
![][image21]

##### **2\. Base imposable de l'impôt sur le revenu (IPR ou IRPP)**

La base nette d'imposition est calculée de manière identique pour les deux stratégies comparées5 :  
![][image22]  
![][image23]

##### **3\. Calcul comparatif des stratégies fiscales (IPR traditionnel vs. IRPP 2026\)**

Le moteur évalue les retenues d'impôt selon les deux stratégies réglementaires :

###### **Stratégie A : IPR traditionnel (Ordonnance-Loi n° 13/008)**

Le calcul s'exécute selon les quatre tranches progressives de l'ancien barème sur la base de ![][image24]5 :

> * *Tranche 1 (3 % de 0 à 162 000 CDF)* : ![][image25]5.  
> * *Tranche 2 (15 % de 162 001 à 1 800 000 CDF)* : ![][image26]17.  
> * *Tranche 3 (30 % de 1 800 001 à 3 600 000 CDF)* : ![][image27]17.  
> * *Tranche 4 (40 % au-delà de 3 600 000 CDF)* : ![][image28]17.

![][image29]  
*Validation du Plafond Fiscal des 30 %* :  
![][image30]  
L'impôt brut théorique (![][image31]) étant inférieur au plafond d'écrêtement (![][image32]), le montant retenu reste inchangé17.  
*Application des abattements familiaux* :  
L'employé justifie de 5 personnes à charge, soit un taux de réduction de 10 % (![][image33]) appliqué directement sur l'impôt5.  
![][image34]  
![][image35]

###### **Stratégie B : IRPP 2026 (Loi n° 23/053)**

Le moteur traite la même base imposable de ![][image24] en appliquant la nouvelle table de décision fiscale à dix tranches6 :

> * *Tranche 1 (0 %)* : ![][image36]  
> * *Tranche 2 (15 %)* : ![][image37]  
> * *Tranche 3 (20 %)* : ![][image38]  
> * *Tranche 4 (22,5 %)* : ![][image39]  
> * *Tranche 5 (25 %)* : ![][image40]  
> * *Tranche 6 (30 %)* : ![][image41]  
> * *Tranche 7 (32,5 %)* : ![][image42]  
> * *Tranche 8 (35 %)* : ![][image43]  
> * *Tranche 9 (37,5 %)* : ![][image44]  
> * *Tranche 10 (40 % au-delà de 1 913 000 CDF)* : ![][image45]

![][image46]  
*Validation du Plafond Fiscal des 30 %* :  
![][image30]  
Dans cette configuration fiscale réformée, l'impôt théorique du barème progressif (![][image47]) dépasse largement la limite des 30 %17. Le moteur de paie applique donc l'**écrêtement obligatoire** pour ramener l'impôt brut au montant maximal autorisé17 :  
![][image48]  
*Application des abattements familiaux* :  
L'employé bénéficie du même taux d'abattement de 10 % appliqué à l'impôt plafonné5 :  
![][image49]  
![][image50]

#### **Étape 6 : Calcul des charges patronales (Non déductibles du salaire)**

L'employeur supporte les cotisations et contributions suivantes, calculées de manière analytique à partir des bases intermédiaires définies à l'étape 4 :

> * **CNSS Patronale (13 % de la Base CNSS)**8 :  
>   ![][image51]  
  * *Branche Retraite/Pensions (5 %)* : ![][image52]  
    
  * *Branche Risques Professionnels (1,5 %)*
      
  * *Branche Prestations Familiales (6,5 %)*  
  
> * **Contribution INPP (3,5 % de la Base INPP - Effectif de 45 salariés)** :  
> * **Contribution ONEM (0,5 % de la Base ONEM)** 

#### **Étape 7 : Calcul du salaire net**

Le salaire net final représente la somme effectivement perçue par le salarié après déduction des prélèvements salariaux :

> * **Sous la stratégie IPR traditionnelle (Antérieure à 2026\)** 
> * **Sous la stratégie IRPP 2026 (Applicable au 1er janvier 2026\)**

#### **Étape 8 : Génération du bulletin de paie et archivage d'audit**

Cette étape compile les résultats calculés pour produire la structure finale du bulletin de paie. L'ensemble des calculs intermédiaires, 
des bases retenues et des versions de paramètres légaux utilisés sont conservés en base de données pour garantir une traçabilité totale.

### **Bulletin de paie comparatif final**

Le tableau suivant présente le bulletin de paie consolidé généré par le moteur, mettant en perspective l'impact direct de la réforme fiscale de 2026 sur la rémunération du salarié et les obligations de l'employeur.

| Rubrique de Paie | Base de Calcul (CDF) | Part Salariale (CDF) - IPR Traditionnel | Part Salariale (CDF) - IRPP 2026 | Part Patronale (CDF) - Système Unique |
| :---- | :---- | :---- | :---- | :---- |
| **Salaire de Base (26 j)** | Contractuel | 3 639 090,00 | 3 639 090,00 | – |
| **Prime de performance** | Variable | 500 000,00 | 500 000,00 | – |
| **Indemnité Logement** | Forfaitaire | 900 000,00 | 900 000,00 | – |
| **Indemnité Transport** | Forfaitaire | 260 000,00 | 260 000,00 | – |
| **SALAIRE BRUT GLOBAL** | **Accumulateur** | **5 299 090,00** | **5 299 090,00** | – |
| **Pensions CNSS Salarié** | 4 139 090,00 | 206 954,50 | 206 954,50 | – |
| **Pensions CNSS Patronal** | 4 139 090,00 | – | – | 206 954,50 |
| **CNSS Accidents du Travail** | 4 139 090,00 | – | – | 62 086,35 |
| **CNSS Prestations Famille** | 4 139 090,00 | – | – | 269 040,85 |
| **Impôt (IPR vs IRPP)** | 3 932 135,50 | 831 072,78 | 1 061 676,58 | – |
| **Taxe INPP (PME 1-50)** | 5 299 090,00 | – | – | 185 468,15 |
| **Taxe ONEM (0.5 %)** | 5 299 090,00 | – | – | 26 495,45 |
| **CUMUL RETENUES / TAXES** | **Accumulateur** | **1 038 027,28** | **1 268 631,08** | **750 045,30** |
| **SALAIRE NET A PAYER** | **Calculé** | **4 261 062,72** | **4 030 458,92** | – |
| **COÛT TOTAL EMPLOYEUR** | **Calculé** | **6 049 135,30** | **6 049 135,30** | **6 049 135,30** |

L'analyse comparative démontre que l'entrée en vigueur de l'IRPP 2026, malgré la mise en place d'une tranche d'imposition à 0 %, conduit à une augmentation de la pression fiscale pour les hauts salaires de la grille en raison de la progressivité rapide des 
taux intermédiaires. Pour un même salaire brut de 5 299 090,00 CDF, l'impôt brut théorique de 1 268 631,08 CDF déclenche l'écrêtement obligatoire au plafond constitutionnel des 30 %, augmentant l'impôt de 230 558,30 CDF par rapport au système antérieur. 
Ce phénomène s'explique par l'augmentation de la taxation des tranches supérieures, tempérée uniquement par les abattements familiaux.

## **Principes d'implémentation et recommandations de développement**

La réussite de la construction du moteur de paie dépend du respect strict des recommandations d'ingénierie et d'implémentation suivantes :

### **Priorité absolue au moteur de calcul**

Le développement du moteur de calcul doit être entièrement achevé, testé et validé de manière autonome avant d'entamer le moindre développement d'interface utilisateur graphique. 
Les algorithmes de paie doivent se comporter comme une bibliothèque logicielle (API ou package métier) indépendante, acceptant des structures de données standardisées en entrée 
(ex. JSON ou structures d'objets) et retournant des résultats formalisés en sortie.

### **Modularité et pureté fonctionnelle**

Chaque règle ou formule réglementaire doit être écrite sous la forme d'une fonction pure. Une fonction pure ne possède aucun effet de bord, ne lit aucune variable globale externe et retourne un résultat déterministe identique pour des paramètres d'entrée identiques.  
L'accès aux bases de données pour récupérer les paramètres légaux (taux, SMIG, barèmes d'impôt) doit être délégué à des modules de service d'infrastructure, injectés dans les processeurs du pipeline au démarrage de l'exécution.

### **Stratégie de tests unitaires rigoureuse**

L'assurance qualité du moteur repose sur la mise en œuvre d'une suite exhaustive de tests unitaires automatisés pour chaque stratégie de calcul. Les cas de tests doivent couvrir de manière systématique :

> * Les comportements aux limites (*edge cases*) des tranches d'imposition de l'IRPP (valeurs de salaire brut exactement égales aux bornes de chaque tranche).  
> * La robustesse de la formule de validation de la règle d'écrêtement constitutionnel des 30 %17.  
> * Les calculs de proratisation du salaire de base pour des mois d'embauche ou de départ en cours de période de paie26.  
> * La réintégration et le calcul des charges sociales CNSS sur les dépassements de plafonds de l'indemnité de logement8.

### **Traçabilité et historique d'audit**

Le moteur de paie doit conserver une trace historique détaillée de tous les calculs exécutés. Pour chaque bulletin généré, le système doit stocker non seulement les montants finaux, mais également un instantané (*snapshot*) des formules, des règles d'arrondi 
et des valeurs exactes des paramètres légaux en vigueur au cours de la période.  
Cette traçabilité absolue est essentielle pour répondre à deux impératifs majeurs :

> 1. **Explication pédagogique** : Permettre au gestionnaire de paie d'expliquer à l'employé, de manière claire et détaillée, l'origine de chaque montant figurant sur son bulletin (par exemple, détailler le calcul étape par étape d'une majoration d'heure supplémentaire ou d'un abattement familial).  
> 2. **Audit réglementaire et conformité** : Fournir aux inspecteurs du travail, de la CNSS ou de la DGI les éléments justificatifs prouvant le calcul exact des bases de cotisations et le respect rigoureux des textes de loi, évitant ainsi des redressements ou des sanctions pour défaut ou déclaration incorrecte.
