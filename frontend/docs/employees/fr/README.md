## 1. L'Annuaire "Command Center" (Vue Liste)

Une interface ultra-performante pour naviguer dans des centaines de profils.

    Filtres à Facettes Persistants : Une barre latérale gauche permettant de filtrer par Département, Statut (Onboarding, Actif, Suspendu), et Lieu de travail.
    Quick-Action Row : Au survol d'un employé, des micro-boutons apparaissent pour : "Appeler le contact d'urgence", "Télécharger le dernier contrat" ou "Changer le statut".
    Avatar-Driven UI : Utilisation systématique de l'avatar avec un indicateur de couleur pour le statut (Vert pour Actif, Orange pour Période d'essai, Rouge pour Suspendu).

## 2. Le Dossier "Profil 360°" (Vue Détail)

Une mise en page structurée en onglets pour ne pas noyer l'utilisateur.

    Le Header "Identité" : Nom, Matricule, et le bouton critique "Action de Cycle de Vie" (Transition, Suspension, Offboard) mis en évidence.
    Onglet "Vault" (Documents) : Une grille de fichiers montrant des aperçus (thumbnails) des pièces d'identité. Les documents expirant bientôt sont surlignés en ambre.
    Timeline de Statut : À droite ou en bas, une ligne de vie verticale montrant chaque étape du collaborateur dans l'entreprise depuis son onboarding.

## 3. Le "Family & Emergency" Hub

Un espace dédié à la protection sociale.

    Hiérarchie des Contacts : Les contacts d'urgence sont affichés sous forme de liste numérotée (Priorité 1, 2, 3) avec des boutons d'appel direct.
    Visualisation des Ayants Droit : Une vue simplifiée des enfants à charge, affichant les âges calculés dynamiquement pour l'éligibilité aux allocations.

## 4. Le Workflow d'Onboarding (Assistant)

    Steppers (Étapes) : Un formulaire multi-étapes pour l'enregistrement d'un nouvel employé : Identité > Contrat > Documents > Famille.
    Checklist de Conformité : Un indicateur de progression qui montre si le dossier est complet (ex: "ID manquant", "Adresse non renseignée").

## 5. Composants UI spécifiques (Stack oxtemplate)

    Tabs : Pour naviguer entre Infos Personnelles, Documents, Famille et Historique.
    Avatar : Composant central avec fallback automatique sur les initiales de l'employé.
    DataTable : Avec pagination et tri côté serveur (via TanStack Table) pour gérer des milliers d'employés sans ralentissement.
    Hover Card : Pour afficher un résumé rapide (téléphone, manager, poste) sans cliquer sur le profil.

