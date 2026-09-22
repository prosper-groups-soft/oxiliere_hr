# Sémantique — Que signifie chaque état ?

- **En cours de chargement initial** : aucune donnée n'est encore disponible. On affiche un indicateur de chargement plein page, car il n'y a rien d'autre à montrer.
- **En cours de rechargement** : des données sont déjà affichées, mais une mise à jour est en cours (changement de filtre, de page, ou rafraîchissement). On garde la liste visible et on montre une fine barre de progression en haut, pour signaler que quelque chose se passe sans masquer le contenu.
- **Vide (vrai vide)** : le chargement a réussi, mais il n'existe tout simplement aucune donnée (par exemple, aucun compte bancaire n'a encore été créé). On affiche un message d'accueil qui invite à créer la première entrée, avec une icône métier (par exemple un portefeuille pour les comptes) et un bouton d'action.
- **Vide filtré (recherche sans résultat)** : des données existent, mais rien ne correspond aux filtres ou à la recherche en cours (par exemple, "Aucun compte ne correspond à vos critères pour « Equity »"). C'est un état différent du vrai vide : on affiche une loupe barrée, on rappelle les critères actifs, et on propose de réinitialiser les filtres plutôt que de créer une nouvelle entrée.
- **En erreur sans données** : le premier chargement a échoué (problème réseau, serveur indisponible). On affiche un message d'erreur explicite et un bouton pour réessayer.
- **En erreur avec données déjà affichées** : une mise à jour a échoué, mais l'ancienne liste est toujours valable. On la laisse visible, on signale l'erreur discrètement et on propose de réessayer.
- **Changement de filtres** : dès que l'utilisateur modifie un critère de recherche ou un filtre, on revient à la première page, car les résultats précédents ne correspondent plus.

Ces distinctions permettent d'éviter les confusions fréquentes entre "on charge pour la première fois" et "on met à jour des données déjà affichées".
