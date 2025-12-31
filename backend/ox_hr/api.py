from ninja_extra import NinjaExtraAPI
from hr.employees.api import get_all_employee_api
from oxutils.jwt.auth import get_auth_handlers, basic_no_password_auth
from oxutils.permissions.controllers import PermissionController
from oxutils.oxiliere.controllers import SetupController





api = NinjaExtraAPI(
    title="Oxiliere HR API",
    description="API for Oxiliere HR",
    version="1.0.0",
    auth=get_auth_handlers([basic_no_password_auth]),
)



api.register_controllers(
    SetupController,
    PermissionController,
    *get_all_employee_api(),
)
