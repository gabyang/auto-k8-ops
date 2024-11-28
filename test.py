from kubernetes import client, watch
import os

'''
This code here defines the configuration object which tells the client that we will authenticate using Bearer token.
'''
configuration = client.Configuration()
configuration.api_key_prefix["authorization"] = "Bearer"
configuration.host = "https://127.0.0.1:63382"
configuration.api_key["authorization"] = os.getenv("KIND_TOKEN", None)

# For testing purposes
configuration.verify_ssl = False

api_client = client.ApiClient(configuration)
v1 = client.CoreV1Api(api_client)

ret = v1.list_namespaced_pod(namespace="default", watch=False)
for pod in ret.items:
    print(f"Name: {pod.metadata.name}, Namespace: {pod.metadata.namespace} IP: {pod.status.pod_ip}")


'''
The following code here creates a deployment 
'''
deployment_name = "my-deploy"
deployment_manifest = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {"name": deployment_name, "namespace": "default"},
    "spec": {"replicas": 3,
             "selector": {
                "matchLabels": {
                    "app": "nginx"
                }},
        "template": {"metadata": {"labels": {"app": "nginx"}},
            "spec": {"containers": [
                {"name": "nginx", "image": "nginx:1.21.6", "ports": [{"containerPort": 80}]}]
            }
        },
    }
}

import time
from kubernetes.client.rest import ApiException

v1 = client.AppsV1Api(api_client)

response = v1.create_namespaced_deployment(body=deployment_manifest, namespace="default")
while True:
    try:
        response = v1.read_namespaced_deployment_status(name=deployment_name, namespace="default")
        if response.status.available_replicas != 3:
            print("Waiting for Deployment to become ready...")
            time.sleep(5)
        else:
            break
    except ApiException as e:
        print(f"Exception when calling AppsV1Api -> read_namespaced_deployment_status: {e}\n")


'''
We want to watch for Events beyond CRUD operations
'''
from functools import partial

v1 = client.CoreV1Api(api_client)

count = 10
w = watch.Watch()
for event in w.stream(partial(v1.list_namespaced_event, namespace="default"), timeout_seconds=10):
    print(f"Event - Message: {event['object']['message']} at {event['object']['metadata']['creationTimestamp']}")
    count -= 1
    if not count:
        w.stop()
print("Finished namespace stream.")
