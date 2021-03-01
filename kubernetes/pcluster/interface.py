from .decription import ContainerSpec, TaskSpec, JobSpec
from kubernetes.client.rest import ApiException
from typing import Dict
import enum


NAMESPACE = 'default'
GROUP = 'batch.volcano.sh'
VERSION = 'v1alpha1'
PLURAL = 'jobs'
PRETTY = 'true'
API_VERSION = 'batch.volcano.sh/v1alpha1'
KIND = 'Job'

RATIO_LIMIT_RESOURCES_TO_REQUESTS = 1

RUNENVS = [
    {
        "os": "Linux",
        "extension_node": None,
        "runenv": ("PYTHON3", 42),
        "feature" : ("ABAQUS","v2021.05")
    },
    {
        "os": "Linux",
        "extension_node": None,
        "runenv": ("PYTHON3", 42),
        "feature" : ("EXCEL","2020")
    },
    {
        "os": "Linux",
        "extension_node": None,
        "runenv": ("COBOL", 42),
        "feature" : ("NX","2020")
    },
]

class TaskState(enum.Enum):
    """Task states.

    From the scheduler point of view, each task can be in one of the
    following states:
        PENDING A task is not started yet.
        IDLE: A task consumes insignificant amount of resources.
        LOADED: A task consumes memory, but does not consume CPU.
        ACTIVE: A task consumes both CPU and memory.
        COMPLETED: A task is finished.
        FAILED: Task failed.
        CANCELLED: Task canceled and removed from the queue.
    """

    PENDING = enum.auto()
    RUNNING = enum.auto()
    COMPLETED = enum.auto()

class Client:
    def __init__(self, custom_object_api, core_api):
        self.custom_object_api = custom_object_api
        self.core_api = core_api
    
    def container_spec_to_dict(self, container_spec: ContainerSpec) -> Dict:
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


    def task_spec_to_dict(self, task_spec: TaskSpec) -> Dict:
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
            container = self.container_spec_to_dict(container_spec)
            task['template']['spec']['containers'].append(container)
        
        return task


    def job_spec_to_dict(self, job_spec: JobSpec) -> Dict:
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
            task = self.task_spec_to_dict(task_spec)
            job['spec']['tasks'].append(task)
        
        return job
    
    def _call_api(self, method, *args, **kwargs):
        try:
            return method(*args, **kwargs)
        except ApiException as ex:
            raise BaseException(f"Failed to call '{method.__name__}': {ex}") from ex
    
    def submit_job(self, job: JobSpec):
        return self._call_api(self.custom_object_api.create_namespaced_custom_object,
            GROUP, VERSION, NAMESPACE, PLURAL, self.job_spec_to_dict(job))
    
    def delete_job(self, job_name: str):
        return self._call_api(self.custom_object_api.delete_namespaced_custom_object,
            GROUP, VERSION, NAMESPACE, PLURAL, job_name)
    
    def status_job(self, job_name: str):
        return self._call_api(self.custom_object_api.get_namespaced_custom_object_status,
            GROUP, VERSION, NAMESPACE, PLURAL, job_name)['status']['state']['phase']
    
    def get_pod_name_by_task_name(self, task_name: str):
        return self._call_api(self.core_api.list_namespaced_pod,
            NAMESPACE, label_selector='task-name=%s' % task_name).to_dict()['items'][0]['metadata']['name']
    
    def status_task(self, pod_name: str):
        return self._call_api(self.core_api.read_namespaced_pod_status,
            pod_name, NAMESPACE).to_dict()['status']['phase']

    def delete_task(self, pod_name: str):
        return self._call_api(self.core_api.delete_namespaced_pod,
            pod_name, NAMESPACE)

    def get_stdout_task(self, pod_name: str):
        return self._call_api(self.core_api.read_namespaced_pod_log, 
            pod_name, NAMESPACE)


# def submit_job(job: Dict, client):
#     try:
#         api_response = client.create_namespaced_custom_object(
#             GROUP, VERSION, NAMESPACE, PLURAL, job)
#         return api_response
#     except ApiException as e:
#         raise BaseException("Exception when calling CustomObjectsApi->create_cluster_custom_object: %s\n" % e)


# def delete_job(job_name: str, client):
#     try:
#         api_response = client.delete_namespaced_custom_object(
#             GROUP, VERSION, NAMESPACE, PLURAL, job_name)
#         return api_response
#     except ApiException as e:
#         raise BaseException("Exception when calling CustomObjectsApi->delete_namespaced_custom_object: %s\n" % e)


# def status_job(job_name: str, client):
#     try:
#         api_response = client.get_namespaced_custom_object_status(GROUP, VERSION, NAMESPACE, PLURAL, job_name)
#         return api_response['status']['state']['phase']
#     except ApiException as e:
#         BaseException("Exception when calling CustomObjectsApi->get_namespaced_custom_object_status: %s\n" % e)


# def get_pod_name_by_task_name(task_name: str, client):
#     try:
#         api_response = client.list_namespaced_pod(
#             NAMESPACE, label_selector='task-name=%s' % task_name
#         ).to_dict()['items'][0]['metadata']['name']
#         return api_response
#     except ApiException as e:
#         raise BaseException("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)   


# def status_task(pod_name: str, client):
#     try:
#         api_response = client.read_namespaced_pod_status(
#             pod_name, NAMESPACE)
#         return api_response.to_dict()['status']['phase']
#     except ApiException as e:
#         raise BaseException("Exception when calling CoreV1Api->read_namespaced_pod_status: %s\n" % e)


# def delete_task(pod_name: str, client):
#     try:
#         api_response = client.delete_namespaced_pod(
#             pod_name, NAMESPACE)
#         return api_response
#     except ApiException as e:
#         raise BaseException("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)


# def get_stdout_task(pod_name: str, client):
#     try:
#         api_response = client.read_namespaced_pod_log(
#             pod_name, NAMESPACE)
#         return api_response
#     except ApiException as e:
#         raise BaseException("Exception when calling CoreV1Api->read_namespaced_pod_log: %s\n" % e)


def features(runenvs):
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
