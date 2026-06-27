3:29 PM
Maintenant que j'ai analysé toute la structure, voici mon analyse complète.

Analyse complète de la paie — Alignement avec la RDC
Franchement, bravo 👏, la base est très solide et montre une bonne compréhension de la paie congolaise. Tu as les bons concepts : SMIG, CNSS/INPP/ONEM, IPR progressif, allocations familiales, logement, transport, heures sup en paliers.

Voici mon analyse détaillée par catégorie :

✅ Ce qui est déjà bien aligné avec la RDC
Élément	Statut	Commentaire
SMIG (Salaire Minimum Interprofessionnel Garanti)	✅	Bon, avec suivi historique
CNSS (5% employé / 8% employeur, plafond)	✅	Taux corrects, plafond présent
INPP (par tranche d'effectif)	✅	3%, 2%, 1% selon taille — très bien
ONEM (0.2% employeur uniquement)	✅	Parfait
IPR progressif (4 tranches)	✅	Barème correct jusqu'à 40%
Heures sup (130%, 160%, 200%)	✅	Conforme au Code du Travail
Allocations familiales (1/27 SMIG/enfant/jour)	✅	Bon
Indemnité de logement (30% brut exonéré)	✅	Avec suivi de l'excédent imposable
Indemnité de transport	✅	Présente
Devise CDF/USD + taux de change	✅	Important en RDC
Brutage (Net → Brut)	✅	Utile pour contrats en net
⚠️ Problèmes / Incohérences à corriger
1. Plafond CNSS erroné — Critique
Le plafond CNSS est à 252 750 CDF dans la fixture :

"ceiling_amount": "252750.00"
Mais le plafond CNSS en RDC est de 175 000 CDF par mois (source : CNSS, tarif 2024). À vérifier et éventuellement ramener à la valeur réelle.

2. Taux de change USD/CDF obsolète
Dans payroll_config_defaults.json :

json
"exchange_rate_usd_cdf": "2200.0000"
Mais dans PayrollConfiguration le défaut est 2850.0000. En 2026, le taux réel tourne autour de 2900-3200 CDF. À harmoniser et idéalement utiliser l'API BCC.

3. Heures sup — FIRST_TWO_HOURS mal nommé
Dans l'enum (enums.py) :

python
FIRST_TWO_HOURS = "FIRST_TWO_HOURS", _('First 2 hours beyond 45h/week (130%)')
Mais dans le code (calculators.py et orchestrator.py), tu utilises 6 heures comme premier palier !

python
# DRC Rule: 130% for the first 6 hours, 160% beyond
if std_hours_dec <= 6:
C'est correct pour la RDC (les 6 premières heures sup' à 130% de la 46e à la 51e heure), mais le nom de l'enum prête à confusion. Il faudrait le renommer en FIRST_SIX_HOURS ou FIRST_TIER.

4. Calcul du taxable_base pour l'IPR — À revoir
Dans orchestrator.py (ligne 405) :

python
taxable_base = (gross_salary - cnss_employee) + allowances['taxable_housing_excess']
En RDC, la base imposable IPR c'est : (Salaire brut − CNSS employé) + avantages en nature imposables (excédent logement). C'est globalement correct. Mais il faudrait aussi soustraire les allocations familiales si elles sont déjà incluses dans le brut, car elles sont exonérées d'IPR. Actuellement, les allocations sont ajoutées au net_amount mais pas incluses dans le gross_salary, donc ça va. À documenter clairement.

5. OvertimeRule.WEEKEND non utilisé dans le calcul
Tu définis WEEKEND et HOLIDAY dans OvertimeRuleType mais dans _calculate_gross_salary, seul holiday est passé au calcul :

python
multipliers = {
    'first_period': ...,
    'subsequent': ...,
    'holiday': ...  # ← WEEKEND n'est pas utilisé
}
En RDC, dimanche = 200% et jour férié = 200% aussi. Les deux sont à 200% donc pas d'impact financier, mais WEEKEND devrait alimenter la même clé ou être explicitement géré.

6. Le modèle EmployeeContract utilise is_active mais aussi des dates
Tu as is_active=True sur un contrat ET des start_date/end_date. C'est redondant. En RDC, un contrat a une date de début et soit :

CDI : pas de date de fin (end_date = null
3:29 PM
Tu as fini ?
3:59 PM
Non j'avais été coupé ! Je finis l'analyse maintenant.

⚠️ Problèmes / Incohérences (suite)
6. Redondance is_active + start_date/end_date sur EmployeeContract
Tu utilises is_active=True ET des dates de début/fin. En pratique, un contrat actif est celui dont la date courante est entre start_date et end_date. Le is_active crée une redundancy. Exemple : un contrat périmé (end_date dépassée) pourrait encore être marqué is_active=True. Je recommande de supprimer is_active et d'utiliser les dates systématiquement, ou de garder is_active comme override manuel uniquement.

7. Manque : Prime de risque / salissure / panier
En RDC, beaucoup d'entreprises paient des primes de panier (repas), des primes de risque, ou des indemnités de logement en nature. Ton BonusTypes a MEAL_ALLOWANCE et TRANSPORT_ALLOWANCE mais ces primes sont souvent des montants journaliers (ex: 5 000 CDF/jour de panier), pas des pourcentages. Vérifie que LegalAllowance peut gérer ça proprement.

3:59 PM
4:10 PM
Voilà le plan est dans 
implementation_plan.md
.

Mais pour répondre à tes questions directement :

Prime vs Bonus — La différence
En vrai, ce sont deux choses différentes :

Prime	Bonus
Nature	Contractuelle, prévisible	Discrétionnaire, variable
Régularité	Mensuelle/hebdo (fixe)	Annuelle/semestrielle (variable)
Condition	Liée à un risque/charge (transport, logement)	Liée à la performance
Exemple	Prime de transport, de panier, de logement	13ème mois, prime de rendement
Donc ton frère parle plutôt de bonus de performance — c'est le fruit d'une évaluation.

Le système d'évaluation dont parle ton frère
C'est un module qui manque carrément dans le système ! Le cycle typique en RDC :

Évaluation (annuelle/semestrielle)
    ↓                       
    Note / Score (ex: 85%)
    ↓
    Bonus de performance calculé
    ↓
    Intégré dans la paie
J'ai donc inclus dans le plan la création d'un Module d'Évaluation des Performances avec :

Une grille de critères (ponctualité, qualité, objectifs)
Une notation par employé
Un lien direct vers le calcul des bonus dans la paie
Pour tes questions ouvertes
Primes de panier/risque ? Certaines entreprises en RDC paient ça. On peut les ajouter comme LegalAllowance (comme le transport) ou comme PayrollAdjustment avec un montant journalier.

Brutage (Net→Brut) ? En RDC, beaucoup de contrats sont signés en Net (ce que l'employé reçoit). Le brutage sert à retrouver le brut à partir du net. C'est très utile, garde-le.

J'ai mis le plan en mode review — regarde-le et dis-moi ce que tu veux modifier ou prioriser !

4:10 PM
Tu peux accéder sur internet pour aller chercher certaines informations dont tu en aurais besoin ?

Est-ce que je dois utiliser django-money.

Chaque module doit se trouver dans un dossier : frontend\src\lib\features
backend\hr (un module est une application ici).


Pour le taux de change. J'utilise un module oxutils qui offre cette fonctionnalité :
# Currency Module

**Multi-source currency exchange rate management with automatic fallback**

## Features

- Automatic currency rate synchronization from multiple sources
- BCC Bank (primary) and OpenExchangeRates (fallback) support
- Historical rate tracking with state management
- REST API endpoints for rate queries
- Admin interface for rate monitoring
- Support for 17 major currencies
- Built-in signals for sync success and failure

## Supported Currencies

```python
AVAILABLES_CURRENCIES = [
    "AOA",  # Angolan Kwanza
    "AUD",  # Australian Dollar
    "BIF",  # Burundian Franc
    "CAD",  # Canadian Dollar
    "CHF",  # Swiss Franc
    "CNY",  # Chinese Yuan
    "EUR",  # Euro
    "GBP",  # British Pound
    "JPY",  # Japanese Yen
    "RWF",  # Rwandan Franc
    "TZS",  # Tanzanian Shilling
    "UGX",  # Ugandan Shilling
    "USD",  # US Dollar
    "XAF",  # Central African CFA Franc
    "XDR",  # Special Drawing Rights
    "ZAR",  # South African Rand
    "ZMW"   # Zambian Kwacha
]
```

## Setup

### Installation

Add to your Django settings:

```python
# settings.py
from oxutils.conf import UTILS_APPS

INSTALLED_APPS = [
    *UTILS_APPS,  # Includes 'oxutils.currency'
    # your apps...
]

# Optional: Enable fallback to OpenExchangeRates if BCC fails
OXI_BCC_FALLBACK_ON_OXR = True
```

### Run Migrations

```bash
python manage.py migrate currency
```

## Usage

### Synchronizing Rates

#### Manual Sync

```python
from oxutils.currency.models import CurrencyState

# Sync rates from BCC (with OXR fallback if configured)
state = CurrencyState.sync()

print(f"Synced {state.currencies.count()} currencies from {state.source}")
```

#### Scheduled Sync (Celery)

```python
# tasks.py
from celery import shared_task
from oxutils.currency.models import CurrencyState

@shared_task
def sync_currency_rates():
    """Sync currency rates daily"""
    try:
        state = CurrencyState.sync()
        return f"Synced {state.currencies.count()} rates"
    except Exception as e:
        return f"Failed to sync rates: {str(e)}"

# celery beat schedule
CELERY_BEAT_SCHEDULE = {
    'sync-currency-rates': {
        'task': 'myapp.tasks.sync_currency_rates',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
}
```

### Querying Rates

#### Get Latest Rates

```python
from oxutils.currency.models import CurrencyState

# Get the most recent currency state
state = CurrencyState.objects.latest()

# Access all currencies
for currency in state.currencies.all():
    print(f"{currency.code}: {currency.rate}")

# Get specific currency
usd_rate = state.currencies.get(code='USD')
print(f"USD Rate: {usd_rate.rate}")
```

#### Get Rate by Code

```python
from oxutils.currency.models import CurrencyState

state = CurrencyState.objects.latest()
eur_currency = state.currencies.get(code='EUR')

# Convert amount
amount_in_usd = 100
amount_in_eur = amount_in_usd * float(eur_currency.rate)
```

### Using the Utils

```python
from oxutils.currency.utils import load_rates, update_rates
from oxutils.currency.schemas import CurrencyStateDetailSchema

# Load rates from external source
rates, source = load_rates()
print(f"Loaded {len(rates)} rates from {source}")

# Update rates from schema (useful for distributed systems)
state_schema = CurrencyStateDetailSchema(
    id=uuid.uuid4(),
    source='BCC',
    currencies={'USD': 1.0, 'EUR': 0.85},
    created_at=datetime.now(),
    updated_at=datetime.now()
)
update_rates(state_schema)
```

## REST API Endpoints

The currency module provides REST API endpoints via Django Ninja:

### Register Controllers

```python
# urls.py
from ninja_extra import NinjaExtraAPI
from oxutils.currency.controllers import CurrencyController

api = NinjaExtraAPI()
api.register_controllers(CurrencyController)
```

### Available Endpoints

#### List Currency States

```http
GET /api/currency/states
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "source": "BCC",
      "created_at": "2025-12-21T10:00:00Z",
      "updated_at": "2025-12-21T10:00:00Z"
    }
  ],
  "count": 1,
  "page": 1,
  "page_size": 20
}
```

#### Get Latest State with Rates

```http
GET /api/currency/states/latest
```

**Response:**
```json
{
  "id": "uuid",
  "source": "BCC",
  "created_at": "2025-12-21T10:00:00Z",
  "updated_at": "2025-12-21T10:00:00Z",
  "currencies": {
    "USD": 1.0,
    "EUR": 0.85,
    "GBP": 0.73,
    "XAF": 655.957
  }
}
```

#### Get Specific State

```http
GET /api/currency/states/{state_id}
```

#### Get Current Rates Only

```http
GET /api/currency/rates
```

**Response:**
```json
{
  "USD": 1.0,
  "EUR": 0.85,
  "GBP": 0.73,
  "XAF": 655.957
}
```

#### Get Rate for Specific Currency

```http
GET /api/currency/rates/EUR
```

**Response:**
```json
{
  "EUR": 0.85
}
```

## Models

### CurrencyState

Represents a snapshot of currency rates at a specific time.

**Fields:**
- `id` (UUID): Primary key
- `source` (CharField): Source of rates (BCC or OXR)
- `created_at` (DateTimeField): When the state was created
- `updated_at` (DateTimeField): Last update time

**Methods:**
- `sync()`: Class method to fetch and save new rates

**Manager Methods:**
- `latest()`: Get the most recent currency state with prefetched currencies

### Currency

Individual currency rate within a state.

**Fields:**
- `id` (UUID): Primary key
- `code` (CharField): Currency code (e.g., 'USD', 'EUR')
- `rate` (DecimalField): Exchange rate (max_digits=10, decimal_places=4)
- `state` (ForeignKey): Related CurrencyState

**Validation:**
- Currency code must be in `AVAILABLES_CURRENCIES`
- Rate must be greater than 0

## Admin Interface

The currency module includes a comprehensive Django admin interface:

### CurrencyState Admin

- View all currency states with source and date
- Inline display of all currencies in a state
- Read-only to prevent accidental modifications
- Filter by source and creation date
- Search by ID and source

### Currency Admin

- View individual currency records
- Filter by code, source, and date
- Search by code and state ID
- Read-only to maintain data integrity

## Configuration

### Settings

```python
# settings.py

# Enable fallback to OpenExchangeRates if BCC fails
OXI_BCC_FALLBACK_ON_OXR = True  # Default: False

# Configure bcc-rates library (if needed)
BCC_RATES_CACHE_DIR = '/path/to/cache'  # Optional
```

## Signals

Two signals are fired during currency synchronization. Both use
`send_robust()` — a failing receiver never blocks the sync.

```python
from oxutils.currency.signals import currency_sync_succeeded, currency_sync_failed
```

| Signal | Trigger | Args |
|--------|---------|------|
| `currency_sync_succeeded` | Sync completed | `sender`, `state`, `source`, `count` |
| `currency_sync_failed` | Sync failed (any exception) | `sender`, `error`, `source` |

### Usage

```python
from django.dispatch import receiver
from oxutils.currency.signals import currency_sync_succeeded, currency_sync_failed

@receiver(currency_sync_succeeded)
def on_sync_success(sender, state, source, count, **kwargs):
    # Invalidate caches, notify monitoring, etc.
    cache.delete('latest_rates')

@receiver(currency_sync_failed)
def on_sync_failed(sender, error, source, **kwargs):
    # Send alert, log to Sentry, fallback to cached rates...
    logger.critical(f"Currency sync failed: {error}")
```

## Error Handling

### Sync Failures

```python
from oxutils.currency.models import CurrencyState

try:
    state = CurrencyState.sync()
except ValueError as e:
    # No rates found from any source
    print(f"Sync failed: {e}")
except Exception as e:
    # Other errors (network, parsing, etc.)
    print(f"Unexpected error: {e}")
```

### API Errors

The API returns appropriate HTTP status codes:
- `404`: Currency state or rate not found
- `500`: Internal server error during sync

## Best Practices

1. **Schedule Regular Syncs**: Use Celery Beat to sync rates daily
2. **Monitor Sync Status**: Check logs for sync failures
3. **Use Latest State**: Always query `CurrencyState.objects.latest()` for current rates
4. **Handle Missing Rates**: Always check if a currency exists before accessing
5. **Cache Rates**: Consider caching frequently accessed rates in Redis
6. **Backup States**: Keep historical states for auditing and analysis

## Example: Currency Converter

```python
from oxutils.currency.models import CurrencyState
from decimal import Decimal

class CurrencyConverter:
    def __init__(self):
        self.state = CurrencyState.objects.latest()
        self.rates = {
            c.code: c.rate 
            for c in self.state.currencies.all()
        }
    
    def convert(self, amount: Decimal, from_code: str, to_code: str) -> Decimal:
        """Convert amount from one currency to another"""
        if from_code not in self.rates:
            raise ValueError(f"Currency {from_code} not found")
        if to_code not in self.rates:
            raise ValueError(f"Currency {to_code} not found")
        
        # Convert to base currency (usually USD)
        base_amount = amount / self.rates[from_code]
        
        # Convert to target currency
        return base_amount * self.rates[to_code]

# Usage
converter = CurrencyConverter()
eur_amount = converter.convert(Decimal('100'), 'USD', 'EUR')
print(f"100 USD = {eur_amount} EUR")
```

## Troubleshooting

### Rates Not Syncing

1. Check BCC API availability
2. Verify `OXI_BCC_FALLBACK_ON_OXR` setting
3. Check network connectivity
4. Review logs for specific errors

### Missing Currencies

Ensure the currency code is in `AVAILABLES_CURRENCIES` list.

### Stale Rates

Check when the last sync occurred:
```python
state = CurrencyState.objects.latest()
print(f"Last sync: {state.created_at}")
```

## Dependencies

- `bcc-rates`: Library for fetching rates from BCC and OpenExchangeRates
- `structlog`: Structured logging
- `django-ninja-extra`: REST API framework







