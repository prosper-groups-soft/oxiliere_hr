# Sémantique — Que signifie chaque état ?

- **Actif** : un seul onglet est actif à la fois. Il est mis en valeur par une couleur plus soutenue et un soulignement qui glisse sous son nom.
- **Compteur** : quand un onglet porte un nombre (par exemple, 3 congés en attente), un petit badge arrondi s'affiche à côté de son nom. S'il n'y a rien à signaler, le badge disparaît.
- **Navigation par chemin** : si l'onglet possède un chemin, cliquer dessus change l'URL et précharge les données de la page suivante pour une transition plus fluide.
- **Navigation par événement** : si l'onglet n'a pas de chemin (cas des sous-onglets internes comme le profil employé), cliquer dessus déclenche simplement un changement d'état local.
- **Variante** : par défaut, on utilise le soulignement qui glisse. La pastille est réservée aux réglages, et le fondu enchaîné aux cas où l'on veut un effet plus doux.
