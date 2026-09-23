# Vision — Pourquoi unifier les onglets ?

Chaque module de l'application affiche une barre d'onglets en haut de page (employés, congés, paie, recrutement, etc.). Aujourd'hui, chacun de ces onglets est construit séparément, avec le même code répété pour gérer l'onglet actif, l'icône, le compteur et le soulignement qui glisse.

L'objectif est de ne décrire qu'une seule fois ce qu'est un onglet et comment il se comporte, puis de laisser une petite bibliothèque s'occuper de l'affichage. Ainsi, ajouter un onglet revient à déclarer son nom et son icône, sans toucher à l'animation ou aux styles.
