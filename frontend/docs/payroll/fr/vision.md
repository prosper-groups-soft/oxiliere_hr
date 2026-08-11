# Vision : Moteur de paie RDC

> **Système de calcul automatisé de la paie conforme à la législation de la République Démocratique du Congo**

---

## Pourquoi ce système ?

### Contexte

La gestion de la paie en République Démocratique du Congo impose aux organisations une adaptation permanente face aux réformes du droit du travail, de la fiscalité et de la sécurité sociale. Depuis 2025, plusieurs changements majeurs sont entrés en vigueur : la revalorisation du SMIG (Décret n° 25/22), la modification des taux INPP, et surtout la transition fiscale de l'IPR traditionnel vers le nouvel IRPP à dix tranches au 1er janvier 2026.

### Problèmes identifiés

- **Obsolescence rapide** : Les logiciels de paie monolithiques codent les règles de calcul dans leur source, nécessitant une mise à jour à chaque réforme.
- **Risque de non-conformité** : L'absence d'historisation des paramètres légaux empêche le recalcul conforme d'une paie passée lors d'un contrôle.
- **Opacité des calculs** : Les employés et les gestionnaires ne peuvent pas retracer l'origine détaillée de chaque montant sur un bulletin.
- **Rigidité technique** : L'ajout d'une nouvelle rubrique de paie ou d'une nouvelle cotisation nécessite une modification du code applicatif.

### Opportunité

Construire un moteur de paie dont l'architecture garantit que **les règles de calcul sont interchangeables sans modifier le code source**, en séparant clairement les données, les règles métier et les paramètres légaux.

---

## Objectifs

### Objectif principal

**Calculer automatiquement et conformément la paie d'un travailleur en RDC** en produisant un bulletin de paie légal, traçable et reproductible, pour n'importe quelle période depuis l'entrée en vigueur des paramètres légaux historisés.

### Objectifs secondaires

1. **Pérennité réglementaire** : Permettre l'adaptation du moteur à toute réforme future (fiscale, sociale, conventionnelle) sans modifier une ligne de code de calcul.
2. **Traçabilité totale** : Conserver un snapshot de chaque paramètre légal, formule et règle d'arrondi utilisée pour chaque bulletin généré.
3. **Explicabilité** : Permettre au gestionnaire de paie d'expliquer à l'employé l'origine de chaque montant sur son bulletin.
4. **Multi-régime** : Supporter le calcul selon différents régimes fiscaux (IPR traditionnel, IRPP 2026) et sociaux (CNSS, INPP, ONEM) pour une même période comparative.
5. **Indépendance technologique** : Le moteur de calcul doit fonctionner comme une bibliothèque logicielle autonome, indépendante de l'interface utilisateur.

---

## Principes directeurs

1. **Séparation des préoccupations** — Les données (employés, contrats, éléments de paie), les règles de calcul (CNSS, IRPP, heures supplémentaires) et les paramètres légaux (SMIG, taux, plafonds, barèmes) sont trois couches distinctes et indépendantes.
2. **Aucune valeur légale dans le code** — Tout taux, montant, plafond ou barème est stocké en base de données avec une date de début et une date de fin de validité.
3. **Fonctions pures** — Chaque règle de calcul est une fonction déterministe sans effet de bord : mêmes entrées → mêmes sorties.
4. **Pipeline immuable** — Les huit étapes de calcul s'exécutent toujours dans le même ordre, sans dépendance circulaire.
5. **Conception pilotée par le domaine (DDD)** — Le modèle métier reflète les concepts du droit du travail congolais, pas les structures de programmation.
6. **Auditabilité** — Chaque bulletin est un document figé qui conserve l'empreinte exacte des paramètres et des règles qui l'ont généré.

---

## Parties prenantes

| Rôle | Attente principale |
|------|--------------------|
| **Gestionnaire de paie** | Calculer rapidement et correctement la paie mensuelle, pouvoir expliquer chaque montant aux employés |
| **Directeur financier** | Connaître le coût total employeur par période, anticiper l'impact des réformes sur la masse salariale |
| **Employé** | Recevoir un bulletin de paie clair, compréhensible et conforme à la loi |
| **Inspecteur du travail / CNSS / DGI** | Vérifier la conformité des calculs et des bases de cotisation déclarées |
| **Développeur** | Maintenir et faire évoluer le moteur sans risquer de régressions sur les calculs existants |
| **Intégrateur** | Connecter le moteur à d'autres systèmes (ERP, comptabilité, déclarations sociales) via une API stable |

---

## Périmètre

### Dans le périmètre

- Calcul du salaire brut (salaire de base, primes, heures supplémentaires, indemnités logement et transport, gratifications, avantages en nature)
- Calcul des retenues salariales : cotisation CNSS (5 %), impôt sur le revenu (IPR ou IRPP selon la période)
- Application des barèmes progressifs d'imposition (IPR 4 tranches, IRPP 10 tranches)
- Application des mécanismes de plafonnement (30 % du net imposable) et des abattements familiaux (2 % par personne à charge, max 18 %)
- Calcul des charges patronales : CNSS (13 %), INPP (taux variable selon effectif), ONEM (0,5 %)
- Gestion des exonérations réglementaires : indemnité de logement (30 % du brut imposable), indemnité de transport (frais professionnels)
- Historisation des paramètres légaux avec dates de validité (permettant le recalcul rétroactif)
- Génération du bulletin de paie avec snapshot d'audit
- Calcul comparatif entre régimes fiscaux (simulation IPR vs IRPP)
- Proratisation pour les entrées et sorties en cours de période

### Hors périmètre

- Déclarations sociales et fiscales (DSF) — Le moteur produit les bases, pas les déclarations
- Virement bancaire et paiement — Le moteur produit le net à payer, pas l'ordre de virement
- Gestion des absences et congés — Module séparé (attend le module `leaves`)
- Gestion des contrats et des employés — Modules séparés (`employees`, `contracts`) dont les données sont consommées en entrée
- Gestion de la paie en devise étrangère autre que le mécanisme de taux de change comme donnée d'entrée
- Paie multi-société (un moteur par entité juridique)
- Calcul de la paie pour les stagiaires, indépendants ou travailleurs non-salariés
- Édition papier des bulletins (format PDF) — c'est une fonction d'export séparée

---

## Roadmap

| Version | Fonctionnalités | Critère de succès |
|---------|-----------------|-------------------|
| **V0.1 — Noyau de calcul** | Pipeline 8 étapes, calcul CNSS, calcul IPR (4 tranches), paramètres légaux historisés, cas pratique janvier 2026 validé | Tous les tests unitaires passent sur le cas de référence du Guide |
| **V0.2 — IRPP 2026** | Barème IRPP 10 tranches, plafonnement 30 %, abattements familiaux, exonérations logement/transport, taux de change en entrée | Calculs validés pour les deux régimes fiscaux |
| **V0.3 — Charges patronales** | CNSS patronale (3 branches), INPP (4 taux par effectif), ONEM, coût total employeur | Tableau de bord employeur fonctionnel |
| **V0.4 — Cas particuliers** | Entrées/sorties en cours de période, heures supplémentaires, primes exceptionnelles, saisie-arrêt | Validation des edge cases du Guide |
| **V0.5 — Simulation** | Calcul comparatif IPR vs IRPP, calcul rétroactif sur période historique, scénarios de simulation | Interface de simulation fonctionnelle |
| **V1.0 — Production** | Intégration frontend, export PDF du bulletin, historique d'audit complet, API stable | Déploiement sur jeu de données réel |

> **Note** : Le développement commence par le moteur de calcul (V0.1 à V0.4) avant toute interface graphique. L'interface utilisateur n'est intégrée qu'à partir de V0.5.

---

## Glossaire

| Terme | Définition |
|-------|------------|
| **SMIG** | Salaire Minimum Interprofessionnel Garanti — valeur journalière minimale légale |
| **CNSS** | Caisse Nationale de Sécurité Sociale — organisme de protection sociale |
| **IPR** | Impôt Professionnel sur les Rémunérations — ancien impôt sur le revenu (avant 2026) |
| **IRPP** | Impôt sur le Revenu des Personnes Physiques — nouvel impôt unifié (2026) |
| **INPP** | Institut National de Préparation Professionnelle — contribution formation |
| **ONEM** | Office National de l'Emploi — contribution emploi |
| **Salaire brut** | Somme de tous les gains avant déduction des retenues |
| **Base de calcul** | Assiette intermédiaire construite dynamiquement pour chaque cotisation |
| **Net à payer** | Salaire brut moins toutes les retenues salariales |
| **Coût total employeur** | Salaire brut plus toutes les charges patronales |
| **Pipeline** | Séquence ordonnée et immuable des étapes de calcul |
| **Snapshot d'audit** | Instantané des paramètres, formules et règles ayant servi à un calcul |


























Ces questions sont fondamentales et révèlent des présupposés qui n'étaient pas explicitement tranchés dans nos documents. Laissez-moi vérifier rapidement le Guide.

Searched for "salaire de base|net à payer|brut|négocié"
Searched for "salaire|brut|net|base|négoci"
Viewed Guide_Calcul_Paie_RDC.md:1-100
Viewed Guide_Calcul_Paie_RDC.md:100-250
Viewed metamodel.md:1-50
Viewed metamodel.md:169-220
Viewed catalogue.md:1-60
Viewed metamodel.md:50-168
Viewed semantics.md:1-100
Viewed metamodel.md:265-320
Viewed semantics.md:100-458
Viewed metamodel.md:530-650
Viewed catalogue.md:260-342

Bonjour Kiban. J'ai lu toute la documentation existante en détail. Je peux maintenant te répondre sur tes 4 questions de manière structurée.

---

## Réponse à tes questions

### 1. Embaucher un employé n'importe quel jour — ✅ Oui

Oui, absolument. Un employé peut être embauché n'importe quel jour du mois. La conséquence est que **son salaire doit être proratisé** pour la première période de paie. C'est une règle que nous allons formaliser.

**Ma proposition — Règle de prorata** :
- Le prorata s'applique **aux jours calendaires** (pas ouvrés)
- Formule : `salaire_proratise = salaire_mensuel × (nombre_jours_travaillés / nombre_jours_calendaires_de_la_période)`
- Pour l'embauche : `nombre_jours_travaillés = (date_fin_période - date_embauche + 1)`
- Pour la sortie : `nombre_jours_travaillés = (date_sortie - date_debut_période + 1)`
- Cette proratisation s'applique au **salaire de base** uniquement (les primes sont généralement calculées en mois complet sauf stipulation contraire)

> **Ce choix mérite ta validation** : préfères-tu un prorata **calendaire** (plus simple) ou **ouvré** (plus précis) ? Ma recommandation est **calendaire** car c'est le standard en RDC.

---

### 2. Tous les employés payés au même moment — ✅ Oui

Dans notre métamodèle, **oui, tous les employés actifs sur une période sont payés dans le même run de paie**. C'est le principe de **l'unité de période** que nous avons évoqué et que tu as validé.

Cela signifie :
- Une période = un seul lancement du pipeline pour tous les employés actifs
- Pas de "paie exceptionnelle" individuelle en dehors du run
- Le run peut inclure des employés avec des durées de travail différentes dans le mois (embauche, sortie)

Ce principe est **déjà implicite** dans la conception actuelle (le pipeline traite "un ensemble d'employés"), mais nous allons le rendre **explicite** dans la documentation.

---

### 3. Salaire de base, brut et net en RDC — Analyse détaillée

Ta description de la pratique RDC est très claire. Voici comment je propose de formaliser ces concepts dans notre métamodèle :

#### Salaire négocié en USD = Net à payer

C'est **le concept le plus important**. En RDC :
- Le recruteur et l'employé négocient un **salaire en USD**
- Ce montant est **ce que l'employé reçoit réellement** à la fin du mois
- L'employé **n'a pas connaissance** des charges, impôts et cotisations

**Cela implique un modèle de conception très spécifique** : le salaire négocié n'est PAS le salaire de base (brut), c'est le **NET À PAYER** (ou le **NET AVANT AVANCES/SAISIES**).

#### Les 4 niveaux de salaire

| Concept | Définition | Dans le contrat | Connu de l'employé |
|---------|-----------|-----------------|-------------------|
| **Salaire négocié (USD)** | Montant convenu à l'embauche, exprimé en USD | Oui | Oui — c'est SON salaire |
| **Salaire net à payer (CDF)** | Salaire négocié converti en CDF au taux de la période | Non | Oui — c'est ce qu'il reçoit |
| **Salaire brut (CDF)** | Le net + toutes les retenues (CNSS 5% + IRPP + ...) | Non | Non — l'employé ne le voit pas |
| **Salaire de base contractuel (CDF)** | La partie fixe du brut, avant primes | Oui, mais en USD converti | Non — c'est administratif |

#### Le vrai schéma de calcul

```
Salaire négocié en USD (ex: 1 000 $)
         │
         ▼ taux de change de la période (ex: 2 850)
         │
Salaire net à payer en CDF (ex: 2 850 000 CDF)
         │
         ▼ + retenues (CNSS + IRPP + ...)
         │
Salaire brut (ex: calculé par inversion des formules)
         │
         ▼ × structure de rémunération
         │
Salaire de base (partie fixe du brut)
```

**C'est un modèle "net vers brut"** (à l'envers des standards occidentaux) : on part du net négocié, on remonte au brut par calcul inverse.

⚠️ **Cependant**, ce modèle est plus complexe à implémenter (calcul par inversion). Nous pouvons aussi envisager un modèle hybride où :
- Le brut est stocké dans le contrat (calculé à partir du net négocié)
- Le pipeline fait le calcul "brut → net" classique
- À la fin, on vérifie que le net calculé = net négocié

**Question pour toi** : Est-ce que tu confirmes ce modèle "net vers brut" en entrée (le contrat stocke le net négocié, le brut est déduit), ou préfères-tu un modèle "brut vers net" classique (le contrat stocke le brut, on calcule le net) ? Les deux peuvent fonctionner, le choix a des implications sur l'architecture.

---

### 4. Avances, primes, bonus — Oui, dans le périmètre paie

Ta question est très pertinente car ces éléments sont souvent gérés par des modules séparés dans d'autres systèmes. Voici mon analyse :

#### Primes et bonus — ✅ Oui, clairement dans le périmètre

Les primes et bonus sont des **éléments de paie** (gains) qui :
- S'ajoutent au salaire brut
- Sont soumis aux cotisations (sauf exceptions)
- Figurent sur le bulletin de paie
- Sont déjà dans le catalogue (`PRIME_PERF`, `PRIME_FONCT`, `PRIME_RISQUE`, `PRIME_PANIER`, `GRATIF_13EME`, `GRATIF_EXCEP`, `COMMISSION`)

**Décision D4 déjà validée** : tous les types concrets sont listés dans le catalogue → les primes et bonus y figurent déjà.

#### Avances sur salaire — ✅ Oui, dans le périmètre, mais avec un statut spécial

Les avances sur salaire sont **dans le périmètre** car :
- Elles sont déduites du net à payer sur le bulletin
- Elles impactent la trésorerie de la paie
- Le gestionnaire de paie doit les gérer

**Mais elles ont un statut spécial** :
- Ce ne sont pas des gains (pas d'impôt, pas de cotisation)
- Ce sont des **déductions pré-comptées** (l'employé a déjà reçu l'argent)
- Dans le catalogue : `AVANCE_SAL` en catégorie `autre`, tous les flags d'assujettissement à `faux`

**Ce qui est déjà dans le code frontend** : Le store `payrollStore` gère déjà les avances avec un CRUD complet (create, update, delete), des statuts (`pending`, `approved`, `paid`, `rejected`), et une route dédiée `/payroll/advances`.

**Ma proposition** : Conserver les avances comme **déductions** dans le périmètre paie, mais prévoir une **gestion de cycle de vie** (demande → approbation → déduction sur le bulletin) qui pourrait être partagée avec le module RH.

---

## Prochaines étapes

Une fois que tu auras répondu à mes deux questions :
1. **Prorata calendaire ou ouvrés ?**
2. **Modèle "net vers brut" ou "brut vers net" ?**

Je mettrai à jour directement les 3 documents :
- **`metamodel.md`** : ajouter la règle de prorata dans le contrat, l'unité de période dans le processus, clarifier le salaire de base
- **`semantics.md`** : nouvelle section sur le prorata d'embauche/sortie
- **`catalogue.md`** : ajouter le cas d'embauche en cours de mois au cas pratique janvier 2026

Et bien sûr recréer le `docs/payroll/en/api.md` perdu.