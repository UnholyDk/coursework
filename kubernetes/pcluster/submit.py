import dataclasses
from .decription import JobSpec, TaskSpec, ContainerSpec, VolumeMountsSpec
from typing import Dict
from pprint import pprint


from kubernetes import client, config
from kubernetes.client.rest import ApiException


NAMESPACE = 'default'
GROUP = 'batch.volcano.sh'
VERSION = 'v1alpha1'
PLURAL = 'jobs'
PRETTY = 'true'
API_VERSION = 'batch.volcano.sh/v1alpha1'
KIND = 'Job'


def container_spec_to_dict(container_spec: ContainerSpec) -> Dict:
    container = {}
    container['command'] = container_spec.command
    container['image'] = container_spec.image
    container['name'] = container_spec.name

    container['resources'] = {}

    if container_spec.resourses_limit is not None:
        container['resources']['limits'] = {}
        if container_spec.resourses_limit.cpu is not None:
            container['resources']['limits']['cpu'] = container_spec.resourses_limit.cpu
        if container_spec.resourses_limit.memory is not None:
            container['resources']['limits']['memory'] = container_spec.resourses_limit.memory
    
    if container_spec.resourses_requests is not None:
        container['resources']['requests'] = {}
        if container_spec.resourses_requests.cpu is not None:
            container['resources']['requests']['cpu'] = container_spec.resourses_requests.cpu
        if container_spec.resourses_requests.memory is not None:
            container['resources']['requests']['memory'] = container_spec.resourses_requests.memory

    if container_spec.volume_mounts is not None:
        container['volumeMounts'] = []
        volume_mount = {}
        volume_mount['name'] = container_spec.volume_mounts.name
        volume_mount['mountPath'] = container_spec.volume_mounts.mount_path
        container['volumeMounts'].append(volume_mount)
    
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


def submit_job(job: Dict, client):
    try:
        api_response = client.create_namespaced_custom_object(
            GROUP, VERSION, NAMESPACE, PLURAL, job)
        return api_response
    except ApiException as e:
        raise BaseException("Exception when calling CustomObjectsApi->create_cluster_custom_object: %s\n" % e)


def delete_job(job_name: str, client):
    try:
        api_response = client.delete_namespaced_custom_object(
            GROUP, VERSION, NAMESPACE, PLURAL, job_name)
        return api_response
    except ApiException as e:
        raise BaseException("Exception when calling CustomObjectsApi->delete_namespaced_custom_object: %s\n" % e)


def status_job(job_name: str, client):
    try:
        api_response = client.get_namespaced_custom_object_status(GROUP, VERSION, NAMESPACE, PLURAL, job_name)
        return api_response['status']['state']['phase']
    except ApiException as e:
        BaseException("Exception when calling CustomObjectsApi->get_namespaced_custom_object_status: %s\n" % e)


def get_pod_name_by_task_name(task_name: str, client):
    try:
        api_response = client.list_namespaced_pod(
            NAMESPACE, label_selector='task-name=%s' % task_name
        ).to_dict()['items'][0]['metadata']['name']
        return api_response
    except ApiException as e:
        raise BaseException("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)   


def status_task(pod_name: str, client):
    try:
        api_response = client.read_namespaced_pod_status(
            pod_name, NAMESPACE)
        return api_response.to_dict()['status']['phase']
    except ApiException as e:
        raise BaseException("Exception when calling CoreV1Api->read_namespaced_pod_status: %s\n" % e)


def delete_task(pod_name: str, client):
    try:
        api_response = client.delete_namespaced_pod(
            pod_name, NAMESPACE)
        return api_response
    except ApiException as e:
        raise BaseException("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)


def get_stdout_task(pod_name: str, client):
    try:
        api_response = client.read_namespaced_pod_log(
            pod_name, NAMESPACE)
        return api_response
    except ApiException as e:
        raise BaseException("Exception when calling CoreV1Api->read_namespaced_pod_log: %s\n" % e)
