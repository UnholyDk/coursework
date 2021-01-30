import dataclasses
from typing import List


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
    cpu: int = None
    memory: str = None # Example value: "4096Mi", "4Gi"

    def __post_init__(self):
        """Post init validation checks."""
        assert self.name, "The queue must have a name"


@dataclasses.dataclass
class TaskSpec:
    pass


@dataclasses.dataclass
class JobSpec:
    # Job name
    name: str

    # The minimal available pods to run for this Job
	# Defaults to the summary of tasks' replicas
    min_available: int = None

    # schedulerName indicates the scheduler that will schedule the job. 
    # Currently, the value can be volcano or default-scheduler, withvolcano` selected by default.
    scheduler_name: str = "volcano"

    # Specifies the queue that will be used in the scheduler, 
    # "default" queue is used this leaves empty.
    queue: str = "default"

    # Specifies the maximum number of retries before marking this Job failed. 
    # Defaults to 3.
    max_retry: int = 3

    # Tasks specifies the task specification of Job
    tasks: List[TaskSpec]

    def __post_init__(self):
        """Post init validation checks."""
        assert self.name, "The Job must have a name"

        assert len(self.tasks) > 0, "Job has no tasks"
        
        if self.min_available is None:
            self.min_available = len(self.tasks)


