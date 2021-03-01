from typing import Dict
from .decription import ContainerSpec, TaskSpec, JobSpec


NAMESPACE = 'default'
GROUP = 'batch.volcano.sh'
VERSION = 'v1alpha1'
PLURAL = 'jobs'
PRETTY = 'true'
API_VERSION = 'batch.volcano.sh/v1alpha1'
KIND = 'Job'

RATIO_LIMIT_RESOURCES_TO_REQUESTS = 1


def container_spec_to_dict(container_spec: ContainerSpec) -> Dict:
    container = {}
    container['command'] = container_spec.exec
    container['image'] = container_spec.image
    container['name'] = container_spec.name

    container['resources'] = {}

    container['resources']['limits'] = {}
    container['resources']['requests'] = {}
    if container_spec.cpu is not None:
        container['resources']['limits']['cpu'] = container_spec.cpu
        container['resources']['requests']['cpu'] = RATIO_LIMIT_RESOURCES_TO_REQUESTS * container_spec.cpu
    if container_spec.memory is not None:
        container['resources']['limits']['memory'] = container_spec.memory
        container['resources']['requests']['memory'] = RATIO_LIMIT_RESOURCES_TO_REQUESTS * container_spec.memory

    if container_spec.volume_mounts is not None:
        container['volumeMounts'] = []
        volume_mount = {}
        for name in container_spec.volume_mounts:
            volume_mount['name'] = name
            volume_mount['mountPath'] = container_spec.volume_mounts[name]
            container['volumeMounts'].append(volume_mount)
    
    container['env'] = []
    for env_name in container_spec.env:
        key_value = {}
        key_value['name'] = env_name
        key_value['value'] = container_spec.env[env_name]
        container['env'].append(key_value)
    
    container['securityContext'] = {}
    container['securityContext']['runAsGroup'] = container_spec.owner + 20000
    container['securityContext']['runAsUser'] = container_spec.owner + 20000
    container['securityContext']['runAsNonRoot'] = True
    container['securityContext']['allowPrivilegeEscalation'] = False

    if container_spec.cwd is not None:
        container['workingDir'] = container_spec.cwd
    return container


def task_spec_to_dict(task_spec: TaskSpec) -> Dict:
    task = {}
    task['name'] = task_spec.name
    task['replicas'] = task_spec.replicas
    task['template'] = {'spec': {'containers': [], 'restartPolicy': 'Never'}}

    
    task['template']['metadata'] = {}
    task['template']['metadata']['labels'] = {'task-name': task_spec.name}

    if task_spec.volume_name is not None:
        volume = {}
        volume['name'] = task_spec.volume_name
        volume['persistentVolumeClaim'] = {'claimName': task_spec.claim_name}
        task['template']['spec']['volumes'] = [volume]

    for container_spec in task_spec.containers:
        container = container_spec_to_dict(container_spec)
        task['template']['spec']['containers'].append(container)
    
    return task


def job_spec_to_dict(job_spec: JobSpec) -> Dict:
    job = {}
    job['apiVersion'] = API_VERSION
    job['kind'] = KIND
    job['metadata'] = {'name': job_spec.name, 'namespace': NAMESPACE}
    job['spec'] = {}
    job['spec']['minAvailable'] = job_spec.min_available
    job['spec']['queue'] = job_spec.queue
    job['spec']['schedulerName'] = job_spec.scheduler_name
    job['spec']['tasks'] = []

    for task_spec in job_spec.tasks:
        task = task_spec_to_dict(task_spec)
        job['spec']['tasks'].append(task)
    
    return job