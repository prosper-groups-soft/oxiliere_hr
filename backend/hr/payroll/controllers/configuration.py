"""
PAYROLL CONFIGURATION CONTROLLER

Manages payroll system configuration:
- Global payroll settings
- SMIG rates
- Social contribution rates
- Overtime rules
- Tax brackets
- Legal allowances
"""

import logging
from typing import List
from uuid import UUID
from injector import inject

from django.core.exceptions import ValidationError
from ninja import Query
from ninja.pagination import paginate
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    ControllerBase,
)
from oxutils.pagination.cursor import CursorPagination

from hr.payroll.models import (
    PayrollConfiguration,
    SMIGConfiguration,
    SocialContributionRate,
    OvertimeRule,
    TaxBracket,
    LegalAllowance,
)

from hr.payroll.schemas import (
    # Configuration
    PayrollConfigurationOut,
    ConfigurePayrollIn,
    PayrollConfigurationUpdateIn,
    # SMIG
    SMIGConfigurationCreateIn,
    SMIGConfigurationOut,
    SMIGConfigurationUpdateIn,
    SMIGConfigurationListFilterIn,
    # Social Contributions
    SocialContributionRateCreateIn,
    SocialContributionRateOut,
    SocialContributionRateUpdateIn,
    SocialContributionRateListFilterIn,
    # Overtime Rules
    OvertimeRuleCreateIn,
    OvertimeRuleOut,
    OvertimeRuleUpdateIn,
    OvertimeRuleListFilterIn,
    # Tax Brackets
    TaxBracketCreateIn,
    TaxBracketOut,
    TaxBracketUpdateIn,
    TaxBracketListFilterIn,
    # Legal Allowances
    LegalAllowanceCreateIn,
    LegalAllowanceOut,
    LegalAllowanceUpdateIn,
    LegalAllowanceListFilterIn,
)

from hr.payroll.services.integration.configuration import ConfigurationService


logger = logging.getLogger(__name__)


@api_controller('/payroll/configuration', tags=['Payroll Configuration'])
class PayrollConfigurationController(ControllerBase):
    """
    Configuration management for the payroll system.
    
    Responsibilities:
    - Global payroll settings (currency, payment method, work hours)
    - SMIG rates management
    - Social contribution rates
    - Overtime rules
    - Tax brackets
    - Legal allowances
    """

    @inject
    def __init__(self, config_service: ConfigurationService):
        self.config_service = config_service

    # ===== PAYROLL CONFIGURATION =====

    @http_get('/', response=PayrollConfigurationOut)
    def get_configuration(self):
        """
        Retrieve global payroll configuration (singleton pattern).
        
        Returns the current payroll settings for the entire system.
        """
        logger.debug("[Payroll Config] Retrieving global configuration")

        config = PayrollConfiguration.objects.first()
        if not config:
            logger.warning("[Payroll Config] No configuration found (create one)")
            return self.create_response(
                {"detail": "Payroll configuration not initialized"},
                status_code=404,
            )

        return config

    @http_post('/', response={201: PayrollConfigurationOut})
    def create_configuration(self, data: ConfigurePayrollIn):
        """
        Create global payroll configuration (should be called once).
        
        This initializes the system with default settings.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Payroll Config] Creating global configuration", extra={"actor": actor})

        try:
            config = self.config_service.create_configuration(
                data=data.model_dump(),
                actor=actor,
            )
            logger.info("[Payroll Config] Configuration created successfully")
            return 201, config

        except ValidationError as e:
            logger.warning("[Payroll Config] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/', response=PayrollConfigurationOut)
    def update_configuration(self, data: PayrollConfigurationUpdateIn):
        """
        Update global payroll configuration.
        
        Allows modifying system-wide settings like currency, payment method, etc.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Payroll Config] Updating configuration", extra={"actor": actor})

        try:
            config = self.config_service.update_configuration(
                data=data.model_dump(exclude_unset=True),
                actor=actor,
            )
            logger.info("[Payroll Config] Configuration updated successfully")
            return config

        except ValidationError as e:
            logger.warning("[Payroll Config] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== SMIG RATES =====

    @http_get('/smig/', response=List[SMIGConfigurationOut])
    @paginate(CursorPagination)
    def list_smig_rates(self, filters: SMIGConfigurationListFilterIn = Query(...)):
        """
        List all SMIG (minimum wage) configurations with history.
        
        Returns all past and current minimum wage settings.
        """
        logger.debug("[SMIG] Listing SMIG rates", extra={"filters": filters.model_dump()})

        qs = SMIGConfiguration.objects.all().order_by('-effective_date')
        return filters.filter(qs)

    @http_post('/smig/', response={201: SMIGConfigurationOut})
    def create_smig_rate(self, data: SMIGConfigurationCreateIn):
        """
        Create a new SMIG (minimum wage) rate.
        
        Used when minimum wage changes occur.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[SMIG] Creating new SMIG rate", extra={"actor": actor})

        try:
            smig = self.config_service.create_smig_rate(
                data=data.model_dump(),
                actor=actor,
            )
            logger.info("[SMIG] SMIG rate created", extra={"effective_date": smig.effective_date})
            return 201, smig

        except ValidationError as e:
            logger.warning("[SMIG] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/smig/{smig_id}', response=SMIGConfigurationOut)
    def update_smig_rate(self, smig_id: UUID, data: SMIGConfigurationUpdateIn):
        """
        Update an existing SMIG rate.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[SMIG] Updating SMIG rate", extra={"smig_id": smig_id, "actor": actor})

        try:
            smig = self.config_service.update_smig_rate(
                smig_id=smig_id,
                data=data.model_dump(exclude_unset=True),
                actor=actor,
            )
            return smig

        except ValidationError as e:
            logger.warning("[SMIG] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== SOCIAL CONTRIBUTION RATES =====

    @http_get('/contributions/', response=List[SocialContributionRateOut])
    @paginate(CursorPagination)
    def list_contribution_rates(self, filters: SocialContributionRateListFilterIn = Query(...)):
        """
        List all social contribution rates (CNSS, ONEM, INPP, etc.).
        
        Returns current rates for each contribution type.
        """
        logger.debug("[Contributions] Listing contribution rates", extra={"filters": filters.model_dump()})

        qs = SocialContributionRate.objects.all().order_by('contribution_type')
        return filters.filter(qs)

    @http_post('/contributions/', response={201: SocialContributionRateOut})
    def create_contribution_rate(self, data: SocialContributionRateCreateIn):
        """
        Create a new social contribution rate.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Contributions] Creating contribution rate", extra={"actor": actor})

        try:
            rate = self.config_service.create_contribution_rate(
                data=data.model_dump(),
                actor=actor,
            )
            logger.info("[Contributions] Contribution rate created")
            return 201, rate

        except ValidationError as e:
            logger.warning("[Contributions] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/contributions/{rate_id}', response=SocialContributionRateOut)
    def update_contribution_rate(self, rate_id: UUID, data: SocialContributionRateUpdateIn):
        """
        Update an existing social contribution rate.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Contributions] Updating contribution rate", extra={"rate_id": rate_id})

        try:
            rate = self.config_service.update_contribution_rate(
                rate_id=rate_id,
                data=data.model_dump(exclude_unset=True),
                actor=actor,
            )
            return rate

        except ValidationError as e:
            logger.warning("[Contributions] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== OVERTIME RULES =====

    @http_get('/overtime/', response=List[OvertimeRuleOut])
    def list_overtime_rules(self, filters: OvertimeRuleListFilterIn = Query(...)):
        """
        List all overtime rules (multipliers by hour count or holiday status).
        
        Example: First 2 hours = 130%, subsequent = 160%, holidays = 200%.
        """
        logger.debug("[Overtime] Listing overtime rules", extra={"filters": filters.model_dump()})

        qs = OvertimeRule.objects.all().order_by('rule_type', 'starting_hour')
        return filters.filter(qs)

    @http_post('/overtime/', response={201: OvertimeRuleOut})
    def create_overtime_rule(self, data: OvertimeRuleCreateIn):
        """
        Create a new overtime rule.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Overtime] Creating overtime rule", extra={"actor": actor})

        try:
            rule = self.config_service.create_overtime_rule(
                data=data.model_dump(),
                actor=actor,
            )
            logger.info("[Overtime] Overtime rule created")
            return 201, rule

        except ValidationError as e:
            logger.warning("[Overtime] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/overtime/{rule_id}', response=OvertimeRuleOut)
    def update_overtime_rule(self, rule_id: UUID, data: OvertimeRuleUpdateIn):
        """
        Update an existing overtime rule.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Overtime] Updating overtime rule", extra={"rule_id": rule_id})

        try:
            rule = self.config_service.update_overtime_rule(
                rule_id=rule_id,
                data=data.model_dump(exclude_unset=True),
                actor=actor,
            )
            return rule

        except ValidationError as e:
            logger.warning("[Overtime] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== TAX BRACKETS =====

    @http_get('/taxes/', response=List[TaxBracketOut])
    def list_tax_brackets(self, filters: TaxBracketListFilterIn = Query(...)):
        """
        List all tax brackets for progressive IPR calculation.
        
        Returns brackets for the current fiscal year.
        """
        logger.debug("[Taxes] Listing tax brackets", extra={"filters": filters.model_dump()})

        qs = TaxBracket.objects.all().order_by('fiscal_year', 'min_amount')
        return filters.filter(qs)

    @http_post('/taxes/', response={201: TaxBracketOut})
    def create_tax_bracket(self, data: TaxBracketCreateIn):
        """
        Create a new tax bracket.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Taxes] Creating tax bracket", extra={"actor": actor})

        try:
            bracket = self.config_service.create_tax_bracket(
                data=data.model_dump(),
                actor=actor,
            )
            logger.info("[Taxes] Tax bracket created")
            return 201, bracket

        except ValidationError as e:
            logger.warning("[Taxes] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/taxes/{bracket_id}', response=TaxBracketOut)
    def update_tax_bracket(self, bracket_id: UUID, data: TaxBracketUpdateIn):
        """
        Update an existing tax bracket.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Taxes] Updating tax bracket", extra={"bracket_id": bracket_id})

        try:
            bracket = self.config_service.update_tax_bracket(
                bracket_id=bracket_id,
                data=data.model_dump(exclude_unset=True),
                actor=actor,
            )
            return bracket

        except ValidationError as e:
            logger.warning("[Taxes] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== LEGAL ALLOWANCES =====

    @http_get('/allowances/', response=List[LegalAllowanceOut])
    def list_allowances(self, filters: LegalAllowanceListFilterIn = Query(...)):
        """
        List all legal allowances (family, housing, transport, etc.).
        
        Returns current allowance configurations.
        """
        logger.debug("[Allowances] Listing legal allowances", extra={"filters": filters.model_dump()})

        qs = LegalAllowance.objects.all().order_by('allowance_type')
        return filters.filter(qs)

    @http_post('/allowances/', response={201: LegalAllowanceOut})
    def create_allowance(self, data: LegalAllowanceCreateIn):
        """
        Create a new legal allowance.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Allowances] Creating allowance", extra={"actor": actor})

        try:
            allowance = self.config_service.create_allowance(
                data=data.model_dump(),
                actor=actor,
            )
            logger.info("[Allowances] Allowance created")
            return 201, allowance

        except ValidationError as e:
            logger.warning("[Allowances] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/allowances/{allowance_id}', response=LegalAllowanceOut)
    def update_allowance(self, allowance_id: UUID, data: LegalAllowanceUpdateIn):
        """
        Update an existing legal allowance.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Allowances] Updating allowance", extra={"allowance_id": allowance_id})

        try:
            allowance = self.config_service.update_allowance(
                allowance_id=allowance_id,
                data=data.model_dump(exclude_unset=True),
                actor=actor,
            )
            return allowance

        except ValidationError as e:
            logger.warning("[Allowances] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)
