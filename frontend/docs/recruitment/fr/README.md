## 1. Le "Board" de Recrutement (Vue Pipeline)

C'est le cœur opérationnel.

    Tableau Kanban Interactif : Chaque colonne représente une phase (Tri, Shortlist, Entretien, Offre). Les candidats sont des cartes que l'on peut faire glisser (Drag & Drop).
    Indicateurs de Vitesse : Sur chaque carte, un petit badge indique depuis combien de jours le candidat est dans cette phase (pour éviter les goulots d'étranglement).
    Quick-Filter : Une barre de recherche CMD+K pour isoler instantanément les candidats par score (ex: "Score > 80") ou par compétence.

## 2. Le Profil Candidat "Split-View"

Inspiré par les interfaces de support client haut de gamme.

    Le Dossier Central : À gauche, les infos personnelles et le CV affiché via un lecteur PDF intégré (évite de télécharger le fichier).
    Le Flux d'Activité : À droite, une timeline de tous les échanges : notes des recruteurs, scores des entretiens et historique des emails.
    Scorecard d'Évaluation : Un composant visuel affichant la moyenne des notes données par les différents interviewers.

## 3. Le Scheduler d'Entretiens (Vue Calendrier)

    Conflits d'Interviewer : Une vue synchronisée avec le module Calendar pour voir les disponibilités des managers avant de programmer un entretien.
    Lien Vidéo Automatisé : Un champ qui génère ou stocke le lien Meet/Zoom directement dans l'invitation.

## 4. Le Dashboard Analytique (Hiring Metrics)

    Le Funnel (Entonnoir) : Un graphique montrant la déperdition : 500 candidatures → 50 shortlists → 10 entretiens → 1 embauche.
    Source Performance : Un diagramme circulaire montrant d'où viennent vos meilleurs talents (LinkedIn, Site carrière, Cooptation).

## 5. Composants UI spécifiques (Stack oxtemplate)

    Badge : Pour les statuts de candidature avec des variantes : Outline pour "En attente", Destructive pour "Rejeté".
    Dialog : Pour remplir rapidement une fiche d'évaluation après un entretien.
    Sheet (Tiroir) : Pour créer une nouvelle JobOffer sans quitter la vue du pipeline.
    Scroll Area : Pour gérer les longues listes de candidats dans les colonnes du Kanban.
