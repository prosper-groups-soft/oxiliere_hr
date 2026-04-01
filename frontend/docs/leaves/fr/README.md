## 1. Le "Balance Wallet" (Tableau de Bord Personnel)

C'est la vue "Libre-Service" pour l'employé.

    Cartes de Solde Dynamiques : Utilisation de jauges de progression circulaires ou de barres de progression shadcn/ui pour afficher le ratio "Jours pris / Jours alloués".
    Compte à Rebours d'Expiration : Un petit widget d'alerte (type Linear) indiquant : "Attention : 4 jours de report expirent le 31 mars".
    Timeline des Demandes : Une liste chronologique épurée avec des badges de statut (En attente, Validé, Refusé).

## 2. Le "Manager Inbox" (File d'Attente des Approbations)

Une vue optimisée pour les responsables.

    Vue "Split-Screen" : À gauche, la liste des demandes entrantes. À droite, le détail avec une détection de conflit intégrée (ex: "2 autres membres de l'équipe sont absents à cette période").
    Actions en un clic : Boutons Approve (Vert subtil) et Reject (Rouge) accessibles directement au survol de la ligne pour traiter les demandes en masse.

## 3. Le "Team Planner" (Vue Calendrier d'Équipe)

Une vue horizontale (Gantt-style) indispensable pour la coordination.

    Grille de Présence : Les lignes représentent les employés, les colonnes les jours du mois. Les blocs de congés sont colorés selon le type (Annuel, Maladie, Circonstanciel).
    Filtre de Département : Pour visualiser uniquement l'impact sur une équipe spécifique.

## 4. L'Architecte de Politiques (Configuration Admin)

Une interface technique mais claire pour les RH.

    Tableau des Règles d'Ancienneté : Un éditeur de barème permettant de définir que Ancienneté > 5 ans = +2 jours.
    Workflow Builder : Une interface simple pour définir qui valide quoi (Manager direct -> RH).

## 5. Composants UI spécifiques (Stack oxtemplate)

    Progress Bar : Pour visualiser la consommation des soldes.
    Sheet (Side Drawer) : Pour le formulaire de demande de congé (évite de quitter la page actuelle).
    Popover : Pour afficher le motif d'un refus ou le justificatif d'un congé de circonstance.
    Calendar : En mode sélection de plage (range) pour choisir les dates de début et de fin.
