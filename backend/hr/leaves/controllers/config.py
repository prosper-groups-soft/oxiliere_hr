from typing   import List
from uuid     import UUID
from ninja    import Query
from injector import inject
from ninja.pagination import paginate

from ninja_extra import (
    api_controller, 
    http_get, 
    http_post, 
    http_patch, 
    http_delete, 
    ControllerBase
)
from oxutils.pagination.cursor import CursorPagination
from oxutils.permissions.perms import ScopePermission
from hr.leaves.services import (
    LeavePolicyService,
    SeniorityRuleService,
    LeaveInitializerService,
    CircumstanceLeaveRuleService
)
from hr.leaves.schemas import (
    LeavePolicyOut, LeavePolicyCreate, LeavePolicyUpdate,
    
    SeniorityRuleOut, SeniorityRuleCreate,
    SeniorityRuleUpdate, SeniorityRuleFilter,
    
    CircumstanceLeaveRuleOut, CircumstanceLeaveRuleCreate,
    CircumstanceLeaveRuleUpdate, CircumstanceLeaveRuleFilter
)
# Cache integration
from hr.services.cache_helpers import cache_api_response


@api_controller('/config', tags=['Leave Configuration'])
class LeaveConfigController(ControllerBase):
    """ Manages the structural setup of leave policies, seniority rewards, and special leave rules. """

    @inject
    def __init__(
        self,
        policy_service: LeavePolicyService,
        seniority_service: SeniorityRuleService,
        circumstance_service: CircumstanceLeaveRuleService,
        initializer_service: LeaveInitializerService
    ):
        self.policy_service = policy_service
        self.seniority_service = seniority_service
        self.circumstance_service = circumstance_service
        self.initializer_service = initializer_service
        
    @http_post('/init-defaults', response={204: None})
    def initialize_defaults(self):
        """ Installs standard labor law policies and rules. Safe to run multiple times. """
        self.initializer_service.initialize_defaults()
        return 204, None

    # --- Leave Policies ---

    @http_get('/policies', response=List[LeavePolicyOut], permissions=[ScopePermission('leaves:r')])
    @paginate(CursorPagination)
    @cache_api_response(timeout=60*60*24*7, key_prefix="leave_policies_list", user_specific=False)
    def list_policies(self):
        """ Lists all active leave policies across different jurisdictions or categories. """
        return self.policy_service.list()

    @http_post('/policies', response={201: LeavePolicyOut}, permissions=[ScopePermission('leaves:w')])
    def create_policy(self, data: LeavePolicyCreate):
        """ Establishes a new global or localized leave policy. """
        return 201, self.policy_service.create(data=data.model_dump())

    @http_patch('/policies/{policy_id}', response=LeavePolicyOut, permissions=[ScopePermission('leaves:u')])
    def update_policy(self, policy_id: UUID, data: LeavePolicyUpdate):
        """ Updates the core parameters of an existing leave policy. """
        instance = self.policy_service.get(id=policy_id)
        return self.policy_service.update(
            instance=instance, 
            data=data.model_dump(exclude_unset=True)
        )

    # --- Seniority Rules ---
    
    @http_get('/policies/{policy_id}/seniority-rules', response=List[SeniorityRuleOut])
    @paginate(CursorPagination)
    @cache_api_response(timeout=60*60*24*7, key_prefix="seniority_rules_{policy_id}", user_specific=False)
    def list_seniority_rules(self, policy_id: UUID, filters: SeniorityRuleFilter = Query(...)):
        """ Lists bonus leave rules based on service length for a specific policy. """
        qs = self.seniority_service.list(policy_id=policy_id)
        return filters.filter(qs)

    @http_post('/policies/{policy_id}/seniority-rules', response={201: SeniorityRuleOut})
    def create_seniority_rule(self, policy_id: UUID, data: SeniorityRuleCreate):
        """ Adds a new seniority-based leave benefit to a policy. """
        return 201, self.seniority_service.create(
            data=data.model_dump(),
            policy_id=policy_id
        )

    @http_patch('/seniority-rules/{rule_id}', response=SeniorityRuleOut)
    def update_seniority_rule(self, rule_id: UUID, data: SeniorityRuleUpdate):
        """ Modifies the parameters of an existing seniority rule. """
        instance = self.seniority_service.get(id=rule_id)
        return self.seniority_service.update(
            instance=instance,
            data=data.model_dump(exclude_unset=True)
        )

    @http_delete('/seniority-rules/{rule_id}', response={204: None})
    def delete_seniority_rule(self, rule_id: UUID):
        """ Removes a seniority rule from the system. """
        instance = self.seniority_service.get(id=rule_id)
        self.seniority_service.delete(instance=instance)
        return 204, None

    # --- Circumstance Rules ---

    @http_get('/policies/{policy_id}/circumstance-rules', response=List[CircumstanceLeaveRuleOut])
    @paginate(CursorPagination)
    @cache_api_response(timeout=60*60*24*7, key_prefix="circumstance_rules_{policy_id}", user_specific=False)
    def list_circumstance_rules(
        self,
        policy_id: UUID,
        filters: CircumstanceLeaveRuleFilter = Query(...)
    ):
        """ Lists special leave entitlements (e.g., family events) for a specific policy. """
        qs = self.circumstance_service.list(policy_id=policy_id)
        return filters.filter(qs)

    @http_post('/policies/{policy_id}/circumstance-rules', response={201: CircumstanceLeaveRuleOut})
    def create_circumstance_rule(
        self,
        policy_id: UUID,
        data: CircumstanceLeaveRuleCreate
    ):
        """ Defines a new category of special leave for a specific policy. """
        return 201, self.circumstance_service.create(
            data=data.model_dump(),
            policy_id=policy_id
        )

    @http_patch('/circumstance-rules/{rule_id}', response=CircumstanceLeaveRuleOut)
    def update_circumstance_rule(self, rule_id: UUID, data: CircumstanceLeaveRuleUpdate):
        """ Updates the duration or terms of a special leave category. """
        instance = self.circumstance_service.get(id=rule_id)
        return self.circumstance_service.update(
            instance=instance,
            data=data.model_dump(exclude_unset=True)
        )

    @http_delete('/circumstance-rules/{rule_id}', response={204: None})
    def delete_circumstance_rule(self, rule_id: UUID):
        """ Removes a special leave category from the system. """
        instance = self.circumstance_service.get(id=rule_id)
        self.circumstance_service.delete(instance=instance)
        return 204, None

