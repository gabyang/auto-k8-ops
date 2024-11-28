# Automating Kubernetes Operations
Many of the task that we can perform are same, boring and easy to automate. Oftentimes it's simple enough to whip up a quick shell script with a bunch of kubectl commands, but for more complicated automation tasks bash just isn't good enough, and you need the power of proper language, such as Python. This repository is experimenting with how we can do that

The cluster is using a Service Account to generate long-lived tokens. The tokens can be easily retrieved through running these commands:
```
kubectl create sa playground
kubectl describe sa playground
export KIND_TOKEN=$(kubectl get secret playground-token-<token hash> -o json | jq -r .data.token | base64 --decode)
```

Check to see if the authentication works:
```
curl -k -X GET -H "Authorization: Bearer $KIND_TOKEN" <URL of application control plane>/apis
```

create cluster role and role binding
```
kubectl create clusterrole manage-pods \
    --verb=get --verb=list --verb=watch --verb=create --verb=update --verb=patch --verb=delete \
    --resource=pods

kubectl -n default create rolebinding sa-manage-pods \
    --clusterrole=manage-pods \
    --serviceaccount=default:playground

kubectl create clusterrolebinding sa-cluster-admin \
  --clusterrole=cluster-admin \
  --serviceaccount=default:playground
```