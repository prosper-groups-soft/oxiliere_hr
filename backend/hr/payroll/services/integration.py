from decimal                           import Decimal
from datetime                          import date
from hr.employees.services.family      import EmployeeFamilyService
from hr.attendance.services.summary    import AttendanceSummaryService
from hr.attendance.services.scheduling import SchedulingService
from hr.leaves.services.leave          import LeaveRequestService
from hr.employees.models               import Employee


class PayrollIntegrationService:
    """
    Bridge service to fetch data from other modules (Attendance, Employee).
    Calls internal services of these modules to respect modular decoupling.
    """

    @classmethod
    def get_worked_days_data(cls, employee_id, start_date: date, end_date: date):
        """
        Fetches attendance data for the period using AttendanceSummaryService.
        """
        summary = AttendanceSummaryService.get_attendance_summary(
            employee_id=employee_id, 
            start_date=start_date, 
            end_date=end_date
        )
        
        return {
            'regular_days': summary['regular_days'],
            'total_worked_hours': summary['total_worked_hours'],
            'overtime_hours_standard': summary['overtime_hours_standard'],
            'overtime_hours_holiday': summary['overtime_hours_holiday'],
            'absence_days': summary['absence_days']
        }

    @classmethod
    def get_employee_family_data(cls, employee_id):
        """
        Fetches dependent child count using EmployeeFamilyService.
        """
        count = EmployeeFamilyService.get_dependent_count(employee_id)
        return {
            'child_count': count
        }

    @classmethod
    def get_employee_leave_data(cls, employee_id, start_date: date, end_date: date):
        """
        Fetches leave history for the period using LeaveRequestService.
        """
        employee = Employee.objects.get(id=employee_id)
        leaves = LeaveRequestService.get_leaves_for_period(employee, start_date, end_date)
        
        return {
            'paid_leave_days': leaves['paid_days'],
            'unpaid_leave_days': leaves['unpaid_days']
        }

    @classmethod
    def get_theoretical_working_days(cls, employee_id, start_date: date, end_date: date):
        """
        Calculates the theoretical number of working days based on the employee's schedule.
        """
        employee = Employee.objects.get(id=employee_id)
        days = SchedulingService.count_working_days_for_employee(employee, start_date, end_date)
        return Decimal(str(days))

