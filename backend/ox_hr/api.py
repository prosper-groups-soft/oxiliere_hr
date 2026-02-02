from ninja_extra      import NinjaExtraAPI
from oxutils.jwt.auth import get_auth_handlers, basic_no_password_auth
from oxutils.permissions.controllers import PermissionController
from oxutils.oxiliere.controllers    import SetupController

from hr.employees.controllers  import get_all_ctrls_employees
from hr.leaves.controllers     import get_all_ctrls_leaves
from hr.attendance.controllers import get_all_ctrls_attendance
from hr.jobs.controllers    import get_all_ctrls_jobs
from hr.banking.controllers import get_all_ctrls_banking
from hr.recruitment.controllers import get_all_ctrls_recruitment
from hr.calendar.controllers import get_all_ctrls_calendar
from hr.payroll.controllers  import get_all_ctrls_payroll


api = NinjaExtraAPI(
    title="Oxiliere - HR System API",
    description="Human Resources Management System",
    version="1.0.0",
    auth=get_auth_handlers([basic_no_password_auth])
)


# Regidter Controllers
api.register_controllers(
    SetupController,
    PermissionController,
    *get_all_ctrls_employees(),   # Employees Module
    *get_all_ctrls_leaves(),      # Leaves Module
    *get_all_ctrls_attendance(),  # Attendance Module
    *get_all_ctrls_jobs(),        # Jobs Module
    *get_all_ctrls_recruitment(), # Recruitment Module
    *get_all_ctrls_banking(),     # Banking Module
    *get_all_ctrls_calendar(),    # Calendar Module
    *get_all_ctrls_payroll(),     # Payroll Module
)

