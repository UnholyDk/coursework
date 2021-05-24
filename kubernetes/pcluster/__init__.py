"""
Resources manager API.
"""

from .interface import (
    TaskState,
    submit_job,
    delete_job,
    status_job,
    status_task,
    get_stdout_task,
    features
)
from .decription import TaskSpec, JobSpec
from .config import *