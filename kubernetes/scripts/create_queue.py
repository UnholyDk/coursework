import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint

queue = {
    "apiVersion": "scheduling.volcano.sh/v1beta1",
    "kind": "Queue",
    "metadata": {"name": "great-queue"},
    "spec": {
        "weight": 1,
        "reclaimable": True,
        "capability" : {
            "cpu": 2
        }
    },
    "status": {"state": "Open"}
}

configuration = kubernetes.client.Configuration()
configuration.host = "http://localhost:8080"

# Enter a context with an instance of the API kubernetes.client
with kubernetes.client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = kubernetes.client.CustomObjectsApi(api_client)
group = 'scheduling.volcano.sh' # str | the custom resource's group
version = 'v1beta1' # str | the custom resource's version
plural = 'queues' # str | the custom resource's plural name. For TPRs this would be lowercase plural kind.
body = queue # object | The JSON schema of the Resource to create.
pretty = 'true'
try:
    api_response = api_instance.create_cluster_custom_object(group, version, plural, body, pretty=pretty)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CustomObjectsApi->create_cluster_custom_object: %s\n" % e)
