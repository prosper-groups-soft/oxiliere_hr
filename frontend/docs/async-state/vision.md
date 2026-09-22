# Vision — Pourquoi une machine à état pour la récupération des données ?

Dans l'application Oxiliere HR, chaque page qui affiche une liste paginée (employés, campagnes de recrutement, campagnes de performance, etc.) doit gérer les mêmes situations : on attend les données, on les reçoit, il n'y en a pas, ou une erreur réseau survient. Aujourd'hui, ce raisonnement est copié-collé dans chaque page, avec les mêmes composants visuels (barre de chargement, message d'erreur, liste vide) et la même logique de rechargement.

L'objectif de cette bibliothèque est de ne décrire qu'une seule fois ce que signifie "récupérer des données", puis de le réutiliser partout. On passe d'une logique dispersée à un cycle de vie partagé, ce qui rend l'ajout d'une nouvelle page beaucoup plus simple et réduit le risque d'incohérences visuelles ou de bugs de rechargement.

Cette documentation explique le concept, indépendamment de la technologie utilisée (Svelte, TanStack Query ou autre).
