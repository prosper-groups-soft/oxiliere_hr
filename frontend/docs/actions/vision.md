# Vision — Pourquoi unifier les actions et les filtres ?

Dans chaque module de l'application (employés, congés, paie, recrutement, etc.), la barre d'actions en haut de page se ressemble beaucoup : on y retrouve un bouton pour créer, un sélecteur de tri, et plusieurs menus pour filtrer les données. Aujourd'hui, chacun de ces menus est construit séparément, avec le même code répété pour chaque dimension (unité, statut, type de contrat, etc.).

Cette répétition rend l'ajout d'un nouveau filtre coûteux et augmente le risque d'incohérences visuelles. De plus, multiplier les menus oblige l'utilisateur à ouvrir plusieurs endroits pour affiner sa recherche, ce qui alourdit l'expérience.

L'objectif est de ne décrire qu'une seule fois ce qu'est un filtre ou un tri, puis de laisser une petite bibliothèque s'occuper de les afficher de manière cohérente. Ainsi, ajouter un filtre revient à déclarer son nom et ses options, sans toucher à l'interface.
