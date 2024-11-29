# Automating `kubectl rollout restart`
from kubernetes import dynamic
from kubernetes.client import api_client
from kubernetes import client
import datetime
import os

'''
The way kubectl does it is by updating Deployment Annotations, more specifically, 
setting kubectl.kubernetes.io/restartedAt to current time. This works because any 
change made to Pod spec causes a restart.
'''

configuration = client.Configuration()
configuration.api_key_prefix["authorization"] = "Bearer"
configuration.host = "https://127.0.0.1:63382"
configuration.api_key["authorization"] = os.getenv("KIND_TOKEN", None)
configuration.verify_ssl = False
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

client = dynamic.DynamicClient(api_client.ApiClient(configuration=configuration))

api = client.resources.get(api_version="apps/v1", kind="Deployment")

deployment_manifest["spec"]["template"]["metadata"]["annotations"] = {
    "kubectl.kubernetes.io/restartedAt": datetime.datetime.now(datetime.timezone.utc).isoformat()
}

deployment_patched = api.patch(body=deployment_manifest, name=deployment_name, namespace="default")

'''
Success! Running `kubectl describe deployment` shows:

Events:
  Type    Reason             Age   From                   Message
  ----    ------             ----  ----                   -------
  Normal  ScalingReplicaSet  47s   deployment-controller  Scaled up replica set my-deploy-5bf69b7449 to 1
  Normal  ScalingReplicaSet  46s   deployment-controller  Scaled down replica set my-deploy-cb69f686c to 2
  Normal  ScalingReplicaSet  46s   deployment-controller  Scaled up replica set my-deploy-5bf69b7449 to 2
  Normal  ScalingReplicaSet  45s   deployment-controller  Scaled down replica set my-deploy-cb69f686c to 1
  Normal  ScalingReplicaSet  45s   deployment-controller  Scaled up replica set my-deploy-5bf69b7449 to 3
  Normal  ScalingReplicaSet  44s   deployment-controller  Scaled down replica set my-deploy-cb69f686c to 0

it shows the gradual process of scaling down the old ReplicaSet and scaling up the new one during the rollout
'''
