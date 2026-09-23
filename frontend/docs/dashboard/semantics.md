# Sémantique — Que signifie chaque état ?

- **Visible selon le rôle** : un widget n'est même pas interrogé s'il n'est pas autorisé pour le rôle en cours. Par exemple, la masse salariale globale n'est jamais demandée pour un collaborateur.
- **En cours de rafraîchissement** : pendant une mise à jour, l'ancienne valeur reste affichée avec une discrète indication de chargement, pour ne pas faire clignoter l'écran.
- **Vide filtré** : si un widget de type liste ne trouve rien à cause des filtres (par exemple, aucun congé en attente ce mois-ci), on l'explique avec un message adapté, plutôt qu'en laissant une zone blanche.
- **Période** : par défaut, tous les widgets observent le mois en cours. Changer la période (mois ou trimestre) s'applique à l'ensemble du tableau de bord, pour garder une vision cohérente.
