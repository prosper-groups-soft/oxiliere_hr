import logging
from decimal import Decimal
from typing  import Dict, Any
from uuid    import UUID

from django.db import transaction
from django.core.exceptions import ValidationError

from hr.payroll.models import (
    PayrollConfiguration,
    SMIGConfiguration,
    SocialContributionRate,
    OvertimeRule,
    TaxBracket,
    LegalAllowance,
)
from hr.payroll.services.cache import PayrollCacheService


logger = logging.getLogger(__name__)


class ConfigurationService:
    """ Manages system-wide payroll settings, statutory rates, and legal rules. """

    # ===== PAYROLL CONFIGURATION =====

    @classmethod
    @transaction.atomic
    def create_configuration(cls, data: Dict[str, Any], actor=None) -> PayrollConfiguration:
        """ Initializes the global payroll configuration. """
        logger.debug("[Config] Creating payroll configuration", extra={"actor": actor})

        # Check if configuration already exists
        if PayrollConfiguration.objects.exists():
            logger.warning("[Config] Configuration already exists")
            raise ValidationError("Payroll configuration already exists. Use update instead.")

        # Validate currency
        currency = data.get('currency', 'CDF')
        if currency not in ['CDF', 'USD']:
            logger.warning("[Config] Invalid currency", extra={"currency": currency})
            raise ValidationError(f"Invalid currency: {currency}")

        # Create configuration
        config = PayrollConfiguration.objects.create(**data)

        logger.info("[Config] Configuration created successfully")
        return config

    @classmethod
    @transaction.atomic
    def update_configuration(cls, data: Dict[str, Any], actor=None) -> PayrollConfiguration:
        """ Updates the global payroll configuration settings. """
        logger.debug("[Config] Updating configuration", extra={"actor": actor})

        config = PayrollConfiguration.objects.first()
        if not config:
            logger.warning("[Config] No configuration found to update")
            raise ValidationError("Payroll configuration not initialized. Create one first.")

        # Update fields
        for key, value in data.items():
            if hasattr(config, key) and value is not None:
                setattr(config, key, value)

        config.save()

        # Clear all payroll-related caches
        PayrollCacheService.clear_config_cache()

        logger.info("[Config] Configuration updated and all caches cleared")
        return config

    # ===== SMIG RATES =====

    @classmethod
    @transaction.atomic
    def create_smig_rate(cls, data: Dict[str, Any], actor=None) -> SMIGConfiguration:
        """ Records a new SMIG (minimum wage) rate entry. """
        logger.debug("[SMIG] Creating SMIG rate", extra={"data": data, "actor": actor})

        # Validate amount
        amount = Decimal(str(data.get('amount', 0)))
        if amount <= 0:
            logger.warning("[SMIG] Invalid SMIG amount", extra={"amount": amount})
            raise ValidationError("SMIG amount must be positive")

        # Validate effective_date
        effective_date = data.get('effective_date')
        if not effective_date:
            logger.warning("[SMIG] Missing effective_date")
            raise ValidationError("effective_date is required")

        # Check if rate already exists for this date
        if SMIGConfiguration.objects.filter(effective_date=effective_date).exists():
            logger.warning("[SMIG] Rate already exists for this date", extra={"date": effective_date})
            raise ValidationError(f"SMIG rate already exists for {effective_date}")

        # Create SMIG rate
        smig = SMIGConfiguration.objects.create(**data)

        logger.info(
            "[SMIG] SMIG rate created",
            extra={"effective_date": effective_date, "amount": amount}
        )
        return smig

    @classmethod
    @transaction.atomic
    def update_smig_rate(cls, smig_id: UUID, data: Dict[str, Any], actor=None) -> SMIGConfiguration:
        """ Updates an existing SMIG rate entry. """
        logger.debug("[SMIG] Updating SMIG rate", extra={"smig_id": smig_id})

        smig = SMIGConfiguration.objects.get(id=smig_id)

        # Validate amount if provided
        if 'amount' in data:
            amount = Decimal(str(data['amount']))
            if amount <= 0:
                raise ValidationError("SMIG amount must be positive")

        # Update fields
        for key, value in data.items():
            if hasattr(smig, key) and value is not None:
                setattr(smig, key, value)

        smig.save()
        logger.info("[SMIG] SMIG rate updated", extra={"smig_id": smig_id})
        return smig

    # ===== SOCIAL CONTRIBUTION RATES =====

    @classmethod
    @transaction.atomic
    def create_contribution_rate(cls, data: Dict[str, Any], actor=None) -> SocialContributionRate:
        """ Creates a new statutory social contribution rate (CNSS, ONEM, INPP). """
        logger.debug("[Contributions] Creating contribution rate", extra={"data": data})

        # Validate percentage rates
        employee_rate = Decimal(str(data.get('employee_rate', 0)))
        employer_rate = Decimal(str(data.get('employer_rate', 0)))

        if employee_rate < 0 or employer_rate < 0:
            logger.warning("[Contributions] Invalid rates", extra={"employee": employee_rate, "employer": employer_rate})
            raise ValidationError("Rates must be non-negative")

        if employee_rate > 100 or employer_rate > 100:
            logger.warning("[Contributions] Rates exceed 100%")
            raise ValidationError("Rates cannot exceed 100%")

        # Check if type already exists
        contribution_type = data.get('contribution_type')
        if SocialContributionRate.objects.filter(contribution_type=contribution_type).exists():
            logger.warning(
                "[Contributions] Type already exists",
                extra={"type": contribution_type}
            )
            raise ValidationError(f"Contribution type {contribution_type} already exists")

        # Create rate
        rate = SocialContributionRate.objects.create(**data)

        logger.info(
            "[Contributions] Rate created",
            extra={"type": contribution_type, "employee": employee_rate, "employer": employer_rate}
        )
        return rate


    @classmethod
    @transaction.atomic
    def update_contribution_rate(cls, rate_id: UUID, data: Dict[str, Any], actor=None) -> SocialContributionRate:
        """ Updates an existing social contribution rate. """
        logger.debug("[Contributions] Updating contribution rate", extra={"rate_id": rate_id})

        rate = SocialContributionRate.objects.get(id=rate_id)

        # Validate rates if provided
        if 'employee_rate' in data:
            emp_rate = Decimal(str(data['employee_rate']))
            if emp_rate < 0 or emp_rate > 100:
                raise ValidationError("Employee rate must be between 0 and 100")

        if 'employer_rate' in data:
            emp_rate = Decimal(str(data['employer_rate']))
            if emp_rate < 0 or emp_rate > 100:
                raise ValidationError("Employer rate must be between 0 and 100")

        # Update fields
        for key, value in data.items():
            if hasattr(rate, key) and value is not None:
                setattr(rate, key, value)

        rate.save()
        logger.info("[Contributions] Rate updated", extra={"rate_id": rate_id})
        return rate

    # ===== OVERTIME RULES =====

    @classmethod
    @transaction.atomic
    def create_overtime_rule(cls, data: Dict[str, Any], actor=None) -> OvertimeRule:
        """ Creates a new rule for calculating overtime multipliers. """
        logger.debug("[Overtime] Creating overtime rule", extra={"data": data})

        # Validate multiplier
        multiplier = Decimal(str(data.get('multiplier', 1)))
        if multiplier < 1:
            logger.warning("[Overtime] Invalid multiplier", extra={"multiplier": multiplier})
            raise ValidationError("Multiplier must be >= 1.0")

        # Validate starting_hour
        starting_hour = int(data.get('starting_hour', 0))
        if starting_hour < 0:
            logger.warning("[Overtime] Invalid starting_hour", extra={"hour": starting_hour})
            raise ValidationError("starting_hour must be non-negative")

        # Create rule
        rule = OvertimeRule.objects.create(**data)

        logger.info(
            "[Overtime] Rule created",
            extra={"type": data.get('rule_type'), "hour": starting_hour, "multiplier": multiplier}
        )
        return rule
    

    @classmethod
    @transaction.atomic
    def update_overtime_rule(cls, rule_id: UUID, data: Dict[str, Any], actor=None) -> OvertimeRule:
        """ Updates an existing overtime rule. """
        logger.debug("[Overtime] Updating overtime rule", extra={"rule_id": rule_id})

        rule = OvertimeRule.objects.get(id=rule_id)

        # Validate multiplier if provided
        if 'multiplier' in data:
            multiplier = Decimal(str(data['multiplier']))
            if multiplier < 1:
                raise ValidationError("Multiplier must be >= 1.0")

        if 'starting_hour' in data:
            hour = int(data['starting_hour'])
            if hour < 0:
                raise ValidationError("starting_hour must be non-negative")

        # Update fields
        for key, value in data.items():
            if hasattr(rule, key) and value is not None:
                setattr(rule, key, value)

        rule.save()
        
        # Clear overtime rules cache
        PayrollCacheService.clear_overtime_cache()
        
        logger.info("[Overtime] Rule updated and cache cleared", extra={"rule_id": rule_id})
        return rule
    

    # ===== TAX BRACKETS =====

    @classmethod
    @transaction.atomic
    def create_tax_bracket(cls, data: Dict[str, Any], actor=None) -> TaxBracket:
        """ Creates a new tax bracket for progressive income tax (IPR) calculations. """
        logger.debug("[Taxes] Creating tax bracket", extra={"data": data})

        # Validate amounts
        min_amount = Decimal(str(data.get('min_amount', 0)))
        max_amount = Decimal(str(data.get('max_amount', 0)))
        tax_rate = Decimal(str(data.get('tax_rate', 0)))

        if min_amount < 0 or max_amount < 0:
            logger.warning("[Taxes] Invalid amounts")
            raise ValidationError("Amounts must be non-negative")

        if min_amount >= max_amount:
            logger.warning("[Taxes] min_amount >= max_amount")
            raise ValidationError("min_amount must be less than max_amount")

        if tax_rate < 0 or tax_rate > 100:
            logger.warning("[Taxes] Invalid tax_rate", extra={"rate": tax_rate})
            raise ValidationError("Tax rate must be between 0 and 100")

        # Check for overlapping brackets
        fiscal_year = data.get('fiscal_year')
        overlapping = TaxBracket.objects.filter(
            fiscal_year=fiscal_year,
            min_amount__lt=max_amount,
            max_amount__gt=min_amount,
        )
        if overlapping.exists():
            logger.warning("[Taxes] Overlapping bracket exists")
            raise ValidationError("This bracket overlaps with existing brackets")

        # Create bracket
        bracket = TaxBracket.objects.create(**data)

        logger.info(
            "[Taxes] Bracket created",
            extra={"fiscal_year": fiscal_year, "min": min_amount, "max": max_amount, "rate": tax_rate}
        )
        return bracket

    @classmethod
    @transaction.atomic
    def update_tax_bracket(cls, bracket_id: UUID, data: Dict[str, Any], actor=None) -> TaxBracket:
        """ Updates an existing tax bracket configuration. """
        logger.debug("[Taxes] Updating tax bracket", extra={"bracket_id": bracket_id})

        bracket = TaxBracket.objects.get(id=bracket_id)

        # Validate amounts if provided
        if 'min_amount' in data or 'max_amount' in data:
            min_amt = Decimal(str(data.get('min_amount', bracket.min_amount)))
            max_amt = Decimal(str(data.get('max_amount', bracket.max_amount)))

            if min_amt >= max_amt:
                raise ValidationError("min_amount must be less than max_amount")

        if 'tax_rate' in data:
            rate = Decimal(str(data['tax_rate']))
            if rate < 0 or rate > 100:
                raise ValidationError("Tax rate must be between 0 and 100")

        # Update fields
        for key, value in data.items():
            if hasattr(bracket, key) and value is not None:
                setattr(bracket, key, value)

        bracket.save()
        logger.info("[Taxes] Bracket updated", extra={"bracket_id": bracket_id})
        return bracket

    # ===== LEGAL ALLOWANCES =====

    @classmethod
    @transaction.atomic
    def create_allowance(cls, data: Dict[str, Any], actor=None) -> LegalAllowance:
        """ Creates a new statutory allowance (Family, Housing, Transport). """
        logger.debug("[Allowances] Creating allowance", extra={"data": data})

        # Validate amount
        amount = Decimal(str(data.get('base_amount', 0)))
        if amount < 0:
            logger.warning("[Allowances] Invalid amount")
            raise ValidationError("Allowance amount must be non-negative")

        if data.get('calculation_method') == 'PERCENTAGE' and amount > 100:
            logger.warning("[Allowances] Percentage > 100%")
            raise ValidationError("Percentage cannot exceed 100")

        # Check if type already exists
        allowance_type = data.get('allowance_type')
        if LegalAllowance.objects.filter(allowance_type=allowance_type).exists():
            logger.warning("[Allowances] Type already exists", extra={"type": allowance_type})
            raise ValidationError(f"Allowance type {allowance_type} already exists")

        # Create allowance
        allowance = LegalAllowance.objects.create(**data)

        logger.info(
            "[Allowances] Allowance created",
            extra={"type": allowance_type, "amount": amount, "method": data.get('calculation_method')}
        )
        return allowance

    @classmethod
    @transaction.atomic
    def update_allowance(cls, allowance_id: UUID, data: Dict[str, Any], actor=None) -> LegalAllowance:
        """ Updates an existing statutory allowance configuration. """
        logger.debug("[Allowances] Updating allowance", extra={"allowance_id": allowance_id})

        allowance = LegalAllowance.objects.get(id=allowance_id)

        # Validate amount if provided
        if 'base_amount' in data:
            amount = Decimal(str(data['base_amount']))
            if amount < 0:
                raise ValidationError("Allowance amount must be non-negative")

            if allowance.calculation_mode == 'PERCENTAGE' and amount > 100:
                raise ValidationError("Percentage cannot exceed 100")

        # Update fields
        for key, value in data.items():
            if hasattr(allowance, key) and value is not None:
                setattr(allowance, key, value)

        allowance.save()
        
        # Invalidate cache
        PayrollCacheService.clear_allowance_cache()
        
        logger.info("[Allowances] Allowance updated and cache cleared", extra={"allowance_id": allowance_id})
        return allowance

