"""
Description of the entities that are needed for the pcluster
"""

import dataclasses
from typing import List, Tuple, Optional, Dict

PENDING = 'Pending'
RUNNING = 'Running'
COMPLETED = 'Completed'

# @dataclasses.dataclass
# class VolumeMountsSpec:
#     # https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#volumemount-v1-core

#     # This must match the Name of a Volume.
#     name: str

#     # Path within the container at which the volume should be mounted.
#     # Must not contain ':'.
#     mount_path: str


@dataclasses.dataclass
class ExecutorSpec:
    """Executor specification."""
    # https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#container-v1-core

    # Name of the container specified as a DNS_LABEL. 
    # Each container in a pod must have a unique name (DNS_LABEL)
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

    # Compute Resources required by this container
    # More info:
    # https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/
    cpu: float
    memory: int

    storage: Dict[str, str]

    # Directory to run task in. None runs it in a temporary directory.
    cwd: Optional[str] = None

    os: str = "Linux"


    # Pod volumes to mount into the container's filesystem.
    volume_mounts: Dict[str, str] = None

    extension_node: Optional[str] = None
    image: str = None

    def __post_init__(self):
        """Post init validation checks."""
        assert self.exec, "Path to the task executable is missing!"
        self.image = \
            f'pseven-calc-{self.runenv[0].lower()}-{self.runenv[1]}-{self.require[0].lower()}-{self.require[1]}'
        for key in self.storage:
            self.env[f'DA__P7__PCLUSTER__STORAGE__{key}'] = self.storage[key]
        assert 1 <= self.owner <= 9999, "User ID must be between 1 and 9999"
        

@dataclasses.dataclass
class QueueSpec:
    """Queue specification."""
    # Queue name
    name: str

    # Capability indicates the upper limit of resources the queue can use.
    # It is a hard constraint.
    cpu: float
    memory: int

    # The weight of queue to share the resources with each other.
    # Weight indicates the relative weight of a queue in cluster resource division.
    weight: int = 1

    # Reclaimable specifies whether to allow other queues to reclaim
    # extra resources occupied by a queue when the queue uses more
    # resources than allocated. The default value is true.
    reclaimable: bool = True


    def __post_init__(self):
        """Post init validation checks."""
        assert self.name, "The queue must have a name"


@dataclasses.dataclass
class TaskSpec:
    """Task specification."""
    # Name specifies the name of task
    name: str

    container: ExecutorSpec

    # Replicas specifies the replicas of this TaskSpec in Job
    replicas: int = 1
    volume_name: str = None
    claim_name: str = None

    def __post_init__(self):
        assert self.name, "The task must have a name"
        assert len(self.containers) > 0, "Task has no containers"
    

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
