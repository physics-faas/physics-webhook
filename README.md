# physics-webhook
Webhook for the PHYSICS EU project

## How to deploy it

* First build the image of the webhook (or use the one I already created at
  docker.io/luis5tb/physics-webhook) and push it to your repo:

```
podman build -t docker.io/luis5tb/physics-webhook .
podman push docker.io/luis5tb/physics-webhook
```

* Create the CA and certificates
```
openssl req -nodes -new -x509 -keyout ca.key -out ca.crt -subj "/CN=Admission Controller Webhook PHYSICS CA"

openssl genrsa -out webhook-server-tls.key 2048

openssl req -new -key webhook-server-tls.key -subj "/CN=physics-admission-controller.physics-infra.svc" | openssl x509 -req -CA ca.crt -CAkey ca.key -CAcreateserial -out webhook-server-tls.crt
```

* Create the physics-admin namespace

```
kubectl create namespace physics-infra
```

* Create the TLS secret or copy the information into the 002-webhook-secret.yaml
```
kubectl create secret tls physics-admission-controller-secret --key=webhook-server-tls.key --cert=webhook-server-tls.crt -n physics-infra
```

* Add the caBundle to the MutatingWebHookConfiguration
```
cat ca.crt | base64
(copy output)
vi 004-webhook.yaml (replace ADD_CA_BUNDLE with the copied base64 ca.crt)
```

* Create the resources:

```
kubectl apply -f 001-service.yaml
kubectl apply -f 002-webhook-secret.yaml (only if tls secret not created in
previous step)
kubectl apply -f 003-admission-controller.yaml
kubectl apply -f 004-webhook.yaml
```

## How to use it

To make it less intrussive, the webhook only applies to pods created in certain
namespaces. This namespaces must be labelled with the label stated at the
namespaceSelector on 004-webhook.yaml. If not modified, `physics-webhook:
enabled`.

So, to make the webhook to apply in the pods created in a certain namespace you
need to edit it and add that label.

```
oc edit namespace NAMESPACE_NAME
```

Once that is done, you need to state in the pods what scheduler to use, if
different from the default. This is done by adding an specific annotation:

* With the key speficied at the 003-admission-controller when starting the
  webhook_sever, by default `physics-scheduler` (option
  `--scheduler-label=physics-scheduler`)

* With the value of the scheduler to use. For instance, if the scheduler name is
  `energy-aware`, the pod must be annotated as:

```
apiVersion: v1
kind: Pod
metadata:
  annotations:
    *physics-scheduler: energy*
  labels:
    run: test
  name: test
  namespace: physics-infra
spec:
  containers:
  - image: kuryr/demo
    imagePullPolicy: Always
    name: test
```

Then, you can simply create your pod as check the schedulerName is set
accordingly:

```
kubectl create -f pod.yaml
kubectl get pod test -o yaml | grep schedulerName
  schedulerName: energy-aware
```

