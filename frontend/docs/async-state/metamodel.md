# Métamodèle — De quoi parle-t-on ?

## Les idées principales

- **Une ressource asynchrone** représente n'importe quelle donnée qui arrive avec un délai (une liste d'employés, des unités organisationnelles, etc.). Elle possède à tout moment un état : on ne sait pas encore ce qu'elle contient, on est en train de charger, on a reçu une réponse, ou une erreur s'est produite.
- **Une requête** décrit comment obtenir cette ressource : quels paramètres envoyer (page, recherche, filtres) et où aller les chercher.
- **Les filtres** regroupent tous les critères choisis par l'utilisateur : la recherche textuelle, les filtres par catégorie, la pagination et le tri.

## Le cycle de vie

Au départ, la ressource est au repos. Dès qu'on lance une recherche, elle passe en chargement. Selon la réponse du serveur, elle devient disponible ou en erreur. Si l'utilisateur modifie un filtre ou demande un rechargement, elle repasse en chargement tout en gardant l'ancienne donnée visible jusqu'à l'arrivée de la nouvelle.

## Ce qui ne doit jamais arriver

Par exemple, pendant un rechargement, l'ancienne liste reste affichée (on ne l'efface pas brutalement). De même, une erreur n'efface pas les données déjà obtenues : elle s'affiche à côté, et l'utilisateur peut réessayer sans perdre ce qu'il voyait.
