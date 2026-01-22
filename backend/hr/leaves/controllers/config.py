from typing import List
from uuid import UUID
from ninja import Query
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
from injector import inject
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


@api_controller('/config', tags=['Leave Configuration'])
class LeaveConfigController(ControllerBase):

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
        """
        Initialize default leave configuration:
        - Leave policies
        - Seniority rules
        - Circumstance rules
        - Public holidays

        This operation is idempotent and safe to call multiple times.
        """
        self.initializer_service.initialize_defaults()
        return 204, None

    # --- Leave Policies ---

    @http_get('/policies', response=List[LeavePolicyOut])
    @paginate(CursorPagination)
    def list_policies(self):
        """List all leave policies."""
        return self.policy_service.list()

    @http_post('/policies', response={201: LeavePolicyOut})
    def create_policy(self, data: LeavePolicyCreate):
        """Create a new leave policy (e.g. DRC Policy, Expatriate Policy)."""
        return 201, self.policy_service.create(data=data.model_dump())

    @http_patch('/policies/{policy_id}', response=LeavePolicyOut)
    def update_policy(self, policy_id: UUID, data: LeavePolicyUpdate):
        """Partially update a leave policy using BaseCRUDService."""
        instance = self.policy_service.get(id=policy_id)
        return self.policy_service.update(
            instance=instance, 
            data=data.model_dump(exclude_unset=True)
        )

    # --- Seniority Rules ---
    
    @http_get('/policies/{policy_id}/seniority-rules', response=List[SeniorityRuleOut])
    @paginate(CursorPagination)
    def list_seniority_rules(self, policy_id: UUID, filters: SeniorityRuleFilter = Query(...)):
        """List seniority rules for a specific leave policy."""
        qs = self.seniority_service.list(policy_id=policy_id)
        return filters.filter(qs)

    @http_post('/policies/{policy_id}/seniority-rules', response={201: SeniorityRuleOut})
    def create_seniority_rule(self, policy_id: UUID, data: SeniorityRuleCreate):
        """Create a seniority rule linked to the policy specified in the URL."""
        return 201, self.seniority_service.create(
            data=data.model_dump(),
            policy_id=policy_id
        )

    @http_patch('/seniority-rules/{rule_id}', response=SeniorityRuleOut)
    def update_seniority_rule(self, rule_id: UUID, data: SeniorityRuleUpdate):
        """Partially update a seniority rule."""
        instance = self.seniority_service.get(id=rule_id)
        return self.seniority_service.update(
            instance=instance,
            data=data.model_dump(exclude_unset=True)
        )

    @http_delete('/seniority-rules/{rule_id}', response={204: None})
    def delete_seniority_rule(self, rule_id: UUID):
        """Delete a seniority rule."""
        instance = self.seniority_service.get(id=rule_id)
        self.seniority_service.delete(instance=instance)
        return 204, None

    # --- Circumstance Rules ---

    @http_get('/policies/{policy_id}/circumstance-rules', response=List[CircumstanceLeaveRuleOut])
    @paginate(CursorPagination)
    def list_circumstance_rules(
        self,
        policy_id: UUID,
        filters: CircumstanceLeaveRuleFilter = Query(...)
    ):
        """List circumstance leave rules for a specific policy."""
        qs = self.circumstance_service.list(policy_id=policy_id)
        return filters.filter(qs)

    @http_post('/policies/{policy_id}/circumstance-rules', response={201: CircumstanceLeaveRuleOut})
    def create_circumstance_rule(
        self,
        policy_id: UUID,
        data: CircumstanceLeaveRuleCreate
    ):
        """Define a new circumstance rule (e.g. Marriage) for this policy."""
        return 201, self.circumstance_service.create(
            data=data.model_dump(),
            policy_id=policy_id
        )

    @http_patch('/circumstance-rules/{rule_id}', response=CircumstanceLeaveRuleOut)
    def update_circumstance_rule(self, rule_id: UUID, data: CircumstanceLeaveRuleUpdate):
        """Partially update a circumstance rule."""
        instance = self.circumstance_service.get(id=rule_id)
        return self.circumstance_service.update(
            instance=instance,
            data=data.model_dump(exclude_unset=True)
        )

    @http_delete('/circumstance-rules/{rule_id}', response={204: None})
    def delete_circumstance_rule(self, rule_id: UUID):
        """Delete a circumstance rule."""
        instance = self.circumstance_service.get(id=rule_id)
        self.circumstance_service.delete(instance=instance)
        return 204, None

