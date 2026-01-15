from ninja_extra import NinjaExtraAPI
from oxutils.jwt.auth import get_auth_handlers, basic_no_password_auth
from oxutils.permissions.controllers import PermissionController
from oxutils.oxiliere.controllers import SetupController

from hr.employees.controllers import get_all_employees_ctrls
from hr.leaves.controllers import get_all_leaves_ctrls
from hr.attendance.controllers import get_all_attendance_ctrls
from hr.jobs.controllers import get_all_jobs_ctrls
from hr.banking.controllers import get_all_banking_ctrls
from hr.recruitment.controllers import get_all_recruitment_ctrls
from hr.calendar.controllers import get_all_calendar_ctrls


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
    *get_all_employees_ctrls(),   # Employees Module
    *get_all_leaves_ctrls(),      # Leaves Module
    *get_all_attendance_ctrls(),  # Attendance Module
    *get_all_jobs_ctrls(),        # Jobs Module
    *get_all_recruitment_ctrls(), # Recruitment Module
    *get_all_banking_ctrls(),     # Banking Module
    *get_all_calendar_ctrls()     # Calendar Module
)

