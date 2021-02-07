import dataclasses
from typing import List


@dataclasses.dataclass
class VolumeMountsSpec:
    name: str
    mount_path: str


@dataclasses.dataclass
class ResourceSpec:
    memory: str = None
    cpu: str = None


@dataclasses.dataclass
class ContainerSpec:
    name: str
    image: str
    command: List[str]
    volume_mounts: VolumeMountsSpec = None

    resourses_requests: ResourceSpec = None
    resourses_limit: ResourceSpec = None


@dataclasses.dataclass
class QueueSpec:
    # Queue name
    name: str

    # The weight of queue to share the resources with each other.
    # Weight indicates the relative weight of a queue in cluster resource division.
    weight: int = 1

    # Reclaimable specifies whether to allow other queues to reclaim
    # extra resources occupied by a queue when the queue uses more
    # resources than allocated. The default value is true.
    reclaimable: bool = True

    # Capability indicates the upper limit of resources the queue can use.
    # It is a hard constraint.
    capability: ResourceSpec = None

    def __post_init__(self):
        """Post init validation checks."""
        assert self.name, "The queue must have a name"


@dataclasses.dataclass
class TaskSpec:

    # Name specifies the name of task
    name: str

    containers: List[ContainerSpec]

    # Replicas specifies the replicas of this TaskSpec in Job
    replicas: int = 1
    volume_name: str = None
    claim_name: str = None

    def __post__init__(self):
        assert self.name, "The task must have a name"
        assert len(self.containers) > 0, "Task has no containers"
    

@dataclasses.dataclass
class JobSpec:
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

    # # Specifies the maximum number of retries before marking this Job failed. 
    # # Defaults to 3.
    # max_retry: int = 3

    def __post_init__(self):
        """Post init validation checks."""
        assert self.name, "The Job must have a name"

        assert len(self.tasks) > 0, "Job has no tasks"
        
        if self.min_available is None:
            self.min_available = len(self.tasks)
