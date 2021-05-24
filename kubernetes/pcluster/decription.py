"""
Description of the entities that are needed for the pcluster
"""

import dataclasses
from typing import List, Tuple, Optional, Dict

PENDING = 'Pending'
RUNNING = 'Running'
COMPLETED = 'Completed'


@dataclasses.dataclass
class TaskSpec:
    """Task specification."""
    # Name specifies the name of task
    name: str

    # Entrypoint array. Not executed within a shell. 
    # The docker image's ENTRYPOINT is used if this is not provided.
    # Variable references $(VAR_NAME) are expanded using the container's environment.
    # If a variable cannot be resolved, the reference in the input string will be unchanged.
    # The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME).
    # Escaped references will never be expanded, regardless of whether the variable exists or not.
    # Cannot be updated. More info:
    # https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/#running-a-command-in-a-shell
    exec: List[str]

    owner: int

    # Environment variables for the task: name:value.
    env: Dict[str, str]

    runenv: Tuple[str, int]
    require: Optional[Tuple[str, Optional[str]]]

    storage: Dict[str, str]

    # Compute Resources required by this container
    # More info:
    # https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/
    cpu: float
    memory: int

    # Pod volumes to mount into the container's filesystem.
    volume_mounts: Dict[str, str] = None

    # Directory to run task in. None runs it in a temporary directory.
    cwd: Optional[str] = None

    os: str = "Linux"

    extension_node: Optional[str] = None

    # Replicas specifies the replicas of this TaskSpec in Job
    replicas: int = 1
    volume_name: str = None
    claim_name: str = None

    def __post_init__(self):
        assert self.name, "The task must have a name"
        assert self.exec, "Path to the task executable is missing!"
        assert 1 <= self.owner <= 9999, "User ID must be between 1 and 9999"
    

@dataclasses.dataclass
class JobSpec:
    """Job specification."""
    # Job name
    name: str

    # Tasks specifies the task specification of Job
    tasks: List[TaskSpec]

    # The minimal available pods to run for this Job
	# Defaults to the summary of tasks' replicas
    min_available: int = None

    # schedulerName indicates the scheduler that will schedule the job. 
    # Currently, the value can be volcano or default-scheduler, withvolcano` selected by default.
    scheduler_name: str = "volcano"

    # Specifies the queue that will be used in the scheduler, 
    # "default" queue is used this leaves empty.
    queue: str = "default"

    def __post_init__(self):
        """Post init validation checks."""
        assert self.name, "The Job must have a name"

        assert len(self.tasks) > 0, "Job has no tasks"
        
        if self.min_available is None:
            self.min_available = len(self.tasks)
