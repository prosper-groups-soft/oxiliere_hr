# Module Paie - Oxilière HR

## 📖 Vue d'ensemble

Le module **Paie** (Payroll) gère l'intégralité du processus de calcul et de génération des bulletins de salaire selon les normes **légales de la République Démocratique du Congo (RDC) 2026**.

### Périmètre fonctionnel

✅ Calcul du **salaire brut** (fixe/horaire, brutage Net→Brut)  
✅ Gestion des **heures supplémentaires** (6h à 130%, puis 160%)  
✅ Déductions pour **absences non payées** (proratisation)  
✅ Contributions sociales : **CNSS (5%)**, ONEM, INPP  
✅ Impôt sur le revenu professionnel (**IPR progressif**)  
✅ **Allocations légales** : familiales, logement (plafond 30%), transport  
✅ Avances sur salaire avec **priorité de remboursement**  
✅ Ajustements (primes, déductions personnalisées)  
✅ **Multi-devises** avec taux de change appliqués  
✅ Congés payés (maintien de salaire)  

---

## 🏗️ Architecture

```
hr/payroll/
├── models.py                   # Modèles de données
├── enums.py                    # Énumérations (statuts, types)
├── services/
│   ├── orchestrator.py         # Orchestrateur principal (CŒUR)
│   ├── payroll_run.py          # Gestion des périodes de paie
│   ├── contributions.py        # Calcul CNSS/ONEM/INPP
│   ├── taxes.py                # Calcul IPR progressif
│   ├── legal_allowances.py     # Allocations légales
│   ├── advances.py             # Gestion avances sur salaire
│   ├── adjustments.py          # Résolution ajustements
│   ├── brutage.py              # Brutage (Net → Brut)
│   ├── exchange.py             # Taux de change
│   ├── calculators.py          # Utilitaires calcul
│   ├── integration.py          # Intégration données externes
│   └── __init__.py
├── tests.py                    # Tests unitaires & intégration
└── admin.py                    # Interface Django Admin
```

---

## 🔄 Flux de traitement

### Étape 1: Lancement de la période de paie
```python
from hr.payroll.services.payroll_run import PayrollRunService

run = PayrollRunService.create_payroll_run(
    start_date=date(2026, 1, 1),
    end_date=date(2026, 1, 31),
    description="Paie Janvier 2026"
)
```

### Étape 2: Traitement orchestré
```python
from hr.payroll.services.orchestrator import PayrollOrchestrator

PayrollOrchestrator.process_run(run)
# ✓ Génère les bulletins pour tous les contrats actifs
# ✓ Atomique : tout ou rien
```

### Étape 3: Validation et export
```python
# Le statut passe de DRAFT → VALIDATED automatiquement
# Bulletins disponibles pour export PDF, téléchargement, etc.
```

---

## 📊 Processus détaillé du bulletin

Pour chaque employé, `PayrollOrchestrator._generate_single_payslip()` exécute 7 étapes :

### **STAGE 1: Récupération des données**
- Jours travaillés / absences / congés  
- Données familiales (nb enfants)  
- Taille de la compagnie (pour INPP)  
- Taux de change (si contrat en devise étrangère)

**Source** : `PayrollIntegrationService`

### **STAGE 2: Calcul du salaire brut**
```
Brut = Salaire de Base + Heures Supplémentaires + Primes
```

**Cas spécifiques :**
- **Salaire NET contractuel** → Brutage vers Brut (via `GrossUpService`)
- **Contrat horaire** → Totalisation (heures travaillées + congés payés)
- **Multi-devise** → Conversion au CDF

**Source** : `_calculate_gross_salary()`

### **STAGE 3: Déductions pour absences**
Si salaire **FIXE** et absences non payées :
```
Déduction = (Brut / Diviseur) × Jours absence
Diviseur = 26 (jours théoriques) ou configurable
```

**Source** : `_apply_absence_deductions()`

### **STAGE 4: Contributions & Impôts**

#### Contributions sociales
```
CNSS Employee = Brut × 5%
ONEM Employer = 100% employeur
INPP Employer = 100% employeur
```

#### Impôt sur le revenu professionnel
```
Base Taxable = (Brut - CNSS) + Excédent Logement Imposable
IPR = Progressif par tranches (taux DRC 2026)
```

#### Allocations légales
- **Familiales** : 5 000 CDF/enfant (plafond 2)
- **Logement** : 30% du salaire de base (max. 5 000 CDF)
- **Transport** : 2 000 CDF (fixe)

**Source** : `_calculate_social_contributions()`, `_calculate_tax_and_allowances()`

### **STAGE 5: Avances sur salaire**
Déduction en priorité :
1. Avances anciennes (plus de 2 mois)
2. Avances récentes (solde disponible)

```
Net avant avances = (Brut + Allocations) - (CNSS + IPR + Déductions)
Déduction avances = Min(Avances dues, Net avant avances × 20%)
```

**Source** : `_process_advances()`, `AdvanceService`

### **STAGE 6: Création du bulletin**
```
NET FINAL = (Brut + Allocations) - (CNSS + IPR + Avances + Autres déductions)
```

**Persistance** : `EmployeePayslip` + lignes détail (`PayslipLine`)

### **STAGE 7: Lignes de détail**
Chaque composant du bulletin est enregistré en ligne détaillée :
- Salaire de base
- Heures supplémentaires
- Primes
- Allocations
- Contributions
- Impôts
- Avances

---

## 🎯 Cas d'usage : Exemple complet

### Données initiales
- **Employé** : Jean Doe
- **Contrat** : Salaire FIXE brut 10 000 CDF
- **Famille** : 2 enfants
- **Période** : Janvier 2026 (22 jours travaillés)
- **Absences** : 0 jour
- **Avances** : 500 CDF (résiduelle)

### Traitement

**STAGE 2: Salaire brut**
```
Brut = 10 000 CDF
```

**STAGE 4: Contributions & Impôts**
```
CNSS (5%) = 500 CDF
Allocations = 500 (enfants) + 1000 (logement) + 200 (transport) = 1700 CDF
Taxable = (10000 - 500) + 500 = 10 000 CDF
IPR = 1200 CDF (selon barème progressif)
```

**STAGE 5: Avances**
```
Net avant avances = (10000 + 1700) - (500 + 1200) = 10 000 CDF
Déduction avance = 500 CDF ✓
```

**STAGE 6: Net final**
```
NET = (10000 + 1700) - (500 + 1200 + 500) = 9500 CDF
```

### Bulletin final
| Composant | Montant |
|-----------|---------|
| Salaire de Base | 10 000 |
| **Brut** | **10 000** |
| Allocations familiales | 500 |
| Indemnité logement | 1 000 |
| Frais transport | 200 |
| **Total Allocations** | **1 700** |
| CNSS (5%) | -500 |
| IPR | -1 200 |
| Avance remboursement | -500 |
| **NET À PAYER** | **9 500** |

---

## ⚙️ Configuration

### Modèle: `PayrollConfiguration`

```python
config = PayrollConfiguration.objects.first()

# Paramètres clés
config.currency                          # Devise (CDF)
config.work_hours_per_month              # Heures/mois théoriques (195)
config.include_leaves_in_payroll         # Inclure congés (True)
config.leave_deduction_divisor           # Diviseur absence (26)
config.fixed_deduction_per_absent_day    # Déduction fixe/jour (optionnel)
config.default_payment_method            # Virement/Chèque/Liquide
```

---

## 🧪 Tests

### Lancer les tests
```bash
python manage.py test hr.payroll.tests
```

### Classes de test
- `PayrollOrchestratorTestCase` : Tests d'intégration complets
  - ✅ Génération complète de bulletin
  - ✅ Prévention des doublons
  - ✅ Déductions absence
  - ✅ Contributions sociales
  - ✅ Impôts & allocations
  - ✅ Traitement batch multi-employés

---

## 🐛 Dépannage

### Erreur : "Only draft payroll runs can be processed"
```python
# Assurez-vous que le PayrollRun a le statut DRAFT
run.status = PayrollStatus.DRAFT
run.save()
```

### Erreur : "attribute 'child_count' missing"
```python
# Vérifier que PayrollIntegrationService retourne les données
# Ou mockerles données dans les tests
```

### Bulletin zéro ou négatif
```python
# Vérifier:
# 1. Contrat actif (is_active=True)
# 2. Salaire base > 0
# 3. Configuration complète
# 4. Taux de change correct
```

---

## 📝 Notes légales (DRC 2026)

### Références légales
- 📄 **Loi n° 015/2002** : Code du travail (salaire minimum, heures sup)
- 📄 **Arrêté n° 68/11** : Heures supplémentaires (6h @ 130%, puis 160%)
- 📄 **Décret n° 14/018** : CNSS (5% employé, 5% employeur)
- 📄 **Ordonnance n° 70/267** : Allocations familiales (5 000 CDF max)
- 📄 **Code des impôts 2023** : IPR avec barème progressif

### Points importants
⚠️ **Salaire minimum** : Vérifier le SMIG actualisé (non géré par ce module)  
⚠️ **Heures supplémentaires** : Limites légales (max. 10h/jour, 60h/mois)  
⚠️ **Indemnité logement** : Plafonnée à 30% du salaire  
⚠️ **Retenues avances** : Max. 20% du net  

---

## 📞 Support & Améliorations

### À faire
- [ ] Export PDF personnalisé (templates)
- [ ] Validation automatique avant clôture
- [ ] Historique & révisions de bulletin
- [ ] Intégration comptabilité (journaux paie)
- [ ] Déclarations sociales (CNSS, IPR)
- [ ] Dashboard tableau de bord

### Rapports les plus courants
1. Liste des bulletins par période
2. Résumé paie (masse salariale, contributions)
3. Détail par employé (net, déductions, allocations)
4. Conformité légale (min, max heures)

---
