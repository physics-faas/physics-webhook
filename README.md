# physics-webhook
Webhook for the PHYSICS EU project

## How to use

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

* Create the TLS secret or copy the information into the 002-webhook-secret.yaml
```
kubectl create secret tls physics-admission-controller-secret --key=webhook-server-tls.key --cert=webhook-server-tls.crt
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
