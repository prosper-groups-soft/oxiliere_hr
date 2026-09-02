import logging
from typing   import List
from uuid     import UUID
from injector import inject

from django.core.exceptions import ValidationError
from ninja import Query
from ninja.pagination import paginate
from ninja_extra      import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    ControllerBase,
)
from ninja_extra.pagination import (
    paginate,
    PageNumberPaginationExtra,
    PaginatedResponseSchema
)
from oxutils.permissions.perms import ScopePermission

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

from hr.payroll.services import (
    ConfigurationService, 
    PayrollInitService
)
# Cache integration
from hr.services.cache_helpers import cache_api_response
from hr.payroll.services.cache import PayrollCacheService
from hr.payroll.services.integration.exchange import ExchangeRateService


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
    def __init__(
        self, 
        config_service: ConfigurationService, 
        init_service: PayrollInitService
    ):
        self.config_service = config_service
        self.init_service = init_service

    # ===== PAYROLL CONFIGURATION =====

    @http_get('/', response=PayrollConfigurationOut, permissions=[ScopePermission('payroll:r')])
    def get_configuration(self):
        """
        Retrieve global payroll configuration (singleton pattern).
        Returns the current payroll settings for the entire system.
        Auto-initializes from fixture if not exists.
        """
        logger.debug("[Payroll Config] Retrieving global configuration")

        # Try to get cached config first
        config = PayrollCacheService.get_configuration()

        if not config:
            logger.warning("[Payroll Config] No configuration found, initializing from fixture...")
            try:
                # Initialize from fixture
                summary = self.init_service.init_payroll_configurations()
                logger.info(f"[Payroll Config] Auto-initialized: {summary}")

                # Retry getting the config (from DB, not cache)
                config = PayrollConfiguration.objects.first()
                if not config:
                    logger.error("[Payroll Config] Failed to auto-initialize")
                    return self.create_response(
                        {"detail": "Failed to initialize payroll configuration"},
                        status_code=500,
                    )
            except Exception as e:
                logger.error(f"[Payroll Config] Error auto-initializing: {str(e)}")
                return self.create_response(
                    {"detail": f"Error initializing payroll configuration: {str(e)}"},
                    status_code=500,
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

    @http_patch('/', response=PayrollConfigurationOut, permissions=[ScopePermission('payroll:a')])
    def update_config(self, data: PayrollConfigurationUpdateIn):
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
            return config

        except ValidationError as e:
            logger.warning("[Payroll Config] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== SMIG RATES =====

    @http_get('/smig/', response=PaginatedResponseSchema[SMIGConfigurationOut], permissions=[ScopePermission('payroll:r')])
    @paginate(PageNumberPaginationExtra, page_size=50)
    @cache_api_response(timeout=60*60*24, key_prefix="smig_rates_list", user_specific=False)
    def list_smig_rates(self, filters: SMIGConfigurationListFilterIn = Query(...)):
        """
        List all SMIG (minimum wage) configurations with history.
        Returns all past and current minimum wage settings.
        """
        logger.debug("[SMIG] Listing SMIG rates", extra={"filters": filters.model_dump()})

        qs = SMIGConfiguration.objects.all().order_by('-effective_date')
        return filters.filter(qs)

    @http_post('/smig/', response={201: SMIGConfigurationOut}, permissions=[ScopePermission('payroll:w')])
    def create_smig_config(self, data: SMIGConfigurationCreateIn):
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

    @http_patch('/smig/{smig_id}', response=SMIGConfigurationOut, permissions=[ScopePermission('payroll:u')])
    def update_smig_config(self, smig_id: UUID, data: SMIGConfigurationUpdateIn):
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

    @http_get('/contributions/', response=PaginatedResponseSchema[SocialContributionRateOut], permissions=[ScopePermission('payroll:r')])
    @paginate(PageNumberPaginationExtra, page_size=50)
    @cache_api_response(timeout=60*60*24, key_prefix="social_contribution_rates_list", user_specific=False)
    def list_contribution_rates(self, filters: SocialContributionRateListFilterIn = Query(...)):
        """
        List all social contribution rates (CNSS, ONEM, INPP, etc.).
        Returns current rates for each contribution type.
        """
        logger.debug("[Contributions] Listing contribution rates", extra={"filters": filters.model_dump()})

        qs = SocialContributionRate.objects.all().order_by('contribution_type')
        return filters.filter(qs)

    @http_post('/social-rates/', response={201: SocialContributionRateOut}, permissions=[ScopePermission('payroll:w')])
    def create_social_rate(self, data: SocialContributionRateCreateIn):
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

    @http_patch('/social-rates/{rate_id}', response=SocialContributionRateOut, permissions=[ScopePermission('payroll:u')])
    def update_social_rate(self, rate_id: UUID, data: SocialContributionRateUpdateIn):
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

    @http_get('/overtime/', response=List[OvertimeRuleOut], permissions=[ScopePermission('payroll:r')])
    @cache_api_response(timeout=60*60*24, key_prefix="overtime_rules", user_specific=False)
    def list_overtime_rules(self, filters: OvertimeRuleListFilterIn = Query(...)):
        """
        List all overtime rules (multipliers by hour count or holiday status).
        Example: First 2 hours = 130%, subsequent = 160%, holidays = 200%.
        """
        logger.debug("[Overtime] Listing overtime rules", extra={"filters": filters.model_dump()})

        qs = OvertimeRule.objects.all().order_by('rule_type', 'multiplier')
        return filters.filter(qs)

    @http_post('/overtime/', response={201: OvertimeRuleOut}, permissions=[ScopePermission('payroll:w')])
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

    @http_patch('/overtime/{rule_id}', response=OvertimeRuleOut, permissions=[ScopePermission('payroll:u')])
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

    @http_get('/tax-brackets/', response=List[TaxBracketOut], permissions=[ScopePermission('payroll:r')])
    @cache_api_response(timeout=60*60*24, key_prefix="tax_brackets", user_specific=False)
    def list_tax_brackets(self, filters: TaxBracketListFilterIn = Query(...)):
        """
        List all tax brackets for progressive IPR calculation.
        Returns brackets for the current fiscal year.
        """
        logger.debug("[Taxes] Listing tax brackets", extra={"filters": filters.model_dump()})

        qs = TaxBracket.objects.all().order_by('lower_limit')
        return filters.filter(qs)

    @http_post('/tax-brackets/', response={201: TaxBracketOut}, permissions=[ScopePermission('payroll:w')])
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

    @http_patch('/tax-brackets/{bracket_id}', response=TaxBracketOut, permissions=[ScopePermission('payroll:u')])
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
    @cache_api_response(timeout=60*60*24, key_prefix="legal_allowances_list", user_specific=False)
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

    @http_post('/allowances/reset/', response={200: dict}, permissions=[ScopePermission('payroll:a')])
    def reset_allowances(self):
        """
        Réinitialise les allocations légales depuis les valeurs par défaut (fixture).
        Recharge UNIQUEMENT legal_allowances.json — ne touche pas aux autres paramètres.
        """
        logger.info("[Allowances] Resetting legal allowances from fixture")
        try:
            count = self.init_service.reset_legal_allowances()
            return {"status": "success", "reset_count": count}
        except Exception as e:
            logger.error("[Allowances] Error resetting allowances", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=500)

    @http_get('/exchange-rate/', response={200: dict}, permissions=[ScopePermission('payroll:r')])
    def get_exchange_rate(self, refresh: bool = Query(False, description='Force une re-synchronisation BCC avant la lecture')):
        """
        Retrieve the active USD → CDF exchange rate.
        Priority: live rate (BCC via oxutils.currency) → manual config → default.

        Avec `?refresh=true`, force une re-synchronisation depuis BCC avant la
        lecture (utilisé par le bouton « Recharger » de l'UI kickoff).
        """
        try:
            if refresh:
                rate, source = ExchangeRateService.get_exchange_rate_with_source_forced('USD', 'CDF')
            else:
                rate, source = ExchangeRateService.get_exchange_rate_with_source('USD', 'CDF')
            return {
                'rate': str(rate),
                'source': source,
                'currency_pair': 'USD/CDF',
            }
        except Exception as e:
            logger.error('[ExchangeRate] Error retrieving exchange rate', extra={'error': str(e)})
            return self.create_response({'detail': str(e)}, status_code=500)

    @http_post('/init/', response={200: dict})
    def init_payroll(self):
        """
        Initialize all payroll configurations.
        Should be called once to set up the system.
        """
        logger.info("[Payroll Init] Initializing payroll configurations")

        try:
            summary = self.init_service.init_payroll_configurations()
            logger.info("[Payroll Init] Payroll configurations initialized successfully")
            return {"status": "success", "summary": summary}

        except Exception as e:
            logger.error("[Payroll Init] Error initializing payroll configurations", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=500)

