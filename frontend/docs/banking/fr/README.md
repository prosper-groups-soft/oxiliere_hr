## 1. Le "Vault" (Vue Employé - Détails Bancaires)

C'est ici que la précision visuelle est maximale.

    Cartes de Comptes Dynamiques : Au lieu d'une simple liste, chaque compte est représenté par une "carte" épurée affichant la devise en gros, le logo de la banque (ou un placeholder généré), et le statut de vérification (Verified, Pending).
    Sélecteur de Devise Intelligent : Un système d'onglets ou de "chips" pour basculer entre les comptes (USD, CDF, EUR). Le compte Primaire est mis en avant avec une bordure subtile et un badge distinctif.
    Visualiseur d'IBAN/SWIFT : Un composant avec bouton "Copy to clipboard" intégré, utilisant une police monospace (type JetBrains Mono) pour une lisibilité parfaite des caractères.

## 2. Le Répertoire des Institutions (Bank Directory)

Une vue d'ensemble pour la gestion structurelle.

    Grille de Logos : Une vue en galerie ou liste dense montrant les institutions financières et les fournisseurs de Mobile Money (M-Pesa, Orange Money) avec des icônes distinctes.
    Filtre par Pays et Type : Barre de recherche persistante en haut (CMD+K compatible) pour isoler rapidement les banques par pays ou les institutions gérant la paie de masse.

## 3. Le Centre de Vérification (Compliance Hub)

Une vue dédiée aux gestionnaires RH/Trésorerie pour valider les nouveaux comptes.

    Split View (Vue partagée) : À gauche, la liste des comptes "Unverified". À droite, le détail avec l'historique des modifications (Audit Trail) et les boutons d'action critiques (Verify, Block).
    Indicateur de Santé des Données : Un widget montrant le pourcentage d'employés ayant un compte primaire configuré par devise de paie, pour éviter les erreurs de virement.

## 4. Rapports de Paiement (Payroll Exports)

    Prévisualisation du Bordereau : Avant l'export, une table haute densité simulant le virement de masse, avec mise en évidence des comptes bloqués ou manquants pour éviter les rejets bancaires.

## 5. Composants UI spécifiques (Stack oxtemplate)

    Context Menu : Sur chaque compte pour des actions rapides (Set as Primary, Deactivate, View Audit).
    Dialog (Modal) : Pour la création de compte, avec une validation Zod en temps réel (ex: vérifier la longueur du numéro de compte selon la banque sélectionnée).
    Alert Dialog : Pour les actions irréversibles comme le blocage d'un compte.
