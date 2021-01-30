from kubernetes import client, config
from kubernetes.client.rest import ApiException
from pprint import pprint


def main():
    job = {
        "apiVersion": "batch.volcano.sh/v1alpha1",
        "kind": "Job",
        "metadata": {"name": "job-sleep5",
		    "namespace": "default"},
        "spec": {
            "minAvailable": 1,
            "queue": "great-queue",
            "schedulerName": "volcano",
            "tasks": [
                {
                    "name": "python",
                    "replicas": 1,
                    "template": {
                        "spec": {
                            "containers": [
                                {
                                    "command": [
                                        "python3",
                                        "-c",
                                        "import time; print('START'); time.sleep(20); print('OK')"
                                    ],
                                    "image": "python",
                                    "name": "python"
                                }
                            ],
                            "restartPolicy": "Never"
                        }
                    }
                }
            ]
        }
    }
    configuration = client.Configuration()
    configuration.host = "http://localhost:8080"
    # Create a job object with client-python API. The job we
    # created is same as the `pi-job.yaml` in the /examples folder.
    with client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
        api_instance = client.CustomObjectsApi(api_client)
    namespace = 'default'
    group = 'batch.volcano.sh' # str | the custom resource's group
    version = 'v1alpha1' # str | the custom resource's version
    plural = 'jobs' # str | the custom resource's plural name. For TPRs this would be lowercase plural kind.
    body = job # object | The JSON schema of the Resource to create.
    pretty = 'true'
    try:
        api_response = api_instance.create_namespaced_custom_object(group, version, namespace, plural, body, pretty=pretty)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling CustomObjectsApi->create_cluster_custom_object: %s\n" % e)


if __name__ == '__main__':
    main()