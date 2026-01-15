from typing       import Tuple
from .application import ApplicationController
from .hiring      import HiringController
from .interview   import InterviewController
from .job_offer   import JobOfferController


def get_all_recruitment_ctrls() -> Tuple:
    return (
        ApplicationController,
        HiringController,
        InterviewController,
        JobOfferController
    )


__all__ = [
    'ApplicationController',
    'HiringController',
    'InterviewController',
    'JobOfferController'
]

