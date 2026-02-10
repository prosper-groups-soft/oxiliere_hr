## 1. Le "Payroll Run" Control (Centre d'Exécution)

C'est votre tableau de bord de lancement.

    Stepper de Processus : Une barre de progression en haut de page divisée en étapes claires : Préparation → Calcul → Révision → Approbation → Paiement.
    Visualiseur de Masse Salariale : Un graphique en barres empilées montrant la répartition : Salaire Net / Cotisations Sociales / Taxes / Allocations.
    Bouton d'Action Critique : Un bouton "Approve & Pay" protégé par une double confirmation (Dialog) pour éviter tout lancement accidentel.

## 2. Le Bulletin de Paie Interactif (Smart Payslip)

Au lieu d'un simple PDF statique, proposez une vue web haute définition.

    Accordion de Détails : Des sections dépliables pour : Rémunération de base, Heures supplémentaires (avec détail du calcul), Déductions (Absences/Avances).
    Comparateur de Période : Une petite flèche (verte/rouge) à côté du net à payer indiquant la variation par rapport au mois précédent avec une explication au survol (ex: "+15h supplémentaires").
    Mode "Audit" : Un interrupteur permettant aux RH de voir les formules de calcul appliquées derrière chaque ligne (ex: Salaire de base / 26 * jours présents).

## 3. Gestionnaire d'Avances (Cash Flow Hub)

Une interface dédiée au suivi des prêts et remboursements.

    Cartes de Solde d'Avances : Pour chaque employé ayant une avance, une carte affichant le "Montant Restant" et le "Taux de Remboursement" actuel.
    Workflow d'Approbation : Une file d'attente pour les nouvelles demandes d'avances avec un indicateur de risque (ex: "Le montant dépasse 50% du salaire net").

## 4. Configuration des Règles (The "Engine" Room)

    Éditeur de Taux : Une interface simplifiée pour mettre à jour les taux CNSS, INSS et le SMIG sans toucher au code.
    Sélecteur de Devises (FX) : Un widget affichant le taux de change USD/CDF du jour utilisé pour la paie, avec possibilité d'historique.

## 5. Composants UI spécifiques (Stack oxtemplate)

    Table (High Density) : Pour le registre de paie, permettant de filtrer par département ou statut de paiement.
    Separator : Pour structurer les différentes sections du bulletin de paie de manière élégante.
    Tooltip : Pour expliquer les acronymes légaux (ex: "CNSS : Caisse Nationale de Sécurité Sociale").
    Stats Card : Pour afficher les totaux globaux (Net total, Total cotisations) en haut de page.

