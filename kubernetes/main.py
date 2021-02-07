from pcluster.submit import *
from pcluster.decription import TaskSpec, JobSpec, VolumeMountsSpec, ContainerSpec

from pprint import pprint
import time
from kubernetes import client, config
from kubernetes.client.rest import ApiException


configuration = client.Configuration()
configuration.host = "http://localhost:8080"

with client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    custom_object_api = client.CustomObjectsApi(api_client)
    core_api = client.CoreV1Api(api_client)


task1 = TaskSpec(
    name='task1-name',
    volume_name='storage',
    claim_name='dir-data-claim',
    containers=[
        ContainerSpec(
            name='container1-name',
            image='busybox',
            command=["sh", "-c","echo 'Hello123' | tee -a /logs/hello.txt"],
            volume_mounts=VolumeMountsSpec(name='storage', mount_path='/logs')
        )
    ]
)

task2 = TaskSpec(
    name='task2-name',
    volume_name='storage',
    claim_name='dir-data-claim',
    containers=[
        ContainerSpec(
            name='container2-name',
            image='python',
            command=["python3", "-c", "import time; print('START'); time.sleep(5); print('OK')"],
            volume_mounts=VolumeMountsSpec(name='storage', mount_path='/logs')
        )
    ]
)

NAME_JOB = 'job-name'

job1 = JobSpec(
    name=NAME_JOB,
    tasks=[task1, task2],
    queue='test'
)



# response = submit_job(job_spec_to_dict(job1), custom_object_api)
# print('Job successful created with uid: %s' % response['metadata']['uid'])

# print('Sleeping 6 second ...')
# time.sleep(6)

# response = status_job(NAME_JOB, custom_object_api)['state']['phase']
# print('Status job: %s' % status_job(NAME_JOB, custom_object_api)['state']['phase'])
# print('-' * 20)


# print('Sleeping 3 second ...')
# time.sleep(3)
# print('Status job: %s' % status_job(NAME_JOB, custom_object_api)['state']['phase'])
# print('-' * 20)

response = get_pod_name_by_task_name('task2-name', core_api)
pprint(response)

response = delete_task(response, core_api)
pprint(response)

# print('Sleeping 5 second ...')
# time.sleep(5)
# print('Status job: %s' % status_job(NAME_JOB, custom_object_api)['state']['phase'])
# print('-' * 20)


# print('Sleeping 3 second ...')
# time.sleep(3)

# response = delete_job('job-name', custom_object_api)
# print('Job deleted with status: %s' % response['status'])
