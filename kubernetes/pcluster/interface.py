"""
class Client
for calls to different methods associated with jobs and tasks
"""

from .decription import TaskSpec, JobSpec
from kubernetes.client.rest import ApiException
from .config import *
from typing import Dict
import enum

PENDING = 'Pending'
RUNNING = 'Running'
COMPLETED = 'Completed'

class TaskState(enum.Enum):
    """Task states.

    From the scheduler point of view, each task can be in one of the
    following states:
        PENDING A task is not started yet.
        RUNNING A task started
        COMPLETED: A task is finished.
    """
    PENDING = enum.auto()
    RUNNING = enum.auto()
    COMPLETED = enum.auto()


def _task_spec_to_k8s_spec(task_spec: TaskSpec, job_spec: JobSpec) -> Dict:
    """
    A function that an object of the taskspec class writes to a dictionary
    for further sending an api request
    """
    task = {}
    task['name'] = task_spec.name
    task['replicas'] = 1
    task['template'] = {'spec': {'containers': [], 'restartPolicy': 'Never'}}

    
    task['template']['metadata'] = {}
    task['template']['metadata']['labels'] = {
        'task-name': task_spec.name,
        'job-name': job_spec.name}

    volume = {}
    volume['name'] = VOLUME_NAME
    volume['persistentVolumeClaim'] = {'claimName': CLAIM_NAME}
    task['template']['spec']['volumes'] = [volume]

    container = {}
    container['command'] = task_spec.exec
    container['image'] = \
        f'pseven-calc-{task_spec.runenv[0].lower()}-{task_spec.runenv[1]}-{task_spec.require[0].lower()}-{task_spec.require[1]}'
    container['name'] = task_spec.name

    container['resources'] = {}

    container['resources']['limits'] = {}
    container['resources']['requests'] = {}
    if task_spec.cpu is not None:
        container['resources']['limits']['cpu'] = task_spec.cpu
        container['resources']['requests']['cpu'] = RATIO_LIMIT_RESOURCES_TO_REQUESTS * task_spec.cpu
    if task_spec.memory is not None:
        container['resources']['limits']['memory'] = task_spec.memory
        container['resources']['requests']['memory'] = RATIO_LIMIT_RESOURCES_TO_REQUESTS * task_spec.memory

    container['volumeMounts'] = []
    volume_mount = {}
    for path in task_spec.storage.values():
        volume_mount['name'] = VOLUME_NAME
        volume_mount['mountPath'] = path
        container['volumeMounts'].append(volume_mount)
    
    container['env'] = []
    for env_name in task_spec.env:
        key_value = {}
        key_value['name'] = env_name
        key_value['value'] = task_spec.env[env_name]
        container['env'].append(key_value)
    
    for env_name in task_spec.storage:
        key_value = {}
        key_value['name'] = f'DA__P7__PCLUSTER__STORAGE__{env_name}'
        key_value['value'] = task_spec.storage[env_name]
        container['env'].append(key_value)
    
    container['securityContext'] = {}
    container['securityContext']['runAsGroup'] = job_spec.owner + 20000
    container['securityContext']['runAsUser'] = job_spec.owner + 20000
    container['securityContext']['runAsNonRoot'] = True
    container['securityContext']['allowPrivilegeEscalation'] = False

    if task_spec.cwd is not None:
        container['workingDir'] = task_spec.cwd
    task['template']['spec']['containers'].append(container)
    
    return task


def _job_spec_to_k8s_spec(job_spec: JobSpec) -> Dict:
    """
    A function that an object of the jobspec class writes to a dictionary
    for further sending an api request
    """
    job = {}
    job['apiVersion'] = API_VERSION
    job['kind'] = KIND
    job['metadata'] = {'name': job_spec.name, 'namespace': NAMESPACE}
    job['spec'] = {}
    job['spec']['minAvailable'] = len(job_spec.tasks)
    job['spec']['queue'] = QUEUE
    job['spec']['schedulerName'] = SCHEDULER
    job['spec']['tasks'] = []

    for task_spec in job_spec.tasks:
        task = _task_spec_to_k8s_spec(task_spec, job_spec)
        job['spec']['tasks'].append(task)
    
    return job

def _call_api(method, *args, **kwargs):
    try:
        return method(*args, **kwargs)
    except ApiException as ex:
        raise BaseException(f"Failed to call '{method.__name__}': {ex}") from ex

def submit_job(job: JobSpec):
    """
    Send a job to the queue
    """
    return _call_api(custom_object_api.create_namespaced_custom_object,
        GROUP, VERSION, NAMESPACE, PLURAL, _job_spec_to_k8s_spec(job))

def delete_job(job: JobSpec):
    """
    Remove a job from the queue
    """
    return _call_api(custom_object_api.delete_namespaced_custom_object,
        GROUP, VERSION, NAMESPACE, PLURAL, job.name)

def status_job(job_name: str):
    """
    Status job
    """
    phase = _call_api(custom_object_api.get_namespaced_custom_object_status,
        GROUP, VERSION, NAMESPACE, PLURAL, job_name)['status']['state']['phase']
    if phase == RUNNING:
        return TaskState.RUNNING
    elif phase == COMPLETED:
        return TaskState.COMPLETED
    elif phase == PENDING:
        return TaskState.PENDING

def _get_pod_name_by_task_name(task_name: str, job_name: str):
    """
    Get the name of the pod that matches the task
    """
    return _call_api(core_api.list_namespaced_pod,
        NAMESPACE, label_selector='task-name=%s,job-name=%s' % (task_name, job_name)).to_dict()['items'][0]['metadata']['name']

def status_task(task_name: str, job_name: str):
    """
    Status task
    """
    pod_name = _get_pod_name_by_task_name(task_name, job_name)
    phase = _call_api(core_api.read_namespaced_pod_status,
        pod_name, NAMESPACE).to_dict()['status']['phase']
    if phase == RUNNING:
        return TaskState.RUNNING
    elif phase == COMPLETED:
        return TaskState.COMPLETED
    elif phase == PENDING:
        return TaskState.PENDING


def get_stdout_task(task_name: str, job_name: str):
    """
    Get an output task
    """
    pod_name = _get_pod_name_by_task_name(task_name, job_name)
    return _call_api(core_api.read_namespaced_pod_log, 
        pod_name, NAMESPACE)


def features(runenvs):
    """
    Information about the capabilities of the cluster.
    show the user a list of available "features"
    and additional computational nodes.
    """
    output = {}
    for runenv in runenvs:
        if runenv['runenv'] in output:
            output[runenv['runenv']].append(runenv['feature'])
        else:
            output[runenv['runenv']] = [runenv['feature']]
    
    result = []
    for runenv in output:
        result.append(
            {
                "os": "Linux",
                "extension_node": None,
                "runenv": runenv,
                "features": output[runenv]
            }
        )
    
    return result
