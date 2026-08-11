import json
import logging
from pathlib import Path
from django.conf import settings
from safedelete.models import HARD_DELETE
from hr.payroll.services.cache import PayrollCacheService
from hr.payroll.models import (
    TaxBracket,
    LegalAllowance,
    OvertimeRule,
    PayrollAdjustment,
    SMIGConfiguration,
    SocialContributionRate,
    PayrollConfiguration,
    ProfessionalCategory,
)


logger = logging.getLogger(__name__)


class PayrollInitService:

    def init_payroll_configurations(self):
        """Global initialization with logging of steps."""
        configs = {
            'payroll_config_defaults.json'   : PayrollConfiguration,
            'irpp_2026_tax_brackets.json'    : TaxBracket,
            'legal_allowances.json'          : LegalAllowance,
            'overtime_rules.json'            : OvertimeRule,
            'payroll_adjustments.json'       : PayrollAdjustment,
            'smig_defaults.json'             : SMIGConfiguration,
            'social_contributions.json'      : SocialContributionRate,
            'professional_categories.json'   : ProfessionalCategory,
        }
        
        summary = {}
        logger.info("Starting the initialization of payroll configurations...")

        for filename, model_class in configs.items():
            try:
                count = self._load_fixture_to_model(filename, model_class)
                summary[model_class.__name__] = count
                logger.info(f"Success : {count} entries synchronized for {model_class.__name__} ({filename}).")
            except Exception as e:
                logger.error(f"Error importing {filename} for model {model_class.__name__} : {str(e)}")
                summary[model_class.__name__] = "Error"

        # Clear all payroll-related caches to ensure fresh data is served
        try:
            logger.info("Clearing payroll caches...")
            PayrollCacheService.clear_config_cache()
            logger.info("All payroll caches cleared successfully.")
        except Exception as e:
            logger.error(f"Error clearing caches: {str(e)}")

        logger.info("Payroll initialization completed.")
        return summary

    def _load_fixture_to_model(self, filename, model_class):
        # BASE_DIR points to ox_hr/, fixtures are in backend/fixtures/
        fixture_path = Path(settings.BASE_DIR).parent / 'hr' / 'fixtures' / 'payroll' / 'cd' / filename

        logger.info(f"[{model_class.__name__}] Loading fixture: {fixture_path}")

        if not fixture_path.exists():
            logger.warning(f"Fixture file not found: {fixture_path}")
            return 0

        with open(fixture_path, 'r', encoding='utf-8') as f:
            data_list = json.load(f)

        logger.info(f"[{model_class.__name__}] Found {len(data_list)} items in fixture")

        # For a complete reset: hard delete all existing records first
        # This ensures no conflicts with unique constraints and removes stale data
        deleted_count, _ = model_class.objects.all().delete(force_policy=HARD_DELETE)
        if deleted_count > 0:
            logger.info(f"[{model_class.__name__}] Hard deleted {deleted_count} existing records")

        count = 0
        for item in data_list:
            fields = item.get('fields', {})
            pk = item.get('pk')

            logger.info(f"[{model_class.__name__}] Processing PK: {pk}, fields: {list(fields.keys())}")

            try:
                # Create new record
                model_class.objects.create(pk=pk, **fields)
                logger.info(f"[{model_class.__name__}] Created PK: {pk}")
                count += 1
            except Exception as e:
                logger.error(f"[{model_class.__name__}] Error processing PK {pk}: {str(e)}")
                raise

        return count

    def reset_legal_allowances(self) -> int:
        """Recharge uniquement les allocations légales depuis leur fixture (réinitialisation ciblée)."""
        count = self._load_fixture_to_model('legal_allowances.json', LegalAllowance)
        if count > 0:
            PayrollCacheService.clear_allowance_cache()
            PayrollCacheService.clear_legal_allowances_cache()
            logger.info(f"Legal allowances reset: {count} allowances reloaded from fixture.")
        return count

    def reset_adjustments(self) -> int:
        """Recharge uniquement le catalogue d'éléments de paie depuis sa fixture (réinitialisation ciblée)."""
        count = self._load_fixture_to_model('payroll_adjustments.json', PayrollAdjustment)
        if count > 0:
            PayrollCacheService.clear_adjustment_types_cache()
            logger.info(f"Payroll adjustments reset: {count} items reloaded from fixture.")
        return count

    def reset_professional_categories(self) -> int:
        """Recharge la grille des catégories professionnelles (7 classes x 4 échelons) depuis la fixture."""
        count = self._load_fixture_to_model('professional_categories.json', ProfessionalCategory)
        if count > 0:
            PayrollCacheService.clear_config_cache()
            logger.info(f"Professional categories reset: {count} entries reloaded from fixture.")
        return count

