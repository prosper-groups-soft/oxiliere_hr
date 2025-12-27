class LeaveError(Exception):
    pass

class LeaveValidationError(LeaveError):
    pass

class LeaveOverlapError(LeaveError):
    pass

class LeaveWorkflowError(LeaveError):
    pass

class LeavePermissionError(LeaveError):
    pass
