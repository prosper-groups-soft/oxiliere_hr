from ninja_extra      import NinjaExtraAPI
from django.core.exceptions import ValidationError
from oxutils.jwt.auth import get_auth_handlers, basic_no_password_auth
from oxutils.permissions.controllers import PermissionController
from oxutils.oxiliere.controllers    import UserController
from core.controllers.access_extensions import AccessExtensionController

from hr.employees.controllers  import get_all_ctrls_employees
from hr.leaves.controllers     import get_all_ctrls_leaves
from hr.attendance.controllers import get_all_ctrls_attendance
from hr.jobs.controllers       import get_all_ctrls_jobs
from hr.banking.controllers    import get_all_ctrls_banking
from hr.recruitment.controllers import get_all_ctrls_recruitment
from hr.calendar.controllers    import get_all_ctrls_calendar
from hr.payroll.controllers     import get_all_ctrls_payroll
from hr.performance.controllers import get_all_ctrls_performance


api = NinjaExtraAPI(
    title="Oxiliere - HR System API",
    description="Human Resources Management System",
    version="1.0.0",
    auth=get_auth_handlers([basic_no_password_auth])
)


# Global exception handler for ValidationErrors from Signals
@api.exception_handler(ValidationError)
def validation_error_handler(request, exc):
    message = str(exc.messages[0]) if hasattr(exc, 'messages') and exc.messages else str(exc)
    return api.create_response(request, {"detail": message}, status=400)


# Regidter Controllers
api.register_controllers(
    UserController,
    PermissionController,
    AccessExtensionController,
    *get_all_ctrls_employees(),   # Employees Module
    *get_all_ctrls_leaves(),      # Leaves Module
    *get_all_ctrls_attendance(),  # Attendance Module
    *get_all_ctrls_jobs(),        # Jobs Module
    *get_all_ctrls_recruitment(), # Recruitment Module
    *get_all_ctrls_banking(),     # Banking Module 
    *get_all_ctrls_calendar(),    # Calendar Module
    *get_all_ctrls_payroll(),     # Payroll Module
    *get_all_ctrls_performance(), # Performance Module
)

