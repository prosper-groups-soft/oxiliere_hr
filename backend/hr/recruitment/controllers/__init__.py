from typing       import Any
from .application import ApplicationController
from .candidate   import CandidateController
from .hiring      import HiringController
from .interview   import InterviewController
from .job_offer   import JobOfferController


def get_all_ctrls_recruitment() -> tuple[type[Any], ...]:
    return (
        ApplicationController,
        CandidateController,
        HiringController,
        InterviewController,
        JobOfferController,
    )


__all__ = [
    'ApplicationController',
    'CandidateController',
    'HiringController',
    'InterviewController',
    'JobOfferController',
]

