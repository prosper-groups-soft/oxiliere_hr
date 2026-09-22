# Catalogue — À quoi ça ressemble concrètement ?

## Exemple 1 : La liste des employés (cas paginé)

L'utilisateur arrive sur la page des employés. Il peut taper une recherche, choisir plusieurs filtres (unité, statut, contrat), trier par nom, et naviguer entre les pages. Chaque action déclenche une requête qui renvoie une partie de la liste et le nombre total de résultats. L'interface doit donc gérer à la fois la pagination et l'affichage des filtres actifs.

## Exemple 2 : La liste des unités organisationnelles (cas simple)

Ici, on affiche simplement toutes les unités disponibles, sans pagination ni tri complexe. Il suffit de charger la liste une fois et de la garder à jour. C'est le même principe que précédemment, mais avec moins de paramètres.

Ces deux exemples montrent que la même idée s'applique, que la requête soit complexe ou très simple. Si la bibliothèque fonctionne pour ces deux cas, elle fonctionnera pour les autres pages de l'application (recrutement, performance, paie, etc.).
