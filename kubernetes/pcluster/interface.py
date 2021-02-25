from .decription import JobSpec, TaskSpec, ContainerSpec, VolumeMountsSpec
from typing import Dict


from kubernetes import client, config
from kubernetes.client.rest import ApiException


NAMESPACE = 'default'
GROUP = 'batch.volcano.sh'
VERSION = 'v1alpha1'
PLURAL = 'jobs'
PRETTY = 'true'
API_VERSION = 'batch.volcano.sh/v1alpha1'
KIND = 'Job'

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
