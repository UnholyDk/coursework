from kubernetes import client

configuration = client.Configuration()
configuration.host = "http://localhost:8080"

with client.ApiClient(configuration) as api_client:
	custom_object_api = client.CustomObjectsApi(api_client)
	core_api = client.CoreV1Api(api_client)


NAMESPACE = 'default'
GROUP = 'batch.volcano.sh'
VERSION = 'v1alpha1'
PLURAL = 'jobs'
PRETTY = 'true'
API_VERSION = 'batch.volcano.sh/v1alpha1'
KIND = 'Job'

RATIO_LIMIT_RESOURCES_TO_REQUESTS = 1

# schedulerName indicates the scheduler that will schedule the job. 
# Currently, the value can be volcano or default-scheduler, withvolcano` selected by default.
SCHEDULER = "volcano"

# Specifies the queue that will be used in the scheduler, 
# "default" queue is used this leaves empty.
QUEUE = 'test'

VOLUME_NAME = 'storage'
CLAIM_NAME = 'dir-data-claim'

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