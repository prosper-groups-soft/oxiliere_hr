from typing  import Tuple
from .career import CareerController
from .dev    import DevelopmentController
from .job    import JobController
from .org    import OrganizationController


def get_all_jobs_ctrls() -> Tuple:
    """
    Groups and returns all controllers associated with the recruitment 
    and career development modules for router registration.
    """
    return (
        CareerController,
        JobController,
        OrganizationController,
        DevelopmentController
    )


__all__ = [
    'CareerController',
    'JobController',
    'OrganizationController',
    'DevelopmentController'
]

