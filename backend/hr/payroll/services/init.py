import json
import os
import logging
from django.conf import settings
from hr.payroll.models import (
    TaxBracket, 
    LegalAllowance, 
    OvertimeRule, 
    PayrollAdjustment, 
    SMIGConfiguration, 
    SocialContributionRate
)


logger = logging.getLogger(__name__)


class PayrollInitService:

    def init_payroll_configurations(self):
        """Global initialization with logging of steps."""
        configs = {
            'ipr_tax_brackets.json'    : TaxBracket,
            'legal_allowances.json'    : LegalAllowance,
            'overtime_rules.json'      : OvertimeRule,
            'payroll_adjustments.json' : PayrollAdjustment,
            'smig_defaults.json'       : SMIGConfiguration,
            'social_contributions.json': SocialContributionRate,
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

        logger.info("Payroll initialization completed.")
        return summary

    def _load_fixture_to_model(self, filename, model_class):
        fixture_path = os.path.join(
            settings.BASE_DIR, 
            'fixtures', 
            'payroll/cd',
            filename
        )
        
        if not os.path.exists(fixture_path):
            logger.warning(f"Fixture file not found: {fixture_path}")
            return 0

        with open(fixture_path, 'r', encoding='utf-8') as f:
            data_list = json.load(f)

        count = 0
        for item in data_list:
            fields = item.get('fields', {})
            pk = item.get('pk')

            # Update or create based on PK
            obj, created = model_class.objects.update_or_create(
                pk=pk,
                defaults=fields
            )
            
            action = "Created" if created else "Updated"
            logger.debug(f"[{model_class.__name__}] {action} PK: {pk}")
            count += 1
        
        return count

