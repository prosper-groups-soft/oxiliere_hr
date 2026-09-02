Bonne question — c'est justement le point crucial à bien comprendre. Laisse-moi vérifier le code backend exact pour te répondre précisément (et pas de mémoire).

Listed directory payroll
Listed directory controllers
Searched for "def (process|review|approve|complete|create)|@router\.(post|put|patch)|PayrollStatus\."
Searched for "process|review|approve|complete|status"
Listed directory services
Searched for "def |class "
Viewed payroll_run.py:1-80
Searched for "def |status =|PayrollStatus|transition"
Viewed payroll_run.py:120-340
Viewed payroll_run.py:340-470

J'ai l'image complète du backend. Vérifions les endpoints côté frontend pour être précis sur ce qui est réellement appelé.

Searched for "processRun|reviewRun|approveRun|completeRun|createRun|fetchRunDetail|fetchRunSummary"
Searched for "processRun|reviewRun|approveRun|completeRun|createRun"
Searched for "processRun"
Viewed payrollRun.api.svelte.ts:1-141

Voici le détail complet, étape par étape, avec ce qui se passe **côté backend** (source de vérité) et **côté frontend** (simple reflet).

## Réponse courte

- **Le backend est la source de vérité** : chaque validation = une mutation HTTP qui persiste en base de données (statut + données associées).
- **Le frontend ne persiste rien des calculs** : après chaque action, il re-lit le détail depuis l'API pour se resynchroniser. Son seul rôle persistant est de mémoriser l'`id` du run actif pour restaurer l'onglet après un F5.

## Détail par étape

### 0. Création (kickoff) — « Lancer l'exécution »

| | |
|---|---|
| **Backend** | `POST /payroll/runs` → `PayrollRunService.create_run` crée un `PayrollRun` en **`DRAFT`** en base. Persiste : `start_date`, `end_date`, `exchange_rate_applied`, et `params_snapshot` (la sélection employés : `scope`, `org_unit_ids`, `employee_ids`). |
| **Frontend** | [KickoffForm](file:///c:/Users/kiban/Desktop/Projects/Programmation/Oxiliere/oxiliere_hr/frontend/src/lib/features/payroll/components/run/kickoff/KickoffForm.svelte#L156-L176) appelle `createPayrollRunFromDates()`, puis `onCreated()` → passe à l'étape « Préparation ». |

C'est ici que **tout est réellement persisté une fois pour toutes** : période, taux de change et sélection sont figés dans `params_snapshot`.

### 1. Préparation — aucune action backend

C'est une vue **d'analyse en lecture seule**. Aucun appel API de mutation. Les données (bénéficiaires, anomalies, période) sont lues du `PayrollRun` déjà chargé.

### 2. Calcul — « Calculer la paie »

| | |
|---|---|
| **Backend** | `POST …/process` → [start_payroll_processing](file:///c:/Users/kiban/Desktop/Projects/Programmation/Oxiliere/oxiliere_hr/backend/hr/payroll/services/payroll_run.py#L256-L322) : garde `DRAFT` obligatoire, passe à **`PROCESSING`**, puis l'`orchestrator.process_run(run)` **génère les fiches de paie** (`EmployeePayslip` + lignes) en base, et termine à **`VALIDATED`**. |
| **Frontend** | [calculatePayroll](file:///c:/Users/kiban/Desktop/Projects/Programmation/Oxiliere/oxiliere_hr/frontend/src/lib/features/payroll/stores/runs/payrollRunStore.svelte.ts#L499-L507) appelle `processRun()`, puis `fetchRunDetail()` + `fetchRunList()` pour rafraîchir l'état. |

### 3. Révision — « Réviser »

| | |
|---|---|
| **Backend** | `POST …/review` → [review_payroll_run](file:///c:/Users/kiban/Desktop/Projects/Programmation/Oxiliere/oxiliere_hr/backend/hr/payroll/services/payroll_run.py#L356-L377) : garde `VALIDATED` obligatoire, passe à **`REVIEWED`**. |
| **Frontend** | `reviewPayroll()` → `reviewRun()`, puis re-fetch. |

### 4. Approbation — « Approuver »

| | |
|---|---|
| **Backend** | `POST …/approve` → [approve_payroll_run](file:///c:/Users/kiban/Desktop/Projects/Programmation/Oxiliere/oxiliere_hr/backend/hr/payroll/services/payroll_run.py#L381-L402) : garde `REVIEWED` obligatoire, passe à **`APPROVED`**. |
| **Frontend** | `approvePayroll()` → `approveRun()`, puis re-fetch. |

### 5. Paiement — « Finaliser le paiement »

| | |
|---|---|
| **Backend** | `POST …/complete` → [complete_payroll_run](file:///c:/Users/kiban/Desktop/Projects/Programmation/Oxiliere/oxiliere_hr/backend/hr/payroll/services/payroll_run.py#L326-L352) : garde `VALIDATED`/`REVIEWED`/`APPROVED`, vérifie qu'il y a des fiches, puis passe à **`PAID`** (clôture finale). |
| **Frontend** | `processPayment()` → `completeRun()`, puis re-fetch. Si `paid`, `clearActiveRun()` ferme l'onglet dynamique. |

## Faut-il persister côté frontend ?

**Non, pas les valeurs métier.** Le flux est :

```
bouton validé → appel API → backend persiste → frontend re-fetch → UI mise à jour
```

Le frontend **ne garde pas de brouillon local** des calculs/révisions. Il reflète toujours l'état du backend.

La **seule persistance côté frontend** est purement technique, pour restaurer l'onglet après un rechargement :

- `localStorage` : l'`id` du run actif (`payroll:activeRunId`).
- `sessionStorage` : le flag `payroll:startingNewRun` (avant la création du `DRAFT`).

Ces deux-là sont gérés dans [payrollRunStore.svelte.ts](file:///c:/Users/kiban/Desktop/Projects/Programmation/Oxiliere/oxiliere_hr/frontend/src/lib/features/payroll/stores/runs/payrollRunStore.svelte.ts#L35-L38).

## Point d'attention important

Les transitions backend sont **gardées** : chaque action exige le statut précédent exact (ex. calcul requiert `DRAFT`, révision requiert `VALIDATED`, etc.). Donc l'ordre des étapes est imposé par le serveur, pas seulement par l'UI — c'est lui qui garantit l'intégrité du cycle de vie. Le mapping statut backend → statut UI se fait dans [backendToPayrollStatus](file:///c:/Users/kiban/Desktop/Projects/Programmation/Oxiliere/oxiliere_hr/frontend/src/lib/features/payroll/types/types.ts#L44-L55).

