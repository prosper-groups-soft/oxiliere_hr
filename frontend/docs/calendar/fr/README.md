## 1. La "Timeline Master" (Vue Calendrier)

Inspiré par Linear, le calendrier ne doit pas être un simple tableau statique.

    Affichage Multi-Niveaux : Une vue "Année" pour la vision globale (détection des ponts et périodes de paie courtes) et une vue "Mois" pour le détail opérationnel.
    Indicateurs d'Impact : Les jours "Non travaillables" (fériés, fermetures) sont marqués par une couleur de fond subtile (ex: gris léger ou hachures) pour que les RH visualisent immédiatement les trous dans la production.
    Drag-to-Create : Possibilité de cliquer et glisser sur plusieurs jours pour créer une "Fermeture Entreprise" (pont, congés techniques) instantanément.

## 2. Le Gestionnaire de Récurrence

Une interface dédiée à la maintenance annuelle.

    Smart Suggestions : Un panneau latéral qui propose d'importer les jours fériés nationaux basés sur le CountryCode (via une bibliothèque externe ou API).
    Tableau de Bord des Événements : Une liste haute densité permettant de voir d'un coup d'œil quels événements sont récurrents et lesquels sont ponctuels.

## 3. Le "Impact Previewer" (Aperçu de l'impact)

C'est la touche "haute performance" du module.

    Simulation de Paie : Lors de l'ajout d'un jour férié, un petit widget affiche : "Impact estimé : -1 jour ouvré pour 450 employés".
    Conflits d'événements : Alerte visuelle si une formation (Événement spécial) est placée sur un jour de fermeture entreprise.

## 4. Filtres de Périmètre (Scope Switcher)

    Segmentation Géographique : Un sélecteur élégant en haut de page pour filtrer les événements : "Tout le groupe", "Siège Social", "Usine A", "Filiale France".
    Tags de Catégorie : Utilisation de badges colorés (shadcn/ui Badge) pour distinguer rapidement : [Férié], [Fermeture], [Formation].

## 5. Composants UI spécifiques (Stack oxtemplate)

    Calendar : Le composant de base, étendu pour supporter les points de couleur sous les dates (événements multiples).
    Popover : Pour afficher les détails d'un événement au survol ou au clic sans changer de page.
    Switch : Pour activer/désactiver rapidement le statut "Travaillable" dans le formulaire de création.

