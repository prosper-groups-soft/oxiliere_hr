# UX — Récupération des données

Principe directeur : **ne jamais laisser l'utilisateur se demander si l'application a planté, si elle cherche encore, ou si elle n'a rien trouvé.** Chaque état doit avoir une traduction visuelle distincte et rassurante.

## Les quatre visages

- **Premier chargement** : la page est vide, on montre un message qui respire ("Chargement des employés") avec une animation douce. On évite l'écran blanc qui fait douter.
- **Mise à jour en arrière-plan** : la liste reste visible, on ajoute simplement une fine barre qui glisse en haut. L'utilisateur continue de lire pendant que les nouvelles données arrivent — on ne lui arrache pas ce qu'il regardait.
- **Rien à afficher** : si les filtres ne donnent aucun résultat, on l'explique avec bienveillance ("Aucun employé ne correspond à votre recherche") et on propose de réinitialiser les filtres en un clic, plutôt que de laisser un tableau vide et silencieux.
- **Erreur** : si le serveur ne répond pas, on le dit clairement, sans jargon, et on donne un moyen immédiat de réessayer. Si des données étaient déjà affichées, on les garde et on signale l'erreur à côté, pour ne pas punir l'utilisateur d'un problème réseau passager.

## Le fil conducteur

La recherche, les filtres et la pagination forment une conversation : chaque action (taper, filtrer, changer de page) relance naturellement la recherche. L'interface reflète cette conversation avec des puces de filtres visibles, un compteur de résultats, et un retour à la première page dès qu'un critère change — comme si on feuilletait un catalogue qui se remet au début quand on change de rayon.

Cette cohérence, portée par `AsyncView`, garantit que toutes les pages de l'application parlent le même langage visuel, quel que soit le module (RH, recrutement, paie).
