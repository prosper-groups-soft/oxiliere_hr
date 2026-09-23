# Métamodèle — De quoi parle-t-on ?

- **Un tableau de bord** rassemble plusieurs indicateurs pour un rôle donné (par exemple "vue RH" ou "vue collaborateur").
- **Un widget** est une petite tuile qui affiche un seul type d'information : un chiffre clé, une liste ou une alerte. Il ne sait pas à quoi il ressemble à l'écran, il sait seulement quelle information il doit montrer.
- **Une métrique** est la valeur métier derrière un widget : comment elle se calcule, sur quelle période, et à partir de quel seuil une alerte se déclenche.
- **La portée du rôle** détermine qui a le droit de voir quoi. C'est elle qui décide si un widget est visible et s'il doit même interroger le serveur.

## Cycle de vie

On configure d'abord le tableau de bord pour un rôle, puis chaque widget interroge sa source de données, calcule sa métrique et s'affiche. Ensuite, il se rafraîchit périodiquement ou sur demande, en gardant l'ancienne valeur visible pendant la mise à jour.
