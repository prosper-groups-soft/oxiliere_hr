from typing  import Any
from .dev    import DevelopmentController
from .job    import JobController
from .org    import OrganizationController
from .transition import TransitionController
from .career     import CareerController
from .vacancy    import VacancyController


def get_all_ctrls_jobs() -> tuple[type[Any], ...]:
    """
    Groups and returns all controllers associated with the recruitment 
    and career development modules for router registration.
    """
    return (
        CareerController,
        JobController,
        OrganizationController,
        DevelopmentController,
        TransitionController,
        VacancyController
    )


__all__ = [
    'CareerController',
    'JobController',
    'OrganizationController',
    'DevelopmentController',
    'TransitionController',
    'VacancyController'
]

