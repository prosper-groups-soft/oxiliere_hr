# Migration Sheets → `forms` + `forms-bindings`

> Référence : `BankAccountSheet.svelte` comme modèle. Lot par lot, migrables d'abord puis extensions.

## Migrés (26 + 6 inline forms)

| # | Module | Sheet | Avant | Après | Réduction |
|---|--------|-------|-------|-------|-----------|
| 1 | banking | `accounts/sheets/BankAccountSheet.svelte` | ref | ref | — |
| 2 | banking | `directory/sheets/BankInstitutionSheet.svelte` | 339 | ~85 | −75% |
| 3 | calendar | `components/sheets/EventSheet.svelte` | 321 | ~95 | −70% |
| 4 | jobs | `careers/seniority/sheets/SenioritySheet.svelte` | 335 | ~75 | −77% |
| 5 | jobs | `mobility/vacancies/sheets/VacancySheet.svelte` | 357 | ~85 | −76% |
| 6 | admin | `access/components/sheets/users/AccessUserCreateSheet.svelte` | 299 | ~90 | −70% |
| 7 | attendance | `register/sheets/ManualPunchSheet.svelte` | 178 | ~70 | −61% |
| 8 | payroll | `advances/sheets/AdvanceRequestSheet.svelte` | 470 | ~90 | −81% |
| 9 | leaves | `requests/sheets/LeaveRequestSheet.svelte` | 530 | ~120 | −77% |
| 10 | attendance | `config/sheets/policy/PolicySheet.svelte` | 352 | ~90 | −74% |
| 11 | jobs | `careers/positions/sheets/PositionSheet.svelte` | 893 | ~110 | −88% |
| 12 | attendance | `config/sheets/shift/AssignmentSheet.svelte` | 411 | ~110 | −73% |
| 13 | attendance | `config/sheets/shift/BulkAssignmentSheet.svelte` | 477 | ~110 | −77% |
| 14 | jobs | `mobility/transitions/sheets/TransitionSheet.svelte` | 455 | ~95 | −79% |
| 15 | recruitment | `interview/InterviewSheet.svelte` | 425 | ~95 | −78% |
| 16 | recruitment | `interview/FeedbackSheet.svelte` | 295 | ~70 | −76% |
| 17 | recruitment | `candidate/OfferSheet.svelte` | 169 | ~55 | −67% |
| 18 | recruitment | `candidate/CandidateSheet.svelte` | 591 | ~95 | −84% |
| 19 | recruitment | `campaign/CampaignSheet.svelte` | 740 | ~110 | −85% |
| 20 | admin | `access/group-sheet/GroupSheet.svelte` | 208 | ~70 | −66% |
| 21 | performance | `campaigns/sheets/CampaignSheet.svelte` | 578 | ~85 | −85% |
| 22 | performance | `reviews/sheets/ReviewSheet.svelte` | 547 | ~75 | −86% |
| 23 | employees | `info/forms/EmployeeProfileForm.svelte` | 274 | ~90 | −67% |
| 24 | employees | `contract/forms/EmployeeContractForm.svelte` | 535 | ~100 | −81% |
| 25 | employees | `family/contacts/forms/EmergencyContactForm.svelte` | 130 | ~40 | −69% |
| 26 | employees | `family/children/forms/ChildForm.svelte` | 149 | ~40 | −73% |
| 27 | employees | `education/forms/EmployeeEducationForm.svelte` | 242 | ~55 | −77% |
| 28 | employees | `documents/forms/EmployeeDocumentForm.svelte` | 188 | ~50 | −73% |
| — | employees | `header/edit/EmployeeEditSheet.svelte` | 130 | 90 | réécrit (wrapper) |
| — | forms | `components/hosts/FormView.svelte` | — | — | + `showSubmit` prop |

**Moyenne : ~−77%.** Pattern : `FieldConfig[]` + `createForm({ host: { type: 'sheet' }, layout: { type: 'section' }, onSubmit: persist(...) })` + `FormView` + `extras` slot pour UI custom. Validation via `validators.*` + `invariant`.

## Reportés — non-forms / sur-mesure

| Sheet | Raison |
|-------|--------|
| `jobs/OrgStructureSheet.svelte` (686) | Hybride liste + form inline — garder sur-mesure |
| `payroll/AdvanceDetailSheet` (326) | Lecture seule (cards + table échéances) — pas un form |
| `payroll/AdvanceApproveSheet` (461) | Double mode %/mois + fenêtre déduction — extension `RepaymentPlanField` dédiée |
| `payroll/RunDetailSheet` / `PayslipDetailSheet` / `attendance/PolicyDetailsSheet` / `PolicyComparisonSheet` | Detail/compare — hors scope |
| `recruitment/CandidateProfileSheet` (38) | Wrapper `<CandidateProfile>` lecture seule |
| `recruitment/EvaluationSheet` (162) | Critères dynamiques `evaluationTemplate` — extension `ScoringField` |
| `recruitment/CandidateSheet` (fait, allégé) | Multi-positions + priorities retirés (SRP) |
| `recruitment/CampaignSheet` (fait, allégé) | Evaluation template retiré |

## À faire (migrables simples restants, non entamés)

- `payroll`: `AdvanceDetailSheet`, `AdvanceApproveSheet`, `RunDetailSheet`, `PayslipDetailSheet`
- `performance`: `CampaignSheet`, `ReviewSheet` (phase 2)
- `recruitment`: 7 sheets (`CandidateSheet`, `CandidateProfileSheet`, `EvaluationSheet`, `OfferSheet`, `CampaignSheet`, `InterviewSheet`, `FeedbackSheet`) — à trier
- `employees`: `EmployeeEditSheet`, `EmployeeLifecycleSheet`
- `jobs`: `OrgStructureSheet` (sur-mesure)

## Validation

- `npx tsc --noEmit --skipLibCheck` non concluant (projet sans `typescript` en npx). `npm run check` (`svelte-check`) trop lent sur ce repo — validation visuelle `npm run dev` recommandée par sheet.
