## 1. L'Organigramme Interactif (Visual Org Chart)

C'est la pièce maîtresse du module.

    Vue Arborescente Dynamique : Une interface de type "Canvas" (zoomable et déplaçable) qui affiche la hiérarchie des départements. Chaque nœud affiche le nom du département, le nombre d'employés (Headcount) et la photo du manager.
    Drill-Down : En cliquant sur un département, l'interface se concentre sur celui-ci et ouvre un panneau latéral affichant la liste des membres et les sous-départements.

## 2. Le Référentiel des Carrières (Career Mapping)

Une vue pour les RH afin de structurer les parcours de croissance.

    Matrice des Séniorités : Un tableau comparatif montrant les niveaux (JUNIOR → EXECUTIVE) et les exigences pour chaque position.
    Path Visualizer : Pour un employé donné, afficher une timeline montrant son évolution : les transitions de type PROMOTION ou TRANSFER sont marquées par des icônes distinctes.

## 3. Gestion des Transitions (Promotion & Mobility Hub)

Une interface dédiée aux mouvements de personnel.

    Le Formulaire de Transition : Utilise un stepper (étape par étape) pour gérer le passage d'une position à l'autre. L'interface doit comparer "Ancienne position vs Nouvelle position" avec les changements de département et de manager.
    Le "Vacancy Tracker" : Une vue listant les positions définies mais non pourvues (via l'endpoint /reports/vacancies), permettant de lancer des demandes de recrutement.

## 4. Matrice de Compétences & Formations

    Le "Radar Chart" : Pour chaque position, un graphique en radar montrant les compétences requises.
    Le Registre des Certifications : Une liste haute densité avec des indicateurs de validité. Les certificats expirant dans moins de 30 jours clignotent ou utilisent un badge Orange.

## 5. Composants UI spécifiques (Stack oxtemplate)

    Tree Structure / Accordion : Pour la vue hiérarchique simplifiée des départements dans la barre latérale.
    Command Menu : Pour rechercher instantanément un département ou une position (CMD+K > "Backend").
    Badge : Pour identifier visuellement les niveaux de séniorité avec un code couleur (ex: Purple pour C-LEVEL, Blue pour Senior).
    Dialog (Modal) : Pour créer rapidement une nouvelle JobFamily sans quitter la vue d'ensemble.

